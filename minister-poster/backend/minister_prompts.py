"""
Announcement-poster prompts: one per style, in two groups.

How a style works
-----------------
  prompt_builder.build_prompt() sends:  IDENTITY_PREFIX + <the style prompt> + size + no-text
  poster_builder then draws the name, title, dates and the CONFIRMED stamp on top.

Because that overlay lands in the bottom third, every style prompt must say the
lower third should fade to deep shadow, and the upper third should stay calm.
The two examples below are neutral on purpose. Replace them with prompts that fit
your event, keeping this structure:

  1. Genre + shot type + subject  2. Pose and expression  3. Wardrobe
  4. The one hero visual element  5. Lighting recipe  6. Background
  7. Where the text overlay goes  8. Named colour grade + scale word

To add a style: write a prompt here, register it below, add it to
frontend/src/data/ministerStyles.js, and (optionally) add a video prompt in
backend/video_client.py.
"""

IDENTITY_PREFIX = (
    "Using the provided reference photo, generate the following portrait while keeping "
    "the person's face, skin tone, facial features, and overall identity exactly as they "
    "appear in the reference. Do not alter their face in any way.\n\n"
)

PROMPT_EXAMPLE_A = """A photorealistic cinematic full-body portrait of a confident speaker, styled as an
official announcement poster. They stand on a rooftop at golden hour, feet at shoulder
width, facing the camera directly with a calm, assured expression and the faintest
smile. They wear a sharply tailored dark suit with a crisp open-collar shirt.

Behind them the city skyline glows amber, softly out of focus. Warm backlight traces
the edge of their shoulders and hair.

The lighting is cinematic: a low golden key from behind-left, soft fill from the front,
subsurface scattering on skin, physically accurate fabric detail.

The lower third of the image graduates to deep shadow for text overlay. The upper third
is open sky for the event name.

Warm amber and deep navy colour grading. Confident, grounded, editorial scale."""

PROMPT_EXAMPLE_B = """A photorealistic cinematic mid-body portrait of a warm, expressive performer, styled as
an official announcement poster. They stand at a microphone on a dark stage, head
slightly raised, eyes bright, mid-smile, one hand resting on the stand. They wear
smart-casual stage clothing in deep colours.

Soft beams of coloured stage light cut through light haze behind them; a few warm
bokeh points glow in the dark auditorium.

The lighting is intimate and cinematic: a warm front key, a cool rim light, subsurface
scattering on skin, physically accurate reflections on the microphone.

The lower third of the image graduates to deep black for text overlay. The upper third
holds dark haze for the event name.

Deep teal and warm magenta colour grading. Warm, lively, intimate scale."""

# ─────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────

MINISTER_PROMPTS: dict[str, str] = {
    "example_a": PROMPT_EXAMPLE_A,
    "example_b": PROMPT_EXAMPLE_B,
}

GROUP_A_STYLES = ["example_a"]
GROUP_B_STYLES = ["example_b"]

# Per-style overlay config (stamp rotation, stamp color, text alignment)
STYLE_OVERLAY_CONFIG: dict[str, dict] = {
    "example_a": {"rotation": -6, "stamp_color": "gold",  "align": "left"},
    "example_b": {"rotation": +6, "stamp_color": "white", "align": "right"},
}


def has_style(style_id: str) -> bool:
    return style_id in MINISTER_PROMPTS


def get_category(style_id: str) -> str:
    if style_id in GROUP_A_STYLES:
        return "a"
    if style_id in GROUP_B_STYLES:
        return "b"
    raise ValueError(f"Unknown style: {style_id!r}")
