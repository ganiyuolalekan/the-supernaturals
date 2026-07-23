import os
import asyncio
import logging
from datetime import date, datetime, timezone
from functools import partial

log = logging.getLogger(__name__)

DAILY_LIMIT = 3
COOLDOWN_SECONDS = 300  # 5 minutes


def _get_supabase():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Per-IP rate limiting — 3 generations/day + 5 min cooldown between each.
# Persisted in Supabase (not in-memory) so limits survive Render's free-tier
# instance spinning down and restarting after idle periods.
# ---------------------------------------------------------------------------

def _check_rate_limit_sync(ip: str) -> tuple[bool, str | None, int | None]:
    """Returns (allowed, error_code, retry_after_seconds)."""
    client = _get_supabase()
    if not client:
        return True, None, None  # Supabase not configured — fail open

    today = date.today().isoformat()
    try:
        result = client.table("rate_limits").select("*").eq("ip", ip).execute()
        row = result.data[0] if result.data else None
    except Exception:
        log.warning("Rate limit lookup failed — failing open", exc_info=True)
        return True, None, None

    if not row or row["day"] != today:
        return True, None, None

    if row["count"] >= DAILY_LIMIT:
        return False, "daily_limit_reached", None

    if row["last_generated_at"]:
        last = datetime.fromisoformat(row["last_generated_at"])
        elapsed = (datetime.now(timezone.utc) - last).total_seconds()
        if elapsed < COOLDOWN_SECONDS:
            return False, "rate_limited", int(COOLDOWN_SECONDS - elapsed)

    return True, None, None


async def check_rate_limit(ip: str) -> tuple[bool, str | None, int | None]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_check_rate_limit_sync, ip))


def _record_generation_sync(ip: str) -> None:
    client = _get_supabase()
    if not client:
        return
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    try:
        result = client.table("rate_limits").select("*").eq("ip", ip).execute()
        row = result.data[0] if result.data else None
        if row and row["day"] == today:
            client.table("rate_limits").update(
                {"count": row["count"] + 1, "last_generated_at": now}
            ).eq("ip", ip).execute()
        else:
            client.table("rate_limits").upsert(
                {"ip": ip, "day": today, "count": 1, "last_generated_at": now}
            ).execute()
    except Exception:
        log.warning("Failed to record generation for rate limiting — non-fatal", exc_info=True)


async def record_generation(ip: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_record_generation_sync, ip))
