import os
import time
import uuid
import base64
import secrets
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

from validator import validate_image
from gemini_client import generate_minister_image
from poster_builder import build_poster, ensure_fonts
from video_client import generate_announcement_video
from minister_prompts import has_style, get_category
from storage import (
    upload_poster_to_cloudinary,
    upload_video_to_cloudinary,
    save_to_supabase,
    get_all_submissions,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Ensuring fonts are present…")
    ensure_fonts()
    yield


app = FastAPI(title="Announcement Poster Generator", lifespan=lifespan)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5174,http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory video job store: submission_id -> {"status", "video_url", "error"}
_video_jobs: dict[str, dict] = {}

security = HTTPBasic()

ERROR_MESSAGES = {
    "file_too_large":     "Photo exceeds 5 MB. Please compress it and try again.",
    "invalid_file_type":  "Only JPEG and PNG images are supported.",
    "image_too_small":    "Photo must be at least 512 × 512 pixels.",
    "no_face_detected":   "No face detected. Please upload a clear, front-facing photo.",
    "multiple_faces":     "Please upload a photo with only one person.",
    "generation_failed":  "Image generation failed. Please try again.",
    "content_policy":     "Gemini declined this request. Try a different photo.",
    "invalid_style":      "Unknown style. Please select a valid style.",
}


def _require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    # No default: with ADMIN_PASSWORD unset the admin routes stay closed.
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if not admin_password:
        raise HTTPException(status_code=503, detail="Admin disabled: set ADMIN_PASSWORD")
    username_ok = secrets.compare_digest(credentials.username.encode(), b"admin")
    password_ok = secrets.compare_digest(credentials.password.encode(), admin_password.encode())
    if not (username_ok and password_ok):
        raise HTTPException(status_code=401, detail="Unauthorized",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username


# ─────────────────────────────────────────────
# Background video generation task
# ─────────────────────────────────────────────

async def _generate_video_task(
    submission_id: str,
    poster_bytes: bytes,
    style_id: str,
    category: str,
    minister_name: str,
) -> None:
    try:
        log.info("Video generation started for submission %s  style=%s", submission_id, style_id)
        video_bytes = await generate_announcement_video(poster_bytes, style_id, category)

        try:
            video_url, _ = await upload_video_to_cloudinary(video_bytes, submission_id, minister_name)
        except Exception:
            # Fallback: base64 data URL
            video_url = f"data:video/mp4;base64,{base64.b64encode(video_bytes).decode()}"

        _video_jobs[submission_id] = {
            "status": "ready", "video_url": video_url, "error": None,
            "engine": getattr(generate_announcement_video, "_last_engine", "unknown"),
        }
        log.info("Video ready for submission %s", submission_id)

    except Exception as exc:
        log.error("Video generation failed for %s: %s", submission_id, exc, exc_info=True)
        _video_jobs[submission_id] = {"status": "failed", "video_url": None, "error": str(exc)}


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/health")
async def health():
    api_key = os.getenv("GEMINI_API_KEY", "")
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemini_key_set": bool(api_key) and api_key != "your_gemini_api_key_here",
        "gemini_model": os.getenv("GEMINI_MODEL", "auto"),
    }


@app.get("/debug/gemini")
async def debug_gemini():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"ok": False, "error": "GEMINI_API_KEY not set"}
    try:
        client = genai.Client(api_key=api_key)
        all_models = [m.name for m in client.models.list()]
        image_gen  = [n for n in all_models if any(k in n.lower() for k in ("image", "imagen", "flash-image"))]
        video_gen  = [n for n in all_models if any(k in n.lower() for k in ("veo", "video"))]
        return {
            "ok": True,
            "all_models": all_models,
            "image_generation_models": image_gen,
            "video_generation_models": video_gen,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/generate")
async def generate(
    request: Request,
    background_tasks: BackgroundTasks,
    minister_name: str  = Form(..., min_length=1, max_length=120),
    minister_title: str = Form("", max_length=200),
    style_id: str       = Form(..., min_length=1, max_length=50),
    image: UploadFile   = File(...),
):
    client_ip = request.client.host if request.client else "unknown"

    if not has_style(style_id):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "invalid_style",
                    "message": ERROR_MESSAGES["invalid_style"]},
        )

    category = get_category(style_id)
    image_bytes = await image.read()

    is_valid, error_code = validate_image(image_bytes, image.filename, image.content_type)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": error_code,
                    "message": ERROR_MESSAGES.get(error_code, "Invalid image.")},
        )

    # ── Generate portrait ───────────────────────────────────
    try:
        portrait_bytes = await generate_minister_image(
            image_bytes,
            image.content_type or "image/jpeg",
            style_id,
        )
    except RuntimeError as exc:
        err_str = str(exc).lower()
        error_code = "content_policy" if "content policy" in err_str else "generation_failed"
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": error_code,
                    "message": ERROR_MESSAGES[error_code], "debug": str(exc)},
        )

    # ── Apply text overlay ────────────────────────────────────────────────
    try:
        poster_bytes = build_poster(portrait_bytes, minister_name, minister_title, style_id)
    except Exception as exc:
        log.error("Poster overlay failed: %s", exc, exc_info=True)
        poster_bytes = portrait_bytes  # Return portrait without overlay as fallback

    submission_id  = str(uuid.uuid4())
    generated_at   = datetime.now(timezone.utc).isoformat()

    # ── Upload poster to Cloudinary ───────────────────────────────────────
    try:
        poster_url, _ = await upload_poster_to_cloudinary(poster_bytes, submission_id, minister_name)
        storage = "cloudinary"
    except Exception:
        poster_url = f"data:image/jpeg;base64,{base64.b64encode(poster_bytes).decode()}"
        storage = "local"

    # Video generation is opt-in — mark as idle until the user requests it
    _video_jobs[submission_id] = {"status": "idle", "video_url": None, "error": None,
                                  "poster_bytes": poster_bytes, "style_id": style_id,
                                  "category": category, "minister_name": minister_name}

    # ── Save to Supabase (non-fatal) ──────────────────────────────────────
    try:
        await save_to_supabase(
            submission_id, minister_name, minister_title,
            category, style_id, poster_url, "", client_ip,
        )
    except Exception:
        pass

    return {
        "success": True,
        "submission_id": submission_id,
        "poster_url": poster_url,
        "video_status": "idle",
        "generated_at": generated_at,
        "storage": storage,
        "category": category,
        "style_id": style_id,
    }


@app.post("/generate-video/{submission_id}")
async def start_video(submission_id: str, background_tasks: BackgroundTasks):
    """Opt-in: trigger video generation for an existing submission."""
    job = _video_jobs.get(submission_id)
    if not job:
        raise HTTPException(status_code=404, detail="Submission not found")
    if job["status"] in ("generating", "ready"):
        return {"status": job["status"], "video_url": job.get("video_url")}

    _video_jobs[submission_id]["status"] = "generating"
    background_tasks.add_task(
        _generate_video_task,
        submission_id,
        job["poster_bytes"],
        job["style_id"],
        job["category"],
        job["minister_name"],
    )
    return {"status": "generating"}


@app.get("/video-status/{submission_id}")
async def video_status(submission_id: str):
    """Poll this endpoint to get video status."""
    job = _video_jobs.get(submission_id)
    if not job:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {
        "submission_id": submission_id,
        "status": job["status"],      # "idle" | "generating" | "ready" | "failed"
        "video_url": job["video_url"],
        "error": job["error"],
    }


@app.get("/submissions")
async def submissions(_admin: str = Depends(_require_admin)):
    data = await get_all_submissions()
    return {"total": len(data), "submissions": data}
