"""
Phase 2 Tests: Document Loading

Tests for PDF and image loading, validation, and text extraction.
"""

import io
import sys
from pathlib import Path

import pytest
from PIL import Image

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def create_test_pdf_with_text(text: str = "Hello World Test Document") -> bytes:
    """Create a simple PDF with text using PyMuPDF."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_test_image(
    width: int = 200,
    height: int = 100,
    color: str = "white",
    text: str = None
) -> bytes:
    """Create a test image."""
    img = Image.new("RGB", (width, height), color)

    if text:
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), text, fill="black")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_large_pdf(num_pages: int = 60) -> bytes:
    """Create a PDF with many pages."""
    import fitz

    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}", fontsize=12)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestFileValidation:
    """Test file validation functionality."""

    def test_validate_valid_pdf(self):
        """Test validation of valid PDF."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        pdf_bytes = create_test_pdf_with_text()

        result = loader.validate_file(pdf_bytes, "test.pdf")

        assert result.is_valid is True
        assert result.file_type == ".pdf"
        assert result.page_count == 1
        assert result.error_message is None

    def test_validate_valid_image(self):
        """Test validation of valid image."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        img_bytes = create_test_image()

        result = loader.validate_file(img_bytes, "test.png")

        assert result.is_valid is True
        assert result.file_type == ".png"
        assert result.page_count == 1

    def test_validate_unsupported_format(self):
        """Test validation of unsupported format."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        result = loader.validate_file(b"fake content", "test.doc")

        assert result.is_valid is False
        assert "Unsupported file format" in result.error_message

    def test_validate_oversized_file(self):
        """Test validation of oversized file."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        # Create content larger than max (simulate 30MB for a 25MB limit)
        large_content = b"x" * (30 * 1024 * 1024)

        result = loader.validate_file(large_content, "large.pdf")

        assert result.is_valid is False
        assert "exceeds maximum" in result.error_message

    def test_validate_too_many_pages(self):
        """Test validation of PDF with too many pages."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        pdf_bytes = create_large_pdf(60)  # More than 50 page limit

        result = loader.validate_file(pdf_bytes, "large.pdf")

        assert result.is_valid is False
        assert "Page count" in result.error_message

    def test_validate_corrupt_pdf(self):
        """Test validation of corrupt PDF."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        result = loader.validate_file(b"not a valid pdf", "corrupt.pdf")

        assert result.is_valid is False
        assert "Corrupt" in result.error_message or "invalid" in result.error_message.lower()

    def test_validate_corrupt_image(self):
        """Test validation of corrupt image."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        result = loader.validate_file(b"not a valid image", "corrupt.png")

        assert result.is_valid is False
        assert "Corrupt" in result.error_message or "invalid" in result.error_message.lower()


class TestPDFLoading:
    """Test PDF loading functionality."""

    def test_load_pdf_with_text(self):
        """Test loading PDF with native text."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        test_text = "This is a test document with some content."
        pdf_bytes = create_test_pdf_with_text(test_text)

        result = loader.load(pdf_bytes, "test.pdf")

        assert result.filename == "test.pdf"
        assert result.file_type == ".pdf"
        assert result.page_count == 1
        assert result.has_native_text is True
        assert test_text in result.raw_text

    def test_load_multipage_pdf(self):
        """Test loading multi-page PDF."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        pdf_bytes = create_large_pdf(5)

        result = loader.load(pdf_bytes, "multipage.pdf")

        assert result.page_count == 5
        assert len(result.pages) == 5
        assert "Page 1" in result.pages[0].text
        assert "Page 5" in result.pages[4].text

    def test_pdf_page_content(self):
        """Test that PageContent is populated correctly."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        pdf_bytes = create_test_pdf_with_text("Page content here")

        result = loader.load(pdf_bytes, "test.pdf")

        assert len(result.pages) == 1
        page = result.pages[0]
        assert page.page_number == 1
        assert "Page content here" in page.text

    def test_scanned_detection_native(self):
        """Test that native text PDFs are not marked as scanned."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        long_text = "This is a long paragraph with enough text to be considered native. " * 10
        pdf_bytes = create_test_pdf_with_text(long_text)

        result = loader.load(pdf_bytes, "native.pdf")

        assert result.has_native_text is True
        # Document with good text extraction should not be scanned
        assert result.is_scanned is False


class TestImageLoading:
    """Test image loading functionality."""

    def test_load_png_image(self):
        """Test loading PNG image."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        img_bytes = create_test_image(text="Test Image")

        result = loader.load(img_bytes, "test.png")

        assert result.filename == "test.png"
        assert result.file_type == ".png"
        assert result.page_count == 1
        assert result.is_scanned is True
        assert result.has_native_text is False
        assert len(result.images) == 1

    def test_load_jpg_image(self):
        """Test loading JPG image."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        # Create JPG
        img = Image.new("RGB", (200, 100), "white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_bytes = buf.getvalue()

        result = loader.load(img_bytes, "test.jpg")

        assert result.file_type == ".jpg"
        assert result.is_scanned is True
        assert len(result.images) == 1

    def test_image_page_content(self):
        """Test PageContent for images."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        img_bytes = create_test_image()

        result = loader.load(img_bytes, "test.png")

        assert len(result.pages) == 1
        page = result.pages[0]
        assert page.page_number == 1
        assert page.is_scanned is True
        assert page.text == ""  # No text before OCR

    def test_image_conversion_rgb(self):
        """Test that images are converted to RGB."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        # Create RGBA image
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        result = loader.load(img_bytes, "rgba.png")

        # Image should be converted to RGB
        assert result.images[0].mode == "RGB"


class TestHelperMethods:
    """Test helper methods."""

    def test_get_extension(self):
        """Test file extension extraction."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        assert loader._get_extension("test.pdf") == ".pdf"
        assert loader._get_extension("test.PDF") == ".pdf"
        assert loader._get_extension("document.PNG") == ".png"
        assert loader._get_extension("no_extension") == ""
        assert loader._get_extension("multi.dot.jpg") == ".jpg"

    def test_page_to_image(self):
        """Test PDF page to image conversion."""
        from src.document_loader import DocumentLoader
        import fitz

        loader = DocumentLoader()
        pdf_bytes = create_test_pdf_with_text("Convert me to image")

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]

        img = loader._page_to_image(page)
        doc.close()

        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
        assert img.width > 0
        assert img.height > 0

    def test_get_page_images(self):
        """Test selective page image extraction."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()
        pdf_bytes = create_large_pdf(5)

        # Get specific pages
        images = loader.get_page_images(pdf_bytes, page_numbers=[1, 3, 5])

        assert len(images) == 3
        assert images[0][0] == 1  # Page number
        assert images[1][0] == 3
        assert images[2][0] == 5

        # All should be valid images
        for page_num, img in images:
            assert isinstance(img, Image.Image)


class TestDocumentLoaderSingleton:
    """Test singleton pattern."""

    def test_get_document_loader(self):
        """Test singleton returns same instance."""
        from src.document_loader import get_document_loader

        loader1 = get_document_loader()
        loader2 = get_document_loader()

        assert loader1 is loader2

    def test_loader_uses_settings(self):
        """Test loader uses configuration settings."""
        from src.document_loader import DocumentLoader
        from app.config import get_settings

        settings = get_settings()
        loader = DocumentLoader()

        assert loader._max_file_size == settings.document.max_file_size_mb * 1024 * 1024
        assert loader._max_pages == settings.document.max_pages


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_load_unsupported_format(self):
        """Test loading unsupported format raises error."""
        from src.document_loader import DocumentLoader

        loader = DocumentLoader()

        with pytest.raises(ValueError, match="Unsupported"):
            loader.load(b"content", "test.doc")

    def test_empty_pdf(self):
        """Test handling PDF with minimal content."""
        from src.document_loader import DocumentLoader
        import fitz

        loader = DocumentLoader()

        # PyMuPDF requires at least one page to create a valid PDF
        # Create a PDF with one blank page instead
        doc = fitz.open()
        doc.new_page()  # Add one blank page
        pdf_bytes = doc.tobytes()
        doc.close()

        result = loader.load(pdf_bytes, "minimal.pdf")

        assert result.page_count == 1
        assert result.pages[0].text == ""

    def test_blank_page_pdf(self):
        """Test PDF with blank pages."""
        from src.document_loader import DocumentLoader
        import fitz

        loader = DocumentLoader()

        doc = fitz.open()
        doc.new_page()  # Add blank page with no text
        pdf_bytes = doc.tobytes()
        doc.close()

        result = loader.load(pdf_bytes, "blank.pdf")

        assert result.page_count == 1
        assert result.pages[0].text == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
