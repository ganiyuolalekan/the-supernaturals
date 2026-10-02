# /about-conference content

All copy for the IGC 2026 page lives here, not in the components.

| File | What it holds |
|---|---|
| `conference.json` | Event facts, hero, About, Who We Are, the five-step journey, Previous Ministers, Plan Your Visit |
| `ministers.json` | The 8 guest ministers, in carousel order |
| `sponsors.json` | The 5 sponsors and their slide sets |

## Adding photos and logos

Put optimised files (WebP/AVIF) in `frontend/public/images/igc/` and set the matching `"image"` / `"logo"` /
`"heroImage"` field to the public path, e.g. `"image": "/images/igc/ministers/pastor-o-jacob.webp"`.
Until a path is set, a labelled placeholder frame is shown. Fields to fill:

- `conference.json`: `event.logos.tig.image`, `event.logos.rccg.image`, `hero.collage[]`, `about.photos[]`,
  `journey.photo`, `previous.photos[]`, `visit.venuePhoto`, `visit.qr` (already set to `/registration_barcode.png`)
- `ministers.json`: `image` (4:5 portrait) on each minister
- `sponsors.json`: `logo`, `heroImage`, and `images[].image` (3 per sponsor)

## Still to fill in (open items from the brief)

- `event.registerUrl`: the Register buttons scroll to the QR panel until this is set.
- `event.social.whatsappUrl`, `youtubeUrl`, `facebookUrl`: shown as plain text until a link is set.
- Katonium: phone and email. Crimson and Connect: email. (`contact` slide, `pending` note.)

## Sponsor slide types

`cover`, `content` (any of `paragraphs`, `pairs`, `cards`, `chips`, with optional `chipsTitle`), `images`, `contact`.
Slides appear in the order listed, so a sponsor can have fewer or more than seven.

## Deep links

`#journey`, `#ministers`, `#sponsors` scroll to a slide. `#ministers/<slug>` and `#sponsors/<slug>/<n>`
open the carousel on that minister or slide.

## /our-sponsors

`our-sponsors.json` drives the dedicated sponsors page. Each sponsor has a logo, a banner photo, an `about`
paragraph, optional `blocks` (`pairs`, `chips`, `cards`, `text`) and an optional `find` card (locations, note,
contactPerson, phones, emails, social). Anything left out is simply not shown, so missing details need no placeholder.
Images are web-sized WebP copies in `frontend/public/images/sponsors/` (`<slug>-logo.webp`, `<slug>-banner.webp`);
the originals stay untouched in `/sponsors`.
