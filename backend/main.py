import os
import time
import uuid
import base64
import secrets
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from validator import validate_image
from gemini_client import generate_supernatural_image, IMAGE_GENERATION_MODELS
from scene_prompts import has_scene, get_active_scene_id, get_scene_schedule
from storage import upload_to_cloudinary, save_to_supabase, get_all_submissions, delete_submission

load_dotenv()

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

# In-memory rate limit store: ip -> unix timestamp of last generation
_rate_store: dict[str, float] = {}
RATE_LIMIT_SECONDS = 300  # 5 minutes

security = HTTPBasic()

ERROR_MESSAGES = {
    "file_too_large": "Your photo exceeds 5 MB. Please compress it and try again.",
    "invalid_file_type": "Only JPEG and PNG images are supported.",
    "image_too_small": "Your photo must be at least 512 × 512 pixels.",
    "no_face_detected": "We couldn't detect a face. Please upload a clear, front-facing photo.",
    "multiple_faces": "Please upload a photo with only one person.",
    "rate_limited": "You've already generated an image recently. Please wait 5 minutes.",
    "generation_failed": "Image generation failed. Please try again.",
    "content_policy": "Gemini declined this request. Try a different photo or contact the admin.",
    "invalid_scene": "Unknown scene. Please pick one of the listed scenes.",
    "scene_not_active": "That scene isn't live this week. Please pick this week's scene.",
    "custom_prompt_too_long": "Your custom prompt is too long. Keep it under 500 characters.",
}


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    admin_password = os.getenv("ADMIN_PASSWORD", "supernaturals2026")
    username_ok = secrets.compare_digest(credentials.username.encode(), b"admin")
    password_ok = secrets.compare_digest(credentials.password.encode(), admin_password.encode())
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


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
    }


@app.get("/active-scene")
async def active_scene():
    """Returns this week's live scene and the full campaign schedule."""
    return {
        "active_scene_id": get_active_scene_id(),
        "schedule": get_scene_schedule(),
    }


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
):
    client_ip = request.client.host if request.client else "unknown"
    name = "Guest"

    # Rate limit check
    now = time.time()
    last = _rate_store.get(client_ip, 0)
    elapsed = now - last
    if elapsed < RATE_LIMIT_SECONDS:
        remaining = int(RATE_LIMIT_SECONDS - elapsed)
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": "rate_limited",
                "message": f"Please wait {remaining} seconds before generating again.",
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

    # Generate supernatural portrait
    try:
        generated_bytes = await generate_supernatural_image(
            image_bytes,
            image.content_type or "image/jpeg",
            scene_id=scene_id,
            custom_prompt=custom_prompt,
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

    submission_id = str(uuid.uuid4())
    generated_at = datetime.now(timezone.utc).isoformat()

    # Try Cloudinary; fall back to base64 data URL for local testing
    try:
        image_url, cloudinary_public_id = await upload_to_cloudinary(
            generated_bytes, submission_id, name
        )
    except Exception:
        data_url = f"data:image/png;base64,{base64.b64encode(generated_bytes).decode()}"
        return {
            "success": True,
            "submission_id": submission_id,
            "image_url": data_url,
            "generated_at": generated_at,
            "storage": "local",
        }

    try:
        await save_to_supabase(submission_id, name, image_url, client_ip, cloudinary_public_id)
    except Exception:
        pass  # Non-fatal — image is already uploaded

    # Record successful generation for rate limiting
    _rate_store[client_ip] = now

    return {
        "success": True,
        "submission_id": submission_id,
        "image_url": image_url,
        "generated_at": generated_at,
        "storage": "cloudinary",
    }


@app.get("/submissions")
async def submissions(_admin: str = Depends(_require_admin)):
    data = await get_all_submissions()
    return {"total": len(data), "submissions": data}


@app.delete("/submissions/{submission_id}")
async def remove_submission(submission_id: str, _admin: str = Depends(_require_admin)):
    await delete_submission(submission_id)
    return {"success": True}
