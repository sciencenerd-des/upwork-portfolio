"""
Document Intelligence System - Core Modules

This package contains the core processing modules:
- document_loader: PDF and image loading with validation
- ocr_engine: OCR processing with Tesseract
- text_processor: Text cleaning, normalization, and chunking
- entity_extractor: Named entity and pattern extraction
- vector_store: ChromaDB vector storage and embeddings
- summarizer: LLM-based document summarization
- qa_engine: RAG-based question answering
- exporter: Data export to JSON, CSV, Excel
- document_store: In-memory session management
"""

from src.document_store import (
    DocumentStore,
    get_document_store,
    reset_document_store,
)

__all__ = [
    "DocumentStore",
    "get_document_store",
    "reset_document_store",
]

__version__ = "1.0.0"
