# I Am Supernatural — The SuperNaturals 2026

A web app that places any person into a cinematic, photorealistic supernatural portrait using Google Gemini AI. Users upload a selfie, choose a biblical scene, optionally add a personal twist, and receive a 1080 × 1620 portrait they can download and share.

---

## What It Does

1. **User uploads a photo** — front-facing, well-lit, single person.
2. **User selects a scene** — 10 biblical moments across 4 categories (Miracles & Power, Authority & Warfare, Fire & Spirit, Ascension & Glory).
3. **User optionally adds a twist** — free-text for personal details like outfit changes, accessories, or extra elements. These are applied faithfully by the AI.
4. **Gemini generates the portrait** — the user's face, skin tone, and build are preserved from the reference photo. The scene's supernatural elements (wings, divine light, VFX, cinematic composition) are applied on top.
5. **User downloads or shares** — the downloaded image has the event logo watermarked in the top-right corner.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.11+) |
| AI | Google Gemini (image generation via `google-genai` SDK) |
| Rate-limit storage | Supabase Postgres (free tier) — no images or personal data |
| Image Processing | Pillow (input portrait-crop), Canvas API (watermark) |

---

## Project Structure

```
i-will-be-there/
├── backend/
│   ├── main.py              # FastAPI app — routes, rate limiting, CORS
│   ├── gemini_client.py     # Gemini API calls + model fallback chain
│   ├── prompt_builder.py    # Assembles the final prompt per scene
│   ├── scene_prompts.py     # 10 photorealistic scene prompt texts
│   ├── validator.py         # Image validation (size, type, face detection)
│   ├── storage.py           # Supabase-backed per-IP rate limiting
│   └── .env                 # API keys (never commit this)
├── frontend/
│   ├── src/
│   │   ├── screens/
│   │   │   ├── Landing.jsx  # Home screen
│   │   │   ├── Upload.jsx   # Photo upload + scene picker + form
│   │   │   └── Result.jsx   # Generated image + download/share
│   │   ├── components/
│   │   │   └── ScenePicker.jsx  # Accordion scene selector
│   │   └── data/
│   │       └── scenes.js    # Scene metadata (IDs, titles, descriptions)
│   ├── public/
│   │   └── logo_stamp.png   # Watermark applied on download/share
│   └── .env                 # VITE_API_URL (never commit with real keys)
└── logo_stamp.png           # Master logo file
```

---

## How the AI Generation Works

### Input preprocessing
Before the photo is sent to Gemini, it is **center-cropped and resized to 1080 × 1620 px** (2:3 portrait). This is the strongest signal to the model to output in portrait orientation, since Gemini mirrors the aspect ratio of the reference image.

### Prompt architecture
Each scene has a full ~30-line photorealistic prompt stored in `backend/scene_prompts.py`. The prompt follows an 11-layer technical formula:

1. Genre tag (`photorealistic fantasy realism`)
2. Shot type and camera angle
3. Subject pose and expression
4. Attire (every scene has its own wardrobe, styled to that scene — modern and clean, never the clothes from the upload)
5. Supernatural VFX description
6. Volumetric lighting recipe
7. Realism anchors (subsurface scattering, feather detail, physically accurate reflections)
8. Background depth and composition
9. Named color grade
10. Scale word
11. No-text directive

`prompt_builder.py` assembles the final string:
```
[scene prompt]

[size directive: portrait 1080 × 1620]

[wardrobe directive — the photo supplies identity, not clothing; the scene's
 wardrobe is fitted to the subject's own gender and build]

[user twist, if any — carries the scene's wardrobe rule, so a clothing request
 changes the garment but not the scene]

[identity lock — face, skin tone, hair and build stay the person's own]

[wing-color lock — wings stay pure white]

No text, no watermarks, no labels of any kind.
```

### Per-scene wardrobe
Street clothes from an upload pulled the generated portraits out of their scene, so each scene now specifies its own styling — deliberately modern and clean (contemporary tailoring, no ancient robes or gowns) so people still look like themselves:

| Scene | Wardrobe |
|---|---|
| Walking on Water | Crisp modern all-white, rolled sleeves, barefoot |
| Commanding the Storm | Off-white shirt under a long ivory storm coat |
| Defeating Giants | White & gold battle armor, modern athletic cut |
| Silencing the Lion | Sharp black tailoring over a white shirt, gold detail |
| Breaking Every Chain | Plain white tee, bare forearms where chains break |
| Walking Through Fire | Pristine white, spotless inside the furnace |
| Anointed with Oil | Modern white ceremonial coat, gold embroidery |
| Ascending on Eagle's Wings | White with a lightweight trailing overlayer |
| Army of Angels | White & gold battle armor, polished and modern |
| Receiving the Mantle | Understated stone-white shirt, dark trousers |

The wardrobe shows on the scene picker in the UI.

Each scene also has a **wardrobe rule** (`SCENE_WARDROBE_RULES` in `scene_prompts.py`) that bounds what a user's twist may do to the clothing. The garment is theirs to choose — a white gown instead of a white shirt, an agbada instead of a suit — but it has to satisfy the rule, so the outfit still belongs to the scene. Walking on Water requires white and bare feet; Defeating Giants requires armor; Walking Through Fire requires pristine and unscorched, and so on. A request that would break the rule isn't refused and doesn't fall back to the default outfit — it's rendered as the asked-for garment adapted to the rule (a white version, an armored version). The scene's setting, VFX, lighting, composition and colour grade are never the twist's to change.

### Model fallback chain
`gemini_client.py` tries models in order until one returns an image:
1. `gemini-2.5-flash-image-preview` — primary, free tier (500 images/day quota)
2. `gemini-3.1-flash-image-preview`
3. `nano-banana-pro-preview`
4. `gemini-3-pro-image-preview`
5. `gemini-2.5-flash-image` — requires billing

### Watermark
Applied **client-side** at download/share time via the Canvas API (`OffscreenCanvas`). The logo is drawn at 28% of image width, top-right corner, 7% transparent. The preview on screen is always clean.

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Service health check |
| `GET` | `/active-scene` | — | This week's live scene + full campaign schedule |
| `GET` | `/debug/gemini` | — | Lists available Gemini models |
| `POST` | `/generate` | — | Generate portrait (rate-limited: 3/day per IP, 5 min cooldown) |

### `POST /generate` form fields

| Field | Required | Description |
|---|---|---|
| `image` | ✅ | JPEG or PNG, max 5 MB, min 512 × 512 px |
| `scene_id` | ✅ | Must match this week's active scene (see `/active-scene`) |
| `custom_prompt` | — | Optional personal twist (max 500 chars) |

---

## Running Locally

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
# Set VITE_API_URL=http://localhost:8000 in frontend/.env
npm run dev
```

Open `http://localhost:5173`.

---

## Environment Variables

### Backend `.env`
```
GEMINI_API_KEY=        # Google AI Studio key — aistudio.google.com/app/apikey
GEMINI_MODEL=          # gemini-2.5-flash-image-preview to force the free tier
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

## Rate Limiting

Up to 3 generations per IP address per day, with a 5-minute cooldown between each. Limits are persisted in Supabase (not in-memory), so they survive Render restarting the free-tier instance after it spins down from inactivity.

If Supabase is unconfigured or unreachable, limits fall back to a **per-process in-memory store** rather than failing open — they still count down, but they reset on restart and aren't shared across instances. `GET /health` reports which store is live:

```json
"supabase": { "configured": true, "connected": false, "store": "memory", "error": "…" }
```

`store: "memory"` with `connected: false` means the quota badge in the UI works but limits are only as durable as the running instance — worth fixing before a big push, since every generation costs money.

On top of the per-IP limit, a global concurrency regulator (`MAX_CONCURRENT_GENERATIONS`) caps how many Gemini calls run at once so a burst of simultaneous requests queues instead of blowing through Gemini's per-minute rate limit. Requests beyond `MAX_QUEUE_DEPTH` get an immediate "high demand" message instead of hanging.

---

## Image Storage

Generated portraits are never persisted server-side — each is returned directly to the browser as a base64 data URL and only exists there. Users must download or share it before leaving the page. The original uploaded selfie is processed in memory and discarded immediately, same as before.
