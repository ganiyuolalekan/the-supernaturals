import io
import os
import asyncio
import logging
from functools import partial
from google import genai
from google.genai import types
from PIL import Image

from prompt_builder import build_prompt

log = logging.getLogger(__name__)

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
IMAGE_GENERATION_MODELS = [
    "gemini-2.5-flash-image-preview",   # primary — free tier, 500 images/day quota
    "gemini-3.1-flash-image-preview",   # fallback — newest preview
    "nano-banana-pro-preview",           # fallback — "Nano Banana Pro" from the project plan
    "gemini-3-pro-image-preview",        # fallback — Gemini 3 Pro image variant
    "gemini-2.5-flash-image",           # fallback — stable, requires billing
]


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to backend/.env")
    return genai.Client(api_key=api_key)


def _generate_sync(
    image_bytes: bytes,
    mime_type: str,
    scene_id: str,
    custom_prompt: str | None = None,
) -> bytes:
    client = _get_client()

    if mime_type in ("image/jpg", "image/webp"):
        mime_type = "image/jpeg"

    # Pre-crop + resize reference photo to 2:3 portrait so Gemini mirrors it
    image_bytes, mime_type = _to_portrait(image_bytes, mime_type)
    log.info("Input resized to %dx%d portrait", _TARGET_W, _TARGET_H)

    prompt = build_prompt(scene_id, custom_prompt)
    log.info("Generating: scene=%s custom_prompt=%s", scene_id, "yes" if custom_prompt else "no")

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
    quota_hit = False

    for model in models_to_try:
        log.info("Trying model: %s", model)
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        log.info("Success with model: %s", model)
                        return part.inline_data.data

            finish_reasons = [str(c.finish_reason) for c in response.candidates]
            errors[model] = f"No image in response. Finish reasons: {finish_reasons}"
            log.warning("Model %s gave no image. Finish reasons: %s", model, finish_reasons)

        except Exception as exc:
            msg = str(exc).lower()
            errors[model] = str(exc)
            log.error("Model %s error: %s", model, exc)

            # Invalid API key — no point trying other models
            if any(k in msg for k in ("api_key_invalid", "invalid api key", "401", "api key not valid")):
                raise RuntimeError(
                    "Your GEMINI_API_KEY is invalid. Check it at https://aistudio.google.com/app/apikey"
                ) from exc

            # Quota/billing — per-model, keep trying but flag it
            if "429" in msg or "resource_exhausted" in msg or "quota" in msg:
                quota_hit = True
                log.warning("Quota hit for model %s, trying next…", model)
                continue  # try next model

    # All models failed — give a clear actionable error
    if quota_hit:
        raise RuntimeError(
            "BILLING_REQUIRED: Image generation with Gemini requires billing to be enabled. "
            "The free tier quota for image generation is 0. "
            "Enable billing at https://aistudio.google.com/billing — "
            "image generation costs roughly $0.04 per image on the pay-as-you-go plan."
        )

    summary = "\n".join(f"  {m}: {e}" for m, e in errors.items())
    raise RuntimeError(f"All image generation models failed:\n{summary}")


async def generate_supernatural_image(
    image_bytes: bytes,
    mime_type: str,
    scene_id: str,
    custom_prompt: str | None = None,
) -> bytes:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(_generate_sync, image_bytes, mime_type, scene_id, custom_prompt),
    )
