"""Document loading for PDF and image files."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path

from pypdf import PdfReader

from src.ocr_engine import extract_text_from_image_bytes

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def _normalize_text(value: str) -> str:
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


@dataclass(slots=True)
class DocumentLoadResult:
    document_id: str
    filename: str
    document_type: str
    pages: list[str]
    used_ocr: bool

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text(self) -> str:
        rendered: list[str] = []
        for idx, page in enumerate(self.pages, start=1):
            rendered.append(f"[Page {idx}]\n{page}".strip())
        return "\n\n".join(rendered).strip()


def load_document(file_bytes: bytes, filename: str) -> DocumentLoadResult:
    """Load bytes into normalized text pages."""
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Allowed: PDF, PNG, JPG, JPEG, TIFF."
        )

    digest_seed = filename.encode("utf-8") + str(len(file_bytes)).encode("utf-8")
    document_id = sha1(digest_seed + file_bytes[:256]).hexdigest()[:16]

    if extension == ".pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [_normalize_text(page.extract_text() or "") for page in reader.pages]
        if not any(pages):
            raise ValueError(
                "PDF has no machine-readable text. For scanned PDFs, convert to image-first OCR flow."
            )

        return DocumentLoadResult(
            document_id=document_id,
            filename=filename,
            document_type="pdf",
            pages=pages,
            used_ocr=False,
        )

    text = _normalize_text(extract_text_from_image_bytes(file_bytes))
    if not text:
        raise ValueError("OCR completed but no readable text was detected.")

    return DocumentLoadResult(
        document_id=document_id,
        filename=filename,
        document_type="image",
        pages=[text],
        used_ocr=True,
    )
