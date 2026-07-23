"""
Prompt construction for The SuperNaturals 2026.

Single API: build_prompt(scene_id, custom_prompt=None) -> str

The 10 full photorealistic prompts live in scene_prompts.py (the source of
truth). This module assembles the final string sent to Gemini by:
  1. Looking up the scene by ID.
  2. Appending the output size directive (portrait 1080 × 1620 px).
  3. Optionally appending the user's custom-prompt block. Clothing,
     accessories, and personal appearance details in the custom prompt
     take priority over defaults — only the scene's supernatural elements
     (wings, divine light, VFX, cinematic composition) are protected.
  4. Always appending the no-text directive on its own line, once.
"""

from scene_prompts import SCENE_PROMPTS


_SIZE_DIRECTIVE = (
    "Output format: portrait orientation, 2:3 aspect ratio, "
    "1080 × 1620 pixels. Compose the full-body or near-full-body figure "
    "to fill this portrait frame naturally."
)

_CUSTOM_PROMPT_WRAPPER = (
    "User's personal customization — apply this faithfully and exactly as requested. "
    "This may include anything: clothing, outfit, accessories, hair, body posture, "
    "motion or action, additional objects, extra people or creatures, environmental "
    "details, or any other element the user specifies. Whatever is described here "
    "takes priority and must appear clearly in the output. "
    "Only the core supernatural identifiers must remain intact: the large white wings, "
    "the divine light and VFX defined by the scene, and the cinematic composition. "
    "Everything else is open to the user's direction: {custom}"
)

_NO_TEXT_DIRECTIVE = "No text, no watermarks, no labels of any kind."


def build_prompt(scene_id: str, custom_prompt: str | None = None) -> str:
    """
    Compose the final prompt for Gemini.

    Args:
        scene_id: One of the 10 keys in SCENE_PROMPTS.
        custom_prompt: Optional user text. Clothing/appearance details here
                       override scene defaults; VFX and composition are kept.

    Raises:
        KeyError: If scene_id is not in SCENE_PROMPTS.
    """
    if scene_id not in SCENE_PROMPTS:
        raise KeyError(f"Unknown scene_id: {scene_id!r}")

    parts: list[str] = [
        SCENE_PROMPTS[scene_id].strip(),
        _SIZE_DIRECTIVE,
    ]

    if custom_prompt:
        custom = custom_prompt.strip()
        if custom:
            parts.append(_CUSTOM_PROMPT_WRAPPER.format(custom=custom))

    parts.append(_NO_TEXT_DIRECTIVE)

    return "\n\n".join(parts)
