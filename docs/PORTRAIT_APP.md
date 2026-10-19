# Portrait app

The generator behind the 2026 campaign: a visitor uploads a selfie, picks the week's scene, optionally adds a "twist", and
gets a 1080 × 1620 portrait back. Backend in [`portrait-app/backend`](../portrait-app/backend), frontend in
[`portrait-app/frontend`](../portrait-app/frontend).

## How it works

1. The upload is validated (type, size, minimum resolution, exactly one face) and **centre-cropped to 1080 × 1620**. Gemini mirrors the
   reference image's aspect ratio, so this is the strongest portrait-orientation signal.
2. [`prompt_builder.py`](../portrait-app/backend/prompt_builder.py) wraps the scene prompt from
   [`scene_prompts.py`](../portrait-app/backend/scene_prompts.py) in identity, wardrobe, size and no-text directives. See
   [PROMPT_LESSONS](PROMPT_LESSONS.md) for why each one exists.
3. [`gemini_client.py`](../portrait-app/backend/gemini_client.py) sends it to the configured Gemini image model, with multi-key failover.
4. The image goes back to the browser as a base64 data URL. The logo watermark is applied client-side at download/share time.

One scene is live per week ([`scene_prompts.py`](../portrait-app/backend/scene_prompts.py) → `get_active_scene_id`). Closed days and daily
caps ([`availability.py`](../portrait-app/backend/availability.py)) keep spend inside a fixed budget.

## Backend files

| File | Role |
|---|---|
| `main.py` | FastAPI app: routes, rate limiting, CORS, `/status`, owner vault routes |
| `gemini_client.py` | Gemini calls, model list, API-key failover, usage accounting |
| `prompt_builder.py` | Assembles the final prompt |
| `scene_prompts.py` | The scene prompts, wardrobe rules and weekly schedule |
| `validator.py` | Image validation incl. face detection (mediapipe) |
| `storage.py` | Supabase-backed per-IP limits and the service-wide daily counter |
| `availability.py` | Closed weekdays, per-weekday caps, timezone |
| `usage_tracker.py` | In-memory counts of Gemini successes, failures and quota blocks |
| `vault.py` | Owner-only unlock (disabled until `VAULT_KEY_HASH` is set) |
| `attendance.py`, `apps_script/Attendance.gs` | Event-day check-in against a Google Sheet |

## Frontend

React 18 + Vite + Tailwind. `src/config/event.js` holds all event copy; `src/data/scenes.js` the scene cards. `src/main.jsx` picks
a page from the URL path, so there is no router:

| Path | Page |
|---|---|
| `/` | The portrait generator |
| `/about-conference` | Scroll-snap event page, driven by `src/data/event/*.json` |
| `/our-sponsors` | Sponsor showcase page |
| `/attend_event`, `/attend_event/first_timers`, `/attend_event/chart` | Door check-in, first-timer follow-up list, live attendance chart |

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Service health check |
| `GET` | `/active-scene` | — | This week's live scene + the scene schedule |
| `GET` | `/debug/gemini` | — | Lists available Gemini models |
| `POST` | `/generate` | — | Generate portrait (rate-limited: 2/day per IP, 5 min cooldown by default) |

### `POST /generate` form fields

| Field | Required | Description |
|---|---|---|
| `image` | ✅ | JPEG or PNG, max 5 MB, min 512 × 512 px |
| `scene_id` | ✅ | Must match this week's active scene (see `/active-scene`) |
| `custom_prompt` | — | Optional personal twist (max 500 chars) |

---

## Running locally

```bash
cd portrait-app/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your keys
uvicorn main:app --reload
```

```bash
cd portrait-app/frontend
npm install
cp .env.example .env          # VITE_API_URL=http://localhost:8000
npm run dev
```

Open `http://localhost:5173`. Set `RATE_LIMIT_DISABLED=true` in the backend `.env` to test without Supabase or per-IP limits (the daily cap still applies).

## Environment Variables

### Backend `.env`
```
GEMINI_API_KEY=        # Google AI Studio key — aistudio.google.com/app/apikey
GEMINI_MODEL=          # e.g. gemini-3.1-flash-image (no free image tier exists)
SUPABASE_URL=          # Used only to persist per-IP rate limits — no images stored
SUPABASE_KEY=
CORS_ORIGINS=*         # Comma-separated or * for open (lock down in production)
MAX_CONCURRENT_GENERATIONS=3   # Concurrent Gemini calls allowed at once
MAX_QUEUE_DEPTH=12             # Requests queued beyond that get a friendly 429
```

### Frontend `.env`
```
VITE_API_URL=http://localhost:8000   # Point to your backend URL
```

---

The full list, with comments, is in `portrait-app/backend/.env.example`.

## Rate Limiting

Up to 2 generations per IP address per day, with a 5-minute cooldown between each. Limits are persisted in Supabase (not in-memory), so they survive Render restarting the free-tier instance after it spins down from inactivity.

If Supabase is unconfigured or unreachable, limits fall back to a **per-process in-memory store** rather than failing open — they still count down, but they reset on restart and aren't shared across instances. `GET /health` reports which store is live:

```json
"supabase": { "configured": true, "connected": false, "store": "memory", "error": "…" }
```

`store: "memory"` with `connected: false` means the quota badge in the UI works but limits are only as durable as the running instance — worth fixing before a big push, since every generation costs money.

On top of the per-IP limit, a global concurrency regulator (`MAX_CONCURRENT_GENERATIONS`) caps how many Gemini calls run at once so a burst of simultaneous requests queues instead of blowing through Gemini's per-minute rate limit. Requests beyond `MAX_QUEUE_DEPTH` get an immediate "high demand" message instead of hanging.

---

## Image Storage

Generated portraits are never persisted server-side — each is returned directly to the browser as a base64 data URL and only exists there. Users must download or share it before leaving the page. The original uploaded selfie is processed in memory and discarded immediately, same as before.
