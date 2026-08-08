"""
When the app is open for generation, and when it is deliberately closed.

Two independent gates sit in front of every generation, both of them budget
controls for a fixed-funding 10-week campaign:

  1. CLOSED DAYS — the app is shut on given weekdays (default Thursday and
     Friday). Because a scene week runs Saturday→Friday, closing Thu+Fri shuts
     the last two days of each scene's week, so the next open day is always the
     day the next scene goes live. Nothing generates on a closed day.

  2. DAILY IMAGE CAP — a service-wide ceiling on successful generations, set
     PER WEEKDAY (DAILY_IMAGE_CAPS), so busy days get more headroom than quiet
     ones. Unlike the per-IP limit in storage.py, this one is NOT bypassed by
     RATE_LIMIT_DISABLED: it guards real money, not fairness. A cap of 0 means
     unlimited, so closures are expressed with CLOSED_WEEKDAYS, never a 0 cap.

Both are evaluated in the campaign's local timezone (APP_TIMEZONE), not UTC, so
"Thursday" means Thursday where the audience actually is.
"""

import os
import logging
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

log = logging.getLogger(__name__)

# The campaign's local timezone. Everything day-shaped (which weekday it is,
# which day the cap belongs to) is computed here rather than in UTC.
DEFAULT_TIMEZONE = "Africa/Lagos"

# Monday=0 … Wednesday=2, Thursday=3, Friday=4 — matches date.weekday().
DEFAULT_CLOSED_WEEKDAYS = "2,3,4"

# Per-weekday image ceilings, "<weekday>:<cap>" comma-separated. Weekdays absent
# from this map fall back to GLOBAL_DAILY_IMAGE_CAP.
DEFAULT_DAILY_IMAGE_CAPS = "5:120,6:30,0:50,1:40"  # Sat 120, Sun 30, Mon 50, Tue 40

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def app_timezone() -> ZoneInfo:
    name = os.getenv("APP_TIMEZONE", DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        log.warning("APP_TIMEZONE=%r is not a valid timezone — falling back to UTC", name)
        return ZoneInfo("UTC")


def local_now() -> datetime:
    return datetime.now(app_timezone())


def local_today() -> date:
    return local_now().date()


def closed_weekdays() -> set[int]:
    """Weekday numbers the app is shut, from CLOSED_WEEKDAYS (empty = never)."""
    raw = os.getenv("CLOSED_WEEKDAYS", DEFAULT_CLOSED_WEEKDAYS).strip()
    if not raw:
        return set()
    days = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 0 <= int(part) <= 6:
            days.add(int(part))
        elif part:
            log.warning("Ignoring invalid CLOSED_WEEKDAYS entry %r", part)
    return days


def is_closed(day: date | None = None) -> bool:
    return (day or local_today()).weekday() in closed_weekdays()


def next_open_date(day: date | None = None) -> date:
    """The next date the app is open, starting from tomorrow relative to `day`.

    Guarded against a config that closes all seven days — returns tomorrow
    rather than looping forever.
    """
    start = day or local_today()
    closed = closed_weekdays()
    if len(closed) >= 7:
        return start + timedelta(days=1)
    candidate = start + timedelta(days=1)
    while candidate.weekday() in closed:
        candidate += timedelta(days=1)
    return candidate


def closed_day_names() -> list[str]:
    return [WEEKDAY_NAMES[d] for d in sorted(closed_weekdays())]


# ── Per-weekday image caps ──────────────────────────────────────────────────

def _fallback_cap() -> int:
    raw = os.getenv("GLOBAL_DAILY_IMAGE_CAP", "40").strip()
    try:
        return max(0, int(raw))
    except ValueError:
        log.warning("GLOBAL_DAILY_IMAGE_CAP=%r is not a number — using 40", raw)
        return 40


def cap_schedule() -> dict[int, int]:
    """weekday -> cap, parsed from DAILY_IMAGE_CAPS ("5:80,6:30,0:50,1:40")."""
    raw = os.getenv("DAILY_IMAGE_CAPS", DEFAULT_DAILY_IMAGE_CAPS).strip()
    schedule: dict[int, int] = {}
    if not raw:
        return schedule
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        day, _, cap = part.partition(":")
        try:
            day_i, cap_i = int(day.strip()), int(cap.strip())
        except ValueError:
            log.warning("Ignoring invalid DAILY_IMAGE_CAPS entry %r", part)
            continue
        if 0 <= day_i <= 6 and cap_i >= 0:
            schedule[day_i] = cap_i
        else:
            log.warning("Ignoring out-of-range DAILY_IMAGE_CAPS entry %r", part)
    return schedule


def daily_cap_for(day: date | None = None) -> int:
    """Today's image ceiling. 0 means uncapped — closures use CLOSED_WEEKDAYS."""
    weekday = (day or local_today()).weekday()
    return cap_schedule().get(weekday, _fallback_cap())


def cap_schedule_by_name() -> dict[str, int]:
    """The cap schedule keyed by day name, for /status and monitoring. Closed
    days are omitted — their cap is meaningless."""
    closed = closed_weekdays()
    return {
        WEEKDAY_NAMES[d]: daily_cap_for_weekday(d)
        for d in range(7)
        if d not in closed
    }


def daily_cap_for_weekday(weekday: int) -> int:
    return cap_schedule().get(weekday, _fallback_cap())
