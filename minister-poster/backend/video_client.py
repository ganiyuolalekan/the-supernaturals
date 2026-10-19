"""
5-second cinematic announcement video generation.

Primary path  : Google Veo 2/3 via google-genai 2.x API
                (GenerateVideosConfig, GenerateVideosSource — plural form)
                Each style has its own action choreography prompt.

Fallback path : Per-frame Pillow rendering → piped to system ffmpeg.
                Zero jitter (no zoompan snapping), smooth LANCZOS scaling,
                cinematic colour grade, vignette, white-flash reveal.
"""

import io
import os
import time
import math
import shutil
import asyncio
import logging
import tempfile
import subprocess
from functools import partial
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Per-style Veo action prompts
# ─────────────────────────────────────────────

_STYLE_PROMPTS: dict[str, str] = {

    # One choreography prompt per style id (see minister_prompts.py). Describe what
    # MOVES in the 5 seconds, not the whole scene: the poster is the first frame.
    "example_a": (
        "5-second cinematic announcement video. "
        "A confident speaker stands on a rooftop at golden hour. "
        "A light breeze moves their jacket; the camera pushes in slowly. "
        "Their eyes stay on the camera and a small smile forms. "
        "Warm amber and deep navy colour grading. Photorealistic."
    ),

    "example_b": (
        "5-second cinematic announcement video. "
        "A performer stands at a microphone on a dark stage. "
        "Coloured beams sweep slowly through the haze behind them; warm bokeh pulses. "
        "They lift their head and smile as the camera drifts in. "
        "Deep teal and warm magenta colour grading. Photorealistic."
    ),
}

# veo-3.0 returns 404 on standard API keys — only veo-2.0 is accessible
VEO_MODELS = [
    "veo-2.0-generate-001",
]


# ─────────────────────────────────────────────
# Veo generation (google-genai 2.x correct API)
# ─────────────────────────────────────────────

def _veo_generate_sync(poster_bytes: bytes, style_id: str) -> bytes | None:
    """
    Try Veo image-to-video with correct google-genai 2.x API.
    Returns mp4 bytes, or None on any failure.
    """
    try:
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key or api_key == "your_gemini_api_key_here":
            log.warning("Veo skipped: GEMINI_API_KEY not set")
            return None

        client = genai.Client(api_key=api_key)
        prompt = _STYLE_PROMPTS.get(style_id) or next(iter(_STYLE_PROMPTS.values()))

        img = Image.open(io.BytesIO(poster_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        img_bytes = buf.getvalue()

        # Veo 2.0 only supports 9:16 | 16:9 | 1:1 — NOT 4:5
        config = types.GenerateVideosConfig(
            durationSeconds=5,
            aspectRatio="9:16",
            numberOfVideos=1,
        )

        for model in VEO_MODELS:
            try:
                log.info("Veo attempting: model=%s  style=%s", model, style_id)

                source = types.GenerateVideosSource(
                    prompt=prompt,
                    image=types.Image(
                        image_bytes=img_bytes,
                        mime_type="image/jpeg",
                    ),
                )
                operation = client.models.generate_videos(
                    model=model,
                    source=source,
                    config=config,
                )
                log.info("Veo operation created: %s  (polling every 8s, max 3 min)",
                         getattr(operation, "name", "?"))

                # Poll — max 3 minutes
                deadline = time.time() + 180
                polls = 0
                while not operation.done:
                    if time.time() > deadline:
                        raise TimeoutError("Veo timed out after 3 min")
                    time.sleep(8)
                    polls += 1
                    operation = client.operations.get(operation)
                    log.info("Veo poll #%d  done=%s", polls, operation.done)

                # Extract video bytes
                resp = operation.response or operation.result
                if resp and resp.generated_videos:
                    for gen_video in resp.generated_videos:
                        vid = gen_video.video
                        if vid is None:
                            continue
                        # Direct bytes (rarely populated by Gemini API)
                        if vid.video_bytes and len(vid.video_bytes) > 1000:
                            log.info("Veo success via video_bytes: %s (%d bytes)",
                                     model, len(vid.video_bytes))
                            return vid.video_bytes
                        # URI — Gemini API requires the key appended as a query param
                        if vid.uri:
                            import urllib.request as urlreq
                            download_url = vid.uri
                            if "key=" not in download_url:
                                sep = "&" if "?" in download_url else "?"
                                download_url = f"{download_url}{sep}key={api_key}"
                            req = urlreq.Request(download_url)
                            with urlreq.urlopen(req, timeout=60) as r:
                                video_bytes = r.read()
                            if len(video_bytes) > 1000:
                                log.info("Veo success via URI: %s (%d bytes)",
                                         model, len(video_bytes))
                                return video_bytes

                log.warning("Veo %s: operation done but no video in response", model)

            except Exception as exc:
                log.warning("Veo model %s failed: %s", model, exc)

        return None

    except Exception as exc:
        log.warning("Veo setup failed: %s", exc)
        return None


# ─────────────────────────────────────────────
# Per-frame Pillow fallback — smooth, no jitter
# ─────────────────────────────────────────────

def _make_vignette(W: int, H: int) -> np.ndarray:
    """Float32 [0,1] array that darkens edges for a cinematic look."""
    xs = np.linspace(-1, 1, W)
    ys = np.linspace(-1, 1, H)
    xg, yg = np.meshgrid(xs, ys)
    dist = np.sqrt(xg ** 2 + yg ** 2)
    # Soft falloff: 1.0 at centre, ~0.6 at corners
    vig = 1.0 - np.clip(dist * 0.42, 0, 0.55)
    return vig.astype(np.float32)


def _find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for path in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg"]:
        if Path(path).exists():
            return path
    return None


def _pillow_cinematic(poster_bytes: bytes) -> bytes:
    """
    Smooth 5-second cinematic reveal:
      - White flash (0 → 0.5 s)
      - Slow zoom-in 1.0 → 1.12× focused on upper body
      - Warm gold colour grade
      - Cinematic vignette
      - Fade to black (4.3 → 5 s)
    Pipes raw RGB frames to ffmpeg; no zoompan jitter.
    """
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg")

    img = Image.open(io.BytesIO(poster_bytes)).convert("RGB")
    W, H = img.size
    W_out = W - (W % 2)
    H_out = H - (H % 2)
    if W_out != W or H_out != H:
        img = img.resize((W_out, H_out), Image.LANCZOS)
    W, H = W_out, H_out

    fps      = 30
    duration = 5
    n_frames = fps * duration  # 150

    vignette = _make_vignette(W, H)                 # shape (H, W) float32
    img_arr  = np.array(img, dtype=np.float32)      # shape (H, W, 3)

    flash_frames  = int(fps * 0.45)   # white flash lasts 0.45 s
    fade_in_end   = int(fps * 0.7)    # fully revealed by 0.7 s
    fade_out_start= int(fps * 4.2)    # begin fade to black at 4.2 s

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "announcement.mp4")

        cmd = [
            ffmpeg, "-y",
            "-f", "rawvideo",
            "-pixel_format", "rgb24",
            "-video_size", f"{W}x{H}",
            "-framerate", str(fps),
            "-i", "pipe:0",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-b:v", "5M",
            "-movflags", "+faststart",
            output_path,
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for i in range(n_frames):
            t    = i / n_frames                        # 0 → 1
            ease = t * t * (3.0 - 2.0 * t)            # smooth-step

            # ── Zoom: 1.0 → 1.12, focused on upper body (35% from top) ──────
            zoom  = 1.0 + 0.12 * ease
            new_w = int(W / zoom)
            new_h = int(H / zoom)
            x0    = (W - new_w) // 2
            y0    = max(0, int(H * 0.35) - int(H * 0.35 / zoom))

            frame_img = img.crop((x0, y0, x0 + new_w, y0 + new_h))
            frame_img = frame_img.resize((W, H), Image.LANCZOS)
            frame     = np.array(frame_img, dtype=np.float32)

            # ── Warm gold colour grade ────────────────────────────────────────
            frame[:, :, 0] = np.clip(frame[:, :, 0] * 1.08, 0, 255)   # warm red
            frame[:, :, 1] = np.clip(frame[:, :, 1] * 1.03, 0, 255)   # slight green
            frame[:, :, 2] = np.clip(frame[:, :, 2] * 0.92, 0, 255)   # cool blue down
            # Lift shadows slightly (cinematic feel)
            frame = np.clip(frame * 1.06 + 4, 0, 255)

            # ── Vignette ──────────────────────────────────────────────────────
            frame[:, :, 0] *= vignette
            frame[:, :, 1] *= vignette
            frame[:, :, 2] *= vignette

            # ── White flash (intro) ───────────────────────────────────────────
            if i < flash_frames:
                flash_alpha = 1.0 - (i / flash_frames)
                frame = frame * (1.0 - flash_alpha) + 255.0 * flash_alpha
            elif i < fade_in_end:
                reveal_alpha = (i - flash_frames) / max(1, fade_in_end - flash_frames)
                frame = frame * reveal_alpha

            # ── Fade to black (outro) ─────────────────────────────────────────
            if i >= fade_out_start:
                fade_alpha = 1.0 - (i - fade_out_start) / max(1, n_frames - fade_out_start)
                frame = frame * fade_alpha

            proc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

        proc.stdin.close()
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg encoding failed (exit {proc.returncode})")

        with open(output_path, "rb") as f:
            return f.read()


# ─────────────────────────────────────────────
# Public async API
# ─────────────────────────────────────────────

async def generate_announcement_video(
    poster_bytes: bytes,
    style_id: str,
    category: str = "",   # kept for backward compat
) -> bytes:
    """
    Tries Veo 2 image-to-video first (9:16, 5 s).
    Falls back to smooth per-frame Pillow+ffmpeg animation on any failure.
    """
    loop = asyncio.get_event_loop()

    veo_bytes = await loop.run_in_executor(
        None, partial(_veo_generate_sync, poster_bytes, style_id)
    )
    if veo_bytes:
        generate_announcement_video._last_engine = "veo-2.0"  # type: ignore
        log.info("Video engine: Veo 2.0 (%d bytes)", len(veo_bytes))
        return veo_bytes

    log.info("Veo unavailable — using Pillow/ffmpeg fallback (style=%s)", style_id)
    generate_announcement_video._last_engine = "pillow-ffmpeg"  # type: ignore
    return await loop.run_in_executor(
        None, partial(_pillow_cinematic, poster_bytes)
    )
