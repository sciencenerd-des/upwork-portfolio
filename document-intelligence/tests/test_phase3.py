"""
Phase 3 Tests: OCR Engine

Tests for Tesseract OCR with preprocessing.
Some tests may be skipped if Tesseract is not installed.
"""

import io
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def tesseract_available() -> bool:
    """Check if Tesseract is available."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def create_text_image(
    text: str,
    width: int = 400,
    height: int = 100,
    font_size: int = 20,
    background: str = "white",
    text_color: str = "black"
) -> Image.Image:
    """Create an image with text for OCR testing."""
    img = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(img)

    # Try to use a basic font, fall back to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    draw.text((10, height // 3), text, fill=text_color, font=font)
    return img


def create_noisy_image(
    text: str,
    noise_level: float = 0.1
) -> Image.Image:
    """Create a noisy image for testing preprocessing."""
    import numpy as np

    img = create_text_image(text, width=400, height=100)
    img_array = np.array(img)

    # Add noise
    noise = np.random.normal(0, noise_level * 255, img_array.shape)
    noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(noisy)


def create_rotated_image(text: str, angle: float = 5) -> Image.Image:
    """Create a slightly rotated image for testing deskew."""
    img = create_text_image(text, width=400, height=100)
    return img.rotate(angle, fillcolor="white", expand=True)


class TestImagePreprocessing:
    """Test image preprocessing functionality."""

    def test_preprocess_converts_to_grayscale(self):
        """Test that preprocessing converts to grayscale."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        rgb_image = create_text_image("Test", background="white")

        # Ensure it's RGB
        assert rgb_image.mode == "RGB"

        processed = engine.preprocess_image(rgb_image)

        # Should be grayscale
        assert processed.mode == "L"

    def test_denoise_image(self):
        """Test denoising functionality."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        noisy = create_noisy_image("Test")
        grayscale = noisy.convert("L")

        denoised = engine._denoise_image(grayscale)

        # Should return an image
        assert isinstance(denoised, Image.Image)

    def test_enhance_contrast(self):
        """Test contrast enhancement."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()

        # Create low contrast image
        img = Image.new("L", (100, 100), 128)

        enhanced = engine._enhance_contrast(img)

        # Should return an image
        assert isinstance(enhanced, Image.Image)

    def test_binarize_image(self):
        """Test binarization."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        img = create_text_image("Test").convert("L")

        binary = engine._binarize_image(img, threshold=150)

        # Should be binary mode
        assert binary.mode == "1"

    def test_preprocessing_disabled(self):
        """Test that preprocessing can be disabled."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        engine._preprocessing = {"enabled": False}

        original = create_text_image("Test")
        processed = engine.preprocess_image(original)

        # Should return original image unchanged
        assert processed is original


@pytest.mark.skipif(not tesseract_available(), reason="Tesseract not installed")
class TestOCRProcessing:
    """Test OCR processing functionality."""

    def test_ocr_clean_image(self):
        """Test OCR on clean image with clear text."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        img = create_text_image("Hello World", font_size=30)

        result = engine.ocr_image(img, page_number=1)

        assert result.page_number == 1
        assert result.processing_time_seconds > 0
        # Text may vary slightly based on font, but should contain words
        # Using case-insensitive check for robustness
        assert "hello" in result.text.lower() or "world" in result.text.lower()

    def test_ocr_returns_confidence(self):
        """Test that OCR returns confidence score."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        img = create_text_image("Test Document", font_size=30)

        result = engine.ocr_image(img)

        # Confidence should be between 0-100
        assert 0 <= result.confidence <= 100

    def test_ocr_multiple_pages(self):
        """Test OCR on multiple pages."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        images = [
            create_text_image("Page One", font_size=30),
            create_text_image("Page Two", font_size=30),
            create_text_image("Page Three", font_size=30)
        ]

        result = engine.ocr_images(images, start_page=1)

        assert len(result.pages) == 3
        assert result.pages[0].page_number == 1
        assert result.pages[1].page_number == 2
        assert result.pages[2].page_number == 3
        assert result.total_processing_time_seconds > 0

    def test_ocr_empty_image(self):
        """Test OCR on blank image."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        blank = Image.new("RGB", (200, 100), "white")

        result = engine.ocr_image(blank)

        # Should return empty or minimal text, no error
        assert result.error is None

    def test_ocr_with_preprocessing(self):
        """Test OCR with preprocessing enabled."""
        from src.ocr_engine import OCREngine

        engine = OCREngine()
        img = create_text_image("Preprocessing Test", font_size=25)

        result_with = engine.ocr_image(img, preprocess=True)
        result_without = engine.ocr_image(img, preprocess=False)

        # Both should complete without error
        assert result_with.error is None
        assert result_without.error is None


class TestOCRWithoutTesseract:
    """Test OCR engine behavior when Tesseract is not available."""

    def test_ocr_without_tesseract_returns_error(self):
        """Test that OCR returns error when Tesseract unavailable."""
        from src.ocr_engine import OCREngine, TESSERACT_AVAILABLE

        if TESSERACT_AVAILABLE:
            pytest.skip("Tesseract is available")

        engine = OCREngine()
        img = create_text_image("Test")

        result = engine.ocr_image(img)

        assert result.error is not None
        assert "not available" in result.error.lower()


class TestOCRResult:
    """Test OCRResult dataclass."""

    def test_ocr_result_creation(self):
        """Test OCRResult creation."""
        from src.ocr_engine import OCRResult

        result = OCRResult(
            page_number=1,
            text="Sample text",
            confidence=95.5,
            processing_time_seconds=1.5
        )

        assert result.page_number == 1
        assert result.text == "Sample text"
        assert result.confidence == 95.5
        assert result.processing_time_seconds == 1.5
        assert result.error is None

    def test_ocr_result_with_error(self):
        """Test OCRResult with error."""
        from src.ocr_engine import OCRResult

        result = OCRResult(
            page_number=1,
            text="",
            confidence=0.0,
            processing_time_seconds=0.5,
            error="OCR failed"
        )

        assert result.error == "OCR failed"


class TestOCRBatchResult:
    """Test OCRBatchResult dataclass."""

    def test_ocr_batch_result_creation(self):
        """Test OCRBatchResult creation."""
        from src.ocr_engine import OCRResult, OCRBatchResult

        pages = [
            OCRResult(page_number=1, text="Page 1", confidence=90.0, processing_time_seconds=1.0),
            OCRResult(page_number=2, text="Page 2", confidence=85.0, processing_time_seconds=1.2)
        ]

        result = OCRBatchResult(
            pages=pages,
            total_text="Page 1\n\nPage 2",
            average_confidence=87.5,
            total_processing_time_seconds=2.2
        )

        assert len(result.pages) == 2
        assert result.average_confidence == 87.5
        assert result.total_processing_time_seconds == 2.2


class TestOCREngineSingleton:
    """Test singleton pattern."""

    def test_get_ocr_engine(self):
        """Test singleton returns same instance."""
        from src.ocr_engine import get_ocr_engine

        engine1 = get_ocr_engine()
        engine2 = get_ocr_engine()

        assert engine1 is engine2

    def test_engine_uses_settings(self):
        """Test engine uses configuration settings."""
        from src.ocr_engine import OCREngine
        from app.config import get_settings

        settings = get_settings()
        engine = OCREngine()

        assert engine._language == settings.ocr.language
        assert engine._timeout == settings.ocr.timeout_per_page_seconds


class TestPageContentUpdate:
    """Test updating PageContent with OCR results."""

    @pytest.mark.skipif(not tesseract_available(), reason="Tesseract not installed")
    def test_update_page_content(self):
        """Test updating PageContent with OCR."""
        from src.ocr_engine import OCREngine
        from app.models import PageContent

        engine = OCREngine()

        pages = [
            PageContent(page_number=1, text="", is_scanned=True),
            PageContent(page_number=2, text="", is_scanned=True)
        ]

        images = [
            (1, create_text_image("Page 1 OCR", font_size=30)),
            (2, create_text_image("Page 2 OCR", font_size=30))
        ]

        updated = engine.update_page_content(pages, images)

        # Pages should have text now
        assert len(updated) == 2
        # At least one page should have some text
        has_text = any(p.text for p in updated)
        assert has_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
