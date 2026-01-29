"""
Document Intelligence System - Application Package

This package contains the web application components:
- config: Configuration management
- models: Pydantic data models
- main: FastAPI application
- streamlit_app: Streamlit web interface
"""

from app.config import get_settings, get_prompts, settings, prompts
from app.models import (
    DocumentStatus,
    DocumentType,
    ExportFormat,
    EntityType,
    ExtractedEntity,
    ExtractedEntities,
    ProcessedDocument,
    DocumentSummary,
    QARequest,
    QAResponse,
)

__all__ = [
    "get_settings",
    "get_prompts",
    "settings",
    "prompts",
    "DocumentStatus",
    "DocumentType",
    "ExportFormat",
    "EntityType",
    "ExtractedEntity",
    "ExtractedEntities",
    "ProcessedDocument",
    "DocumentSummary",
    "QARequest",
    "QAResponse",
]
