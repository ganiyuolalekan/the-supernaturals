import os
import io
import re
import asyncio
from functools import partial


# ---------------------------------------------------------------------------
# Cloudinary
# ---------------------------------------------------------------------------

def _cloudinary_upload_sync(image_bytes: bytes, submission_id: str, name: str) -> tuple[str, str]:
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    name_slug = re.sub(r"[^a-z0-9]+", "-", name.lower())[:30].strip("-")
    public_id = f"supernaturals-2026/{submission_id}_{name_slug}"

    result = cloudinary.uploader.upload(
        io.BytesIO(image_bytes),
        public_id=public_id,
        overwrite=True,
        resource_type="image",
        format="jpg",
        quality="auto:good",
        transformation=[{"width": 1080, "crop": "limit"}],
    )

    return result["secure_url"], result["public_id"]


async def upload_to_cloudinary(image_bytes: bytes, submission_id: str, name: str) -> tuple[str, str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, partial(_cloudinary_upload_sync, image_bytes, submission_id, name)
    )


# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------

def _get_supabase():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def _save_sync(submission_id: str, name: str, generated_url: str, ip: str, cloudinary_public_id: str) -> None:
    client = _get_supabase()
    if not client:
        return
    client.table("submissions").insert(
        {
            "id": submission_id,
            "name": name,
            "generated_url": generated_url,
            "cloudinary_public_id": cloudinary_public_id,
            "ip_address": ip,
        }
    ).execute()


async def save_to_supabase(
    submission_id: str,
    name: str,
    generated_url: str,
    ip: str,
    cloudinary_public_id: str,
) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, partial(_save_sync, submission_id, name, generated_url, ip, cloudinary_public_id)
    )


def _get_submissions_sync() -> list[dict]:
    client = _get_supabase()
    if not client:
        return []
    result = client.table("submissions").select("*").order("created_at", desc=True).execute()
    return result.data or []


async def get_all_submissions() -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_submissions_sync)


def _delete_submission_sync(submission_id: str) -> None:
    client = _get_supabase()
    if not client:
        return
    client.table("submissions").delete().eq("id", submission_id).execute()


async def delete_submission(submission_id: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_delete_submission_sync, submission_id))
