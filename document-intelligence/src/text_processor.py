"""
Text Processor Module

Handles text cleaning, normalization, structure detection, and chunking.
- Clean OCR artifacts and normalize whitespace
- Detect document structure (headers, paragraphs, lists)
- Sentence boundary detection
- Chunk text with overlap for RAG
- Track page numbers through chunks
"""

import re
import uuid
import logging
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings
from app.models import TextChunk, PageContent

logger = logging.getLogger(__name__)

# Try to import spaCy for sentence detection
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Using basic sentence splitting.")


@dataclass
class ProcessedText:
    """Result of text processing."""
    cleaned_text: str
    chunks: list[TextChunk]
    word_count: int
    sentence_count: int
    structure: dict  # Document structure analysis


class TextProcessor:
    """
    Processes raw text for document intelligence pipeline.
    """

    def __init__(self):
        self.settings = get_settings()
        self._chunk_size = self.settings.text_processing.chunk_size
        self._chunk_overlap = self.settings.text_processing.chunk_overlap
        self._min_chunk_size = self.settings.text_processing.min_chunk_size

        # Load spaCy model for sentence detection
        self._nlp = None
        if SPACY_AVAILABLE:
            self._load_spacy_model()

    def _load_spacy_model(self) -> None:
        """Load spaCy model for NLP tasks."""
        try:
            model_name = self.settings.entity_extraction.spacy_model
            self._nlp = spacy.load(model_name, disable=["ner", "lemmatizer"])
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            # Try loading a smaller model
            try:
                self._nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
                logger.info("Loaded fallback spaCy model: en_core_web_sm")
            except OSError:
                logger.warning("No spaCy model available. Using basic sentence splitting.")
                self._nlp = None

    # =========================================================================
    # Text Cleaning
    # =========================================================================

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Operations:
        - Remove OCR artifacts
        - Normalize whitespace
        - Fix common OCR errors
        - Handle special characters
        - Normalize unicode
        """
        if not text:
            return ""

        # Normalize unicode
        import unicodedata
        text = unicodedata.normalize("NFKC", text)

        # Remove null bytes and control characters (except newlines and tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Fix common OCR artifacts
        text = self._fix_ocr_artifacts(text)

        # Normalize whitespace
        text = self._normalize_whitespace(text)

        # Remove excessive blank lines
        text = re.sub(r"\n{4,}", "\n\n\n", text)

        return text.strip()

    def _fix_ocr_artifacts(self, text: str) -> str:
        """Fix common OCR errors and artifacts."""
        # Common character substitutions
        replacements = {
            "ﬁ": "fi",
            "ﬂ": "fl",
            "ﬀ": "ff",
            "ﬃ": "ffi",
            "ﬄ": "ffl",
            "—": "-",
            "–": "-",
            "'": "'",
            "'": "'",
            """: '"',
            """: '"',
            "…": "...",
            "\u00a0": " ",  # Non-breaking space
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Fix common OCR misreads
        # l/I/1 confusion at word boundaries
        text = re.sub(r"\bl\b", "I", text)  # Standalone l -> I

        # Remove isolated single characters that are likely noise
        text = re.sub(r"(?<!\w)[^a-zA-Z0-9\s.,;:!?'\"()-](?!\w)", "", text)

        # Fix spacing around punctuation
        text = re.sub(r"\s+([.,;:!?])", r"\1", text)
        text = re.sub(r"([.,;:!?])(?=[a-zA-Z])", r"\1 ", text)

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Normalize multiple spaces to single
        text = re.sub(r" {2,}", " ", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove trailing whitespace from lines
        text = "\n".join(line.rstrip() for line in text.split("\n"))

        return text

    # =========================================================================
    # Structure Detection
    # =========================================================================

    def detect_structure(self, text: str) -> dict:
        """
        Detect document structure (headers, paragraphs, lists).

        Returns dict with:
        - headers: List of detected headers
        - paragraphs: List of paragraph boundaries
        - lists: List of detected lists
        - sections: High-level section breakdown
        """
        lines = text.split("\n")

        structure = {
            "headers": [],
            "paragraphs": [],
            "lists": [],
            "sections": []
        }

        current_section = None
        current_paragraph_start = 0
        in_list = False
        list_start = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                # End of paragraph
                if current_paragraph_start < i:
                    structure["paragraphs"].append({
                        "start_line": current_paragraph_start,
                        "end_line": i - 1
                    })
                current_paragraph_start = i + 1

                # End list if in one
                if in_list:
                    structure["lists"].append({
                        "start_line": list_start,
                        "end_line": i - 1
                    })
                    in_list = False
                continue

            # Detect headers (all caps, short, or ending with colon)
            if self._is_header(stripped):
                structure["headers"].append({
                    "line": i,
                    "text": stripped,
                    "level": self._get_header_level(stripped)
                })

                if current_section:
                    current_section["end_line"] = i - 1
                    structure["sections"].append(current_section)

                current_section = {
                    "title": stripped,
                    "start_line": i,
                    "end_line": None
                }

            # Detect list items
            if self._is_list_item(stripped):
                if not in_list:
                    in_list = True
                    list_start = i

        # Close final paragraph
        if current_paragraph_start < len(lines):
            structure["paragraphs"].append({
                "start_line": current_paragraph_start,
                "end_line": len(lines) - 1
            })

        # Close final section
        if current_section:
            current_section["end_line"] = len(lines) - 1
            structure["sections"].append(current_section)

        return structure

    def _is_header(self, line: str) -> bool:
        """Check if line is a header."""
        # Short lines in ALL CAPS
        if len(line) < 60 and line.isupper() and len(line.split()) <= 8:
            return True

        # Lines ending with colon (common header pattern)
        if len(line) < 50 and line.endswith(":") and not line.startswith(" "):
            return True

        # Numbered sections (1. Introduction, 2.1 Methods)
        if re.match(r"^\d+\.?\d*\s+[A-Z]", line):
            return True

        return False

    def _get_header_level(self, header: str) -> int:
        """Determine header level (1-3)."""
        # Main headers: ALL CAPS or numbered without decimal
        if header.isupper() or re.match(r"^\d+\s+", header):
            return 1

        # Sub-headers: Decimal numbered (2.1, 3.2.1)
        if re.match(r"^\d+\.\d+", header):
            return 2

        return 3

    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item."""
        patterns = [
            r"^[-•*]\s+",  # Bullet points
            r"^\d+[.)]\s+",  # Numbered lists
            r"^[a-z][.)]\s+",  # Lettered lists
            r"^[ivxIVX]+[.)]\s+",  # Roman numerals
        ]
        return any(re.match(p, line) for p in patterns)

    # =========================================================================
    # Sentence Detection
    # =========================================================================

    def detect_sentences(self, text: str) -> list[str]:
        """
        Detect sentence boundaries in text.
        Uses spaCy if available, otherwise basic regex.
        """
        if not text.strip():
            return []

        if self._nlp:
            return self._spacy_sentence_detect(text)
        return self._basic_sentence_detect(text)

    def _spacy_sentence_detect(self, text: str) -> list[str]:
        """Use spaCy for sentence detection."""
        # Process in chunks to handle large texts
        max_length = 100000
        sentences = []

        for i in range(0, len(text), max_length):
            chunk = text[i:i + max_length]
            doc = self._nlp(chunk)
            sentences.extend([sent.text.strip() for sent in doc.sents])

        return sentences

    def _basic_sentence_detect(self, text: str) -> list[str]:
        """Basic regex-based sentence detection."""
        # Split on sentence-ending punctuation followed by space and capital
        pattern = r"(?<=[.!?])\s+(?=[A-Z])"
        raw_sentences = re.split(pattern, text)

        # Clean up
        sentences = []
        for sent in raw_sentences:
            sent = sent.strip()
            if sent:
                sentences.append(sent)

        return sentences

    # =========================================================================
    # Text Chunking
    # =========================================================================

    def chunk_text(
        self,
        text: str,
        page_contents: Optional[list[PageContent]] = None,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> list[TextChunk]:
        """
        Split text into overlapping chunks for vector storage.

        Args:
            text: Text to chunk
            page_contents: Optional page info for tracking page numbers
            chunk_size: Override default chunk size
            overlap: Override default overlap

        Returns:
            List of TextChunk objects
        """
        if not text.strip():
            return []

        chunk_size = chunk_size or self._chunk_size
        overlap = overlap or self._chunk_overlap

        # Build page position map if available
        page_map = self._build_page_map(page_contents) if page_contents else {}

        # Try sentence-aware chunking
        sentences = self.detect_sentences(text)

        if sentences:
            chunks = self._chunk_by_sentences(
                sentences, text, chunk_size, overlap, page_map
            )
        else:
            chunks = self._chunk_by_characters(
                text, chunk_size, overlap, page_map
            )

        return chunks

    def _build_page_map(self, pages: list[PageContent]) -> dict:
        """Build mapping of character positions to page numbers."""
        page_map = {}
        current_pos = 0

        for page in pages:
            if page.text:
                page_map[current_pos] = page.page_number
                current_pos += len(page.text) + 2  # +2 for paragraph separator

        return page_map

    def _get_page_for_position(self, position: int, page_map: dict) -> Optional[int]:
        """Get page number for character position."""
        if not page_map:
            return None

        for pos, page_num in sorted(page_map.items(), reverse=True):
            if position >= pos:
                return page_num

        return list(page_map.values())[0] if page_map else None

    def _chunk_by_sentences(
        self,
        sentences: list[str],
        full_text: str,
        chunk_size: int,
        overlap: int,
        page_map: dict
    ) -> list[TextChunk]:
        """Create chunks based on sentence boundaries."""
        chunks = []
        current_chunk = []
        current_size = 0
        current_position = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # If single sentence exceeds chunk size, split it
            if sentence_len > chunk_size:
                # First, finalize current chunk
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, current_position, page_map, len(chunks)
                    ))
                    current_chunk = []
                    current_size = 0

                # Split long sentence by characters
                for sub_chunk in self._split_long_text(sentence, chunk_size, overlap):
                    chunks.append(self._create_chunk(
                        sub_chunk, current_position, page_map, len(chunks)
                    ))
                    current_position += len(sub_chunk) - overlap

                continue

            # Check if adding sentence exceeds chunk size
            if current_size + sentence_len + 1 > chunk_size:
                # Finalize current chunk
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk(
                        chunk_text, current_position, page_map, len(chunks)
                    ))

                    # Keep overlap sentences
                    overlap_text = chunk_text[-overlap:] if len(chunk_text) > overlap else chunk_text
                    overlap_sentences = self._get_sentences_for_overlap(
                        current_chunk, overlap
                    )
                    current_chunk = overlap_sentences
                    current_size = sum(len(s) for s in current_chunk)
                    current_position += len(chunk_text) - current_size

            current_chunk.append(sentence)
            current_size += sentence_len + 1

        # Final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self._min_chunk_size:
                chunks.append(self._create_chunk(
                    chunk_text, current_position, page_map, len(chunks)
                ))

        return chunks

    def _get_sentences_for_overlap(
        self,
        sentences: list[str],
        target_overlap: int
    ) -> list[str]:
        """Get sentences from end that fit within overlap size."""
        result = []
        total_len = 0

        for sentence in reversed(sentences):
            if total_len + len(sentence) <= target_overlap:
                result.insert(0, sentence)
                total_len += len(sentence) + 1
            else:
                break

        return result

    def _chunk_by_characters(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
        page_map: dict
    ) -> list[TextChunk]:
        """Create chunks by character position with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at word boundary
            if end < len(text):
                # Look for space near end
                space_pos = text.rfind(" ", start + chunk_size - 50, end)
                if space_pos > start:
                    end = space_pos

            chunk_text = text[start:end].strip()

            if len(chunk_text) >= self._min_chunk_size:
                chunks.append(self._create_chunk(
                    chunk_text, start, page_map, len(chunks)
                ))

            start = end - overlap

        return chunks

    def _split_long_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> list[str]:
        """Split long text into chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            # Try to break at word boundary
            if end < len(text):
                space_pos = text.rfind(" ", start + chunk_size - 50, end)
                if space_pos > start:
                    end = space_pos

            chunks.append(text[start:end].strip())
            start = end - overlap

        return chunks

    def _create_chunk(
        self,
        text: str,
        position: int,
        page_map: dict,
        chunk_index: int
    ) -> TextChunk:
        """Create a TextChunk object."""
        return TextChunk(
            chunk_id=f"chunk_{chunk_index:04d}_{uuid.uuid4().hex[:8]}",
            text=text,
            page_number=self._get_page_for_position(position, page_map),
            start_char=position,
            end_char=position + len(text),
            metadata={
                "chunk_index": chunk_index,
                "char_count": len(text),
                "word_count": len(text.split())
            }
        )

    # =========================================================================
    # Main Processing
    # =========================================================================

    def process(
        self,
        text: str,
        pages: Optional[list[PageContent]] = None
    ) -> ProcessedText:
        """
        Full text processing pipeline.

        Args:
            text: Raw text to process
            pages: Optional page content for page tracking

        Returns:
            ProcessedText with cleaned text, chunks, and structure
        """
        # Clean text
        cleaned = self.clean_text(text)

        # Detect structure
        structure = self.detect_structure(cleaned)

        # Detect sentences
        sentences = self.detect_sentences(cleaned)

        # Create chunks
        chunks = self.chunk_text(cleaned, pages)

        return ProcessedText(
            cleaned_text=cleaned,
            chunks=chunks,
            word_count=len(cleaned.split()),
            sentence_count=len(sentences),
            structure=structure
        )


# Singleton instance
_text_processor: Optional[TextProcessor] = None


def get_text_processor() -> TextProcessor:
    """Get or create text processor instance."""
    global _text_processor
    if _text_processor is None:
        _text_processor = TextProcessor()
    return _text_processor
