"""OCR utilities."""

from __future__ import annotations

import io

from PIL import Image, UnidentifiedImageError

try:
    import pytesseract
except Exception:  # pragma: no cover - import fallback for minimal environments
    pytesseract = None


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Extract text from image bytes using Tesseract OCR."""
    if pytesseract is None:
        raise RuntimeError(
            "pytesseract is unavailable. Install Tesseract OCR and the pytesseract package."
        )

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError as exc:  # pragma: no cover - defensive path
        raise ValueError("Unsupported or corrupted image file.") from exc

    text = pytesseract.image_to_string(image)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()
