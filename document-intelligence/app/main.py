"""
FastAPI Backend

REST API for Document Intelligence System.
- Upload and process documents
- Get summaries and entities
- RAG-based Q&A
- Export to multiple formats
"""

import io
import asyncio
import logging
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import (
    ProcessedDocument,
    DocumentMetadata,
    DocumentStatus,
    DocumentSummary,
    ExtractedEntities,
    QARequest,
    QAResponse,
    QAMessage,
    ExportFormat,
    UploadResponse,
    StatusResponse,
    ErrorResponse,
)
from src.document_store import get_document_store
from src.document_loader import get_document_loader
from src.ocr_engine import get_ocr_engine
from src.text_processor import get_text_processor
from src.entity_extractor import get_entity_extractor
from src.vector_store import get_document_vector_store
from src.summarizer import get_summarizer
from src.qa_engine import get_qa_engine
from src.exporter import get_exporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Intelligence API",
    description="API for document processing with OCR, entity extraction, summarization, and Q&A",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get settings
settings = get_settings()


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Document Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "status": "GET /status/{doc_id}",
            "summary": "GET /summary/{doc_id}",
            "entities": "GET /entities/{doc_id}",
            "qa": "POST /qa/{doc_id}",
            "export": "GET /export/{doc_id}/{format}",
            "delete": "DELETE /document/{doc_id}",
        }
    }


# =============================================================================
# Document Upload & Processing
# =============================================================================

async def process_document_async(doc_id: str, file_content: bytes, filename: str):
    """
    Background task to process uploaded document.
    """
    store = get_document_store()
    loader = get_document_loader()
    ocr_engine = get_ocr_engine()
    text_processor = get_text_processor()
    entity_extractor = get_entity_extractor()
    vector_store = get_document_vector_store()
    summarizer = get_summarizer()

    try:
        # Update status to processing
        doc = store.get_document(doc_id)
        if not doc:
            logger.error(f"Document {doc_id} not found in store")
            return

        store.set_status(doc_id, DocumentStatus.PROCESSING)

        # Step 1: Load document
        logger.info(f"Loading document: {filename}")
        load_result = loader.load(file_content, filename)

        if not load_result:
            store.set_error(doc_id, "Failed to load document")
            return

        # Update metadata
        doc.metadata.page_count = load_result.page_count
        doc.metadata.is_scanned = load_result.is_scanned

        # Step 2: Extract text (OCR if needed)
        logger.info(f"Extracting text from {load_result.page_count} pages")
        from app.models import PageContent
        pages = []
        all_text = []

        # Map images to their page indices (images are only for scanned pages)
        image_idx = 0

        for page in load_result.pages:
            page_text = page.text or ""
            ocr_confidence = None
            is_scanned = page.is_scanned

            # If page is scanned and we have an image for it, run OCR
            if is_scanned and image_idx < len(load_result.images):
                ocr_result = ocr_engine.process_image(load_result.images[image_idx])
                if ocr_result and ocr_result.text:
                    page_text = ocr_result.text
                    ocr_confidence = ocr_result.confidence
                image_idx += 1

            pages.append(PageContent(
                page_number=page.page_number,
                text=page_text,
                is_scanned=is_scanned,
                ocr_confidence=ocr_confidence
            ))
            all_text.append(page_text)

        doc.pages = pages
        doc.raw_text = "\n\n".join(all_text)

        # Step 3: Process text (clean, chunk)
        logger.info("Processing text")
        processed = text_processor.process(doc.raw_text)
        doc.chunks = processed.chunks

        # Step 4: Extract entities
        logger.info("Extracting entities")
        doc.entities = entity_extractor.extract(doc.raw_text)

        # Add page numbers to entities where possible
        for page in pages:
            page_text = page.text.lower()
            for entity_list in [doc.entities.dates, doc.entities.amounts,
                               doc.entities.invoice_numbers, doc.entities.gstins,
                               doc.entities.pans]:
                for entity in entity_list:
                    if entity.value.lower() in page_text and not entity.page_number:
                        entity.page_number = page.page_number

        # Step 5: Index in vector store
        logger.info("Indexing in vector store")
        if doc.chunks:
            vector_store.index_document(doc_id, doc.chunks)

        # Step 6: Generate summary
        logger.info("Generating summary")
        word_count = len(doc.raw_text.split())
        doc.summary = summarizer.summarize(
            doc.raw_text,
            word_count=word_count,
            page_count=doc.metadata.page_count
        )

        # Mark as completed
        store.update_document(doc_id, doc)
        store.set_status(doc_id, DocumentStatus.COMPLETED)
        logger.info(f"Document {doc_id} processing completed")

    except Exception as e:
        logger.error(f"Processing failed for {doc_id}: {e}")
        store.set_error(doc_id, str(e))


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a document for processing.

    Accepts PDF and image files (PNG, JPG, JPEG, TIFF).
    Processing happens in the background.
    """
    # Validate file type
    allowed_types = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
    filename = file.filename or "document"
    file_ext = "." + filename.lower().split(".")[-1] if "." in filename else ""

    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_types)}"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    max_size = settings.document.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size / 1024 / 1024:.1f}MB. Max: {settings.document.max_file_size_mb}MB"
        )

    # Create document in store
    store = get_document_store()
    doc_id = store.create_document(
        filename=filename,
        file_type=file_ext,
        file_size_bytes=file_size
    )

    # Start background processing
    background_tasks.add_task(process_document_async, doc_id, content, filename)

    return UploadResponse(
        doc_id=doc_id,
        filename=filename,
        file_size_bytes=file_size,
        status=DocumentStatus.PENDING,
        message="Document uploaded. Processing started."
    )


# =============================================================================
# Document Status
# =============================================================================

@app.get("/status/{doc_id}", response_model=StatusResponse)
async def get_status(doc_id: str):
    """
    Get processing status of a document.
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return StatusResponse(
        doc_id=doc_id,
        status=doc.status,
        filename=doc.metadata.filename,
        page_count=doc.metadata.page_count,
        is_scanned=doc.metadata.is_scanned,
        error_message=doc.error_message,
        upload_time=doc.metadata.upload_time,
        has_summary=doc.summary is not None,
        entity_count=doc.entities.total_count if doc.entities else 0
    )


# =============================================================================
# Summary
# =============================================================================

@app.get("/summary/{doc_id}")
async def get_summary(doc_id: str):
    """
    Get document summary.
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    if not doc.summary:
        raise HTTPException(status_code=404, detail="Summary not available")

    return {
        "doc_id": doc_id,
        "summary": {
            "document_type": doc.summary.document_type.value,
            "executive_summary": doc.summary.executive_summary,
            "key_points": doc.summary.key_points,
            "word_count": doc.summary.word_count,
            "page_count": doc.summary.page_count,
        }
    }


# =============================================================================
# Entities
# =============================================================================

@app.get("/entities/{doc_id}")
async def get_entities(
    doc_id: str,
    entity_type: Optional[str] = Query(None, description="Filter by entity type")
):
    """
    Get extracted entities from document.

    Optional filter by entity_type: date, amount, person, organization,
    email, phone, invoice_number, gstin, pan
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    entities = doc.entities

    # Build response
    response = {
        "doc_id": doc_id,
        "total_count": entities.total_count if entities else 0,
    }

    if entities:
        all_entities = {
            "dates": [{"value": e.value, "parsed": e.parsed_date.isoformat() if e.parsed_date else None,
                      "confidence": e.confidence, "page": e.page_number} for e in entities.dates],
            "amounts": [{"value": e.value, "numeric": e.numeric_value, "currency": e.currency,
                        "confidence": e.confidence, "page": e.page_number} for e in entities.amounts],
            "persons": [{"value": e.value, "confidence": e.confidence, "page": e.page_number}
                       for e in entities.persons],
            "organizations": [{"value": e.value, "confidence": e.confidence, "page": e.page_number}
                             for e in entities.organizations],
            "emails": [{"value": e.value, "confidence": e.confidence} for e in entities.emails],
            "phones": [{"value": e.value, "confidence": e.confidence} for e in entities.phones],
            "invoice_numbers": [{"value": e.value, "confidence": e.confidence} for e in entities.invoice_numbers],
            "gstins": [{"value": e.value, "confidence": e.confidence} for e in entities.gstins],
            "pans": [{"value": e.value, "confidence": e.confidence} for e in entities.pans],
        }

        if entity_type:
            entity_type = entity_type.lower()
            type_map = {
                "date": "dates", "dates": "dates",
                "amount": "amounts", "amounts": "amounts",
                "person": "persons", "persons": "persons",
                "organization": "organizations", "organizations": "organizations",
                "email": "emails", "emails": "emails",
                "phone": "phones", "phones": "phones",
                "invoice_number": "invoice_numbers", "invoice_numbers": "invoice_numbers",
                "gstin": "gstins", "gstins": "gstins",
                "pan": "pans", "pans": "pans",
            }
            key = type_map.get(entity_type)
            if key:
                response["entities"] = {key: all_entities[key]}
            else:
                raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")
        else:
            response["entities"] = all_entities

    return response


# =============================================================================
# Q&A
# =============================================================================

@app.post("/qa/{doc_id}", response_model=QAResponse)
async def ask_question(doc_id: str, request: QARequest):
    """
    Ask a question about the document.

    Uses RAG (Retrieval Augmented Generation) to find relevant
    context and generate an answer with citations.
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    # Get conversation history from store (already QAMessage objects)
    qa_history = store.get_conversation_history(doc_id)

    # Get Q&A engine and answer
    qa_engine = get_qa_engine()
    response = qa_engine.answer(
        doc_id=doc_id,
        question=request.question,
        conversation_history=qa_history,
        include_sources=request.include_sources if hasattr(request, 'include_sources') else True
    )

    # Add to conversation history
    store.add_conversation_message(doc_id, "user", request.question)
    store.add_conversation_message(doc_id, "assistant", response.answer)

    return response


# =============================================================================
# Export
# =============================================================================

@app.get("/export/{doc_id}/{format}")
async def export_document(
    doc_id: str,
    format: str,
    include_summary: bool = Query(True, description="Include summary in export"),
    include_entities: bool = Query(True, description="Include entities in export"),
    include_raw_text: bool = Query(False, description="Include raw text in export"),
):
    """
    Export document data.

    Format options: json, csv, excel
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    # Map format string to enum
    format_lower = format.lower()
    format_map = {
        "json": ExportFormat.JSON,
        "csv": ExportFormat.CSV,
        "excel": ExportFormat.EXCEL,
        "xlsx": ExportFormat.EXCEL,
    }

    if format_lower not in format_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Allowed: json, csv, excel"
        )

    export_format = format_map[format_lower]
    exporter = get_exporter()

    try:
        result = exporter.export(
            document=doc,
            format=export_format,
            include_summary=include_summary,
            include_entities=include_entities,
            include_raw_text=include_raw_text
        )

        # Return appropriate response based on format
        if export_format == ExportFormat.JSON:
            return JSONResponse(
                content={"data": result},
                media_type="application/json"
            )
        elif export_format == ExportFormat.CSV:
            return StreamingResponse(
                io.StringIO(result),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={doc_id}_entities.csv"
                }
            )
        else:  # Excel
            return StreamingResponse(
                io.BytesIO(result),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={doc_id}_export.xlsx"
                }
            )

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# =============================================================================
# Delete Document
# =============================================================================

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document and all associated data.
    """
    store = get_document_store()
    vector_store = get_document_vector_store()

    # Check if document exists
    doc = store.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    try:
        vector_store.delete_store(doc_id)
    except Exception as e:
        logger.warning(f"Failed to delete vector store for {doc_id}: {e}")

    # Delete from document store
    store.delete_document(doc_id)

    return {"message": f"Document {doc_id} deleted successfully"}


# =============================================================================
# Suggested Questions
# =============================================================================

@app.get("/questions/{doc_id}")
async def get_suggested_questions(doc_id: str):
    """
    Get suggested questions for a document.
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    qa_engine = get_qa_engine()
    questions = qa_engine.generate_suggested_questions(doc_id)

    return {
        "doc_id": doc_id,
        "suggested_questions": questions
    }


# =============================================================================
# Document Text (for debugging/verification)
# =============================================================================

@app.get("/text/{doc_id}")
async def get_document_text(
    doc_id: str,
    page: Optional[int] = Query(None, description="Specific page number")
):
    """
    Get extracted text from document.
    """
    store = get_document_store()
    doc = store.get_document(doc_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status not in [DocumentStatus.COMPLETED, DocumentStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail=f"Document not ready. Status: {doc.status.value}"
        )

    if page is not None:
        # Get specific page
        for p in doc.pages:
            if p.page_number == page:
                return {
                    "doc_id": doc_id,
                    "page": page,
                    "text": p.text,
                    "is_scanned": p.is_scanned,
                    "ocr_confidence": p.ocr_confidence
                }
        raise HTTPException(status_code=404, detail=f"Page {page} not found")

    # Return all text
    return {
        "doc_id": doc_id,
        "total_pages": len(doc.pages),
        "text": doc.raw_text,
        "pages": [
            {
                "page_number": p.page_number,
                "text_length": len(p.text),
                "is_scanned": p.is_scanned,
                "ocr_confidence": p.ocr_confidence
            }
            for p in doc.pages
        ]
    }


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
