"""
Prompt construction.

Single API: build_prompt(scene_id, custom_prompt=None, gender=None) -> str

The scene prompts live in scene_prompts.py. This module wraps each one in the
directives that made generations reliable during the 2026 event:

  1. Identity primer FIRST: likeness is the top priority.
  2. The scene prompt.
  3. Output size directive (portrait 1080 × 1620).
  4. Wardrobe directive: the reference photo supplies identity, NOT clothing, so
     the clothes in the upload are discarded and the scene's wardrobe is used.
  5. Optional per-scene fix (SCENE_EXTRA_DIRECTIVES) and per-subject directives
     (SUBJECT_DIRECTIVES), both empty by default.
  6. Optional user "twist", wrapped so it decorates the scene but cannot replace
     it, and carrying the scene's wardrobe rule (SCENE_WARDROBE_RULES).
  7. Identity lock LAST (after any custom text) so it has the final word. Likeness
     is stated twice, first and last, because the wardrobe swap is what most
     often pulls the model away from the reference face.
  8. Optional signature-element lock, then the no-text directive, once.

The directives are the product of many rounds of testing. docs/PROMPT_LESSONS.md
explains what each one fixed. Reword them for your event, but keep the order.
"""

from scene_prompts import SCENE_PROMPTS, get_wardrobe_rule, get_extra_directive


_SIZE_DIRECTIVE = (
    "Output format: portrait orientation, 2:3 aspect ratio, "
    "1080 × 1620 pixels. Compose the full-body or near-full-body figure "
    "to fill this portrait frame naturally."
)

_WARDROBE_DIRECTIVE = (
    "Wardrobe: the reference photo is the source of the person's identity, NOT of their "
    "clothing. Whatever they are wearing in the photo — casual, formal, patterned, branded, "
    "or otherwise — is discarded entirely and replaced by the scene wardrobe described above, "
    "which is styled to belong in this exact scene. Render that wardrobe as real, "
    "well-fitted, present-day clothing on this person: natural drape and folds, realistic "
    "fabric weave, seams and stitching, cloth reacting to the scene's wind, water, heat and "
    "light. Cut and fit the outfit to the subject's own gender, body build and proportions "
    "as seen in the reference photo. Clean and dignified: no theatrical costume, nothing "
    "ill-fitting, nothing that looks pasted on. Unless the user's customization below asks "
    "for a specific garment, in which case that garment is what to render."
)

# Directives that apply to one kind of subject. Keys are the values the frontend
# sends as `gender` ("male" / "female"). Empty by default.
#
# In 2026 these held: for women, a modest full-length gown directive (with a hard
# "fully opaque fabric" clause, because backlight made gowns look sheer) plus a
# light-makeup directive; for men, a "no cape, cloak or duster" guard, because
# the model kept adding a floating cape. Write yours here, e.g.:
#   "female": ["SUBJECT IS FEMALE — WARDROBE (hard requirement): ..."],
SUBJECT_DIRECTIVES: dict[str, list[str]] = {
    "male": [],
    "female": [],
}

_CUSTOM_PROMPT_WRAPPER = (
    "User's personal customization — apply it faithfully, but inside the scene, never "
    "instead of it. It may cover clothing, accessories, hair, posture, motion, extra "
    "objects, extra people or creatures, or other details, and whatever it describes must "
    "appear clearly in the output. Two things bound it. "
    "(a) The scene itself is fixed: the setting, the action, the visual effects, the "
    "lighting recipe, the composition and the colour grade described above all stay "
    "exactly as written. The customization decorates the scene; it does not relocate, "
    "restage or replace it. "
    "(b) If the customization asks for different clothing, honour the garment they name — its "
    "type, cut and cultural style — but keep it within this scene's wardrobe rule: "
    "{rule}. Where a clothing request would break that rule, do not refuse it and do not fall "
    "back to the default outfit: render the garment they asked for, adapted to satisfy the "
    "rule. "
    "The user's customization follows: {custom}"
)

_IDENTITY_PRIMER = (
    "This is a likeness-critical portrait. The single most important requirement is that the "
    "face in the output is the exact face in the attached reference photo — same person, "
    "unmistakably. Treat the reference as a photograph of the subject and re-photograph that "
    "same face inside the scene described below."
)

_IDENTITY_LOCK = (
    "Non-negotiable constraint, above every other instruction including the user's "
    "customization: FACIAL LIKENESS. The person in the output is the person in the reference "
    "photo. Reproduce their facial geometry exactly — the shape and width of the face, the "
    "jawline and chin, cheekbones, brow, the exact eye shape, spacing and colour, the nose "
    "shape and width, the lips, the ears, the hairline and hair texture, facial hair, and any "
    "distinguishing marks such as moles, freckles, scars, dimples or glasses. Keep their skin "
    "tone and complexion exactly as photographed. Keep their apparent age, weight and body "
    "build. Do NOT beautify, slim, smooth, lighten, darken, youthen or otherwise idealise the "
    "face, and do not blend it toward a generic model or a different ethnicity. Someone who "
    "knows this person must recognise them instantly at a glance. Only the clothing, the "
    "setting, the pose and the visual effects change. The one exception: if the user's "
    "customization explicitly asks for a hair or facial-hair change, apply that single change "
    "and keep every other facial feature identical."
)

# A "signature element" every image must keep whatever the user asks for. In 2026
# it was "the wings are always pure white" (users kept asking for gold or black
# wings). Leave empty if your event has no such element.
_SIGNATURE_LOCK = ""

_NO_TEXT_DIRECTIVE = "No text, no watermarks, no labels of any kind."


def build_prompt(
    scene_id: str,
    custom_prompt: str | None = None,
    gender: str | None = None,
) -> str:
    """
    Compose the final prompt for Gemini.

    Args:
        scene_id: One of the keys in SCENE_PROMPTS.
        custom_prompt: Optional user text. It varies the wardrobe within the
                       scene's wardrobe rule; the scene itself, the VFX,
                       composition and the identity lock are kept.
        gender: Optional "male"/"female", used to pick SUBJECT_DIRECTIVES.
                Anything else (None, unknown) runs the normal flow.

    Raises:
        KeyError: If scene_id is not in SCENE_PROMPTS.
    """
    if scene_id not in SCENE_PROMPTS:
        raise KeyError(f"Unknown scene_id: {scene_id!r}")

    parts: list[str] = [
        _IDENTITY_PRIMER,
        SCENE_PROMPTS[scene_id].strip(),
        _SIZE_DIRECTIVE,
        _WARDROBE_DIRECTIVE,
    ]

    extra = get_extra_directive(scene_id)
    if extra:
        parts.append(extra)

    parts.extend(SUBJECT_DIRECTIVES.get((gender or "").strip().lower(), []))

    if custom_prompt:
        custom = custom_prompt.strip()
        if custom:
            parts.append(
                _CUSTOM_PROMPT_WRAPPER.format(
                    rule=get_wardrobe_rule(scene_id),
                    custom=custom,
                )
            )

    parts.append(_IDENTITY_LOCK)
    if _SIGNATURE_LOCK:
        parts.append(_SIGNATURE_LOCK)
    parts.append(_NO_TEXT_DIRECTIVE)

    return "\n\n".join(parts)
