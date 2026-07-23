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
| Image Storage | Cloudinary (free tier) |
| Database | Supabase Postgres (free tier) |
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
│   ├── storage.py           # Cloudinary upload + Supabase save
│   └── .env                 # API keys (never commit this)
├── frontend/
│   ├── src/
│   │   ├── screens/
│   │   │   ├── Landing.jsx  # Home screen
│   │   │   ├── Upload.jsx   # Photo upload + scene picker + form
│   │   │   ├── Result.jsx   # Generated image + download/share
│   │   │   └── Admin.jsx    # Password-protected submissions dashboard
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
4. Attire (preserved from photo for most scenes; specific thematic dress for 3 scenes)
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

[user twist, if any — clothing/appearance here overrides scene defaults]

No text, no watermarks, no labels of any kind.
```

### Model fallback chain
`gemini_client.py` tries models in order until one returns an image:
1. `gemini-3.1-flash-image-preview`
2. `nano-banana-pro-preview`
3. `gemini-3-pro-image-preview`
4. `gemini-2.5-flash-image`

### Watermark
Applied **client-side** at download/share time via the Canvas API (`OffscreenCanvas`). The logo is drawn at 28% of image width, top-right corner, 7% transparent. The preview on screen is always clean.

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Service health check |
| `GET` | `/debug/gemini` | — | Lists available Gemini models |
| `POST` | `/generate` | — | Generate portrait (rate-limited: 1 per IP / 5 min) |
| `GET` | `/submissions` | Basic auth | Admin: list all submissions |
| `DELETE` | `/submissions/{id}` | Basic auth | Admin: delete a submission |

### `POST /generate` form fields

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Person's full name (1–100 chars) |
| `image` | ✅ | JPEG or PNG, max 5 MB, min 512 × 512 px |
| `scene_id` | ✅ | One of the 10 scene IDs |
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
GEMINI_MODEL=          # Leave blank to auto-try all models in order
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
SUPABASE_URL=
SUPABASE_KEY=
ADMIN_PASSWORD=        # Password for the /admin dashboard
CORS_ORIGINS=*         # Comma-separated or * for open (lock down in production)
```

### Frontend `.env`
```
VITE_API_URL=http://localhost:8000   # Point to your backend URL
```

---

## Rate Limiting

One generation per IP address every 5 minutes, enforced in-memory on the backend. Restarting the server resets all limits.

---

## Admin Dashboard

Visit `/admin` in the browser. Login: `admin` / `<ADMIN_PASSWORD from .env>`. Shows all generated submissions with name, image, and timestamp. Individual submissions can be deleted.
