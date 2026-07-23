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
| [Google AI Studio](https://aistudio.google.com/app/apikey) | Gemini image generation | Requires billing enabled (~$0.04/image) |
| [Cloudinary](https://cloudinary.com) | Generated image storage | 25 GB storage, 25 GB bandwidth/month |
| [Supabase](https://supabase.com) | Submission metadata | 500 MB database, unlimited rows |

---

## Step 1 — Supabase Setup

1. Create a new Supabase project.
2. Go to **SQL Editor** and run:

```sql
create table submissions (
  id            text primary key,
  name          text not null,
  image_url     text not null,
  cloudinary_id text,
  ip_hash       text,
  created_at    timestamptz default now()
);
```

3. Copy your **Project URL** and **anon public key** from Project Settings → API.

---

## Step 2 — Cloudinary Setup

1. Create a free Cloudinary account.
2. From the dashboard, copy your **Cloud Name**, **API Key**, and **API Secret**.
3. No extra configuration needed — the app creates a `supernaturals` folder automatically.

---

## Step 3 — Deploy the Backend on Render

### 3a. Create a new Web Service

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

### 3b. Set environment variables on Render

In the Render dashboard → Environment, add:

```
GEMINI_API_KEY         = <your key>
GEMINI_MODEL           =                        (leave blank)
CLOUDINARY_CLOUD_NAME  = <your cloud name>
CLOUDINARY_API_KEY     = <your cloudinary key>
CLOUDINARY_API_SECRET  = <your cloudinary secret>
SUPABASE_URL           = <your supabase project URL>
SUPABASE_KEY           = <your supabase anon key>
ADMIN_PASSWORD         = <choose a strong password>
CORS_ORIGINS           = https://your-app.vercel.app
```

> ⚠️ Set `CORS_ORIGINS` to your **exact Vercel URL** once you have it (Step 4 below). Until then you can use `*`.

### 3c. Note your backend URL

After deploy completes, Render gives you a URL like:
```
https://i-will-be-there-api.onrender.com
```
Copy it — you need it for the frontend.

### 3d. Verify the backend is live

```bash
curl https://i-will-be-there-api.onrender.com/health
```

Expected response:
```json
{"status": "ok", "gemini_key_set": true, ...}
```

> 💤 **Note:** Free Render instances spin down after 15 minutes of inactivity. The first request after idle takes ~30 seconds. Consider upgrading to Starter ($7/month) for production to avoid cold starts.

---

## Step 4 — Deploy the Frontend on Vercel

### 4a. Build configuration

1. Go to [vercel.com](https://vercel.com) → New Project → import your repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite** (Vercel detects this automatically).
4. Build Command: `npm run build`
5. Output Directory: `dist`

### 4b. Set environment variables on Vercel

In the Vercel dashboard → Settings → Environment Variables, add:

```
VITE_API_URL = https://i-will-be-there-api.onrender.com
```

Replace the URL with your actual Render backend URL.

### 4c. Deploy

Click **Deploy**. Vercel builds and publishes to a URL like:
```
https://i-will-be-there.vercel.app
```

### 4d. Update CORS on Render

Go back to Render → Environment → update `CORS_ORIGINS` to:
```
https://i-will-be-there.vercel.app
```
Render will redeploy automatically.

---

## Step 5 — Custom Domain (Optional)

### Vercel
1. Vercel dashboard → Domains → Add Domain.
2. Add a CNAME record at your DNS provider pointing to `cname.vercel-dns.com`.
3. Vercel provisions SSL automatically.

### Render
1. Render dashboard → Settings → Custom Domains → Add.
2. Add a CNAME at your DNS provider.
3. Update `CORS_ORIGINS` on Render to include the custom domain.

---

## Step 6 — Verify End-to-End

1. Open your Vercel URL.
2. Upload a test photo, select a scene, tap Generate.
3. Confirm the image is generated and appears in:
   - The result screen
   - Your Cloudinary media library (`supernaturals/` folder)
   - Your Supabase `submissions` table
4. Download the image and check the watermark appears in the top-right corner.
5. Visit `/admin` and log in with your `ADMIN_PASSWORD`.

---

## Scaling for a Large Event

| Concern | Solution |
|---|---|
| Backend cold starts | Upgrade Render to Starter ($7/month) — no spin-down |
| Concurrent users | Render auto-scales; Gemini handles requests sequentially per instance. For high concurrency, add a second Render instance or use a task queue |
| Rate limiting | Currently in-memory (resets on restart). For multi-instance deployments, swap `_rate_store` in `main.py` for a Redis-backed store |
| Image storage bandwidth | Cloudinary free tier allows 25 GB/month. Monitor usage in the Cloudinary dashboard; upgrade if needed |
| Database | Supabase free tier is more than sufficient for thousands of submissions |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `gemini_key_set: false` on `/health` | API key missing or wrong | Check `GEMINI_API_KEY` on Render |
| `BILLING_REQUIRED` error | Gemini free tier has no image quota | Enable billing at aistudio.google.com/billing |
| CORS error in browser | `CORS_ORIGINS` doesn't match frontend URL | Update the env var on Render and redeploy |
| Images not saving | Cloudinary credentials wrong | Check all three Cloudinary vars |
| Admin login fails | Wrong password | Check `ADMIN_PASSWORD` on Render |
| Cold start timeout | Free Render tier | Upgrade to Starter or warm the service with a cron ping |
