"""
In-memory document store with TTL-based session management.
Handles document storage, retrieval, and automatic cleanup.
No persistent storage for privacy.
"""

import asyncio
import logging
import threading
import uuid
from datetime import datetime, timedelta
from typing import Optional
from collections import OrderedDict

from app.models import (
    SessionDocument,
    ProcessedDocument,
    DocumentStatus,
    DocumentMetadata,
    ProcessingProgress,
    QAMessage,
    ExtractedEntities,
    TextChunk,
    PageContent,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class DocumentStore:
    """
    In-memory document store with TTL expiration.
    Thread-safe implementation for concurrent access.
    """

    def __init__(
        self,
        ttl_minutes: Optional[int] = None,
        max_documents: Optional[int] = None,
        cleanup_interval_seconds: Optional[int] = None
    ):
        settings = get_settings()
        self._ttl_minutes = ttl_minutes or settings.session.ttl_minutes
        self._max_documents = max_documents or settings.session.max_documents_per_session
        self._cleanup_interval = cleanup_interval_seconds or settings.session.cleanup_interval_seconds

        # Use OrderedDict for LRU-style eviction
        self._documents: OrderedDict[str, SessionDocument] = OrderedDict()
        self._processing_status: dict[str, ProcessingProgress] = {}
        self._lock = threading.RLock()

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    # =========================================================================
    # Document CRUD Operations
    # =========================================================================

    def generate_doc_id(self) -> str:
        """Generate unique document ID."""
        return str(uuid.uuid4())[:12]

    def create_document(
        self,
        filename: str,
        file_size_bytes: int,
        file_type: str,
        page_count: int = 0,
        is_scanned: bool = False
    ) -> str:
        """
        Create a new document entry and return its ID.
        Initial status is PENDING.
        """
        doc_id = self.generate_doc_id()

        metadata = DocumentMetadata(
            doc_id=doc_id,
            filename=filename,
            file_size_bytes=file_size_bytes,
            file_type=file_type,
            page_count=page_count,
            is_scanned=is_scanned,
            has_native_text=not is_scanned
        )

        document = ProcessedDocument(
            metadata=metadata,
            status=DocumentStatus.PENDING,
            raw_text="",
            pages=[],
            chunks=[],
            entities=ExtractedEntities()
        )

        session_doc = SessionDocument(
            doc_id=doc_id,
            document=document
        )

        with self._lock:
            # Check capacity and evict if needed
            self._evict_if_needed()

            self._documents[doc_id] = session_doc
            self._processing_status[doc_id] = ProcessingProgress(
                doc_id=doc_id,
                status=DocumentStatus.PENDING,
                progress_percent=0,
                current_step="Initialized"
            )

            # Move to end for LRU tracking
            self._documents.move_to_end(doc_id)

        logger.info(f"Created document: {doc_id} ({filename})")
        return doc_id

    def get_document(self, doc_id: str) -> Optional[ProcessedDocument]:
        """Get document by ID, updating access time."""
        with self._lock:
            session_doc = self._documents.get(doc_id)
            if session_doc:
                session_doc.update_access_time()
                self._documents.move_to_end(doc_id)
                return session_doc.document
        return None

    def get_session_document(self, doc_id: str) -> Optional[SessionDocument]:
        """Get full session document including conversation history."""
        with self._lock:
            session_doc = self._documents.get(doc_id)
            if session_doc:
                session_doc.update_access_time()
                self._documents.move_to_end(doc_id)
                return session_doc
        return None

    def update_document(self, doc_id: str, document: ProcessedDocument) -> bool:
        """Update document data."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document = document
                self._documents[doc_id].update_access_time()
                self._documents.move_to_end(doc_id)
                return True
        return False

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from store."""
        with self._lock:
            if doc_id in self._documents:
                del self._documents[doc_id]
                self._processing_status.pop(doc_id, None)
                logger.info(f"Deleted document: {doc_id}")
                return True
        return False

    def document_exists(self, doc_id: str) -> bool:
        """Check if document exists."""
        with self._lock:
            return doc_id in self._documents

    def list_documents(self) -> list[str]:
        """List all document IDs."""
        with self._lock:
            return list(self._documents.keys())

    # =========================================================================
    # Document Update Methods
    # =========================================================================

    def update_raw_text(self, doc_id: str, text: str) -> bool:
        """Update document raw text."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.raw_text = text
                return True
        return False

    def update_pages(self, doc_id: str, pages: list[PageContent]) -> bool:
        """Update document pages."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.pages = pages
                self._documents[doc_id].document.metadata.page_count = len(pages)
                return True
        return False

    def update_chunks(self, doc_id: str, chunks: list[TextChunk]) -> bool:
        """Update document chunks."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.chunks = chunks
                return True
        return False

    def update_entities(self, doc_id: str, entities: ExtractedEntities) -> bool:
        """Update extracted entities."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.entities = entities
                return True
        return False

    def update_summary(self, doc_id: str, summary) -> bool:
        """Update document summary."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.summary = summary
                return True
        return False

    def set_status(self, doc_id: str, status: DocumentStatus) -> bool:
        """Update document status."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.status = status
                return True
        return False

    def set_error(self, doc_id: str, error_message: str) -> bool:
        """Set error message and failed status."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].document.status = DocumentStatus.FAILED
                self._documents[doc_id].document.error_message = error_message
                return True
        return False

    # =========================================================================
    # Processing Status
    # =========================================================================

    def update_progress(
        self,
        doc_id: str,
        status: DocumentStatus,
        progress_percent: int,
        current_step: str,
        message: Optional[str] = None
    ) -> bool:
        """Update processing progress."""
        with self._lock:
            if doc_id in self._documents:
                self._processing_status[doc_id] = ProcessingProgress(
                    doc_id=doc_id,
                    status=status,
                    progress_percent=progress_percent,
                    current_step=current_step,
                    message=message
                )
                self._documents[doc_id].document.status = status
                return True
        return False

    def get_progress(self, doc_id: str) -> Optional[ProcessingProgress]:
        """Get current processing progress."""
        with self._lock:
            return self._processing_status.get(doc_id)

    # =========================================================================
    # Conversation History
    # =========================================================================

    def add_conversation_message(
        self,
        doc_id: str,
        role: str,
        content: str
    ) -> bool:
        """Add message to conversation history."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].add_qa_message(role, content)
                return True
        return False

    def get_conversation_history(self, doc_id: str) -> list[QAMessage]:
        """Get conversation history for document."""
        with self._lock:
            if doc_id in self._documents:
                return self._documents[doc_id].conversation_history.copy()
        return []

    def clear_conversation_history(self, doc_id: str) -> bool:
        """Clear conversation history for document."""
        with self._lock:
            if doc_id in self._documents:
                self._documents[doc_id].conversation_history = []
                return True
        return False

    # =========================================================================
    # TTL and Cleanup
    # =========================================================================

    def _is_expired(self, session_doc: SessionDocument) -> bool:
        """Check if document has expired based on TTL."""
        if self._ttl_minutes <= 0:
            # TTL of 0 means immediate expiration after creation
            return datetime.utcnow() > session_doc.created_at
        expiry_time = session_doc.last_accessed + timedelta(minutes=self._ttl_minutes)
        return datetime.utcnow() > expiry_time

    def _evict_if_needed(self) -> None:
        """Evict oldest documents if over capacity."""
        while len(self._documents) >= self._max_documents:
            # Remove oldest (first) item
            oldest_id = next(iter(self._documents))
            del self._documents[oldest_id]
            self._processing_status.pop(oldest_id, None)
            logger.info(f"Evicted document due to capacity: {oldest_id}")

    def cleanup_expired(self) -> int:
        """Remove expired documents. Returns count of removed documents."""
        removed = 0
        with self._lock:
            expired_ids = [
                doc_id for doc_id, session_doc in self._documents.items()
                if self._is_expired(session_doc)
            ]
            for doc_id in expired_ids:
                del self._documents[doc_id]
                self._processing_status.pop(doc_id, None)
                removed += 1
                logger.info(f"Cleaned up expired document: {doc_id}")
        return removed

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            await asyncio.sleep(self._cleanup_interval)
            try:
                removed = self.cleanup_expired()
                if removed > 0:
                    logger.info(f"Cleanup removed {removed} expired documents")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    def start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if not self._running:
            self._running = True
            try:
                loop = asyncio.get_event_loop()
                self._cleanup_task = loop.create_task(self._cleanup_loop())
            except RuntimeError:
                # No event loop running, skip async cleanup
                logger.warning("No event loop available for cleanup task")

    def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> dict:
        """Get store statistics."""
        with self._lock:
            return {
                "total_documents": len(self._documents),
                "max_documents": self._max_documents,
                "ttl_minutes": self._ttl_minutes,
                "document_ids": list(self._documents.keys())
            }

    def clear_all(self) -> int:
        """Clear all documents. Returns count of removed documents."""
        with self._lock:
            count = len(self._documents)
            self._documents.clear()
            self._processing_status.clear()
            logger.info(f"Cleared all {count} documents")
            return count


# Global document store instance
_document_store: Optional[DocumentStore] = None


def get_document_store() -> DocumentStore:
    """Get or create global document store instance."""
    global _document_store
    if _document_store is None:
        _document_store = DocumentStore()
    return _document_store


def reset_document_store() -> None:
    """Reset global document store (for testing)."""
    global _document_store
    if _document_store:
        _document_store.stop_cleanup_task()
        _document_store.clear_all()
    _document_store = None
