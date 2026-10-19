"""
Applies the text overlay onto the generated supernatural portrait.

Layout — bottom-up, so elements never overlap:

  CONFIRMED png stamp  — overlaid in the lower section, rotated per style
  Minister name        — white bold, below stamp
  Minister title       — gold, wraps to 2 lines max
  Bottom center        : "16 – 18 OCTOBER 2026"

Stamp PNG:  place confirmed.png at  backend/assets/confirmed.png
            Falls back to bold Bebas Neue text if the file is absent.
"""

import io
import math
import logging
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from minister_prompts import STYLE_OVERLAY_CONFIG

log = logging.getLogger(__name__)

FONTS_DIR  = Path(__file__).parent / "fonts"
ASSETS_DIR = Path(__file__).parent / "assets"

GOLD     = (240, 168, 50, 255)
WHITE    = (255, 255, 255, 255)
WHITE_70 = (255, 255, 255, 178)

DATES = "16 – 18 OCTOBER 2026"

_BASE = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf"
_FONT_URLS = {
    "BebasNeue-Regular.ttf":     "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
    "Montserrat-Bold.ttf":       f"{_BASE}/Montserrat-Bold.ttf",
    "Montserrat-ExtraBold.ttf":  f"{_BASE}/Montserrat-ExtraBold.ttf",
    "Montserrat-Regular.ttf":    f"{_BASE}/Montserrat-Regular.ttf",
    "Montserrat-Light.ttf":      f"{_BASE}/Montserrat-Light.ttf",
    "Montserrat-BoldItalic.ttf": f"{_BASE}/Montserrat-BoldItalic.ttf",
    "Montserrat-Italic.ttf":     f"{_BASE}/Montserrat-Italic.ttf",
}


def ensure_fonts() -> None:
    FONTS_DIR.mkdir(exist_ok=True)
    for name, url in _FONT_URLS.items():
        dest = FONTS_DIR / name
        if not dest.exists():
            log.info("Downloading font %s…", name)
            try:
                urllib.request.urlretrieve(url, dest)
            except Exception as exc:
                log.warning("Could not download %s: %s", name, exc)


def _load_font(filename: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = FONTS_DIR / filename
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _measure(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Word-wrap text to max_width with no line cap."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if _measure(draw, candidate, font)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_rotated_text(
    canvas: Image.Image,
    text: str,
    font,
    color: tuple,
    x: int,
    top_y: int,
    angle: float,
    align: str = "left",
) -> None:
    """Draw text with its block top at top_y, rotated by angle degrees."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = dummy.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad = 4
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad, pad), text, font=font, fill=color)

    rotated = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    rx, ry = rotated.size

    text_top_offset = int((ry - th) / 2)
    paste_y = top_y - text_top_offset

    if align == "right":
        paste_x = x - tw - int((rx - tw) / 2)
    else:
        paste_x = x - int((rx - tw) / 2)

    canvas.paste(rotated, (paste_x, paste_y), rotated)


def _overlay_stamp(canvas: Image.Image, stamp_path: Path,
                   target_w: int, center_x: int, top_y: int,
                   angle: float) -> int:
    """
    Overlay the confirmed.png stamp.
    Scales it to target_w, rotates by angle, places top of stamp at top_y.
    Returns the rendered height of the stamp block.
    """
    stamp = Image.open(stamp_path).convert("RGBA")
    sw, sh = stamp.size
    scale  = target_w / sw
    new_h  = int(sh * scale)
    stamp  = stamp.resize((target_w, new_h), Image.LANCZOS)

    if angle != 0:
        stamp = stamp.rotate(angle, expand=True, resample=Image.BICUBIC)

    rx, ry = stamp.size
    paste_x = center_x - rx // 2
    paste_y = top_y
    canvas.paste(stamp, (paste_x, paste_y), stamp)
    return ry


def build_poster(
    portrait_bytes: bytes,
    minister_name: str,
    minister_title: str,
    style_id: str,
) -> bytes:
    """
    Overlay announcement text (and stamp) onto the portrait.
    Returns JPEG bytes of the finished poster.
    """
    ensure_fonts()

    cfg       = STYLE_OVERLAY_CONFIG.get(style_id, {"rotation": 0, "stamp_color": "white", "align": "left"})
    rotation  = cfg["rotation"]
    stamp_col = GOLD if cfg["stamp_color"] == "gold" else WHITE
    align     = cfg["align"]

    img = Image.open(io.BytesIO(portrait_bytes)).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    margin  = int(w * 0.07)
    avail_w = w - 2 * margin

    # ── Fonts ────────────────────────────────────────────────────────────────
    font_conf  = _load_font("BebasNeue-Regular.ttf",    int(h * 0.065))
    font_name  = _load_font("Montserrat-ExtraBold.ttf", int(h * 0.046))
    title_file = "Montserrat-Italic.ttf" if style_id == "atmosphere" else "Montserrat-Regular.ttf"
    font_title = _load_font(title_file,                 int(h * 0.026))
    font_small = _load_font("Montserrat-Light.ttf",     int(h * 0.017))

    gap_sm     = int(h * 0.012)
    gap_md     = int(h * 0.018)
    pad_bottom = int(h * 0.030)

    # ── Check for confirmed.png stamp ────────────────────────────────────────
    stamp_path = ASSETS_DIR / "confirmed.png"
    use_png_stamp = stamp_path.exists()

    # ─────────────────────────────────────────────────────────────────────────
    # Measure all blocks bottom → top
    # ─────────────────────────────────────────────────────────────────────────

    # DATES
    _, dates_h = _measure(draw, DATES, font_small)
    dates_baseline = h - pad_bottom

    # TITLE (optional)
    title_lines = _wrap_text(draw, minister_title, font_title, avail_w) if minister_title.strip() else []
    _, one_title_h = _measure(draw, "Ag", font_title)
    line_leading  = int(one_title_h * 1.35)
    if title_lines:
        title_block_h = one_title_h + line_leading * (len(title_lines) - 1)
        title_top_y   = dates_baseline - dates_h - gap_md - title_block_h
    else:
        title_block_h = 0
        title_top_y   = dates_baseline - dates_h - gap_md

    # NAME
    name_text = minister_name.upper()
    name_w, name_h = _measure(draw, name_text, font_name)
    if name_w > avail_w:
        scale     = avail_w / name_w
        new_size  = max(int(int(h * 0.046) * scale), int(h * 0.026))
        font_name = _load_font("Montserrat-ExtraBold.ttf", new_size)
        name_w, name_h = _measure(draw, name_text, font_name)
    name_top_y = title_top_y - gap_sm - name_h

    # CONFIRMED stamp (PNG only — no text fallback)
    if use_png_stamp:
        stamp_w     = int(avail_w * 0.55)
        stamp_h_est = stamp_w // 3
        try:
            tmp = Image.open(stamp_path)
            sw, sh = tmp.size
            stamp_h_est = int(stamp_w * sh / sw)
        except Exception:
            pass
        conf_block_h = stamp_h_est
        conf_top_y   = name_top_y - gap_md - conf_block_h

        # Safety floor
        if conf_top_y < int(h * 0.62):
            gap_sm      = int(h * 0.008)
            gap_md      = int(h * 0.010)
            title_top_y = dates_baseline - dates_h - gap_md - title_block_h
            name_top_y  = title_top_y - gap_sm - name_h
            conf_top_y  = max(name_top_y - gap_md - conf_block_h, int(h * 0.60))
    else:
        conf_top_y = name_top_y  # no stamp, name starts higher

    # ─────────────────────────────────────────────────────────────────────────
    # Draw
    # ─────────────────────────────────────────────────────────────────────────
    x_pos = (w - margin) if align == "right" else margin

    # CONFIRMED — PNG stamp only (skip if file absent)
    if use_png_stamp:
        cx = int(w * 0.60) if align == "right" else int(w * 0.40)
        _overlay_stamp(img, stamp_path,
                       target_w=int(avail_w * 0.55),
                       center_x=cx,
                       top_y=conf_top_y,
                       angle=rotation * -1)

    # NAME
    na = "lt" if align == "left" else "rt"
    draw.text((x_pos, name_top_y), name_text, font=font_name, fill=WHITE, anchor=na)

    # TITLE
    for i, line in enumerate(title_lines):
        draw.text((x_pos, title_top_y + i * line_leading),
                  line, font=font_title, fill=GOLD, anchor=na)

    # DATES
    draw.text((w // 2, dates_baseline), DATES, font=font_small, fill=WHITE_70, anchor="mb")

    # Export
    out = Image.new("RGB", img.size, (0, 0, 0))
    out.paste(img, mask=img.split()[3])
    buf = io.BytesIO()
    out.save(buf, format="JPEG", quality=93)
    return buf.getvalue()
