"""
Daily Gemini usage tracker — answers two questions the app couldn't before:

  1. "How many image requests have we fired at Gemini today, and how many
     succeeded / failed / got quota-blocked?"  (visibility)
  2. "Are ALL our API keys currently out of quota/credits?"  (a flag the UI
     reads to pause generation and show a 'come back tomorrow' message.)

Multi-key aware: each configured key is tracked separately. One key hitting its
quota only marks that key exhausted — the app fails over to the next key. The
service-wide `limited` flag (which drives the banner) is true only when EVERY
configured key is currently exhausted.

IMPORTANT — exhaustion is a short COOLDOWN, not a day-long latch. When a key 429s
we mark it exhausted for `KEY_RETRY_AFTER_SECONDS` (default 5 min). After that it
is re-probed on the next request. This is what lets the app recover on its own:
if quota eased, a per-minute throttle cleared, or you funded billing, the next
probe succeeds and clears the flag — instead of staying dark until midnight. A
success clears a key immediately. Counters reset at the UTC day rollover; the
configured key list survives it.

State is per-process and in-memory: no DB table, and it re-derives itself from
Gemini's own responses after any restart.
"""

import os
import threading
from datetime import datetime, timezone, timedelta

_lock = threading.Lock()

# How long a key is considered exhausted before it is re-probed.
KEY_RETRY_AFTER_SECONDS = int(os.getenv("KEY_RETRY_AFTER_SECONDS", "300"))

_state: dict = {
    "day": None,           # UTC date (ISO) the counters below belong to
    "requests_sent": 0,    # every generate_content call, all keys
    "successes": 0,        # calls that returned an image
    "failures": 0,         # non-quota failures (no image, errors)
    "quota_blocks": 0,     # calls rejected with 429 / RESOURCE_EXHAUSTED
    "key_ids": [],         # all configured key ids (masked), set at startup
    "exhausted_keys": {},  # key_id -> datetime it was last marked exhausted
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _today() -> str:
    return _now().date().isoformat()


def _roll_if_new_day_locked() -> None:
    """Reset counters + exhaustion when the UTC date changes. Keeps key_ids
    (config, not daily state). Caller holds the lock."""
    today = _today()
    if _state["day"] != today:
        _state.update(
            day=today,
            requests_sent=0,
            successes=0,
            failures=0,
            quota_blocks=0,
            exhausted_keys={},
        )


def _prune_expired_locked() -> None:
    """Drop keys whose cooldown has elapsed — they're eligible to retry."""
    cutoff = _now() - timedelta(seconds=KEY_RETRY_AFTER_SECONDS)
    for kid in [k for k, ts in _state["exhausted_keys"].items() if ts <= cutoff]:
        del _state["exhausted_keys"][kid]


def _refresh_locked() -> None:
    _roll_if_new_day_locked()
    _prune_expired_locked()


def register_keys(ids: list[str]) -> None:
    """Declare the full set of configured key ids so the tracker knows when
    'all keys exhausted' is true. Idempotent; safe to call on every request."""
    with _lock:
        _refresh_locked()
        _state["key_ids"] = list(ids)


def record_request() -> None:
    with _lock:
        _refresh_locked()
        _state["requests_sent"] += 1


def record_success(key_id: str | None = None) -> None:
    with _lock:
        _refresh_locked()
        _state["successes"] += 1
        # A success proves this key is live right now — clear its exhaustion.
        if key_id:
            _state["exhausted_keys"].pop(key_id, None)


def record_failure() -> None:
    with _lock:
        _refresh_locked()
        _state["failures"] += 1


def mark_key_exhausted(key_id: str) -> None:
    """A key hit a quota/429 — mark it exhausted for the cooldown window."""
    with _lock:
        _refresh_locked()
        _state["quota_blocks"] += 1
        _state["exhausted_keys"][key_id] = _now()


def is_key_exhausted(key_id: str) -> bool:
    with _lock:
        _refresh_locked()
        return key_id in _state["exhausted_keys"]


def _is_limited_locked() -> bool:
    ids = _state["key_ids"]
    return bool(ids) and all(k in _state["exhausted_keys"] for k in ids)


def is_limit_reached() -> bool:
    """True only when every configured key is currently exhausted (in cooldown)."""
    with _lock:
        _refresh_locked()
        return _is_limited_locked()


def _retry_after_seconds_locked() -> int | None:
    """Seconds until the soonest-eligible key can be re-probed, when limited."""
    if not _is_limited_locked() or not _state["exhausted_keys"]:
        return None
    soonest = min(_state["exhausted_keys"].values())
    eligible_at = soonest + timedelta(seconds=KEY_RETRY_AFTER_SECONDS)
    return max(0, int((eligible_at - _now()).total_seconds()))


def snapshot() -> dict:
    """A copy of today's counters + per-key state, for the /status endpoint."""
    with _lock:
        _refresh_locked()
        limited = _is_limited_locked()
        return {
            "day": _state["day"],
            "requests_sent": _state["requests_sent"],
            "successes": _state["successes"],
            "failures": _state["failures"],
            "quota_blocks": _state["quota_blocks"],
            "key_ids": list(_state["key_ids"]),
            "exhausted_keys": {k: ts.isoformat() for k, ts in _state["exhausted_keys"].items()},
            "keys_total": len(_state["key_ids"]),
            "keys_exhausted": len(_state["exhausted_keys"]),
            "limited": limited,
            "retry_after_seconds": _retry_after_seconds_locked(),
        }
