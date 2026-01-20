"""
OCR Engine Module

Provides OCR functionality using Tesseract with image preprocessing.
- Image preprocessing (deskew, denoise, contrast enhancement)
- Tesseract OCR with confidence scores
- Multi-page handling with page tracking
- Timeout handling per page
"""

import logging
import signal
from dataclasses import dataclass
from typing import Optional
import concurrent.futures

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from app.config import get_settings
from app.models import PageContent

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result of OCR processing for a single page."""
    page_number: int
    text: str
    confidence: float  # 0-100
    processing_time_seconds: float
    error: Optional[str] = None


@dataclass
class OCRBatchResult:
    """Result of OCR processing for multiple pages."""
    pages: list[OCRResult]
    total_text: str
    average_confidence: float
    total_processing_time_seconds: float


class TimeoutError(Exception):
    """Raised when OCR processing times out."""
    pass


class OCREngine:
    """
    OCR engine using Tesseract with image preprocessing.
    """

    def __init__(self):
        self.settings = get_settings()
        self._language = self.settings.ocr.language
        self._timeout = self.settings.ocr.timeout_per_page_seconds
        self._confidence_threshold = self.settings.ocr.confidence_threshold
        self._preprocessing = self.settings.ocr.preprocessing

        # Check Tesseract availability
        if not TESSERACT_AVAILABLE:
            logger.warning("pytesseract not installed. OCR will not work.")
        elif not self._check_tesseract_installed():
            logger.warning("Tesseract binary not found. OCR will not work.")

    def _check_tesseract_installed(self) -> bool:
        """Check if Tesseract is installed and accessible."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    # =========================================================================
    # Image Preprocessing
    # =========================================================================

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Apply preprocessing to improve OCR accuracy.

        Steps:
        1. Convert to grayscale
        2. Deskew (straighten rotated images)
        3. Denoise
        4. Enhance contrast
        5. Binarization (optional)
        """
        if not self._preprocessing.get("enabled", True):
            return image

        # Convert to grayscale if needed
        if image.mode != "L":
            image = image.convert("L")

        # Apply deskew if enabled and cv2 available
        if self._preprocessing.get("deskew", True) and CV2_AVAILABLE:
            image = self._deskew_image(image)

        # Apply denoising if enabled
        if self._preprocessing.get("denoise", True):
            image = self._denoise_image(image)

        # Enhance contrast if enabled
        if self._preprocessing.get("enhance_contrast", True):
            image = self._enhance_contrast(image)

        return image

    def _deskew_image(self, image: Image.Image) -> Image.Image:
        """Deskew (straighten) a rotated image."""
        if not CV2_AVAILABLE:
            return image

        try:
            # Convert to numpy array
            img_array = np.array(image)

            # Find all non-white pixels
            coords = np.column_stack(np.where(img_array < 250))

            if len(coords) < 10:
                return image

            # Calculate rotation angle
            angle = cv2.minAreaRect(coords)[-1]

            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90

            # Only deskew if angle is significant but not too large
            if abs(angle) > 0.5 and abs(angle) < 15:
                (h, w) = img_array.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    img_array, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return Image.fromarray(rotated)

        except Exception as e:
            logger.debug(f"Deskew failed: {e}")

        return image

    def _denoise_image(self, image: Image.Image) -> Image.Image:
        """Apply denoising to image."""
        try:
            # Use PIL's median filter for basic denoising
            image = image.filter(ImageFilter.MedianFilter(size=3))
        except Exception as e:
            logger.debug(f"Denoise failed: {e}")
        return image

    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast for better OCR."""
        try:
            # Auto-contrast
            image = ImageOps.autocontrast(image, cutoff=2)

            # Additional contrast enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

        except Exception as e:
            logger.debug(f"Contrast enhancement failed: {e}")

        return image

    def _binarize_image(self, image: Image.Image, threshold: int = 150) -> Image.Image:
        """Convert image to binary (black and white)."""
        return image.point(lambda x: 0 if x < threshold else 255, "1")

    # =========================================================================
    # OCR Processing
    # =========================================================================

    def ocr_image(
        self,
        image: Image.Image,
        page_number: int = 1,
        preprocess: bool = True
    ) -> OCRResult:
        """
        Perform OCR on a single image.

        Args:
            image: PIL Image to process
            page_number: Page number for tracking
            preprocess: Whether to apply preprocessing

        Returns:
            OCRResult with extracted text and confidence
        """
        import time
        start_time = time.time()

        if not TESSERACT_AVAILABLE:
            return OCRResult(
                page_number=page_number,
                text="",
                confidence=0.0,
                processing_time_seconds=0.0,
                error="Tesseract not available"
            )

        try:
            # Apply preprocessing
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image

            # Run OCR with timeout
            result = self._run_ocr_with_timeout(processed_image)

            processing_time = time.time() - start_time

            return OCRResult(
                page_number=page_number,
                text=result["text"],
                confidence=result["confidence"],
                processing_time_seconds=processing_time
            )

        except TimeoutError:
            processing_time = time.time() - start_time
            return OCRResult(
                page_number=page_number,
                text="",
                confidence=0.0,
                processing_time_seconds=processing_time,
                error=f"OCR timed out after {self._timeout} seconds"
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OCR error on page {page_number}: {e}")
            return OCRResult(
                page_number=page_number,
                text="",
                confidence=0.0,
                processing_time_seconds=processing_time,
                error=str(e)
            )

    def _run_ocr_with_timeout(self, image: Image.Image) -> dict:
        """Run Tesseract OCR with timeout protection."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._extract_text_and_confidence, image)
            try:
                return future.result(timeout=self._timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"OCR timed out after {self._timeout} seconds")

    def _extract_text_and_confidence(self, image: Image.Image) -> dict:
        """Extract text and confidence from image using Tesseract."""
        # Get detailed data including confidence
        data = pytesseract.image_to_data(
            image,
            lang=self._language,
            output_type=pytesseract.Output.DICT
        )

        # Extract text
        text = pytesseract.image_to_string(image, lang=self._language)

        # Calculate average confidence
        confidences = [
            int(conf) for conf in data["conf"]
            if conf != "-1" and str(conf).isdigit()
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "text": text.strip(),
            "confidence": avg_confidence
        }

    def ocr_images(
        self,
        images: list[Image.Image],
        start_page: int = 1,
        preprocess: bool = True
    ) -> OCRBatchResult:
        """
        Perform OCR on multiple images.

        Args:
            images: List of PIL Images to process
            start_page: Starting page number
            preprocess: Whether to apply preprocessing

        Returns:
            OCRBatchResult with all page results
        """
        results = []

        for i, image in enumerate(images):
            page_num = start_page + i
            logger.info(f"Processing page {page_num}/{start_page + len(images) - 1}")

            result = self.ocr_image(image, page_num, preprocess)
            results.append(result)

        # Combine results
        all_text = "\n\n".join(r.text for r in results if r.text)

        valid_confidences = [r.confidence for r in results if r.confidence > 0]
        avg_confidence = (
            sum(valid_confidences) / len(valid_confidences)
            if valid_confidences else 0.0
        )

        total_time = sum(r.processing_time_seconds for r in results)

        return OCRBatchResult(
            pages=results,
            total_text=all_text,
            average_confidence=avg_confidence,
            total_processing_time_seconds=total_time
        )

    def update_page_content(
        self,
        pages: list[PageContent],
        images: list[tuple[int, Image.Image]]
    ) -> list[PageContent]:
        """
        Update PageContent objects with OCR results.

        Args:
            pages: List of PageContent to update
            images: List of (page_number, image) tuples for OCR

        Returns:
            Updated list of PageContent
        """
        # Create lookup for page numbers that need OCR
        page_to_image = {page_num: img for page_num, img in images}

        for page in pages:
            if page.page_number in page_to_image:
                image = page_to_image[page.page_number]
                result = self.ocr_image(image, page.page_number)

                # Only update if OCR was successful and page had no/little text
                if result.text and (not page.text or len(page.text) < 50):
                    page.text = result.text
                    page.ocr_confidence = result.confidence
                    page.is_scanned = True

        return pages


# Singleton instance
_ocr_engine: Optional[OCREngine] = None


def get_ocr_engine() -> OCREngine:
    """Get or create OCR engine instance."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine
