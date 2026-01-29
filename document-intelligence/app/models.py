"""
Pydantic models for Document Intelligence System.
Defines request/response schemas for API and internal data structures.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    EXTRACTING_TEXT = "extracting_text"
    RUNNING_OCR = "running_ocr"
    EXTRACTING_ENTITIES = "extracting_entities"
    GENERATING_EMBEDDINGS = "generating_embeddings"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Document type classification."""
    INVOICE = "invoice"
    CONTRACT = "contract"
    RECEIPT = "receipt"
    REPORT = "report"
    LETTER = "letter"
    RESUME = "resume"
    LEGAL = "legal"
    UNKNOWN = "unknown"


class ExportFormat(str, Enum):
    """Export format options."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class EntityType(str, Enum):
    """Entity types for extraction."""
    DATE = "date"
    AMOUNT = "amount"
    PERSON = "person"
    ORGANIZATION = "organization"
    EMAIL = "email"
    PHONE = "phone"
    INVOICE_NUMBER = "invoice_number"
    GSTIN = "gstin"
    PAN = "pan"
    ADDRESS = "address"
    CUSTOM = "custom"


# ============================================================================
# Entity Models
# ============================================================================

class ExtractedEntity(BaseModel):
    """Single extracted entity."""
    entity_type: EntityType
    value: str
    label: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    page_number: Optional[int] = None
    position: Optional[dict] = None  # {"start": int, "end": int}

    @field_validator("confidence")
    @classmethod
    def round_confidence(cls, v: float) -> float:
        return round(v, 3)


class AmountEntity(ExtractedEntity):
    """Amount entity with currency."""
    entity_type: EntityType = EntityType.AMOUNT
    numeric_value: Optional[float] = None
    currency: str = "INR"


class DateEntity(ExtractedEntity):
    """Date entity with parsed value."""
    entity_type: EntityType = EntityType.DATE
    parsed_date: Optional[datetime] = None
    date_format: Optional[str] = None


class ExtractedEntities(BaseModel):
    """Collection of all extracted entities."""
    dates: list[DateEntity] = Field(default_factory=list)
    amounts: list[AmountEntity] = Field(default_factory=list)
    persons: list[ExtractedEntity] = Field(default_factory=list)
    organizations: list[ExtractedEntity] = Field(default_factory=list)
    emails: list[ExtractedEntity] = Field(default_factory=list)
    phones: list[ExtractedEntity] = Field(default_factory=list)
    invoice_numbers: list[ExtractedEntity] = Field(default_factory=list)
    gstins: list[ExtractedEntity] = Field(default_factory=list)
    pans: list[ExtractedEntity] = Field(default_factory=list)
    custom: list[ExtractedEntity] = Field(default_factory=list)

    @property
    def total_count(self) -> int:
        """Total number of entities."""
        return (
            len(self.dates) + len(self.amounts) + len(self.persons) +
            len(self.organizations) + len(self.emails) + len(self.phones) +
            len(self.invoice_numbers) + len(self.gstins) + len(self.pans) +
            len(self.custom)
        )

    def to_flat_list(self) -> list[ExtractedEntity]:
        """Convert to flat list of all entities."""
        all_entities = []
        all_entities.extend(self.dates)
        all_entities.extend(self.amounts)
        all_entities.extend(self.persons)
        all_entities.extend(self.organizations)
        all_entities.extend(self.emails)
        all_entities.extend(self.phones)
        all_entities.extend(self.invoice_numbers)
        all_entities.extend(self.gstins)
        all_entities.extend(self.pans)
        all_entities.extend(self.custom)
        return all_entities


# ============================================================================
# Document Models
# ============================================================================

class TextChunk(BaseModel):
    """Text chunk for vector storage."""
    chunk_id: str
    text: str
    page_number: Optional[int] = None
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    metadata: dict = Field(default_factory=dict)


class PageContent(BaseModel):
    """Content from a single page."""
    page_number: int
    text: str
    is_scanned: bool = False
    ocr_confidence: Optional[float] = None


class DocumentSummary(BaseModel):
    """Document summary result."""
    document_type: DocumentType
    executive_summary: str
    key_points: list[str]
    word_count: int = 0
    page_count: int = 0


class DocumentMetadata(BaseModel):
    """Document metadata."""
    doc_id: str
    filename: str
    file_size_bytes: int
    file_type: str
    page_count: int
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    is_scanned: bool = False
    has_native_text: bool = True


class ProcessingProgress(BaseModel):
    """Processing progress update."""
    doc_id: str
    status: DocumentStatus
    progress_percent: int = Field(ge=0, le=100)
    current_step: str
    message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class ProcessedDocument(BaseModel):
    """Fully processed document with all extracted data."""
    metadata: DocumentMetadata
    status: DocumentStatus
    raw_text: str
    pages: list[PageContent]
    chunks: list[TextChunk]
    entities: ExtractedEntities
    summary: Optional[DocumentSummary] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None


# ============================================================================
# Q&A Models
# ============================================================================

class QASource(BaseModel):
    """Source citation for Q&A answer."""
    page: Optional[int] = None
    section: Optional[str] = None
    quote: str
    relevance_score: Optional[float] = None


class QAMessage(BaseModel):
    """Single Q&A message in conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class QARequest(BaseModel):
    """Q&A request payload."""
    question: str = Field(min_length=1, max_length=1000)
    include_sources: bool = True
    conversation_history: list[QAMessage] = Field(default_factory=list)


class QAResponse(BaseModel):
    """Q&A response payload."""
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[QASource] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)
    processing_time_ms: Optional[int] = None


# ============================================================================
# API Request/Response Models
# ============================================================================

class UploadResponse(BaseModel):
    """Document upload response."""
    doc_id: str
    filename: str
    file_size_bytes: int
    status: DocumentStatus
    message: str = "Document uploaded successfully"


class StatusResponse(BaseModel):
    """Processing status response."""
    doc_id: str
    status: DocumentStatus
    filename: Optional[str] = None
    page_count: Optional[int] = None
    is_scanned: Optional[bool] = None
    error_message: Optional[str] = None
    upload_time: Optional[datetime] = None
    has_summary: bool = False
    entity_count: int = 0


class SummaryResponse(BaseModel):
    """Summary response."""
    doc_id: str
    summary: DocumentSummary
    processing_time_ms: Optional[int] = None


class EntitiesResponse(BaseModel):
    """Entities response."""
    doc_id: str
    entities: ExtractedEntities
    total_count: int


class ExportRequest(BaseModel):
    """Export request options."""
    include_summary: bool = True
    include_entities: bool = True
    include_raw_text: bool = False


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    status_code: int


# ============================================================================
# Session/Store Models
# ============================================================================

class SessionDocument(BaseModel):
    """Document stored in session."""
    doc_id: str
    document: ProcessedDocument
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    conversation_history: list[QAMessage] = Field(default_factory=list)

    def update_access_time(self) -> None:
        """Update last access timestamp."""
        self.last_accessed = datetime.utcnow()

    def add_qa_message(self, role: str, content: str) -> None:
        """Add Q&A message to history."""
        self.conversation_history.append(
            QAMessage(role=role, content=content)
        )

    @property
    def is_expired(self) -> bool:
        """Check if session has expired (TTL check done in store)."""
        return False  # Actual TTL check in DocumentStore


# ============================================================================
# Validation Helpers
# ============================================================================

class FileValidation(BaseModel):
    """File validation result."""
    is_valid: bool
    error_message: Optional[str] = None
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None


def validate_file_extension(filename: str, supported: list[str]) -> bool:
    """Validate file extension."""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in supported


def validate_file_size(size_bytes: int, max_mb: int) -> bool:
    """Validate file size."""
    return size_bytes <= max_mb * 1024 * 1024
