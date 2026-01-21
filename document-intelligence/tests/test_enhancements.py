"""
Tests for security and reliability enhancements.
- TTL cleanup
- File validation wiring
- QA fallback behavior
- Rate limiting
- Path sanitization
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestDocumentStoreTTLCleanup:
    """Test TTL-based document cleanup."""

    def test_cleanup_expired_documents(self):
        """Test that expired documents are cleaned up."""
        from src.document_store import DocumentStore, reset_document_store

        # Reset global store to avoid interference
        reset_document_store()

        # Create store with very short TTL (0 = immediate expiration)
        store = DocumentStore(ttl_minutes=0, max_documents=10)

        # Create a document
        doc_id = store.create_document(
            filename="test.pdf",
            file_size_bytes=1000,
            file_type=".pdf"
        )

        # Document should exist immediately after creation
        assert store.document_exists(doc_id)

        # Run cleanup - with TTL=0, document should be considered expired
        removed = store.cleanup_expired()

        # Verify document was removed
        assert removed == 1, f"Expected 1 removed, got {removed}"
        assert not store.document_exists(doc_id)

        # Reset global store after test
        reset_document_store()

    def test_eviction_when_over_capacity(self):
        """Test LRU eviction when max documents exceeded."""
        from src.document_store import DocumentStore

        store = DocumentStore(ttl_minutes=60, max_documents=2)

        # Create 2 documents
        doc_id1 = store.create_document("test1.pdf", 1000, ".pdf")
        doc_id2 = store.create_document("test2.pdf", 1000, ".pdf")

        assert store.document_exists(doc_id1)
        assert store.document_exists(doc_id2)

        # Create a 3rd document - should evict the oldest
        doc_id3 = store.create_document("test3.pdf", 1000, ".pdf")

        assert not store.document_exists(doc_id1)  # Evicted
        assert store.document_exists(doc_id2)
        assert store.document_exists(doc_id3)


class TestFileValidation:
    """Test file validation logic."""

    def test_validate_unsupported_format(self):
        """Test rejection of unsupported file formats."""
        from src.document_loader import get_document_loader

        loader = get_document_loader()

        # Test unsupported format
        validation = loader.validate_file(b"fake content", "test.exe")
        assert not validation.is_valid
        assert "Unsupported file format" in validation.error_message

    def test_validate_oversized_file(self):
        """Test rejection of files exceeding size limit."""
        from src.document_loader import get_document_loader
        from app.config import get_settings

        loader = get_document_loader()
        settings = get_settings()

        # Create content larger than max size
        max_bytes = settings.document.max_file_size_mb * 1024 * 1024
        oversized = b"x" * (max_bytes + 1000)

        validation = loader.validate_file(oversized, "test.pdf")
        assert not validation.is_valid
        assert "exceeds maximum" in validation.error_message.lower()

    def test_validate_valid_image(self):
        """Test validation of valid image file."""
        from src.document_loader import get_document_loader
        from PIL import Image
        import io

        loader = get_document_loader()

        # Create a small valid PNG
        img = Image.new('RGB', (10, 10), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()

        validation = loader.validate_file(png_bytes, "test.png")
        assert validation.is_valid
        assert validation.page_count == 1


class TestQAFallback:
    """Test QA engine fallback behavior."""

    def test_answer_validates_empty_question(self):
        """Test that empty questions raise ValueError."""
        from src.qa_engine import get_qa_engine
        from src.document_store import get_document_store

        qa_engine = get_qa_engine()
        store = get_document_store()

        # Create a document first
        doc_id = store.create_document("test.pdf", 1000, ".pdf")

        with pytest.raises(ValueError, match="Question cannot be empty"):
            qa_engine.answer(doc_id, "   ")

        # Cleanup
        store.delete_document(doc_id)

    def test_answer_validates_missing_document(self):
        """Test that missing doc_id raises ValueError."""
        from src.qa_engine import get_qa_engine

        qa_engine = get_qa_engine()

        with pytest.raises(ValueError, match="not found"):
            qa_engine.answer("nonexistent_doc", "What is this?")

    def test_lexical_fallback_finds_relevant_chunks(self):
        """Test lexical fallback when vector search fails."""
        from src.qa_engine import QAEngine
        from src.document_store import get_document_store
        from app.models import TextChunk, DocumentStatus

        store = get_document_store()

        # Create a document with chunks
        doc_id = store.create_document("test.pdf", 1000, ".pdf")
        doc = store.get_document(doc_id)
        doc.chunks = [
            TextChunk(chunk_id="c1", text="The invoice total is $500.", page_number=1),
            TextChunk(chunk_id="c2", text="Payment is due by December 31st.", page_number=2),
            TextChunk(chunk_id="c3", text="Contact us at support@example.com.", page_number=3),
        ]
        doc.status = DocumentStatus.COMPLETED
        store.update_document(doc_id, doc)

        # Test lexical fallback
        qa_engine = QAEngine()
        chunks = qa_engine._lexical_fallback(doc_id, "What is the total?")

        assert len(chunks) > 0
        # Should find the chunk with "total"
        texts = [c["text"] for c in chunks]
        assert any("total" in t.lower() for t in texts)

        # Cleanup
        store.delete_document(doc_id)


class TestPathSanitization:
    """Test path sanitization for exports."""

    def test_sanitize_removes_directory_traversal(self):
        """Test that directory traversal is removed."""
        from src.exporter import sanitize_filename

        # Various path traversal attempts - should extract just the filename
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("..\\..\\windows\\system32") == "system32"
        assert sanitize_filename("/etc/passwd") == "passwd"
        assert sanitize_filename("C:\\Users\\Admin\\file.pdf") == "file.pdf"

    def test_sanitize_removes_special_characters(self):
        """Test that special characters are replaced."""
        from src.exporter import sanitize_filename

        result = sanitize_filename("file<>:*?|name.pdf")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result
        assert "|" not in result

    def test_sanitize_handles_hidden_files(self):
        """Test that leading dots are removed."""
        from src.exporter import sanitize_filename

        result = sanitize_filename(".hidden")
        assert not result.startswith(".")
        assert result == "hidden"

        result2 = sanitize_filename("..secret")
        assert not result2.startswith(".")
        assert result2 == "secret"

    def test_sanitize_handles_empty(self):
        """Test handling of empty filename."""
        from src.exporter import sanitize_filename

        result = sanitize_filename("")
        assert len(result) > 0


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiter_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        # Import after path setup
        sys.path.insert(0, str(PROJECT_ROOT / "app"))

        from app.main import RateLimiter

        limiter = RateLimiter(requests_per_minute=10)

        # Should allow 10 requests
        for i in range(10):
            assert limiter.is_allowed("client1")

    def test_rate_limiter_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        from app.main import RateLimiter

        limiter = RateLimiter(requests_per_minute=5)

        # Use all allowed requests
        for i in range(5):
            assert limiter.is_allowed("client1")

        # Next request should be blocked
        assert not limiter.is_allowed("client1")

    def test_rate_limiter_per_client(self):
        """Test that rate limits are per-client."""
        from app.main import RateLimiter

        limiter = RateLimiter(requests_per_minute=3)

        # Client 1 uses all requests
        for i in range(3):
            assert limiter.is_allowed("client1")
        assert not limiter.is_allowed("client1")

        # Client 2 should still be allowed
        assert limiter.is_allowed("client2")


class TestHealthCheck:
    """Test enhanced health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_checks(self):
        """Test that health check includes dependency status."""
        from app.main import health_check

        result = await health_check()

        assert "status" in result
        assert "checks" in result
        assert "timestamp" in result
        assert "version" in result

        # Check that dependency checks are included
        checks = result["checks"]
        assert "tesseract" in checks
        assert "spacy" in checks
        assert "chromadb" in checks
        assert "openrouter_api_key" in checks
