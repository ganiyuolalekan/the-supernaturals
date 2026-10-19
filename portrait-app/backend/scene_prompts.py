"""
Scene prompts: the creative heart of the app. Replace the two examples below.

Each scene is one long, photorealistic prompt. The structure that worked for the
2026 event (ten scenes, one live per week) is an 11-layer formula:

  1.  Genre tag                      (e.g. "photorealistic cinematic realism")
  2.  Shot type + camera angle       (full-body, low angle, eye-level wide...)
  3.  Subject pose + expression
  4.  Attire: styled to THIS scene, not the clothes in the upload
  5.  The scene's hero visual effect
  6.  Lighting recipe                (key, rim, volumetric, practicals)
  7.  Realism anchors                (subsurface scattering, fabric weave, reflections)
  8.  Background depth + composition
  9.  Named colour grade
  10. A scale word                   ("epic", "intimate", "serene")
  11. No-text directive              (added by prompt_builder, not written here)

Why attire is written into the scene: street clothes from the upload kept pulling
generated portraits out of their scene, so the photo supplies identity only and
each scene dresses the subject itself. See docs/PROMPT_LESSONS.md.

Adding a scene
--------------
  1. Add its prompt to SCENE_PROMPTS (the key is the scene id).
  2. Add a wardrobe rule to SCENE_WARDROBE_RULES. It bounds what a user's
     free-text "twist" may do to the clothes.
  3. Add its card to frontend/src/data/scenes.js (same id).
  4. Optionally add scene-specific fixes to SCENE_EXTRA_DIRECTIVES.

Scheduling
----------
  One scene is "live" per week, in the order of SCENE_PROMPTS, starting on
  LAUNCH_DATE (env). WEEK_LENGTH_DAYS (env, default 7) changes how long each
  scene stays live. To open every scene at once, edit get_active_scene_id().
"""

import os
from datetime import date, timedelta

# Week 1 starts here (YYYY-MM-DD). Set LAUNCH_DATE in backend/.env.
LAUNCH_DATE = date.fromisoformat(os.getenv("LAUNCH_DATE", "2027-01-01"))
WEEK_LENGTH_DAYS = int(os.getenv("WEEK_LENGTH_DAYS", "7"))

SCENE_PROMPTS: dict[str, str] = {
    "example-scene-one": """A photorealistic cinematic full-body low-angle shot of a figure standing on a wet
city rooftop at dusk, looking directly into the camera with calm, fearless confidence.
They are dressed in crisp, modern all-white: a clean long-sleeved shirt, fully buttoned
and left untucked, loose free-cut white trousers, white sneakers; contemporary tailoring
with visible fabric weave and stitching. Thin beams of warm light break through low
clouds and catch the rain on the rooftop, which reflects the skyline in shallow puddles.
The lighting is cinematic: a strong warm backlight, cool rim lighting tracing the
silhouette, realistic shadows, subsurface scattering on skin, physically accurate
reflections. In the blurry background, a dense city skyline with lit windows. Cool teal
shadows with warm amber highlights. Epic, cinematic scale.""",

    "example-scene-two": """A photorealistic cinematic full-body eye-level shot of a figure walking through a
sunlit wheat field toward the camera, relaxed and smiling, one hand brushing the tops of
the stalks. They wear a simple stone-coloured linen shirt, left untucked, and dark
trousers; natural drape and folds, a gentle breeze moving the fabric. Low golden-hour sun
flares behind them and lights each seed head. The lighting is soft and warm: a golden
backlight, bounced fill from the field, subsurface scattering on skin, physically
accurate reflections. In the blurry background, rolling hills under a pale sky. Warm
gold and soft green colour grading. Serene, open scale.""",
}


# The wardrobe boundary each scene has to stay inside when a user's custom
# prompt asks for different clothing. The garment itself is theirs to choose, but
# it has to satisfy the rule, so the outfit still belongs to the scene.
# prompt_builder injects the matching rule into the custom-prompt block.
SCENE_WARDROBE_RULES: dict[str, str] = {
    "example-scene-one": (
        "the outfit must be white or off-white and clean-lined. Any garment type is fine "
        "as long as it is white; dark or heavily printed clothing is not"
    ),
    "example-scene-two": (
        "the outfit must stay in natural, earthy tones (stone, cream, tan, brown) and "
        "lightweight fabric. Any garment type is fine in those tones; neon, formal or "
        "heavy clothing is not"
    ),
}

# Scene-specific fixes, appended after the generic wardrobe directive. Empty by
# default. Each one below is an example of a real problem we hit in 2026:
#   "shirt tucked in despite the prompt saying untucked"  -> an emphatic fit directive
#   "armour came out as a sleek bodysuit"                 -> a directive naming what to avoid
SCENE_EXTRA_DIRECTIVES: dict[str, str] = {
    # "example-scene-one": (
    #     "SHIRT FIT — hard requirement: the shirt is worn OUTSIDE the trousers, untucked, "
    #     "its hem fully covering the waistline. Do NOT tuck it in."
    # ),
}


def get_wardrobe_rule(scene_id: str) -> str:
    """The scene's wardrobe boundary, used to constrain custom prompts."""
    return SCENE_WARDROBE_RULES.get(scene_id, "the outfit must suit this scene")


def get_extra_directive(scene_id: str) -> str:
    return SCENE_EXTRA_DIRECTIVES.get(scene_id, "")


def get_scene_ids() -> list[str]:
    """Returns all scene IDs, in schedule order."""
    return list(SCENE_PROMPTS.keys())


def has_scene(scene_id: str) -> bool:
    return scene_id in SCENE_PROMPTS


def get_active_scene_id(today: date | None = None) -> str:
    """Returns the one scene scheduled for the current week.

    Before launch, week 1's scene is active (so the app is testable ahead of
    time). After the last scheduled week, the final scene stays active.
    """
    if today is None:
        today = date.today()
    scene_ids = get_scene_ids()
    if today < LAUNCH_DATE:
        return scene_ids[0]
    week_index = (today - LAUNCH_DATE).days // WEEK_LENGTH_DAYS
    week_index = min(week_index, len(scene_ids) - 1)
    return scene_ids[week_index]


def get_scene_schedule() -> list[dict]:
    """Returns every scene with its scheduled week number and active date range."""
    schedule = []
    for i, scene_id in enumerate(get_scene_ids()):
        starts = LAUNCH_DATE + timedelta(days=i * WEEK_LENGTH_DAYS)
        ends = starts + timedelta(days=WEEK_LENGTH_DAYS - 1)
        schedule.append({
            "scene_id": scene_id,
            "week": i + 1,
            "starts": starts.isoformat(),
            "ends": ends.isoformat(),
        })
    return schedule
