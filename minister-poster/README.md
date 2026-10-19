# Announcement poster generator ("minister confirmed")

The twin of the portrait app. Instead of putting every attendee into a scene, it makes one polished "CONFIRMED" announcement
poster, and a 5-second video, for each guest you sign. Upload the guest's photo, choose a style, type their name and title.

Built in a day for the 2026 conference, it ran at about 14 styles in two groups. It is shipped here as a blank template with two
example styles.

## How it works

1. `validator.py` checks the photo (one face, size, type).
2. `prompt_builder.py` sends `IDENTITY_PREFIX` + the style prompt + a size directive + no-text to Gemini (`gemini_client.py`).
   Every style prompt reserves the lower third for text and the upper third for the event name.
3. `poster_builder.py` draws the guest's name, title, the event dates and a rotated `confirmed.png` stamp on top (Pillow; fonts are
   Montserrat and Bebas Neue).
4. `video_client.py` turns the poster into a 5-second video with Google Veo, falling back to a Pillow + ffmpeg render
   (zoom, grade, vignette, flash reveal) when Veo is unavailable.
5. `storage.py` optionally uploads results to Cloudinary and logs submissions to Supabase. Both are optional; **leave them blank
   and the app simply returns results without saving anything**, which is how the 2026 run went.

## Make it yours

| What | Where |
|---|---|
| Event name, dates, hashtag, handle, group labels | `frontend/src/config/event.js` |
| Dates printed on the poster | `EVENT_DATES` in `backend/.env` |
| Your styles | `backend/minister_prompts.py` (prompts, overlay config), `frontend/src/data/ministerStyles.js` (cards), `backend/video_client.py` (video prompts) |
| The stamp | `backend/assets/confirmed.png` (transparent PNG, about 1200 × 420) |
| The watermark | `frontend/public/logo_stamp.png` |

Adding a style means adding the same id in three places: the prompt, the card, the video prompt (optional).

## Run it

```bash
cd minister-poster/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt     # video fallback also needs ffmpeg on your PATH
cp .env.example .env                # at minimum GEMINI_API_KEY
cd .. && bash start.sh              # backend :8001, frontend :5175
```

## Security note

The admin dashboard routes need `ADMIN_PASSWORD`. There is no default: while it is unset, the admin routes stay closed.
