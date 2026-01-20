"""
Phase 1 Tests: Configuration, Models, and Document Store
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestConfigLoading:
    """Test configuration loading from YAML and environment."""

    def test_settings_load_from_yaml(self):
        """Test that settings load correctly from YAML file."""
        from app.config import Settings, CONFIG_DIR

        settings = Settings.from_yaml()

        # Check basic app config
        assert settings.app.name == "Document Intelligence System"
        assert settings.app.version == "1.0.0"

        # Check document config
        assert settings.document.max_file_size_mb == 25
        assert settings.document.max_pages == 50
        assert ".pdf" in settings.document.supported_formats

        # Check OCR config
        assert settings.ocr.engine == "tesseract"
        assert settings.ocr.dpi == 300

        # Check LLM config
        assert settings.llm.provider == "openrouter"
        assert "anthropic/claude" in settings.llm.primary_model

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        from app.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Should be same instance (cached)
        assert settings1 is settings2

    def test_prompts_loading(self):
        """Test that prompts load correctly from YAML."""
        from app.config import Prompts, CONFIG_DIR

        prompts = Prompts()

        # Check summarization prompts exist
        assert len(prompts.summarization_system) > 0
        assert len(prompts.summarization_user) > 0
        assert "{document_text}" in prompts.summarization_user

        # Check Q&A prompts exist
        assert len(prompts.qa_system) > 0
        assert len(prompts.qa_user) > 0
        assert "{context}" in prompts.qa_user
        assert "{question}" in prompts.qa_user

    def test_prompts_formatting(self):
        """Test prompt formatting with parameters."""
        from app.config import get_prompts

        prompts = get_prompts()

        # Test summarization prompt formatting
        system, user = prompts.format_summarization_prompt(
            document_text="Test document content",
            min_points=3,
            max_points=5
        )

        assert "Test document content" in user
        assert "3" in user
        assert "5" in user

        # Test Q&A prompt formatting
        system, user = prompts.format_qa_prompt(
            context="Sample context",
            question="What is this about?",
            conversation_history="Previous message"
        )

        assert "Sample context" in user
        assert "What is this about?" in user
        assert "Previous message" in user

    def test_document_type_patterns(self):
        """Test document type classification patterns."""
        from app.config import get_prompts

        prompts = get_prompts()
        patterns = prompts.document_type_patterns

        assert "invoice" in patterns
        assert "contract" in patterns
        assert "receipt" in patterns
        assert "invoice" in patterns["invoice"]


class TestModels:
    """Test Pydantic models validation."""

    def test_extracted_entity_validation(self):
        """Test ExtractedEntity model validation."""
        from app.models import ExtractedEntity, EntityType

        entity = ExtractedEntity(
            entity_type=EntityType.PERSON,
            value="John Doe",
            confidence=0.95
        )

        assert entity.entity_type == EntityType.PERSON
        assert entity.value == "John Doe"
        assert entity.confidence == 0.95

    def test_extracted_entity_confidence_bounds(self):
        """Test confidence score bounds."""
        from app.models import ExtractedEntity, EntityType

        # Valid confidence
        entity = ExtractedEntity(
            entity_type=EntityType.DATE,
            value="2024-01-15",
            confidence=0.5
        )
        assert entity.confidence == 0.5

        # Confidence should be rounded
        entity = ExtractedEntity(
            entity_type=EntityType.DATE,
            value="2024-01-15",
            confidence=0.12345
        )
        assert entity.confidence == 0.123

    def test_amount_entity(self):
        """Test AmountEntity model."""
        from app.models import AmountEntity, EntityType

        amount = AmountEntity(
            value="15,000.00",
            numeric_value=15000.00,
            currency="INR",
            confidence=0.98
        )

        assert amount.entity_type == EntityType.AMOUNT
        assert amount.numeric_value == 15000.00
        assert amount.currency == "INR"

    def test_date_entity(self):
        """Test DateEntity model."""
        from app.models import DateEntity, EntityType
        from datetime import datetime

        date = DateEntity(
            value="January 15, 2024",
            parsed_date=datetime(2024, 1, 15),
            confidence=0.92
        )

        assert date.entity_type == EntityType.DATE
        assert date.parsed_date.year == 2024
        assert date.parsed_date.month == 1

    def test_extracted_entities_collection(self):
        """Test ExtractedEntities collection."""
        from app.models import (
            ExtractedEntities, ExtractedEntity, AmountEntity,
            DateEntity, EntityType
        )

        entities = ExtractedEntities(
            dates=[
                DateEntity(value="2024-01-15", confidence=0.9)
            ],
            amounts=[
                AmountEntity(value="1000", numeric_value=1000, currency="USD", confidence=0.95)
            ],
            persons=[
                ExtractedEntity(entity_type=EntityType.PERSON, value="John", confidence=0.8)
            ],
            organizations=[
                ExtractedEntity(entity_type=EntityType.ORGANIZATION, value="Acme", confidence=0.85)
            ]
        )

        assert entities.total_count == 4

        flat = entities.to_flat_list()
        assert len(flat) == 4

    def test_document_status_enum(self):
        """Test DocumentStatus enum values."""
        from app.models import DocumentStatus

        assert DocumentStatus.PENDING.value == "pending"
        assert DocumentStatus.PROCESSING.value == "processing"
        assert DocumentStatus.COMPLETED.value == "completed"
        assert DocumentStatus.FAILED.value == "failed"

    def test_document_type_enum(self):
        """Test DocumentType enum values."""
        from app.models import DocumentType

        assert DocumentType.INVOICE.value == "invoice"
        assert DocumentType.CONTRACT.value == "contract"
        assert DocumentType.UNKNOWN.value == "unknown"

    def test_text_chunk_model(self):
        """Test TextChunk model."""
        from app.models import TextChunk

        chunk = TextChunk(
            chunk_id="chunk_001",
            text="This is a test chunk of text.",
            page_number=1,
            start_char=0,
            end_char=30,
            metadata={"section": "introduction"}
        )

        assert chunk.chunk_id == "chunk_001"
        assert chunk.page_number == 1
        assert chunk.metadata["section"] == "introduction"

    def test_document_summary_model(self):
        """Test DocumentSummary model."""
        from app.models import DocumentSummary, DocumentType

        summary = DocumentSummary(
            document_type=DocumentType.INVOICE,
            executive_summary="This is a test invoice for services rendered.",
            key_points=[
                "Total amount: $1,000",
                "Due date: Jan 15, 2024",
                "Vendor: Acme Corp"
            ],
            word_count=500,
            page_count=2
        )

        assert summary.document_type == DocumentType.INVOICE
        assert len(summary.key_points) == 3
        assert summary.page_count == 2

    def test_qa_request_validation(self):
        """Test QARequest validation."""
        from app.models import QARequest

        # Valid request
        request = QARequest(
            question="What is the total amount?",
            include_sources=True
        )
        assert request.question == "What is the total amount?"

        # Empty question should fail
        with pytest.raises(ValueError):
            QARequest(question="")

    def test_qa_response_model(self):
        """Test QAResponse model."""
        from app.models import QAResponse, QASource

        response = QAResponse(
            answer="The total amount is $1,000.",
            confidence=0.95,
            sources=[
                QASource(page=1, section="Summary", quote="Total: $1,000")
            ],
            suggested_questions=["What is the due date?"],
            processing_time_ms=150
        )

        assert response.confidence == 0.95
        assert len(response.sources) == 1
        assert len(response.suggested_questions) == 1

    def test_file_validation_helpers(self):
        """Test file validation helper functions."""
        from app.models import validate_file_extension, validate_file_size

        supported = [".pdf", ".png", ".jpg"]

        # Valid extensions
        assert validate_file_extension("test.pdf", supported) is True
        assert validate_file_extension("image.png", supported) is True

        # Invalid extensions
        assert validate_file_extension("test.doc", supported) is False
        assert validate_file_extension("noext", supported) is False

        # File size validation
        assert validate_file_size(10 * 1024 * 1024, 25) is True  # 10MB < 25MB
        assert validate_file_size(30 * 1024 * 1024, 25) is False  # 30MB > 25MB


class TestDocumentStore:
    """Test in-memory document store."""

    def test_create_document(self):
        """Test document creation."""
        from src.document_store import DocumentStore

        store = DocumentStore()

        doc_id = store.create_document(
            filename="test.pdf",
            file_size_bytes=1024,
            file_type=".pdf",
            page_count=5
        )

        assert doc_id is not None
        assert len(doc_id) == 12
        assert store.document_exists(doc_id)

    def test_get_document(self):
        """Test document retrieval."""
        from src.document_store import DocumentStore
        from app.models import DocumentStatus

        store = DocumentStore()

        doc_id = store.create_document(
            filename="test.pdf",
            file_size_bytes=2048,
            file_type=".pdf",
            page_count=3
        )

        doc = store.get_document(doc_id)

        assert doc is not None
        assert doc.metadata.filename == "test.pdf"
        assert doc.metadata.file_size_bytes == 2048
        assert doc.status == DocumentStatus.PENDING

    def test_get_nonexistent_document(self):
        """Test getting non-existent document returns None."""
        from src.document_store import DocumentStore

        store = DocumentStore()
        doc = store.get_document("nonexistent")

        assert doc is None

    def test_update_document(self):
        """Test document update."""
        from src.document_store import DocumentStore
        from app.models import DocumentStatus

        store = DocumentStore()

        doc_id = store.create_document(
            filename="test.pdf",
            file_size_bytes=1024,
            file_type=".pdf"
        )

        # Update raw text
        store.update_raw_text(doc_id, "This is the document text.")

        doc = store.get_document(doc_id)
        assert doc.raw_text == "This is the document text."

        # Update status
        store.set_status(doc_id, DocumentStatus.COMPLETED)

        doc = store.get_document(doc_id)
        assert doc.status == DocumentStatus.COMPLETED

    def test_delete_document(self):
        """Test document deletion."""
        from src.document_store import DocumentStore

        store = DocumentStore()

        doc_id = store.create_document(
            filename="test.pdf",
            file_size_bytes=1024,
            file_type=".pdf"
        )

        assert store.document_exists(doc_id)

        result = store.delete_document(doc_id)

        assert result is True
        assert not store.document_exists(doc_id)

    def test_delete_nonexistent_document(self):
        """Test deleting non-existent document."""
        from src.document_store import DocumentStore

        store = DocumentStore()
        result = store.delete_document("nonexistent")

        assert result is False

    def test_list_documents(self):
        """Test listing all documents."""
        from src.document_store import DocumentStore

        store = DocumentStore()

        doc1 = store.create_document("doc1.pdf", 1024, ".pdf")
        doc2 = store.create_document("doc2.pdf", 2048, ".pdf")

        docs = store.list_documents()

        assert len(docs) == 2
        assert doc1 in docs
        assert doc2 in docs

    def test_update_progress(self):
        """Test progress tracking."""
        from src.document_store import DocumentStore
        from app.models import DocumentStatus

        store = DocumentStore()

        doc_id = store.create_document("test.pdf", 1024, ".pdf")

        store.update_progress(
            doc_id=doc_id,
            status=DocumentStatus.PROCESSING,
            progress_percent=50,
            current_step="Extracting text",
            message="Processing page 5 of 10"
        )

        progress = store.get_progress(doc_id)

        assert progress.status == DocumentStatus.PROCESSING
        assert progress.progress_percent == 50
        assert progress.current_step == "Extracting text"
        assert progress.message == "Processing page 5 of 10"

    def test_conversation_history(self):
        """Test conversation history management."""
        from src.document_store import DocumentStore

        store = DocumentStore()

        doc_id = store.create_document("test.pdf", 1024, ".pdf")

        # Add messages
        store.add_conversation_message(doc_id, "user", "What is the total?")
        store.add_conversation_message(doc_id, "assistant", "The total is $1,000.")

        history = store.get_conversation_history(doc_id)

        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "What is the total?"
        assert history[1].role == "assistant"

        # Clear history
        store.clear_conversation_history(doc_id)
        history = store.get_conversation_history(doc_id)
        assert len(history) == 0

    def test_ttl_expiration(self):
        """Test TTL-based document expiration."""
        from src.document_store import DocumentStore
        from datetime import datetime, timedelta

        # Create store with very short TTL (1 minute)
        store = DocumentStore(ttl_minutes=1)

        doc_id = store.create_document("test.pdf", 1024, ".pdf")

        # Document should exist initially
        assert store.document_exists(doc_id)

        # Manually set last_accessed to past to simulate expiration
        store._documents[doc_id].last_accessed = datetime.utcnow() - timedelta(minutes=2)

        # Cleanup should remove expired document
        removed = store.cleanup_expired()

        assert removed == 1
        assert not store.document_exists(doc_id)

    def test_max_capacity_eviction(self):
        """Test eviction when max capacity is reached."""
        from src.document_store import DocumentStore

        store = DocumentStore(max_documents=2)

        doc1 = store.create_document("doc1.pdf", 1024, ".pdf")
        doc2 = store.create_document("doc2.pdf", 1024, ".pdf")

        # Both should exist
        assert store.document_exists(doc1)
        assert store.document_exists(doc2)

        # Add third document - should evict oldest (doc1)
        doc3 = store.create_document("doc3.pdf", 1024, ".pdf")

        assert not store.document_exists(doc1)  # Evicted
        assert store.document_exists(doc2)
        assert store.document_exists(doc3)

    def test_update_entities(self):
        """Test updating document entities."""
        from src.document_store import DocumentStore
        from app.models import ExtractedEntities, ExtractedEntity, EntityType

        store = DocumentStore()

        doc_id = store.create_document("invoice.pdf", 1024, ".pdf")

        entities = ExtractedEntities(
            persons=[
                ExtractedEntity(
                    entity_type=EntityType.PERSON,
                    value="John Doe",
                    confidence=0.9
                )
            ]
        )

        store.update_entities(doc_id, entities)

        doc = store.get_document(doc_id)
        assert len(doc.entities.persons) == 1
        assert doc.entities.persons[0].value == "John Doe"

    def test_get_stats(self):
        """Test getting store statistics."""
        from src.document_store import DocumentStore

        store = DocumentStore(max_documents=10, ttl_minutes=30)

        store.create_document("doc1.pdf", 1024, ".pdf")
        store.create_document("doc2.pdf", 2048, ".pdf")

        stats = store.get_stats()

        assert stats["total_documents"] == 2
        assert stats["max_documents"] == 10
        assert stats["ttl_minutes"] == 30
        assert len(stats["document_ids"]) == 2

    def test_clear_all(self):
        """Test clearing all documents."""
        from src.document_store import DocumentStore

        store = DocumentStore()

        store.create_document("doc1.pdf", 1024, ".pdf")
        store.create_document("doc2.pdf", 2048, ".pdf")
        store.create_document("doc3.pdf", 4096, ".pdf")

        assert len(store.list_documents()) == 3

        count = store.clear_all()

        assert count == 3
        assert len(store.list_documents()) == 0

    def test_global_store_singleton(self):
        """Test global store instance."""
        from src.document_store import get_document_store, reset_document_store

        # Reset to clean state
        reset_document_store()

        store1 = get_document_store()
        store2 = get_document_store()

        # Should be same instance
        assert store1 is store2

        # Cleanup
        reset_document_store()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
