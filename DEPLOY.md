# Deployment Guide — I Am Supernatural

Deploy the app for free using **Render** (backend) and **Vercel** (frontend). Both have generous free tiers that cover a conference-scale event.

---

## Before You Deploy

### Clean up local dev settings

Two files carry values used during local/ngrok testing that must be updated before going live:

| File | What to change |
|---|---|
| `frontend/.env` | Replace any `ngrok` URL in `VITE_API_URL` with your Render backend URL (e.g. `https://your-backend.onrender.com`). Vercel reads this at build time — if it still points to an ngrok URL the app will be broken in production. |
| `backend/.env` | `CORS_ORIGINS=*` is fine for now. Once you have your Vercel URL, lock it down to `CORS_ORIGINS=https://your-app.vercel.app`. |

> `frontend/vite.config.js` has `host: '0.0.0.0'` and `allowedHosts: true` which were added for ngrok. These are **dev-server-only settings** — Vercel ignores them entirely during the production build, so no change is needed there.

---

### You need accounts and API keys for:

| Service | Purpose | Free tier |
|---|---|---|
| [Google AI Studio](https://aistudio.google.com/app/apikey) | Gemini image generation | 500 images/day on `gemini-2.5-flash-image-preview` |
| [Supabase](https://supabase.com) | Per-IP rate-limit tracking only — no images or personal data stored | 500 MB database, unlimited rows |

Generated portraits are never stored server-side — they're returned directly to the browser and must be downloaded/shared from there. This keeps the app storage-free, so there's no Cloudinary or other image host to set up.

---

## Step 1 — Supabase Setup

1. Create a new Supabase project.
2. Go to **SQL Editor** and run:

```sql
create table rate_limits (
  ip                 text primary key,
  day                date not null,
  count              int not null default 0,
  last_generated_at  timestamptz
);
```

   This is the only table the app uses — it enforces 3 generations/day per IP plus a 5-minute cooldown, and is checked/updated on every `/generate` call. If you have an older `submissions` table from a previous version, it's no longer used and can be dropped.

3. Copy your **Project URL** and **anon public key** from Project Settings → API.

---

## Step 2 — Deploy the Backend on Render

### 2a. Create a new Web Service

1. Go to [render.com](https://render.com) → New → **Web Service**.
2. Connect your GitHub repo (push the project there first if you haven't).
3. Set the **Root Directory** to `backend`.
4. Set **Runtime** to `Python 3`.
5. Set **Build Command**:
   ```
   pip install -r requirements.txt
   ```
6. Set **Start Command**:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
7. Choose the **Free** instance type.

### 2b. Set environment variables on Render

In the Render dashboard → Environment, add:

```
GEMINI_API_KEY              = <your key>
GEMINI_MODEL                = gemini-2.5-flash-image-preview   (forces the free 500 images/day tier)
SUPABASE_URL                = <your supabase project URL>
SUPABASE_KEY                = <your supabase anon key>
CORS_ORIGINS                = https://your-app.vercel.app
MAX_CONCURRENT_GENERATIONS  = 3    (Gemini calls allowed in flight at once)
MAX_QUEUE_DEPTH              = 12   (requests queued beyond this get a fast "high demand" response)
```

> ⚠️ Set `CORS_ORIGINS` to your **exact Vercel URL** once you have it (Step 3 below). Until then you can use `*`.

### 2c. Note your backend URL

After deploy completes, Render gives you a URL like:
```
https://your-backend.onrender.com
```
Copy it — you need it for the frontend.

### 2d. Verify the backend is live

```bash
curl https://your-backend.onrender.com/health
```

Expected response:
```json
{"status": "ok", "gemini_key_set": true, ...}
```

> 💤 **Note:** Free Render instances spin down after 15 minutes of inactivity. The first request after idle takes ~30-60 seconds. Consider upgrading to Starter ($7/month) for production to avoid cold starts.

---

## Step 3 — Deploy the Frontend on Vercel

### 3a. Build configuration

1. Go to [vercel.com](https://vercel.com) → New Project → import your repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite** (Vercel detects this automatically).
4. Build Command: `npm run build`
5. Output Directory: `dist`

### 3b. Set environment variables on Vercel

In the Vercel dashboard → Settings → Environment Variables, add:

```
VITE_API_URL = https://your-backend.onrender.com
```

Replace the URL with your actual Render backend URL.

### 3c. Deploy

Click **Deploy**. Vercel builds and publishes to a URL like:
```
https://your-app.vercel.app
```

### 3d. Update CORS on Render

Go back to Render → Environment → update `CORS_ORIGINS` to your exact Vercel URL. Render will redeploy automatically.

---

## Step 4 — Custom Domain (Optional)

### Vercel
1. Vercel dashboard → Domains → Add Domain.
2. Add a CNAME record at your DNS provider pointing to `cname.vercel-dns.com`.
3. Vercel provisions SSL automatically.

### Render
1. Render dashboard → Settings → Custom Domains → Add.
2. Add a CNAME at your DNS provider.
3. Update `CORS_ORIGINS` on Render to include the custom domain.

---

## Step 5 — Verify End-to-End

1. Open your Vercel URL.
2. Upload a test photo, select this week's active scene, tap Generate.
3. Confirm the image appears on the result screen and downloads/shares correctly with the watermark.
4. Generate 3 times in a row from the same IP — the 4th should be rejected with the daily-limit message. Check the `rate_limits` row for your IP in Supabase to confirm it's tracking correctly.
5. Background the tab for a minute (switch apps) and return — the result screen should still be there instead of resetting to the landing page.

---

## Scaling for a Large Event

| Concern | Solution |
|---|---|
| Backend cold starts | Upgrade Render to Starter ($7/month) — no spin-down |
| Gemini per-minute rate limit | `MAX_CONCURRENT_GENERATIONS` / `MAX_QUEUE_DEPTH` on Render throttle bursts so they queue instead of erroring — tune lower if you still see 429s from Gemini |
| Concurrent users | Render free tier is single-instance (0.1 CPU / 512 MB) — the concurrency regulator above is the main mitigation short of upgrading the instance type |
| Rate-limit persistence | Stored in Supabase, not in-memory, so it survives Render restarts. If Supabase is briefly unreachable, the check fails open (allows the request) rather than blocking everyone |
| Supabase auto-pause | Free Supabase projects pause after 7 days with zero activity. A quiet week could pause it — the app still works either way (rate-limit check fails open), but you'd lose enforcement until you un-pause it in the Supabase dashboard |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gemini_key_set: false` on `/health` | API key missing or wrong | Check `GEMINI_API_KEY` on Render |
| `BILLING_REQUIRED` error | Gemini free tier quota hit (daily or per-minute) | Wait a minute and retry, or enable billing at aistudio.google.com/billing |
| CORS error in browser | `CORS_ORIGINS` doesn't match frontend URL | Update the env var on Render and redeploy |
| "high demand" errors under light load | `MAX_QUEUE_DEPTH` too low, or Gemini calls are slow/timing out | Check Render logs for the actual Gemini latency; raise `MAX_QUEUE_DEPTH` if the instance can handle it |
| Rate limit not resetting daily | Supabase `rate_limits` row stuck | Check the `day` column matches today's date in Supabase; delete the row to reset manually |
| Cold start timeout | Free Render tier | Upgrade to Starter or warm the service with a cron ping |
