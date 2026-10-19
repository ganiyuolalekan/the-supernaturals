import os
import io
import re
import asyncio
from functools import partial


# ─────────────────────────────────────────────
# Cloudinary
# ─────────────────────────────────────────────

def _cloudinary_upload_sync(
    file_bytes: bytes,
    submission_id: str,
    minister_name: str,
    resource_type: str = "image",
    suffix: str = "",
) -> tuple[str, str]:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    name_slug = re.sub(r"[^a-z0-9]+", "-", minister_name.lower())[:30].strip("-")
    public_id = f"minister-confirmed-2026/{submission_id}_{name_slug}{suffix}"

    upload_kwargs: dict = {
        "public_id": public_id,
        "overwrite": True,
        "resource_type": resource_type,
    }

    if resource_type == "image":
        upload_kwargs.update({
            "format": "jpg",
            "quality": "auto:good",
            "transformation": [{"width": 1080, "crop": "limit"}],
        })
    else:
        upload_kwargs["format"] = "mp4"

    result = cloudinary.uploader.upload(io.BytesIO(file_bytes), **upload_kwargs)
    return result["secure_url"], result["public_id"]


async def upload_poster_to_cloudinary(
    image_bytes: bytes, submission_id: str, minister_name: str
) -> tuple[str, str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(_cloudinary_upload_sync, image_bytes, submission_id, minister_name, "image", "_poster"),
    )


async def upload_video_to_cloudinary(
    video_bytes: bytes, submission_id: str, minister_name: str
) -> tuple[str, str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(_cloudinary_upload_sync, video_bytes, submission_id, minister_name, "video", "_video"),
    )


# ─────────────────────────────────────────────
# Supabase
# ─────────────────────────────────────────────

def _get_supabase():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def _save_sync(
    submission_id: str,
    minister_name: str,
    minister_title: str,
    category: str,
    style_id: str,
    poster_url: str,
    video_url: str,
    ip: str,
) -> None:
    client = _get_supabase()
    if not client:
        return
    client.table("minister_submissions").insert({
        "id": submission_id,
        "minister_name": minister_name,
        "minister_title": minister_title,
        "category": category,
        "style_id": style_id,
        "poster_url": poster_url,
        "video_url": video_url,
        "ip_address": ip,
    }).execute()


async def save_to_supabase(
    submission_id: str,
    minister_name: str,
    minister_title: str,
    category: str,
    style_id: str,
    poster_url: str,
    video_url: str,
    ip: str,
) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        partial(_save_sync, submission_id, minister_name, minister_title,
                category, style_id, poster_url, video_url, ip),
    )


def _get_submissions_sync() -> list[dict]:
    client = _get_supabase()
    if not client:
        return []
    result = (
        client.table("minister_submissions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


async def get_all_submissions() -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_submissions_sync)
