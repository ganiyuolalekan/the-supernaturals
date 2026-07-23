import os
import io
from PIL import Image

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MIN_DIMENSION = 512
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_image(
    image_bytes: bytes,
    filename: str | None,
    content_type: str | None,
) -> tuple[bool, str | None]:
    if len(image_bytes) > MAX_FILE_SIZE:
        return False, "file_too_large"

    ext = os.path.splitext((filename or "").lower())[1]
    ct = (content_type or "").lower().split(";")[0].strip()
    if ct not in ALLOWED_CONTENT_TYPES and ext not in ALLOWED_EXTENSIONS:
        return False, "invalid_file_type"

    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            return False, "image_too_small"
    except Exception:
        return False, "invalid_file_type"

    try:
        face_count = _detect_faces(image_bytes)
        if face_count == 0:
            return False, "no_face_detected"
        if face_count > 1:
            return False, "multiple_faces"
    except ImportError:
        pass  # mediapipe not installed — skip face detection
    except Exception:
        pass  # face detection failed silently — let Gemini handle it

    return True, None


def _detect_faces(image_bytes: bytes) -> int:
    import mediapipe as mp
    import numpy as np

    mp_face = mp.solutions.face_detection

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(img)

    with mp_face.FaceDetection(min_detection_confidence=0.4) as detector:
        results = detector.process(img_array)

    return len(results.detections) if results.detections else 0
