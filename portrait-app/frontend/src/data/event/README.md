# Event page content

All copy for `/about-conference` and `/our-sponsors` lives here, not in the components. Every file ships with placeholder
content in the real schema: edit the values, keep the keys.

| File | What it holds |
|---|---|
| `conference.json` | Event facts, hero, About, Who We Are, the journey timeline, past guests, Plan Your Visit |
| `ministers.json` | Guest speakers, in carousel order (the file and the `ministers` names are historical; they mean "speakers") |
| `sponsors.json` | Sponsors for the `/about-conference` slide dialogs |
| `our-sponsors.json` | Sponsors for the dedicated `/our-sponsors` page |

## Adding photos and logos

Put optimised files (WebP/AVIF) in `portrait-app/frontend/public/images/event/` and set the matching `"image"` / `"logo"` /
`"heroImage"` / `"banner"` field to the public path, e.g. `"image": "/images/event/speakers/jane-doe.webp"`.
Until a path is set, a labelled placeholder frame is shown. Fields to fill:

- `conference.json`: `event.logos.primary.image`, `event.logos.secondary.image`, `hero.collage[]`, `about.photos[]`,
  `journey.photo`, `previous.photos[]`, `visit.venuePhoto`, `visit.qr` (swap `public/registration_qr.png`)
- `ministers.json`: `image` (4:5 portrait) on each speaker
- `sponsors.json`: `logo`, `heroImage`, and `images[].image` (3 per sponsor)
- `our-sponsors.json`: `logo`, `banner` per sponsor (landscape; the page crops banners to 2.2:1 on wide screens)

Resize before you commit: a 1800 px WebP banner is about 60 KB, a 2 MB original is not.

## Sponsor slide types (`sponsors.json`)

`cover`, `content` (any of `paragraphs`, `pairs`, `cards`, `chips`, with optional `chipsTitle`), `images`, `contact`.
Slides appear in the order listed.

## `/our-sponsors` blocks

Each sponsor has a logo, a banner, an `about` paragraph, optional `blocks` (`pairs`, `chips`, `cards`, `text`) and an optional
`find` card (locations, note, contactPerson, phones, emails, social). Anything you leave out is simply not shown, so missing
details need no placeholder.

## Deep links

`#journey`, `#ministers`, `#sponsors` scroll to a slide. `#ministers/<slug>` and `#sponsors/<slug>/<n>` open the carousel on that
speaker or slide.

## Styling

Design tokens (colours, fonts, spacing) are CSS variables at the top of `src/pages/about-conference/event.css`. The brand mark
is `components/Ornament.jsx`.
