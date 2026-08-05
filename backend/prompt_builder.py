"""
Prompt construction for The SuperNaturals 2026.

Single API: build_prompt(scene_id, custom_prompt=None) -> str

The 10 full photorealistic prompts live in scene_prompts.py (the source of
truth). This module assembles the final string sent to Gemini by:
  1. Opening with the identity primer (facial likeness is the top priority)
     and looking up the scene by ID.
  2. Appending the output size directive (portrait 1080 × 1620 px).
  3. Appending the wardrobe directive — each scene now dresses the subject in
     its own styling, so the reference photo is used for identity only and the
     clothes in it are explicitly discarded.
  4. Optionally appending the user's custom-prompt block, carrying the scene's
     wardrobe rule from SCENE_WARDROBE_RULES. A clothing request changes the
     garment (a white gown instead of a white shirt) but has to satisfy that
     rule, so the outfit still belongs to the scene; the scene's setting,
     VFX, lighting and composition are not the customization's to change.
  5. Always appending the facial-likeness and wing-color locks, last in the
     prompt (after any custom text) so they have the final word — the face
     stays the person's own and the wings stay pure white no matter what a
     custom prompt asks for. Likeness is stated twice, first and last, because
     the wardrobe swap is the thing most likely to pull the model away from
     the reference face.
  6. Always appending the no-text directive on its own line, once.
"""

from scene_prompts import SCENE_PROMPTS, get_wardrobe_rule


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
    "well-fitted, present-day clothing on this person: modern tailoring, natural drape and "
    "folds, realistic fabric weave, seams and stitching, cloth reacting to the scene's wind, "
    "water, heat and light. Cut and fit the outfit to the subject's own gender, body build and "
    "proportions as seen in the reference photo — the same styling, adapted so it reads as "
    "clothing that was made for them. Clean, modern and dignified: no theatrical costume, "
    "nothing ill-fitting, nothing that looks pasted on. Default to contemporary tailoring "
    "rather than ancient robes — unless the scene calls for ceremonial dress, or the user's "
    "customization below asks for a specific garment, in which case that garment is what to "
    "render."
)

_CUSTOM_PROMPT_WRAPPER = (
    "User's personal customization — apply it faithfully, but inside the scene, never "
    "instead of it. It may cover clothing, accessories, hair, posture, motion, extra "
    "objects, extra people or creatures, or other details, and whatever it describes must "
    "appear clearly in the output. Two things bound it. "
    "(a) The scene itself is fixed: the setting, the action, the supernatural elements and "
    "VFX, the lighting recipe, the composition and the colour grade described above all stay "
    "exactly as written. The customization decorates the scene; it does not relocate, "
    "restage or replace it. "
    "(b) If the customization asks for different clothing, honour the garment they name — its "
    "type, cut and cultural style, such as a gown, dress, agbada, kaftan, suit or uniform "
    "instead of the garment described above — but keep it within this scene's wardrobe rule: "
    "{rule}. Where a clothing request would break that rule, do not refuse it and do not fall "
    "back to the default outfit: render the garment they asked for, adapted to satisfy the "
    "rule — a white version of it, an armored version of it, a pristine version of it, as the "
    "rule requires. "
    "Wing colour is the one thing no request can change; wings stay pure white regardless. "
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
    "setting, the pose and the supernatural elements change. The one exception: if the user's "
    "customization explicitly asks for a hair or facial-hair change, apply that single change "
    "and keep every other facial feature identical."
)

_WING_COLOR_LOCK = (
    "Non-negotiable constraint, takes priority over every instruction above: the "
    "wings are always pure white — the color of purity. Do not tint, recolor, or "
    "reinterpret them as any other color (gold, black, fire, rainbow, or otherwise), "
    "even if the user's customization above explicitly requests a different wing color. "
    "Ignore any such request and render the wings pure white regardless."
)

_NO_TEXT_DIRECTIVE = "No text, no watermarks, no labels of any kind."


def build_prompt(scene_id: str, custom_prompt: str | None = None) -> str:
    """
    Compose the final prompt for Gemini.

    Args:
        scene_id: One of the 10 keys in SCENE_PROMPTS.
        custom_prompt: Optional user text. It varies the wardrobe within the
                       scene's wardrobe rule (a white gown instead of a white
                       shirt, say) — the scene itself, the VFX, composition
                       and the identity/wing locks are kept.

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
    parts.append(_WING_COLOR_LOCK)
    parts.append(_NO_TEXT_DIRECTIVE)

    return "\n\n".join(parts)
