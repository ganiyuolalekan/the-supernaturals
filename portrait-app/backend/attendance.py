"""
Event-day attendance — /attend/* routes.

Door agents search the registration sheet, confirm the person's number, and
mark them as arrived for a given conference day. The registration Google Sheet
(the Google Form's response sheet) is the system of record: this module reads
it and writes four extra columns back into it:

    attend_friday | attend_saturday | attend_sunday | first_timer

An attend_* cell holds a readable check-in stamp such as "🚶🏽‍♂️: 09:42 ✅" (the
walker matches the person's gender); empty means not arrived. first_timer holds "Yes" or "No" once the agent has answered, and is empty only
until then (or after a full undo).

How it talks to the sheet
-------------------------
A link that merely grants edit access does not let a server write to a sheet —
that needs authentication. So writes go through a small Google Apps Script web
app bound to the sheet (backend/apps_script/Attendance.gs), called with a
shared secret. See DEPLOY.md for the one-time setup.

    ATTENDANCE_SCRIPT_URL     the web app's /exec URL
    ATTENDANCE_SCRIPT_SECRET  the same secret stored in the script properties

For local development, ATTENDANCE_DEMO=true with ATTENDANCE_SHEET_ID reads the
sheet's public CSV export and keeps check-ins in memory — it never writes to
the live sheet.

Speed: every call to Apps Script costs 2-4 s even when it does nothing, so the
backend never makes an agent wait on one if it can avoid it. Rows live in an
in-memory snapshot; reads are served from it and refreshed in the background,
and writes patch the snapshot directly instead of re-reading the sheet.

Privacy: there is no login — the link is meant to be shared only with the
right people. Search results only ever carry a masked phone number; the full
number is compared server-side against what the agent typed. Only the
first-timers list (which exists to be followed up) returns full numbers.
"""

import asyncio
import csv
import io
import json
import logging
import os
import re
import time
import unicodedata
from collections import Counter
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from availability import app_timezone

log = logging.getLogger(__name__)

DAYS = ("friday", "saturday", "sunday")
FIRST_TIMER_COL = "first_timer"
ATTEND_COLS = {d: f"attend_{d}" for d in DAYS}
NEW_COLS = (*ATTEND_COLS.values(), FIRST_TIMER_COL)

# The "home" group, counted separately on the chart (HOME_ORG_NAME is its label).
# HOME_ORG_PATTERN is a regex matched against the registration sheet's church /
# organisation column. People type the same name a dozen ways, so make it forgiving.
# In 2026 it was  pra[iy]s\w*\s*[-_.]?\s*as+\w*  which caught "Praise Assembly",
# "Praiseassembly", "Praise Asssembly", "Praises assembly" and "Praise Assemble"
# but deliberately NOT a bare "RCCG" (any of thousands of other parishes).
# Unset = nobody counts as home.
HOME_ORG_NAME = os.getenv("HOME_ORG_NAME", "Home organisation")
_HOME_ORG_PATTERN = os.getenv("HOME_ORG_PATTERN", "").strip()
HOME_CHURCH_RE = re.compile(_HOME_ORG_PATTERN, re.IGNORECASE) if _HOME_ORG_PATTERN else None

CACHE_TTL_SECONDS = 8      # snapshot older than this is refreshed in the background
GENDERS = ("Male", "Female")
AGE_GROUPS = ("Youth (13-17)", "Young Adult (18-35)", "Adult (35+)")
WALK_IN_SOURCE = "Walk-in"  # shows up under "How they heard" so walk-ins are countable
_FALSY = {"", "no", "false", "0", "n", "-"}


# ---------------------------------------------------------------------------
# Sheet access
# ---------------------------------------------------------------------------

class SheetError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _canon(header: str) -> str | None:
    """Map a sheet header to the field it holds. Matching is by content, not
    position, so reordering columns in the sheet does not break anything."""
    h = header.strip().lower()
    if h in NEW_COLS:
        return h
    if h.startswith("timestamp"):
        return "timestamp"
    if h.startswith("full name") or h == "name":
        return "name"
    if h.startswith("phone"):
        return "phone"
    if h.startswith("gender"):
        return "gender"
    if h.startswith("age group"):
        return "age_group"
    if h.startswith("church"):
        return "church"
    if "transport" in h:
        return "transport"
    if "joining us from" in h:
        return "area"
    if "hear about" in h:
        return "source"
    return None


def _rows_from_table(headers: list[str], table: list[list[str]], first_row: int) -> list[dict]:
    fields = [_canon(h) for h in headers]
    rows = []
    for offset, cells in enumerate(table):
        rec = {"row": first_row + offset}
        for field, value in zip(fields, cells):
            if field:
                rec[field] = str(value).strip()
        if not rec.get("name"):
            continue  # blank spacer row
        for key in ("timestamp", "name", "phone", "gender", "age_group", "church",
                    "transport", "area", "source", *NEW_COLS):
            rec.setdefault(key, "")
        rows.append(rec)
    return rows


class AppsScriptStore:
    """Reads and writes through the Apps Script web app bound to the sheet."""

    def __init__(self, url: str, secret: str):
        self.url = url
        self.secret = secret

    async def _call(self, payload: dict) -> dict:
        body = json.dumps({**payload, "secret": self.secret})
        try:
            # Apps Script answers a POST with a 302 to the result; httpx turns
            # that into a GET, which is exactly what the web app expects.
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.post(
                    self.url, content=body,
                    headers={"Content-Type": "text/plain;charset=utf-8"},
                )
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            log.error("Attendance sheet call failed: %s", exc)
            raise SheetError(
                "sheet_unreachable",
                "Couldn't reach the registration sheet. Check the Apps Script "
                "deployment is set to 'Anyone' and the URL is correct.",
            ) from exc
        if not data.get("ok"):
            code = data.get("error", "sheet_error")
            if code == "bad_action":
                raise SheetError(code, "The sheet script is out of date — redeploy "
                                       "Attendance.gs as a new version (see DEPLOY.md).")
            raise SheetError(code, data.get("message") or f"Sheet rejected the request ({code}).")
        return data

    async def list_rows(self) -> list[dict]:
        data = await self._call({"action": "list"})
        return _rows_from_table(data["headers"], data["rows"], data.get("first_row", 2))

    async def write(self, row: int, expect_name: str, expect_phone: str,
                    updates: dict[str, str], only_if_empty: str | None = None) -> dict:
        return await self._call({
            "action": "write", "row": row,
            "expect_name": expect_name, "expect_phone": expect_phone,
            "updates": updates, "only_if_empty": only_if_empty,
        })


    async def append(self, cells: dict[str, str]) -> int:
        data = await self._call({"action": "append", "cells": cells})
        return int(data["row"])


class DemoStore:
    """Local-only: reads the sheet's public CSV export once and holds
    check-ins in memory. Never writes to the live sheet."""

    def __init__(self, sheet_id: str):
        self.sheet_id = sheet_id
        self._rows: list[dict] | None = None

    async def list_rows(self) -> list[dict]:
        if self._rows is None:
            url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/export?format=csv"
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            table = list(csv.reader(io.StringIO(resp.text)))
            self._rows = _rows_from_table(table[0], table[1:], 2)
        return [dict(r) for r in self._rows]

    async def write(self, row, expect_name, expect_phone, updates, only_if_empty=None) -> dict:
        rec = next((r for r in self._rows or [] if r["row"] == row), None)
        if not rec or rec["name"] != expect_name:
            raise SheetError("row_changed", "That row has changed — search again.")
        if only_if_empty and rec.get(only_if_empty):
            return {"ok": True, "already": True, "current": rec[only_if_empty]}
        rec.update(updates)
        return {"ok": True, "already": False}


    async def append(self, cells: dict[str, str]) -> int:
        await self.list_rows()
        row = max([r["row"] for r in self._rows] + [1]) + 1
        rec = {"row": row, **{k: "" for k in ("timestamp", "name", "phone", "gender", "age_group",
                                              "church", "transport", "area", "source", *NEW_COLS)}}
        rec.update(cells)
        self._rows.append(rec)
        return row


_store = None
_store_key = None


def get_store():
    """The configured store, or None. Rebuilt if the env config changes."""
    global _store, _store_key
    url = os.getenv("ATTENDANCE_SCRIPT_URL", "").strip()
    secret = os.getenv("ATTENDANCE_SCRIPT_SECRET", "").strip()
    demo = os.getenv("ATTENDANCE_DEMO", "").strip().lower() in {"1", "true", "yes", "on"}
    sheet_id = os.getenv("ATTENDANCE_SHEET_ID", "").strip()
    key = (url, secret, demo, sheet_id)
    if key != _store_key:
        _store_key = key
        _store = None
        if url and secret:
            _store = AppsScriptStore(url, secret)
        elif demo and sheet_id:
            _store = DemoStore(sheet_id)
    return _store


class _Cache:
    def __init__(self):
        self.rows: list[dict] | None = None   # None = never loaded
        self.at = 0.0
        self.store = None
        self.version = 0                       # bumped by every local write
        self.task: asyncio.Task | None = None  # in-flight background refresh
        self.lock = asyncio.Lock()


_cache = _Cache()


def _not_configured() -> HTTPException:
    return HTTPException(503, detail={
        "success": False, "error": "not_configured",
        "message": "Attendance isn't connected to the sheet yet (see DEPLOY.md).",
    })


async def _fetch(store) -> None:
    """Read the sheet into the snapshot. If a local write landed while we were
    reading, this read may predate it, so discard it rather than undo the write."""
    started = _cache.version
    rows = await store.list_rows()
    if started != _cache.version:
        return
    _cache.rows, _cache.at, _cache.store = rows, time.monotonic(), store


async def _refresh_in_background(store) -> None:
    try:
        await _fetch(store)
    except Exception as exc:  # keep serving the last snapshot
        log.warning("Background sheet refresh failed: %s", exc)


async def _rows(force: bool = False) -> list[dict]:
    """The rows, fast. Only the very first read (or force=True) waits on Google;
    otherwise a stale snapshot is returned at once and refreshed behind it."""
    store = get_store()
    if store is None:
        raise _not_configured()

    if _cache.rows is None or _cache.store is not store or force:
        async with _cache.lock:
            if _cache.rows is None or _cache.store is not store or force:
                try:
                    await _fetch(store)
                except SheetError as exc:
                    raise HTTPException(502, detail={
                        "success": False, "error": exc.code, "message": exc.message})
        if _cache.rows is None:  # a write raced the very first load
            raise HTTPException(503, detail={"success": False, "error": "busy",
                                             "message": "Loading — try again in a moment."})
        return _cache.rows

    stale = (time.monotonic() - _cache.at) > CACHE_TTL_SECONDS
    if stale and (_cache.task is None or _cache.task.done()):
        _cache.task = asyncio.create_task(_refresh_in_background(store))
    return _cache.rows


def _patch(rec: dict, updates: dict) -> None:
    """Apply a confirmed write to the snapshot so reads see it immediately."""
    rec.update(updates)
    _cache.version += 1


def _distrust_snapshot() -> None:
    _cache.at = 0.0
    _cache.version += 1


async def warm() -> None:
    """Load the snapshot at startup so the first agent doesn't wait for Google."""
    if get_store() is None:
        return
    try:
        await _rows()
    except Exception as exc:
        log.warning("Attendance warm-up failed: %s", exc)


# ---------------------------------------------------------------------------
# Pure helpers (also what the tests exercise)
# ---------------------------------------------------------------------------

def is_home_church(church: str) -> bool:
    return bool(HOME_CHURCH_RE and HOME_CHURCH_RE.search(church or ""))


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def phone_matches(stored: str, typed: str) -> bool:
    """True if what the agent typed is the stored number — either the whole
    number (any of 0803…, +234803…, 234803…) or its last 4+ digits."""
    p, t = _digits(stored), _digits(typed)
    if len(p) < 7 or len(t) < 4:
        return False
    if len(t) >= 10:
        return t[-10:] == p[-10:]
    return p.endswith(t)


def mask_phone(phone: str) -> str:
    d = _digits(phone)
    if len(d) < 7:
        return ""
    return d[:4] + "•" * (len(d) - 6) + d[-2:]


def _attended(value: str) -> bool:
    return value.strip().lower() not in _FALSY


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


_WALKER = "\U0001F6B6\U0001F3FD"  # 🚶🏽
_WALKERS = {"male": _WALKER + "\u200d\u2642\ufe0f", "female": _WALKER + "\u200d\u2640\ufe0f"}


def checkin_label(gender: str, now: datetime | None = None) -> str:
    """What goes in an attend_* cell: "🚶🏽‍♂️: 09:42 ✅". The walker follows the
    person's gender; anything unrecognised gets the neutral one."""
    now = now or datetime.now(app_timezone())
    walker = _WALKERS.get((gender or "").strip().lower(), _WALKER)
    return f"{walker}: {now.strftime('%H:%M')} ✅"


def whatsapp_link(phone: str) -> str | None:
    d = _digits(phone)
    if len(d) == 11 and d.startswith("0"):
        d = "234" + d[1:]
    elif len(d) == 10:
        d = "234" + d
    return f"https://wa.me/{d}" if len(d) >= 11 else None


def public_person(rec: dict, day: str | None = None, *, full_phone: bool = False) -> dict:
    out = {
        "row": rec["row"],
        "name": rec["name"],
        "gender": rec["gender"],
        "age_group": rec["age_group"],
        "church": rec["church"],
        "home_church": is_home_church(rec["church"]),
        "registered_at": rec["timestamp"],
        "first_timer": _attended(rec[FIRST_TIMER_COL]),
        "attended": {d: (rec[ATTEND_COLS[d]] or None) if _attended(rec[ATTEND_COLS[d]]) else None
                     for d in DAYS},
        "phone_masked": mask_phone(rec["phone"]),
        "phone_on_file": len(_digits(rec["phone"])) >= 7,
    }
    if day:
        out["checked_in"] = out["attended"][day] is not None
    if full_phone:
        out["phone"] = rec["phone"]
        out["whatsapp"] = whatsapp_link(rec["phone"])
    return out


def search_people(rows: list[dict], q: str, limit: int = 20) -> list[dict]:
    """Name search: every word typed must appear in the name (any order,
    accents/case ignored). A run of 4+ digits searches phone numbers instead."""
    q = q.strip()
    qd = _digits(q)
    scored = []
    if len(qd) >= 4 and len(qd) >= len(q) - 2:  # looks like a number
        for r in rows:
            if qd in _digits(r["phone"]):
                scored.append((0, r))
    else:
        tokens = _norm(q).split(" ")
        for r in rows:
            name = _norm(r["name"])
            if all(t in name for t in tokens):
                starts = name.startswith(tokens[0])
                scored.append((0 if starts else 1, r))
    scored.sort(key=lambda s: (s[0], _norm(s[1]["name"])))
    return [r for _, r in scored[:limit]]


def _breakdown(rows: list[dict], label_of, is_present) -> list[dict]:
    reg, att = Counter(), Counter()
    for r in rows:
        label = label_of(r) or "Not stated"
        reg[label] += 1
        if is_present(r):
            att[label] += 1
    return [{"label": k, "registered": reg[k], "attended": att[k]}
            for k in sorted(reg, key=lambda k: (-reg[k], k))]


def compute_stats(rows: list[dict], day: str | None = None) -> dict:
    """Aggregates for the chart page. `day` limits "attended" to one day;
    None means attended on at least one day."""
    def present(r: dict) -> bool:
        if day:
            return _attended(r[ATTEND_COLS[day]])
        return any(_attended(r[c]) for c in ATTEND_COLS.values())

    attended = [r for r in rows if present(r)]
    days_attended = Counter(
        sum(_attended(r[c]) for c in ATTEND_COLS.values())
        for r in rows if any(_attended(r[c]) for c in ATTEND_COLS.values())
    )

    other_churches = Counter(
        _norm(r["church"]).title() or "Not stated"
        for r in attended if not is_home_church(r["church"])
    )

    by_hour: Counter = Counter()
    if day:
        for r in attended:
            m = re.search(r"(\d{1,2}):\d{2}", r[ATTEND_COLS[day]])
            if m:
                by_hour[int(m.group(1))] += 1

    def area_label(r):
        return re.sub(r"\s*--.*$", "", r["area"]).strip()

    return {
        "day": day,
        "registered": len(rows),
        "attended": len(attended),
        "per_day": {d: sum(_attended(r[ATTEND_COLS[d]]) for r in rows) for d in DAYS},
        "first_timers": sum(_attended(r[FIRST_TIMER_COL]) for r in attended),
        "home_church": sum(is_home_church(r["church"]) for r in attended),
        "other_church": sum(not is_home_church(r["church"]) for r in attended),
        "registered_home_church": sum(is_home_church(r["church"]) for r in rows),
        "days_attended": {str(n): days_attended.get(n, 0) for n in (1, 2, 3)},
        "age_group": _breakdown(rows, lambda r: r["age_group"], present),
        "gender": _breakdown(rows, lambda r: r["gender"], present),
        "church": _breakdown(
            rows, lambda r: HOME_ORG_NAME if is_home_church(r["church"]) else "Other organisations",
            present),
        "transport": _breakdown(rows, lambda r: r["transport"], present),
        "area": _breakdown(rows, area_label, present),
        "source": _breakdown(rows, lambda r: r["source"], present),
        "other_churches": [{"label": k, "count": v} for k, v in other_churches.most_common(8)],
        "by_hour": [{"hour": h, "count": by_hour[h]} for h in sorted(by_hour)],
    }


def _err(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, detail={"success": False, "error": code, "message": message})


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/attend", include_in_schema=False)


def _day(day: str) -> str:
    day = (day or "").lower()
    if day not in DAYS:
        raise _err(400, "invalid_day", "Day must be friday, saturday or sunday.")
    return day


def _find(rows: list[dict], row: int) -> dict:
    rec = next((r for r in rows if r["row"] == row), None)
    if not rec:
        raise _err(404, "not_found", "That person wasn't found — search again.")
    return rec


def _day_count(rows: list[dict], day: str) -> int:
    return sum(_attended(r[ATTEND_COLS[day]]) for r in rows)


async def _write(rec: dict, updates: dict, only_if_empty: str | None = None) -> dict:
    """One call to the sheet, then patch the snapshot. Errors become HTTP errors."""
    try:
        result = await get_store().write(rec["row"], rec["name"], rec["phone"], updates,
                                         only_if_empty=only_if_empty)
    except SheetError as exc:
        if exc.code == "row_changed":
            _distrust_snapshot()
            raise _err(409, exc.code, exc.message)
        raise _err(502, exc.code, exc.message)
    if result.get("already"):
        _patch(rec, {only_if_empty: result.get("current", rec.get(only_if_empty, ""))})
    else:
        _patch(rec, updates)
    return result


@router.get("/search")
async def search(day: str = Query(...), q: str = Query(default="", max_length=80)):
    day = _day(day)
    rows = await _rows()
    results = search_people(rows, q) if len(q.strip()) >= 2 else []
    return {
        "success": True,
        "results": [public_person(r, day) for r in results],
        "day_checked_in": _day_count(rows, day),
        "registered": len(rows),
        "demo": isinstance(get_store(), DemoStore),
    }


class CheckIn(BaseModel):
    row: int
    day: str
    phone: str = Field(default="", max_length=40)  # optional; checked only if given
    first_timer: bool | None = None                # None = leave as is


@router.post("/check-in")
async def check_in(body: CheckIn):
    day = _day(body.day)
    rows = await _rows()
    rec = _find(rows, body.row)

    # The number is an optional extra check: leave it blank and the name alone
    # is enough. If the agent did type one, it has to be right.
    if body.phone.strip() and not phone_matches(rec["phone"], body.phone):
        raise _err(422, "phone_mismatch",
                   "That number doesn't match the one on the sheet. Ask again, "
                   "or clear the box to register by name.")

    updates = {ATTEND_COLS[day]: checkin_label(rec["gender"])}
    if body.first_timer is not None:
        updates[FIRST_TIMER_COL] = "Yes" if body.first_timer else "No"
    result = await _write(rec, updates, only_if_empty=ATTEND_COLS[day])

    if result.get("already") and body.first_timer is not None \
            and body.first_timer != _attended(rec[FIRST_TIMER_COL]):
        # Another agent got there first and kept their time; still honour the
        # first-timer answer given on this device.
        await _write(rec, {FIRST_TIMER_COL: "Yes" if body.first_timer else "No"})

    return {"success": True, "already": bool(result.get("already")),
            "person": public_person(rec, day), "day_checked_in": _day_count(rows, day)}


class Undo(BaseModel):
    row: int
    day: str


@router.post("/undo")
async def undo(body: Undo):
    day = _day(body.day)
    rows = await _rows()
    rec = _find(rows, body.row)
    updates = {ATTEND_COLS[day]: ""}
    if not any(_attended(rec[ATTEND_COLS[d]]) for d in DAYS if d != day):
        # Fully un-registered: don't leave a stale first-timer flag behind.
        updates[FIRST_TIMER_COL] = ""
    await _write(rec, updates)
    return {"success": True, "person": public_person(rec, day),
            "day_checked_in": _day_count(rows, day)}


class FirstTimer(BaseModel):
    row: int
    value: bool


@router.post("/first-timer")
async def toggle_first_timer(body: FirstTimer):
    rec = _find(await _rows(), body.row)
    await _write(rec, {FIRST_TIMER_COL: "Yes" if body.value else "No"})
    return {"success": True, "person": public_person(rec)}


class WalkIn(BaseModel):
    day: str
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(max_length=40)
    gender: str
    age_group: str = Field(default="", max_length=60)
    church: str = Field(default="", max_length=120)
    first_timer: bool


@router.post("/walk-in")
async def walk_in(body: WalkIn):
    """Register someone who is not on the sheet: append a row (flagged
    "Walk-in") and mark them present for the day in the same write."""
    day = _day(body.day)
    name = re.sub(r"\s+", " ", body.name).strip()
    if len(name) < 2:
        raise _err(422, "invalid_name", "Enter the person's name.")
    if body.gender not in GENDERS:
        raise _err(422, "invalid_gender", "Pick Male or Female.")
    if body.age_group and body.age_group not in AGE_GROUPS:
        raise _err(422, "invalid_age_group", "Pick an age group from the list.")
    phone = body.phone.strip()
    if len(_digits(phone)) < 7:
        # Required for walk-ins: there is no sheet entry to fall back on, and
        # the number is how first-timers get followed up afterwards.
        raise _err(422, "invalid_phone", "Enter the person's phone number (at least 7 digits).")

    rows = await _rows()
    twin = next((r for r in rows if _norm(r["name"]) == _norm(name)
                 and (not phone or not _digits(r["phone"]) or phone_matches(r["phone"], phone))), None)
    if twin:
        raise HTTPException(409, detail={
            "success": False, "error": "already_on_list",
            "message": f"{twin['name']} is already on the list — search for them instead.",
            "person": public_person(twin, day)})

    now = datetime.now(app_timezone())
    cells = {
        # Same shape the Google Form writes, so the column stays consistent.
        "timestamp": f"{now.month}/{now.day}/{now.year} {now:%H:%M:%S}",
        "name": name, "phone": phone, "gender": body.gender,
        "age_group": body.age_group, "church": body.church.strip(),
        "source": WALK_IN_SOURCE,
        ATTEND_COLS[day]: checkin_label(body.gender, now),
        FIRST_TIMER_COL: "Yes" if body.first_timer else "No",
    }
    try:
        row = await get_store().append(cells)
    except SheetError as exc:
        raise _err(502, exc.code, exc.message)

    rec = {"row": row, **{k: "" for k in ("timestamp", "name", "phone", "gender", "age_group",
                                          "church", "transport", "area", "source", *NEW_COLS)}}
    rec.update(cells)
    rows.append(rec)
    _cache.version += 1
    return {"success": True, "person": public_person(rec, day),
            "day_checked_in": _day_count(rows, day), "registered": len(rows)}


@router.get("/first-timers")
async def first_timers():
    rows = await _rows()
    people = [public_person(r, full_phone=True) for r in rows if _attended(r[FIRST_TIMER_COL])]
    people.sort(key=lambda p: p["name"].lower())
    return {"success": True, "people": people}


@router.get("/stats")
async def stats(day: str | None = Query(default=None)):
    day = _day(day) if day and day != "all" else None
    return {"success": True, **compute_stats(await _rows(), day)}
