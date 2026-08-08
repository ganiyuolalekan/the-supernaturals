import os
import uuid
import base64
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

import usage_tracker
import availability
from validator import validate_image
from gemini_client import (
    generate_supernatural_image,
    IMAGE_GENERATION_MODELS,
    QuotaExceededError,
    register_configured_keys,
)
from scene_prompts import has_scene, get_active_scene_id, get_scene_schedule
from storage import (
    check_rate_limit,
    record_generation,
    get_quota,
    check_connection,
    global_cap_status,
    DAILY_LIMIT,
)

load_dotenv()

# Now that .env is loaded, tell the usage tracker the full set of configured
# keys so its 'all keys exhausted' flag is accurate from the first request.
register_configured_keys()

app = FastAPI(title="I Am Supernatural — SuperNaturals 2026")

# CORS
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Concurrency regulator — caps simultaneous Gemini calls so a burst of
# requests queues in-process instead of all hitting Gemini's per-minute rate
# limit at once. Requests beyond the queue depth get a fast, friendly
# "try again shortly" instead of hanging past the client's timeout.
MAX_CONCURRENT_GENERATIONS = int(os.getenv("MAX_CONCURRENT_GENERATIONS", "3"))
MAX_QUEUE_DEPTH = int(os.getenv("MAX_QUEUE_DEPTH", "12"))
_generation_semaphore = asyncio.Semaphore(MAX_CONCURRENT_GENERATIONS)
_queue_depth = 0
_queue_lock = asyncio.Lock()

ERROR_MESSAGES = {
    "file_too_large": "Your photo exceeds 5 MB. Please compress it and try again.",
    "invalid_file_type": "Only JPEG and PNG images are supported.",
    "image_too_small": "Your photo must be at least 512 × 512 pixels.",
    "no_face_detected": "We couldn't detect a face. Please upload a clear, front-facing photo.",
    "multiple_faces": "Please upload a photo with only one person.",
    "rate_limited": "You've already generated an image recently. Please wait a few minutes.",
    "daily_limit_reached": "You've used all 3 free generations for today. Come back tomorrow!",
    "high_demand": "We're experiencing high demand right now. Please try again in a moment.",
    "generation_failed": "Image generation failed. Please try again.",
    "capacity_reached": "We've reached today's image limit. The limit resets daily — please come back tomorrow. Thank you for your patience!",
    "scene_closed": "The scene is closed today. Come back for the next one!",
    "content_policy": "Gemini declined this request. Try a different photo or contact the admin.",
    "invalid_scene": "Unknown scene. Please pick one of the listed scenes.",
    "scene_not_active": "That scene isn't live this week. Please pick this week's scene.",
    "custom_prompt_too_long": "Your custom prompt is too long. Keep it under 500 characters.",
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    api_key = os.getenv("GEMINI_API_KEY", "")
    key_set = bool(api_key) and api_key != "your_gemini_api_key_here"
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemini_key_set": key_set,
        "gemini_model": os.getenv("GEMINI_MODEL", "").strip() or IMAGE_GENERATION_MODELS[0],
        # Where rate limits are actually being stored right now. If this says
        # store="memory", limits reset whenever the instance restarts.
        "supabase": await check_connection(),
    }


@app.get("/active-scene")
async def active_scene():
    """Returns this week's live scene and the full campaign schedule."""
    return {
        "active_scene_id": get_active_scene_id(),
        "schedule": get_scene_schedule(),
    }


@app.get("/quota")
async def quota(request: Request):
    """How many generations the caller's IP has left today (for the UI)."""
    client_ip = request.client.host if request.client else "unknown"
    return await get_quota(client_ip)


def _closed_day_message(today, next_open) -> str:
    """'Come back Saturday' — names the day and date the app reopens.

    Says "next week's scene" only when reopening actually lands in a different
    scene week, so the copy stays true if CLOSED_WEEKDAYS is ever changed.
    """
    day_name = availability.WEEKDAY_NAMES[next_open.weekday()]
    days_away = (next_open - today).days
    when = "tomorrow" if days_away == 1 else f"on {day_name}"
    new_week = get_active_scene_id(next_open) != get_active_scene_id(today)
    what = "Next week's scene" if new_week else "The scene"
    return (
        f"The scene is closed today. {what} goes live {when}"
        f" ({next_open.strftime('%d %b')}) — we'll see you then!"
    )


async def _availability() -> dict:
    """The single source of truth for 'can anyone generate right now?'.

    Three independent gates, checked in the order they matter to a visitor:
      closed_day  — the app is shut today (Thu/Fri), scene locked, modal shown
      daily_cap   — the service-wide budget ceiling for today is spent
      provider    — Gemini itself cut us off (quota/credits)
    """
    today = availability.local_today()
    closed = availability.is_closed(today)
    next_open = availability.next_open_date(today)
    cap = await global_cap_status()
    usage = usage_tracker.snapshot()

    if closed:
        reason, message = "closed_day", _closed_day_message(today, next_open)
    elif cap["reached"]:
        reason, message = "daily_cap", ERROR_MESSAGES["capacity_reached"]
    elif usage["limited"]:
        reason, message = "provider_limit", ERROR_MESSAGES["capacity_reached"]
    else:
        reason, message = None, None

    return {
        "generation_available": reason is None,
        "reason": reason,
        "message": message,
        "closed_today": closed,
        "closed_weekdays": availability.closed_day_names(),
        "next_open": next_open.isoformat(),
        "next_open_scene_id": get_active_scene_id(next_open),
        "today": today.isoformat(),
        "timezone": str(availability.app_timezone()),
        "daily_cap": cap,
        "cap_schedule": availability.cap_schedule_by_name(),
        "per_user_limit": DAILY_LIMIT,
        "retry_after_seconds": usage["retry_after_seconds"],
        "usage": usage,
    }


@app.get("/status")
async def status():
    """Service-wide generation status for the UI and for monitoring.

    `generation_available` is False when the app is closed for the day, when the
    service-wide daily cap is spent, or when Gemini itself cut us off — so the
    frontend can lock the scene and explain why instead of every visitor
    discovering it through a failed generation.
    """
    return await _availability()


@app.get("/debug/gemini")
async def debug_gemini():
    """Lists all available models and highlights image-generation capable ones."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"ok": False, "error": "GEMINI_API_KEY is not set in your .env file"}
    try:
        client = genai.Client(api_key=api_key)
        all_models = list(client.models.list())
        all_names = [m.name for m in all_models]
        image_gen_keywords = ("image-generation", "flash-image", "imagen", "imgen")
        likely_image_gen = [n for n in all_names if any(k in n.lower() for k in image_gen_keywords)]
        return {
            "ok": True,
            "configured_model": os.getenv("GEMINI_MODEL", "").strip() or IMAGE_GENERATION_MODELS[0],
            "all_models": all_names,
            "likely_image_generation_models": likely_image_gen,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/generate")
async def generate(
    request: Request,
    image: UploadFile = File(...),
    scene_id: str = Form(..., min_length=1, max_length=50),
    custom_prompt: str | None = Form(default=None, max_length=500),
    gender: str | None = Form(default=None, max_length=20),
):
    client_ip = request.client.host if request.client else "unknown"

    # Closed day / service-wide daily cap / provider cut-off — all three fail
    # fast with a friendly explanation, before any work is done, so no visitor
    # spends an upload (or a quota-blocked request) rediscovering the wall.
    avail = await _availability()
    if not avail["generation_available"]:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": "scene_closed" if avail["reason"] == "closed_day" else "capacity_reached",
                "message": avail["message"],
                "status": avail,
            },
        )

    # Rate limit check — persisted in Supabase so it survives Render's
    # free-tier instance spinning down and restarting after idle periods.
    allowed, limit_error, retry_after = await check_rate_limit(client_ip)
    if not allowed:
        message = ERROR_MESSAGES[limit_error]
        if limit_error == "rate_limited" and retry_after:
            message = f"Please wait {retry_after} seconds before generating again."
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": limit_error,
                "message": message,
                "quota": await get_quota(client_ip),
            },
        )

    # Validate scene_id up front (before reading large image)
    if not has_scene(scene_id):
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "invalid_scene",
                "message": ERROR_MESSAGES["invalid_scene"],
            },
        )

    # Only this week's scene may be generated — keeps every scene's
    # generations concentrated in its own week across the campaign.
    active_id = get_active_scene_id()
    if scene_id != active_id:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "scene_not_active",
                "message": ERROR_MESSAGES["scene_not_active"],
                "active_scene_id": active_id,
            },
        )

    image_bytes = await image.read()

    # Validate image
    is_valid, error_code = validate_image(image_bytes, image.filename, image.content_type)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": error_code,
                "message": ERROR_MESSAGES.get(error_code, "Invalid image."),
            },
        )

    # Concurrency regulator — queue behind the semaphore instead of flooding
    # Gemini all at once; fast-fail once the queue itself is too deep.
    global _queue_depth
    async with _queue_lock:
        if _queue_depth >= MAX_QUEUE_DEPTH:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": "high_demand",
                    "message": ERROR_MESSAGES["high_demand"],
                },
            )
        _queue_depth += 1

    try:
        async with _generation_semaphore:
            # Re-check the cap here, not just at the top: several requests can
            # clear the entry gate together and only serialise at the semaphore.
            # Without this the cap can be overshot by the concurrency width.
            if (await global_cap_status())["reached"]:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "success": False,
                        "error": "capacity_reached",
                        "message": ERROR_MESSAGES["capacity_reached"],
                    },
                )
            try:
                generated_bytes = await generate_supernatural_image(
                    image_bytes,
                    image.content_type or "image/jpeg",
                    scene_id=scene_id,
                    custom_prompt=custom_prompt,
                    gender=gender,
                )
            except QuotaExceededError as exc:
                # Gemini's daily image quota is spent — the tracker flag is now
                # armed, so subsequent requests short-circuit at the pre-check
                # above. Return the friendly 'come back tomorrow' message.
                log.warning("Daily Gemini quota reached: %s", exc)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "success": False,
                        "error": "capacity_reached",
                        "message": ERROR_MESSAGES["capacity_reached"],
                    },
                )
            except RuntimeError as exc:
                log.error("Gemini generation error: %s", exc)
                err_str = str(exc).lower()
                error_code = "content_policy" if "content policy" in err_str else "generation_failed"
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": error_code,
                        "message": ERROR_MESSAGES[error_code],
                        "debug": str(exc),
                    },
                )
            except Exception as exc:
                log.error("Unexpected generation error: %s", exc, exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": "generation_failed",
                        "message": ERROR_MESSAGES["generation_failed"],
                        "debug": str(exc),
                    },
                )
    finally:
        async with _queue_lock:
            _queue_depth -= 1

    # Images are never persisted server-side — returned directly as a data
    # URL. The original uploaded photo was already discarded after generation.
    await record_generation(client_ip)

    data_url = f"data:image/png;base64,{base64.b64encode(generated_bytes).decode()}"
    return {
        "success": True,
        "submission_id": str(uuid.uuid4()),
        "image_url": data_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "quota": await get_quota(client_ip),
    }
