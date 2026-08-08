import io
import os
import asyncio
import logging
import threading
from functools import partial
from google import genai
from google.genai import types
from PIL import Image

from prompt_builder import build_prompt
import usage_tracker

log = logging.getLogger(__name__)


class QuotaExceededError(RuntimeError):
    """Raised when Gemini rejects the request with a quota / 429 error, i.e.
    the daily image quota is spent. The caller maps this to a friendly
    'come back tomorrow' message instead of a generic failure."""

# Target portrait dimensions sent to Gemini as the reference input.
# Gemini mirrors the input aspect ratio, so pre-cropping to 2:3 portrait
# is the strongest signal for a 1080 × 1620 portrait output.
_TARGET_W = 1080
_TARGET_H = 1620
_TARGET_RATIO = _TARGET_W / _TARGET_H  # 0.667 (2:3)


def _to_portrait(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """
    Center-crop then resize the reference photo to 1080 × 1620 (2:3 portrait).
    Face-safe: width crops are centered; height crops keep the top portion
    (where faces typically live) and trim the bottom.
    Returns (jpeg_bytes, 'image/jpeg').
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    current_ratio = w / h

    if current_ratio > _TARGET_RATIO:
        # Image is too wide (landscape / square) — crop sides, keep full height
        new_w = int(h * _TARGET_RATIO)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < _TARGET_RATIO:
        # Image is taller than 2:3 — crop bottom, keep top (preserves face)
        new_h = int(w / _TARGET_RATIO)
        img = img.crop((0, 0, w, new_h))

    img = img.resize((_TARGET_W, _TARGET_H), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue(), "image/jpeg"

# Models that support image OUTPUT with reference image INPUT.
# Tried in order — first one that responds with an image wins.
#
# Deliberately kept to a SINGLE model. Two reasons:
#   1. Each entry is a separate Gemini request, so a fallback chain multiplies
#      the request count (and how fast quota is spent).
#   2. Image models are priced VERY differently — gemini-3-pro-image costs
#      several times gemini-3.1-flash-lite-image per image. A silent fallback to
#      a pricier model would quietly blow the campaign budget. If you add a
#      fallback here, check its price on ai.google.dev/gemini-api/docs/pricing
#      first and redo the budget math.
#
# gemini-2.5-flash-image: $30/1M output tokens, 1,290 tokens per 1024px image
# → ~$0.039/image. Chosen over gemini-3.1-flash-lite-image (~$0.0336) because
# the lite model's output quality was visibly worse on these portraits.
#
# ⚠ SHUTDOWN 2 OCT 2026. This model is scheduled for retirement partway through
# the campaign — after that date it will 404 and generation stops dead. Before
# then, switch GEMINI_MODEL to gemini-3.1-flash-image (the full model, NOT the
# lite one) and re-check the budget: it is priced higher, from ~$0.045/image.
#
# History: "gemini-2.5-flash-image-preview" (the original Nano Banana, which had
# the free 500/day tier) was RETIRED on 15 Jan 2026 and no longer appears in the
# model list. There is no free image tier on any current model — all of them
# report free_tier_requests limit: 0. Override per-deploy with GEMINI_MODEL.
IMAGE_GENERATION_MODELS = [
    "gemini-2.5-flash-image",   # ~$0.039/image — retires 2 Oct 2026
]


# ── API keys (multi-key with failover) ──────────────────────────────────────
# GEMINI_API_KEYS (comma-separated) is the primary source; the app tries each
# key in order and fails over to the next when one is out of quota/credits.
# GEMINI_API_KEY (single) is still honoured as a fallback so older configs work.
# Each key gets a stable, masked id ("1:uCbs") for logs and the usage tracker —
# the full secret is never logged.
_client_lock = threading.Lock()
_clients: dict[str, genai.Client] = {}


def _key_id(index: int, key: str) -> str:
    return f"{index + 1}:{key[-4:]}"


def load_keys() -> list[tuple[str, str]]:
    """Configured keys as (masked_id, key), read live from the environment."""
    multi = os.getenv("GEMINI_API_KEYS", "").strip()
    if multi:
        raw = [k.strip() for k in multi.split(",")]
    else:
        raw = [os.getenv("GEMINI_API_KEY", "").strip()]
    keys = [k for k in raw if k and k != "your_gemini_api_key_here"]
    return [(_key_id(i, k), k) for i, k in enumerate(keys)]


def register_configured_keys() -> None:
    """Tell the usage tracker the full key set (so it knows when ALL are
    exhausted). Call after the environment is loaded."""
    usage_tracker.register_keys([kid for kid, _ in load_keys()])


def _client_for(key: str) -> genai.Client:
    with _client_lock:
        client = _clients.get(key)
        if client is None:
            client = genai.Client(api_key=key)
            _clients[key] = client
        return client


def _generate_sync(
    image_bytes: bytes,
    mime_type: str,
    scene_id: str,
    custom_prompt: str | None = None,
    gender: str | None = None,
) -> bytes:
    keys = load_keys()
    if not keys:
        raise RuntimeError(
            "No Gemini API key configured. Set GEMINI_API_KEYS (comma-separated) "
            "or GEMINI_API_KEY in backend/.env"
        )
    # Keep the tracker's key set current (so 'all keys exhausted' is accurate).
    usage_tracker.register_keys([kid for kid, _ in keys])

    if mime_type in ("image/jpg", "image/webp"):
        mime_type = "image/jpeg"

    # Pre-crop + resize reference photo to 2:3 portrait so Gemini mirrors it
    image_bytes, mime_type = _to_portrait(image_bytes, mime_type)
    log.info("Input resized to %dx%d portrait", _TARGET_W, _TARGET_H)

    prompt = build_prompt(scene_id, custom_prompt, gender)
    log.info(
        "Generating: scene=%s custom_prompt=%s gender=%s keys=%d",
        scene_id, "yes" if custom_prompt else "no", gender or "unspecified", len(keys),
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )
    ]

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    env_model = os.getenv("GEMINI_MODEL", "").strip()
    models_to_try = ([env_model] if env_model else []) + [
        m for m in IMAGE_GENERATION_MODELS if m != env_model
    ]

    errors: dict[str, str] = {}
    any_quota = False

    # Try each key in order; fail over to the next when one is out of
    # quota/credits. A key already known exhausted today is skipped outright.
    for key_id, key in keys:
        if usage_tracker.is_key_exhausted(key_id):
            log.info("Skipping key %s — already exhausted today", key_id)
            continue

        client = _client_for(key)
        key_quota_hit = False

        for model in models_to_try:
            log.info("Trying key %s model %s", key_id, model)
            usage_tracker.record_request()  # every call counts toward the daily quota
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if part.inline_data and part.inline_data.data:
                            log.info("Success with key %s model %s", key_id, model)
                            usage_tracker.record_success(key_id)
                            return part.inline_data.data

                finish_reasons = [str(c.finish_reason) for c in response.candidates]
                errors[f"{key_id}/{model}"] = f"No image. Finish reasons: {finish_reasons}"
                usage_tracker.record_failure()
                log.warning("Key %s model %s gave no image. %s", key_id, model, finish_reasons)

            except Exception as exc:
                msg = str(exc).lower()
                errors[f"{key_id}/{model}"] = str(exc)
                log.error("Key %s model %s error: %s", key_id, model, exc)

                # Invalid key — skip this whole key, try the next one.
                if any(k in msg for k in ("api_key_invalid", "invalid api key", "401", "api key not valid")):
                    log.warning("Key %s is invalid — failing over to next key", key_id)
                    break

                # Quota/billing/credits — this key is spent for today. Mark it
                # and fail over to the next key.
                if "429" in msg or "resource_exhausted" in msg or "quota" in msg:
                    any_quota = True
                    key_quota_hit = True
                    log.warning("Key %s hit quota — failing over to next key", key_id)
                    break  # stop trying models on this key; move to next key

                usage_tracker.record_failure()

        if key_quota_hit:
            usage_tracker.mark_key_exhausted(key_id)  # arms global flag iff all keys spent

    # Every key failed. If any key was quota/credit blocked, this is the
    # 'come back tomorrow' case (the tracker has armed the flag if ALL are spent).
    if any_quota:
        raise QuotaExceededError(
            "All Gemini keys are out of quota/credits for today. Enable billing "
            "or add credits at https://aistudio.google.com/billing (image "
            "generation ≈$0.04/image; there is no free image tier)."
        )

    summary = "\n".join(f"  {k}: {e}" for k, e in errors.items())
    raise RuntimeError(f"All image generation attempts failed:\n{summary}")


async def generate_supernatural_image(
    image_bytes: bytes,
    mime_type: str,
    scene_id: str,
    custom_prompt: str | None = None,
    gender: str | None = None,
) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(_generate_sync, image_bytes, mime_type, scene_id, custom_prompt, gender),
    )
