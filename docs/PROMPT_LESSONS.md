# Prompt lessons from a real event

What went wrong with image generation during the 2026 campaign, and the directive that fixed each problem. The fixes
are in [`prompt_builder.py`](../portrait-app/backend/prompt_builder.py) (generic) and, for the original wording, at git tag
`event-2026-final`. Read this before you write your own scenes.

## 1. Likeness first, and last

Say it twice: an identity primer **before** the scene and an identity lock **after** everything else, including the user's
free-text request. The wardrobe swap is what pulls the model away from the reference face, so the final instruction
should be the one you most need obeyed. The lock lists specifics (jawline, eye spacing, hairline, marks) and forbids
"beautifying" or drifting toward a generic model.

## 2. The photo supplies a face, not clothes

Street clothes from uploads kept dragging portraits out of their scenes. Each scene now names its own wardrobe, and a
directive says the clothes in the photo are discarded. Keep scene wardrobe modern and clean unless the scene needs costume;
people stop looking like themselves in heavy costume.

## 3. Bound the user's "twist" instead of refusing it

Users want to add things ("wearing an agbada", "my wife beside me"). A wrapper lets them decorate the scene but not replace
it, and carries a per-scene **wardrobe rule** ("white or off-white, any garment type; dark clothing is not"). A request that
breaks the rule is not refused and does not fall back to the default: it is rendered adapted to the rule (a white agbada).
The scene's setting, effects, lighting and colour grade are never the twist's to change.

## 4. Models ignore soft wording, so escalate it

- **Shirts tucked in** despite "left untucked" in the scene text. Fix: a separate, emphatic *hard requirement* directive
  (outside the trousers, hem covering the waistline, no belt visible) applied only to the scenes with a loose shirt.
- **Armour became a sleek sci-fi bodysuit** after a "modern, present-day tailoring" directive was added. Fix: a scene-scoped
  directive describing exactly the ceremonial look wanted *and* a list of what to avoid (gowns, skin-tight dark leggings,
  glossy plastic plate). Lesson: a generic rule can fight a specific scene, so give scenes an override.
- **Capes on men.** A tester spotted a floating cape/cloak/duster. Two causes: the scene text itself (a "storm coat", a
  "trailing overlayer") and the model adding one anyway. Fix both: remove the cause from the scenes *and* add a guard
  directive for non-female subjects. Scope it carefully so it does not forbid effects the scene needs.
- **Transparent gowns.** Backlight and god rays made fabric look sheer. Fix: an explicit *fabric opacity* clause, no exceptions,
  saying light must not pass through the garment.
- **Wing colour requests.** People asked for gold or black wings. A signature-element lock, placed last, held the brand
  element constant whatever the twist said.

## 5. Order matters

Final order: identity primer, scene, size, wardrobe directive, scene fix, subject directives, user twist, identity lock,
signature lock, no-text. Later text wins ties, so put the constraints you cannot lose at the end.

## 6. Orientation is set by the input

Gemini mirrors the reference image's aspect ratio. Centre-cropping the upload to 2:3 (1080 × 1620) before sending was the
strongest portrait-orientation signal, stronger than saying so in the prompt.

## 7. Money and models

- There is **no free image tier**. Every image costs money, so every generation needs a cap.
- Keep a **single model** in the chain. A silent fallback to a pricier model blows the budget; each fallback also multiplies
  requests and quota burn.
- Models retire mid-campaign (twice in 2026). Put the model name in an env var and keep a `/debug` endpoint that lists what
  your key can reach.
- Fail closed: when the rate-limit store is unreachable, fall back to a per-process in-memory store instead of letting everyone
  through. The first version failed open and the daily limit silently stopped applying.

## 8. Cheap operational wins

- A concurrency regulator (3 at a time, queue of 12) turned bursts into short waits instead of rate-limit errors.
- A scheduled `/health` ping kept the free Render instance warm during the active window.
- Apply the watermark client-side, so the preview is clean and the server never stores the image.
- Mobile in-app browsers (Instagram, WhatsApp) break `createImageBitmap` and `OffscreenCanvas`; plain `<img>` + `<canvas>` works.
