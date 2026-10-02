"""
Prompt construction for The SuperNaturals.

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

# Scenes whose wardrobe is a loose white/neutral shirt over trousers. These get an
# extra, emphatic fit directive because the model kept tucking the shirt in despite
# the "left untucked" wording inside the scene text. NOT applied to silencing-the-lion
# (a sharp tailored suit, where the shirt is meant to be tucked) or the armor scenes
# (no shirt to tuck).
_UNTUCKED_SHIRT_SCENES = frozenset({
    "walking-on-water",
    "commanding-the-storm",
    "breaking-every-chain",
    "walking-through-fire",
    "anointed-with-oil",
    "eagle-wings",
    "receiving-the-mantle",
})

_UNTUCKED_SHIRT_DIRECTIVE = (
    "SHIRT FIT — this is a hard requirement, override any default styling instinct: the shirt "
    "(or top) is worn OUTSIDE the trousers, hanging loose and UNTUCKED, its hem falling "
    "naturally below the waistline and fully covering it. Do NOT tuck the shirt into the "
    "trousers, do NOT tuck it behind a belt, and show no waistband, belt or trouser top at the "
    "front — the loose shirt hem hides them. Any long sleeves stay worn down to the wrist and "
    "unfolded (not rolled or pushed up), and the shirt is fully and properly buttoned. The "
    "trousers are loose and free-cut, never tight, slim or skinny."
)

# ── Ceremonial-armor scenes ──────────────────────────────────────────────────
# defeating-giants regressed after the Aug wardrobe directive: its "well-fitted,
# present-day, modern tailoring, contemporary rather than robes" language (plus the
# scene's old "fitted dark underlayer / contemporary athletic not robed" wording)
# turned the majestic white-and-gold ceremonial armor into a sleek modern plate suit
# worn over a skin-tight black bodysuit — a superhero/CG look the client rejected.
# This directive restores the earlier, preferred look: flowing white-and-gold
# ceremonial armor with a fabric tabard drape, regal and photoreal. The generic
# _WARDROBE_DIRECTIVE already permits "ceremonial dress", so this refines rather than
# fights it. Scoped to defeating-giants for now (this week); add other ceremonial
# scene ids here when rolling out.
_CEREMONIAL_ARMOR_SCENES = frozenset({
    "defeating-giants",
})

_CEREMONIAL_ARMOR_DIRECTIVE = (
    "WARDROBE — ceremonial armor (hard requirement, and this is exactly the 'ceremonial dress' "
    "the wardrobe note above allows, so it OVERRIDES any 'contemporary tailoring', 'present-day', "
    "'modern' or 'not robes' wording): dress him as a majestic heavenly warrior in a full suit of "
    "WHITE-AND-GOLD ceremonial ARMOR. He wears a fitted white breastplate/cuirass, shoulder "
    "pauldrons and forearm vambraces with ornate polished-gold filigree edging, and matching "
    "white-and-gold armored greaves that fully cover and armor the legs over plain padded white "
    "leggings. A single narrow gold-edged white tabard panel hangs from a gold waist belt down the "
    "FRONT only, between the legs, like a knight's surcoat — the armored legs stay clearly visible "
    "on either side of it. He is unmistakably a MAN clad in fitted ceremonial armor: regal, "
    "dignified and angelic. STRICTLY AVOID and never render: a full-length gown, dress, robe-dress, "
    "cassock, cloak-dress or wrap-around skirt; anything that reads as a woman's gown or a dress; a "
    "skin-tight black/dark full-body bodysuit, dark leggings or bare dark legs; a sleek modern "
    "'superhero' or sci-fi armored bodysuit; glossy plastic-look plate; and an exaggerated "
    "bodybuilder muscle silhouette. The tabard is a single front panel ONLY — it must NOT wrap "
    "around into a skirt or gown, and the legs must read as armored, not as fabric. Keep it "
    "strictly photographic and photorealistic — real metal and cloth, a real man photographed in "
    "natural light, never an illustrated, painted, cartoon or CG-render look."
)

# ── Male / default subjects ──────────────────────────────────────────────
# A tester noticed a floating cape/cloak/duster on a male generation even
# where the scene text didn't ask for one outright (commanding-the-storm's
# coat and eagle-wings' overlayer were the literal culprits, fixed in
# scene_prompts.py) — this is the belt-and-suspenders guard against Gemini
# adding one anyway. Applied whenever the subject is not female.
_MALE_NO_CAPE_DIRECTIVE = (
    "WARDROBE — no cape, cloak or duster (hard requirement): do not dress him in a separate "
    "flowing cape, cloak, hooded mantle, or long duster-style coat that hangs loose and open "
    "from the shoulders behind him. Any coat or outer layer described above is worn properly "
    "fitted through the body and shoulders, not billowing open like a cape, and must not read "
    "as a distinct garment floating or trailing behind or above him. Any sense of wind or "
    "motion belongs to the wings, his hair, and the hem or sleeves of his actual shirt or "
    "coat — never to an added cape-like layer. This is about his own clothing only: it does "
    "not apply to a separate falling or descending supernatural mantle, fire or light that a "
    "scene's own description calls for as a divine effect, and it does not apply to the "
    "ceremonial armor tabard in the armor scenes, which is a fixed single front panel, not a "
    "cape."
)

# ── Female subjects ────────────────────────────────────────────────────────
# When the subject is a woman, trousers read poorly, so the scene's shirt-and-
# trousers wardrobe is re-cut as a modest, free-flowing full-length gown in the
# same colour and role the scene calls for. This REPLACES the untucked-shirt
# directive above (there is no shirt to tuck). Armor scenes stay armor, worn
# over a flowing skirt. Kept deliberately modest — decent, not glamorous.
_FEMALE_WARDROBE_DIRECTIVE = (
    "SUBJECT IS FEMALE — WARDROBE (hard requirement, overrides the shirt-and-trousers styling "
    "described above): the person in the reference photo is a woman, so dress her for this scene "
    "in a modest, elegant, full-length GOWN — never in trousers. Keep the exact colour, fabric "
    "feel and role the scene's wardrobe calls for: a clean white gown where the scene is white, "
    "an ivory storm gown with a long layer the wind can catch where the scene is ivory, a sharp "
    "dark tailored gown where the scene is dark, a ceremonial white-and-gold gown where the "
    "scene is ceremonial; where the scene is battle armor, render it as elegant white-and-gold "
    "armor worn over a long, flowing skirt. The gown falls loose and free-flowing from the "
    "waistline down, its skirt reaching the ankles or floor and flaring softly so the fabric "
    "drapes over and conceals the shape of her body and hips — decent and dignified, NEVER "
    "tight, clinging, body-hugging, sheer, short, low-cut, off-shoulder or otherwise revealing. "
    "Modest high neckline, shoulders and chest covered, sleeves worn long to the wrist (only "
    "where the scene must show bare forearms, such as breaking chains, may the sleeves end near "
    "the elbow). FABRIC OPACITY — hard requirement, no exceptions: every part of the gown is "
    "made of fully opaque, solid, thick-woven cloth. It is NEVER sheer, see-through, "
    "transparent, translucent, gauzy, mesh, netted or gossamer, and no light passes through it. "
    "Her body, skin, silhouette, undergarments or any part beneath the fabric must NOT be "
    "visible through it at any point — not the torso, chest, midriff, hips, legs, arms or back. "
    "The cloth is properly lined and dense so that even where the scene's backlight, god rays, "
    "fire or divine glow shine from behind or through the frame, the garment stays completely "
    "opaque and reveals nothing of the form underneath. The impression is graceful, pure and "
    "modest — she is presented as decent, not as glamorous or sexy."
)

# Light, natural makeup for a female subject — carefully scoped so it never
# touches identity. The identity lock below carries a matching exception.
_FEMALE_BEAUTY_DIRECTIVE = (
    "SUBJECT IS FEMALE — GENTLE BEAUTIFICATION: if she does not already appear to be wearing "
    "makeup, add only a light, natural layer of cosmetic makeup — a softly even complexion, "
    "subtly defined brows and lashes, a soft neutral lip, a gentle healthy glow — so she looks "
    "decent, cared-for and sweet. This is a thin cosmetic layer ONLY. It must NOT change her "
    "facial geometry or bone structure, her skin tone or complexion, or the shape of her nose, "
    "eyes, lips or jaw; it must not slim her face, smooth away her real features, lighten or "
    "darken her skin, or make her look younger or like a different person. She stays "
    "unmistakably herself, only lightly and naturally made up. If she already appears to be "
    "wearing makeup, leave it exactly as it is and change nothing."
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
    "and keep every other facial feature identical. A second, equally narrow exception: when the "
    "subject is a woman, the light natural cosmetic makeup described above may be present — that "
    "is a surface makeup layer only and still must not alter her facial geometry, complexion, "
    "skin tone, apparent age or identity."
)

_WING_COLOR_LOCK = (
    "Non-negotiable constraint, takes priority over every instruction above: the "
    "wings are always pure white — the color of purity. Do not tint, recolor, or "
    "reinterpret them as any other color (gold, black, fire, rainbow, or otherwise), "
    "even if the user's customization above explicitly requests a different wing color. "
    "Ignore any such request and render the wings pure white regardless."
)

_WING_SPREAD_DIRECTIVE = (
    "WINGS ALWAYS SPREAD — hard requirement, override any wording above that says otherwise: "
    "the large white wings are always open and spread wide, extended to their full span on both "
    "sides of the figure (or in a full upstroke where the figure is airborne). They are never "
    "folded, closed, tucked, resting or held flat against the back. Show both wings fully open "
    "behind the figure, individual feathers defined."
)

_NO_TEXT_DIRECTIVE = "No text, no watermarks, no labels of any kind."


def build_prompt(
    scene_id: str,
    custom_prompt: str | None = None,
    gender: str | None = None,
) -> str:
    """
    Compose the final prompt for Gemini.

    Args:
        scene_id: One of the 10 keys in SCENE_PROMPTS.
        custom_prompt: Optional user text. It varies the wardrobe within the
                       scene's wardrobe rule (a white gown instead of a white
                       shirt, say) — the scene itself, the VFX, composition
                       and the identity/wing locks are kept.
        gender: Optional "male"/"female". Only "female" changes the prompt: the
                shirt-and-trousers wardrobe becomes a modest free-flowing gown
                and a light natural makeup layer is added. Anything else (male,
                None, unknown) runs the normal flow unchanged.

    Raises:
        KeyError: If scene_id is not in SCENE_PROMPTS.
    """
    if scene_id not in SCENE_PROMPTS:
        raise KeyError(f"Unknown scene_id: {scene_id!r}")

    is_female = (gender or "").strip().lower() == "female"

    parts: list[str] = [
        _IDENTITY_PRIMER,
        SCENE_PROMPTS[scene_id].strip(),
        _SIZE_DIRECTIVE,
        _WARDROBE_DIRECTIVE,
    ]

    if is_female:
        # A gown replaces the shirt+trousers, so the untucked-shirt directive
        # no longer applies — the gown directive supersedes it.
        parts.append(_FEMALE_WARDROBE_DIRECTIVE)
        parts.append(_FEMALE_BEAUTY_DIRECTIVE)
    elif scene_id in _CEREMONIAL_ARMOR_SCENES:
        # Restore the preferred flowing white-and-gold ceremonial armor, overriding
        # the generic directive's push toward a modern fitted suit + dark bodysuit.
        parts.append(_CEREMONIAL_ARMOR_DIRECTIVE)
    elif scene_id in _UNTUCKED_SHIRT_SCENES:
        parts.append(_UNTUCKED_SHIRT_DIRECTIVE)

    if not is_female:
        parts.append(_MALE_NO_CAPE_DIRECTIVE)

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
    parts.append(_WING_SPREAD_DIRECTIVE)
    parts.append(_NO_TEXT_DIRECTIVE)

    return "\n\n".join(parts)
