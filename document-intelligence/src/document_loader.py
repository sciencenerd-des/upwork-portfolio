"""
Document Loader Module

Handles loading and validation of PDF and image documents.
- PDF files: native text extraction with PyMuPDF, scanned detection
- Images: PNG, JPG, TIFF support
- File validation: size, format, page limits
"""

import io
import logging
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional, Union
from dataclasses import dataclass

import fitz  # PyMuPDF
from PIL import Image

from app.config import get_settings
from app.models import FileValidation, PageContent

logger = logging.getLogger(__name__)


@dataclass
class LoadedDocument:
    """Result of loading a document."""
    filename: str
    file_type: str
    file_size_bytes: int
    page_count: int
    is_scanned: bool
    has_native_text: bool
    pages: list[PageContent]
    images: list[Image.Image]  # For OCR processing
    raw_text: str  # Native text if available


class DocumentLoader:
    """
    Loads and validates documents (PDF and images).
    Detects scanned vs native PDF and extracts text where available.
    """

    def __init__(self):
        self.settings = get_settings()
        self._supported_formats = set(self.settings.document.supported_formats)
        self._max_file_size = self.settings.document.max_file_size_mb * 1024 * 1024
        self._max_pages = self.settings.document.max_pages

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_file(
        self,
        file_content: bytes,
        filename: str
    ) -> FileValidation:
        """
        Validate file before processing.
        Checks: format, size, corruption, page count.
        """
        # Check file extension
        ext = self._get_extension(filename)
        if ext not in self._supported_formats:
            return FileValidation(
                is_valid=False,
                error_message=f"Unsupported file format: {ext}. Supported: {', '.join(self._supported_formats)}",
                file_type=ext,
                file_size_bytes=len(file_content)
            )

        # Check file size
        if len(file_content) > self._max_file_size:
            return FileValidation(
                is_valid=False,
                error_message=f"File size ({len(file_content) / 1024 / 1024:.1f}MB) exceeds maximum ({self.settings.document.max_file_size_mb}MB)",
                file_type=ext,
                file_size_bytes=len(file_content)
            )

        # For PDFs, check page count and corruption
        if ext == ".pdf":
            try:
                doc = fitz.open(stream=file_content, filetype="pdf")
                page_count = len(doc)
                doc.close()

                if page_count > self._max_pages:
                    return FileValidation(
                        is_valid=False,
                        error_message=f"Page count ({page_count}) exceeds maximum ({self._max_pages})",
                        file_type=ext,
                        file_size_bytes=len(file_content),
                        page_count=page_count
                    )

                return FileValidation(
                    is_valid=True,
                    file_type=ext,
                    file_size_bytes=len(file_content),
                    page_count=page_count
                )

            except Exception as e:
                return FileValidation(
                    is_valid=False,
                    error_message=f"Corrupt or invalid PDF file: {str(e)}",
                    file_type=ext,
                    file_size_bytes=len(file_content)
                )

        # For images, validate format
        if ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif"]:
            try:
                img = Image.open(io.BytesIO(file_content))
                img.verify()  # Verify it's a valid image

                return FileValidation(
                    is_valid=True,
                    file_type=ext,
                    file_size_bytes=len(file_content),
                    page_count=1  # Single image = 1 page
                )

            except Exception as e:
                return FileValidation(
                    is_valid=False,
                    error_message=f"Corrupt or invalid image file: {str(e)}",
                    file_type=ext,
                    file_size_bytes=len(file_content)
                )

        return FileValidation(
            is_valid=True,
            file_type=ext,
            file_size_bytes=len(file_content)
        )

    # =========================================================================
    # Loading
    # =========================================================================

    def load(
        self,
        file_content: bytes,
        filename: str
    ) -> LoadedDocument:
        """
        Load a document from bytes.
        Returns LoadedDocument with extracted content.
        """
        ext = self._get_extension(filename)

        if ext == ".pdf":
            return self._load_pdf(file_content, filename)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".tif"]:
            return self._load_image(file_content, filename, ext)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def load_from_path(self, file_path: Union[str, Path]) -> LoadedDocument:
        """Load document from file path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            content = f.read()

        return self.load(content, path.name)

    def _load_pdf(self, file_content: bytes, filename: str) -> LoadedDocument:
        """Load and process PDF document."""
        doc = fitz.open(stream=file_content, filetype="pdf")

        pages: list[PageContent] = []
        images: list[Image.Image] = []
        all_text = []
        has_native_text = False
        scanned_page_count = 0

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract native text
            text = page.get_text("text").strip()
            is_scanned = self._is_page_scanned(page, text)

            if text:
                has_native_text = True
            if is_scanned:
                scanned_page_count += 1

            pages.append(PageContent(
                page_number=page_num + 1,
                text=text,
                is_scanned=is_scanned
            ))
            all_text.append(text)

            # If scanned or low text, render page as image for OCR
            if is_scanned or len(text) < 50:
                img = self._page_to_image(page)
                images.append(img)

        doc.close()

        # Determine if document is primarily scanned
        is_scanned = scanned_page_count > len(pages) / 2

        return LoadedDocument(
            filename=filename,
            file_type=".pdf",
            file_size_bytes=len(file_content),
            page_count=len(pages),
            is_scanned=is_scanned,
            has_native_text=has_native_text,
            pages=pages,
            images=images,
            raw_text="\n\n".join(all_text)
        )

    def _load_image(
        self,
        file_content: bytes,
        filename: str,
        ext: str
    ) -> LoadedDocument:
        """Load image file."""
        img = Image.open(io.BytesIO(file_content))

        # Convert to RGB if necessary
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        return LoadedDocument(
            filename=filename,
            file_type=ext,
            file_size_bytes=len(file_content),
            page_count=1,
            is_scanned=True,  # Images always need OCR
            has_native_text=False,
            pages=[PageContent(page_number=1, text="", is_scanned=True)],
            images=[img],
            raw_text=""
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_extension(self, filename: str) -> str:
        """Extract lowercase file extension."""
        if "." not in filename:
            return ""
        return "." + filename.rsplit(".", 1)[-1].lower()

    def _is_page_scanned(self, page: fitz.Page, text: str) -> bool:
        """
        Determine if a PDF page is scanned (image-based) vs native text.

        Heuristics:
        1. Very little or no text extracted
        2. Page has embedded images covering most area
        3. Text-to-image ratio is very low
        """
        # If significant text, it's native
        if len(text) > 100:
            return False

        # Check for images on page
        image_list = page.get_images(full=True)
        if not image_list:
            # No images and no text - might be blank or vector-based
            return len(text) < 20

        # Calculate image coverage
        page_rect = page.rect
        page_area = page_rect.width * page_rect.height

        total_image_area = 0
        for img in image_list:
            try:
                # Get image bbox
                xref = img[0]
                # Estimate image area (simplified)
                total_image_area += page_area * 0.7  # Assume large images
            except Exception:
                pass

        # If images cover significant area and little text, it's scanned
        if total_image_area > page_area * 0.5 and len(text) < 100:
            return True

        return False

    def _page_to_image(
        self,
        page: fitz.Page,
        dpi: int = None
    ) -> Image.Image:
        """Convert PDF page to PIL Image for OCR."""
        if dpi is None:
            dpi = self.settings.ocr.dpi

        # Calculate zoom factor for desired DPI (default PDF is 72 DPI)
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        # Render page to pixmap
        pix = page.get_pixmap(matrix=matrix)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        return img

    def get_page_images(
        self,
        file_content: bytes,
        page_numbers: Optional[list[int]] = None
    ) -> list[tuple[int, Image.Image]]:
        """
        Extract specific pages as images.
        Useful for selective OCR.
        """
        doc = fitz.open(stream=file_content, filetype="pdf")
        images = []

        if page_numbers is None:
            page_numbers = list(range(1, len(doc) + 1))

        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                page = doc[page_num - 1]
                img = self._page_to_image(page)
                images.append((page_num, img))

        doc.close()
        return images


# Singleton instance
_document_loader: Optional[DocumentLoader] = None


def get_document_loader() -> DocumentLoader:
    """Get or create document loader instance."""
    global _document_loader
    if _document_loader is None:
        _document_loader = DocumentLoader()
    return _document_loader
