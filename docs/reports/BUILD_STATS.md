# Build stats and at-a-glance summary

Everything measurable about the 2026 campaign in one place. Detail lives in the other reports:
[attendance](ATTENDANCE_REPORT.md) · [generation](GENERATION_REPORT.md).

## The campaign at a glance

| | |
|---|---:|
| People on the registration sheet | 774 |
| …pre-registered through the form | 434 |
| …walk-ins added at the door | 340 |
| Checked in on at least one day | 558 |
| First-timers among attendees | 325 |
| Friday / Saturday / Sunday check-ins | 431 / 312 / 3 (Sunday under-recorded) |
| Portrait generations recorded (lower bound) | 136 |
| Distinct visitors who generated | 97 |
| Portrait scenes shipped | 10 |
| Announcement poster styles built (minister app) | 14 (7 + 7) |
| Standalone pages built | 5 (conference, sponsors, check-in, first-timers, chart) |
| Commits on the portrait app | 33 |
| Calendar span of the portrait build | 23 Jul – 12 Oct 2026 (81 days) |

## Timeline (portrait app, from git history)

| Date | What shipped |
|---|---|
| 23 Jul | First commit; test services and first Render + Vercel deployments |
| 28–29 Jul | Registration barcode, keep-warm workflow, white-wings fix |
| 5–6 Aug | Scene and messaging updates; download bug; per-scene wardrobes; gender-aware prompts; "tucked-in" fixes |
| 8 Aug | Launch day (week 1 scene live); cost management; framing clean-up; model update |
| 12–15 Aug | Owner "vault" path; transparency fix |
| 22 Aug | Prompt-builder rework, armor and standing-pose fixes, outfit fixes |
| 2 Oct | `/about-conference` and `/our-sponsors` pages; male no-cape fix; Vercel SPA rewrite |
| 12 Oct | `/attend_event` check-in, first-timers list and attendance chart; walk-ins; faster reads |

Commits per month: July 10, August 13, October 10 (September had none; generation ran on the deployed build).
The full original build is preserved at git tag `event-2026-final`, and the original poster app at `event-2026-minister-poster`.

## Size of the code at the event tag

| Language | Files | Lines |
|---|---:|---:|
| Python (backend) | 10 | 2,776 |
| JSX (React) | 27 | 3,319 |
| JavaScript | 6 | 407 |
| CSS | 3 | 627 |
| Apps Script | 1 | 167 |
| JSON content and data | 6 | 747 |
| Markdown | 3 | 471 |
| Workflow YAML | 1 | 33 |

79 tracked files in total. The twin app, [`minister-poster/`](../../minister-poster/), was about 2,900 lines
(1,885 Python, 834 JSX, 173 JS) across 20 source files. It was never under version control, so it has no commit history; its original source is archived at tag `event-2026-minister-poster`.

## What was built

**Portrait app** (`portrait-app/`): upload a selfie, pick the week's scene, optionally add a "twist", get a 1080 × 1620 portrait
with the event logo watermarked on download. FastAPI + Gemini image generation; React + Vite + Tailwind;
Supabase for per-IP limits and a service-wide daily cap; Render and Vercel for hosting.

**Announcement poster app** (`minister-poster/`): upload a guest's photo, pick one of 14 styles in two groups, get a poster
with name, title, dates and a CONFIRMED stamp drawn on top, plus a 5-second announcement video (Veo, with a Pillow + ffmpeg fallback).

**Event pages**: a scroll-snap conference page, a sponsors page, and a door-staff attendance system that writes check-ins to
a Google Sheet through an Apps Script web app.

## Cost and budget controls

Image generation has no free tier, so the campaign ran on a fixed budget: per-visitor limits, per-weekday caps, closed days,
a concurrency limit, and a single image model chosen on price. Two model retirements (15 Jan and 2 Oct 2026) had to be handled
along the way. The lessons are in [PROMPT_LESSONS](../PROMPT_LESSONS.md).
