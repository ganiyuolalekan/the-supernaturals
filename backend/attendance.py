"""
Event-day attendance — /attend/* routes.

Door agents search the registration sheet, confirm the person's number, and
mark them as arrived for a given conference day. The registration Google Sheet
(the Google Form's response sheet) is the system of record: this module reads
it and writes four extra columns back into it:

    attend_friday | attend_saturday | attend_sunday | first_timer

An attend_* cell holds the check-in time ("2026-10-16 09:42"); empty means not
arrived. first_timer holds "Yes" or is empty.

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

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from availability import app_timezone

log = logging.getLogger(__name__)

DAYS = ("friday", "saturday", "sunday")
FIRST_TIMER_COL = "first_timer"
ATTEND_COLS = {d: f"attend_{d}" for d in DAYS}
NEW_COLS = (*ATTEND_COLS.values(), FIRST_TIMER_COL)

# "RCCG Praise Assembly", "Praise assembly", "Praiseassembly", "RCCG, Praise
# Assembly Parish", plus the typos people actually typed ("Praise Asssembly",
# "Praises assembly", "Praise Assemble", "Rccg praise ass"). A bare "RCCG" is
# deliberately NOT a match — that is any of thousands of other parishes.
HOME_CHURCH_RE = re.compile(r"pra[iy]s\w*\s*[-_.]?\s*as+\w*", re.IGNORECASE)

CACHE_TTL_SECONDS = 5
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
        self.rows: list[dict] = []
        self.at = 0.0
        self.store_id = None
        self.lock = asyncio.Lock()


_cache = _Cache()


async def _rows(force: bool = False) -> list[dict]:
    store = get_store()
    if store is None:
        raise HTTPException(503, detail={
            "success": False, "error": "not_configured",
            "message": "Attendance isn't connected to the sheet yet (see DEPLOY.md).",
        })
    async with _cache.lock:
        fresh = (time.monotonic() - _cache.at) < CACHE_TTL_SECONDS
        if force or not fresh or _cache.store_id is not store:
            try:
                _cache.rows = await store.list_rows()
            except SheetError as exc:
                raise HTTPException(502, detail={
                    "success": False, "error": exc.code, "message": exc.message,
                })
            _cache.at = time.monotonic()
            _cache.store_id = store
        return _cache.rows


def _invalidate() -> None:
    _cache.at = 0.0


# ---------------------------------------------------------------------------
# Pure helpers (also what the tests exercise)
# ---------------------------------------------------------------------------

def is_home_church(church: str) -> bool:
    return bool(HOME_CHURCH_RE.search(church or ""))


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
            m = re.match(r"\d{4}-\d{2}-\d{2} (\d{2}):\d{2}", r[ATTEND_COLS[day]])
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
            rows, lambda r: "RCCG Praise Assembly" if is_home_church(r["church"]) else "Other churches",
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


@router.get("/search")
async def search(day: str = Query(...), q: str = Query(default="", max_length=80)):
    day = _day(day)
    rows = await _rows()
    results = search_people(rows, q) if len(q.strip()) >= 2 else []
    return {
        "success": True,
        "results": [public_person(r, day) for r in results],
        "day_checked_in": sum(_attended(r[ATTEND_COLS[day]]) for r in rows),
        "registered": len(rows),
        "demo": isinstance(get_store(), DemoStore),
    }


class CheckIn(BaseModel):
    row: int
    day: str
    phone: str = Field(default="", max_length=40)
    unverified: bool = False          # agent couldn't confirm the number
    first_timer: bool | None = None   # None = leave as is


@router.post("/check-in")
async def check_in(body: CheckIn):
    day = _day(body.day)
    rec = _find(await _rows(), body.row)

    if not body.unverified and not phone_matches(rec["phone"], body.phone):
        raise _err(422, "phone_mismatch",
                   "That number doesn't match the one on the sheet. Ask them again, "
                   "or check in without number confirmation if they can't recall it.")

    updates = {ATTEND_COLS[day]: time_now()}
    if body.first_timer is not None:
        updates[FIRST_TIMER_COL] = "Yes" if body.first_timer else ""
    store = get_store()
    try:
        result = await store.write(rec["row"], rec["name"], rec["phone"], updates,
                                   only_if_empty=ATTEND_COLS[day])
    except SheetError as exc:
        raise _err(409 if exc.code == "row_changed" else 502, exc.code, exc.message)
    _invalidate()

    rec = _find(await _rows(force=True), body.row)
    person = public_person(rec, day)
    if result.get("already"):
        # Another agent got there first — keep their time, but still honour a
        # first-timer tick the agent set on this device.
        if body.first_timer is not None and body.first_timer != person["first_timer"]:
            await toggle_first_timer(FirstTimer(row=body.row, value=body.first_timer))
            person = public_person(_find(await _rows(force=True), body.row), day)
    return {"success": True, "already": bool(result.get("already")), "person": person}


class Undo(BaseModel):
    row: int
    day: str


@router.post("/undo")
async def undo(body: Undo):
    day = _day(body.day)
    rec = _find(await _rows(), body.row)
    updates = {ATTEND_COLS[day]: ""}
    still_attending = any(
        _attended(rec[ATTEND_COLS[d]]) for d in DAYS if d != day
    )
    if not still_attending:
        # Fully un-registered: don't leave a stale first-timer flag behind to
        # be re-sent (or pre-ticked) when they are registered again.
        updates[FIRST_TIMER_COL] = ""
    try:
        await get_store().write(rec["row"], rec["name"], rec["phone"], updates)
    except SheetError as exc:
        raise _err(409 if exc.code == "row_changed" else 502, exc.code, exc.message)
    _invalidate()
    return {"success": True, "person": public_person(_find(await _rows(force=True), body.row), day)}


class FirstTimer(BaseModel):
    row: int
    value: bool


@router.post("/first-timer")
async def toggle_first_timer(body: FirstTimer):
    rec = _find(await _rows(), body.row)
    try:
        await get_store().write(rec["row"], rec["name"], rec["phone"],
                                {FIRST_TIMER_COL: "Yes" if body.value else ""})
    except SheetError as exc:
        raise _err(409 if exc.code == "row_changed" else 502, exc.code, exc.message)
    _invalidate()
    return {"success": True, "person": public_person(_find(await _rows(force=True), body.row))}


@router.get("/first-timers")
async def first_timers():
    rows = await _rows(force=True)
    people = [public_person(r, full_phone=True) for r in rows if _attended(r[FIRST_TIMER_COL])]
    people.sort(key=lambda p: p["name"].lower())
    return {"success": True, "people": people}


@router.get("/stats")
async def stats(day: str | None = Query(default=None)):
    day = _day(day) if day and day != "all" else None
    return {"success": True, **compute_stats(await _rows(force=True), day)}


def time_now() -> str:
    from datetime import datetime
    return datetime.now(app_timezone()).strftime("%Y-%m-%d %H:%M")
