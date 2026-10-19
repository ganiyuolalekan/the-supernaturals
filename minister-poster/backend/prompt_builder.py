"""
Prompt construction for the announcement-poster generator.
Assembles the final string sent to Gemini.
"""

from minister_prompts import MINISTER_PROMPTS, IDENTITY_PREFIX


_SIZE_DIRECTIVE = (
    "Output format: portrait orientation, 4:5 aspect ratio, "
    "1080 × 1350 pixels. Compose the full-body or near-full-body figure "
    "to fill this portrait frame naturally. The lower quarter of the image "
    "must graduate to near-black for text overlay."
)

_NO_TEXT_DIRECTIVE = "No text, no watermarks, no labels of any kind."


def build_prompt(style_id: str) -> str:
    """
    Build the full Gemini prompt for an announcement portrait.
    Includes identity-preservation prefix, scene body, size directive,
    and no-text footer.
    """
    if style_id not in MINISTER_PROMPTS:
        raise KeyError(f"Unknown style_id: {style_id!r}")

    parts = [
        IDENTITY_PREFIX.strip(),
        MINISTER_PROMPTS[style_id].strip(),
        _SIZE_DIRECTIVE,
        _NO_TEXT_DIRECTIVE,
    ]

    return "\n\n".join(parts)
