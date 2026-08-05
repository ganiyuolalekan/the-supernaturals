import os
import asyncio
import logging
import threading
from datetime import date, datetime, timezone
from functools import partial

log = logging.getLogger(__name__)

DAILY_LIMIT = 3
COOLDOWN_SECONDS = 300  # 5 minutes

_client = None
_client_lock = threading.Lock()

# Per-process fallback store, used whenever Supabase is unconfigured or
# unreachable. Limits then apply per running instance and reset on restart —
# weaker than the Supabase-backed version, but far better than failing open
# and letting one person generate unlimited (paid) images. /health reports
# which store is actually live.
_memory_rows: dict[str, dict] = {}
_memory_lock = threading.Lock()


def _get_supabase():
    global _client
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return None
    with _client_lock:
        if _client is None:
            from supabase import create_client
            _client = create_client(url, key)
    return _client


def _load_row(ip: str) -> dict | None:
    """The IP's row from Supabase, falling back to the in-memory store."""
    client = _get_supabase()
    if client:
        try:
            result = client.table("rate_limits").select("*").eq("ip", ip).execute()
            return result.data[0] if result.data else None
        except Exception:
            log.warning("Supabase read failed — using in-memory limits", exc_info=True)
    with _memory_lock:
        return _memory_rows.get(ip)


def _save_row(ip: str, row: dict) -> None:
    """Persist the IP's row to Supabase, falling back to the in-memory store."""
    client = _get_supabase()
    if client:
        try:
            client.table("rate_limits").upsert({"ip": ip, **row}).execute()
            return
        except Exception:
            log.warning("Supabase write failed — using in-memory limits", exc_info=True)
    with _memory_lock:
        _memory_rows[ip] = row


# ---------------------------------------------------------------------------
# Per-IP rate limiting — 3 generations/day + 5 min cooldown between each.
# Persisted in Supabase (not in-memory) so limits survive Render's free-tier
# instance spinning down and restarting after idle periods.
# ---------------------------------------------------------------------------

def _check_rate_limit_sync(ip: str) -> tuple[bool, str | None, int | None]:
    """Returns (allowed, error_code, retry_after_seconds)."""
    today = date.today().isoformat()
    row = _load_row(ip)

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
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    row = _load_row(ip)
    count = row["count"] + 1 if row and row["day"] == today else 1
    _save_row(ip, {"day": today, "count": count, "last_generated_at": now})


async def record_generation(ip: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(_record_generation_sync, ip))


# ---------------------------------------------------------------------------
# Quota lookup — how many generations this IP has used today, for the UI to
# show "X of 3 left". Read-only; never blocks. Falls back to a full quota if
# Supabase is unconfigured/unreachable so the UI degrades gracefully.
# ---------------------------------------------------------------------------

def _full_quota() -> dict:
    return {"used": 0, "limit": DAILY_LIMIT, "remaining": DAILY_LIMIT, "cooldown_remaining": 0}


def _get_quota_sync(ip: str) -> dict:
    today = date.today().isoformat()
    row = _load_row(ip)

    if not row or row["day"] != today:
        return _full_quota()

    used = min(row["count"], DAILY_LIMIT)
    cooldown_remaining = 0
    if row["last_generated_at"]:
        last = datetime.fromisoformat(row["last_generated_at"])
        elapsed = (datetime.now(timezone.utc) - last).total_seconds()
        if elapsed < COOLDOWN_SECONDS:
            cooldown_remaining = int(COOLDOWN_SECONDS - elapsed)

    return {
        "used": used,
        "limit": DAILY_LIMIT,
        "remaining": max(0, DAILY_LIMIT - used),
        "cooldown_remaining": cooldown_remaining,
    }


async def get_quota(ip: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(_get_quota_sync, ip))


# ---------------------------------------------------------------------------
# Connectivity check for /health — answers "is Supabase actually working?"
# rather than just "are the env vars set?". Without this the app looks healthy
# while silently rate-limiting in memory only.
# ---------------------------------------------------------------------------

def _check_connection_sync() -> dict:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        return {
            "configured": False,
            "connected": False,
            "store": "memory",
            "error": "SUPABASE_URL / SUPABASE_KEY not set in backend/.env",
        }
    try:
        _get_supabase().table("rate_limits").select("ip").limit(1).execute()
        return {"configured": True, "connected": True, "store": "supabase", "error": None}
    except Exception as exc:
        return {
            "configured": True,
            "connected": False,
            "store": "memory",
            "error": f"{type(exc).__name__}: {exc}"[:200],
        }


async def check_connection() -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _check_connection_sync)
