# Adapting the template to your event

A checklist, in the order that gets you to a working demo fastest. Everything is meant to be run locally first
(see [PORTRAIT_APP.md](PORTRAIT_APP.md) and [minister-poster/README.md](../minister-poster/README.md)).

## 0. Decide what you need

| If you want… | Use |
|---|---|
| People to make a shareable AI portrait of themselves | `portrait-app/` |
| Announcement posters/videos for guests you sign | `minister-poster/` |
| An event landing page and a sponsors page | `portrait-app/frontend` routes `/about-conference`, `/our-sponsors` |
| Door check-in and an attendance dashboard | `portrait-app` routes `/attend_event/*` + `backend/apps_script/` |

They are independent: delete what you do not need.

## 1. Branding (10 minutes)

| File | Change |
|---|---|
| `portrait-app/frontend/src/config/event.js` | Name, headline, tagline, hashtag, handle, register/social links, watermark path |
| `minister-poster/frontend/src/config/event.js` | Name, dates, hashtag, handle, what you call your guests, group labels |
| `portrait-app/frontend/public/logo.png`, `logo_stamp.png` | Favicon/brand mark and the download watermark (transparent PNG, light on dark works best) |
| `minister-poster/frontend/public/logo_stamp.png`, `minister-poster/backend/assets/confirmed.png` | Watermark and the poster stamp |
| `portrait-app/frontend/index.html`, `minister-poster/frontend/index.html` | Page title and description |
| `portrait-app/frontend/tailwind.config.js` | Colour palette (`divine`, `cosmic`) |

## 2. Your scenes (the creative work)

1. Read [PROMPT_LESSONS.md](PROMPT_LESSONS.md) first. It will save you days.
2. Write each scene in `portrait-app/backend/scene_prompts.py` using the 11-layer formula in the file's docstring.
3. Add a wardrobe rule per scene in `SCENE_WARDROBE_RULES`.
4. Add a card per scene in `portrait-app/frontend/src/data/scenes.js` (same `id`, a `week` number).
5. Set `LAUNCH_DATE` (and optionally `WEEK_LENGTH_DAYS`) in `portrait-app/backend/.env`.
6. When a scene misbehaves, add a fix in `SCENE_EXTRA_DIRECTIVES` rather than loosening the generic directives.
7. Want men and women dressed differently? Fill `SUBJECT_DIRECTIVES` in `prompt_builder.py`.
8. Have a brand element that must never change? Set `_SIGNATURE_LOCK` in `prompt_builder.py`.

Poster styles work the same way in `minister-poster/backend/minister_prompts.py` and `frontend/src/data/ministerStyles.js`.

## 3. Budget (do this before you go public)

Every image costs money. In `portrait-app/backend/.env` set `GLOBAL_DAILY_IMAGE_CAP`, optionally `DAILY_IMAGE_CAPS` per weekday and
`CLOSED_WEEKDAYS`, plus `APP_TIMEZONE`. Per-visitor limits are `DAILY_LIMIT` in `storage.py`. Check your model's price and make sure it
has not been retired (`GET /debug/gemini` lists what your key can reach).

## 4. Event pages

Edit the JSON in `portrait-app/frontend/src/data/event/` (see its README). Add images under `portrait-app/frontend/public/images/event/`
and point the JSON at them. The page runs with placeholders, so you can fill it in gradually. To drop a section, remove its slide from
`AboutConference.jsx`.

## 5. Attendance (optional)

Needs a registration Google Sheet (a Google Form's response sheet works). Follow the "Event-day attendance" section of
[DEPLOY.md](DEPLOY.md). Then in `portrait-app/backend/.env`:

- `HOME_ORG_NAME` and `HOME_ORG_PATTERN`: the group you want counted separately, and a forgiving regex for how people type it.
- The sheet needs columns the code recognises: name, phone, gender, age group, church (or organisation), transport, area, source.
  Header matching is in `_canon()` in `attendance.py` and the same function in `Attendance.gs`.
- The three event days are `friday/saturday/sunday` in `attendance.py` (`DAYS`) and `frontend/src/pages/attend-event/api.js`. Change both together.
- Set `VITE_EVENT_TIMEZONE` for the frontend so "today" is correct.

## 6. Deploy

[DEPLOY.md](DEPLOY.md). Vercel root: `portrait-app/frontend`. Render root: `portrait-app/backend`. The Vercel config already rewrites
unknown paths to `index.html`, which the page routes need.

## 7. Before you share the link

- [ ] No real keys committed; `.env` files are git-ignored
- [ ] A daily cap is set and the model name is current
- [ ] You generated a portrait from a real phone photo, on a phone
- [ ] `/health` shows Supabase connected (otherwise limits only last until the process restarts)
- [ ] If you use the vault or admin dashboard, you set your own `VAULT_KEY_HASH` / `ADMIN_PASSWORD`

## Known rough edges

- Names inherited from the original build: the `ministers` / `previous` keys in the event JSON mean "speakers" / "past guests";
  the poster app's database columns still say `minister_*`.
- The attendance feature assumes a three-day, Friday to Sunday event.
- `scene_prompts.py` ships with two example scenes only. Prompts that worked for the 2026 theme are at tag `event-2026-final`.
