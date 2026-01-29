"""
Tests for Exporter Module.
Covers JSON/CSV/Excel export with various options and filename sanitization.
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime

import pytest
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.models import (
    ProcessedDocument,
    DocumentMetadata,
    DocumentStatus,
    DocumentSummary,
    DocumentType,
    ExtractedEntities,
    ExtractedEntity,
    DateEntity,
    AmountEntity,
    EntityType,
    TextChunk,
    PageContent,
    ExportFormat,
)
from src.exporter import Exporter, sanitize_filename, get_exporter


def create_test_document() -> ProcessedDocument:
    """Create a test document for export testing."""
    metadata = DocumentMetadata(
        doc_id="test123",
        filename="test_document.pdf",
        file_size_bytes=1024,
        file_type=".pdf",
        page_count=2,
        is_scanned=False,
        has_native_text=True,
    )
    
    summary = DocumentSummary(
        document_type=DocumentType.INVOICE,
        executive_summary="This is a test invoice document.",
        key_points=["Point 1", "Point 2", "Point 3"],
        word_count=100,
        page_count=2,
    )
    
    entities = ExtractedEntities(
        dates=[
            DateEntity(
                value="January 15, 2024",
                parsed_date=datetime(2024, 1, 15),
                confidence=0.95,
                page_number=1,
            )
        ],
        amounts=[
            AmountEntity(
                value="$1,000.00",
                numeric_value=1000.0,
                currency="USD",
                confidence=0.98,
                page_number=1,
            )
        ],
        persons=[
            ExtractedEntity(
                entity_type=EntityType.PERSON,
                value="John Doe",
                confidence=0.9,
                page_number=1,
            )
        ],
        organizations=[
            ExtractedEntity(
                entity_type=EntityType.ORGANIZATION,
                value="Acme Corp",
                confidence=0.85,
                page_number=1,
            )
        ],
        emails=[
            ExtractedEntity(
                entity_type=EntityType.EMAIL,
                value="john@example.com",
                confidence=0.99,
            )
        ],
        phones=[
            ExtractedEntity(
                entity_type=EntityType.PHONE,
                value="+1-555-1234",
                confidence=0.9,
            )
        ],
        invoice_numbers=[
            ExtractedEntity(
                entity_type=EntityType.INVOICE_NUMBER,
                value="INV-2024-001",
                confidence=0.95,
            )
        ],
    )
    
    pages = [
        PageContent(page_number=1, text="Page 1 content", is_scanned=False),
        PageContent(page_number=2, text="Page 2 content", is_scanned=False),
    ]
    
    chunks = [
        TextChunk(chunk_id="c1", text="Chunk 1 text", page_number=1),
        TextChunk(chunk_id="c2", text="Chunk 2 text", page_number=2),
    ]
    
    return ProcessedDocument(
        metadata=metadata,
        status=DocumentStatus.COMPLETED,
        raw_text="Page 1 content\n\nPage 2 content",
        pages=pages,
        chunks=chunks,
        entities=entities,
        summary=summary,
    )


class TestSanitizeFilename:
    """Tests for filename sanitization function."""

    def test_sanitize_normal_filename(self):
        """Test sanitizing normal filename."""
        result = sanitize_filename("report.pdf")
        assert result == "report.pdf"

    def test_sanitize_removes_directory_traversal(self):
        """Test that directory traversal is removed."""
        result = sanitize_filename("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_sanitize_windows_path_traversal(self):
        """Test Windows-style path traversal removal."""
        result = sanitize_filename("..\\..\\system32")
        assert ".." not in result
        assert "\\" not in result

    def test_sanitize_removes_dangerous_chars(self):
        """Test removal of dangerous characters."""
        result = sanitize_filename("file<name>:test?.pdf")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "?" not in result

    def test_sanitize_handles_hidden_files(self):
        """Test handling of hidden files."""
        result = sanitize_filename(".hidden_file")
        assert not result.startswith(".")

    def test_sanitize_empty_returns_default(self):
        """Test empty filename returns default."""
        result = sanitize_filename("")
        assert result == "export"

    def test_sanitize_only_dots_returns_default(self):
        """Test filename with only dots."""
        result = sanitize_filename("...")
        assert result == "export"


class TestExporterJSON:
    """Tests for JSON export functionality."""

    def test_export_json_basic(self):
        """Test basic JSON export."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc)
        
        assert isinstance(result, str)
        data = json.loads(result)
        assert "metadata" in data
        assert "export_time" in data

    def test_export_json_with_summary(self):
        """Test JSON export includes summary."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_summary=True)
        
        data = json.loads(result)
        assert "summary" in data
        assert data["summary"]["document_type"] == "invoice"

    def test_export_json_without_summary(self):
        """Test JSON export without summary."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_summary=False)
        
        data = json.loads(result)
        assert "summary" not in data

    def test_export_json_with_entities(self):
        """Test JSON export includes entities."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_entities=True)
        
        data = json.loads(result)
        assert "entities" in data
        assert "dates" in data["entities"]
        assert "amounts" in data["entities"]

    def test_export_json_without_entities(self):
        """Test JSON export without entities."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_entities=False)
        
        data = json.loads(result)
        assert "entities" not in data

    def test_export_json_with_raw_text(self):
        """Test JSON export includes raw text."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_raw_text=True)
        
        data = json.loads(result)
        assert "raw_text" in data
        assert "pages" in data
        assert len(data["pages"]) == 2

    def test_export_json_without_raw_text(self):
        """Test JSON export without raw text."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_json(doc, include_raw_text=False)
        
        data = json.loads(result)
        assert "raw_text" not in data
        assert "pages" not in data


class TestExporterCSV:
    """Tests for CSV export functionality."""

    def test_export_csv_basic(self):
        """Test basic CSV export."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_csv(doc)
        
        assert isinstance(result, str)
        assert "entity_type" in result
        assert "value" in result

    def test_export_csv_contains_all_entities(self):
        """Test CSV export contains all entity types."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_csv(doc)
        
        # Check for various entity types
        assert "date" in result.lower()
        assert "amount" in result.lower()
        assert "person" in result.lower()
        assert "organization" in result.lower()

    def test_export_csv_empty_entities(self):
        """Test CSV export with empty entities."""
        exporter = Exporter()
        doc = create_test_document()
        doc.entities = ExtractedEntities()  # Empty entities
        
        result = exporter.export_csv(doc)
        
        # Should still have headers
        assert isinstance(result, str)
        assert "entity_type" in result


class TestExporterExcel:
    """Tests for Excel export functionality."""

    def test_export_excel_basic(self):
        """Test basic Excel export."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_excel(doc)
        
        assert isinstance(result, bytes)
        # Should be valid Excel file
        df = pd.read_excel(io.BytesIO(result), sheet_name=None)
        assert len(df) > 0

    def test_export_excel_with_summary(self):
        """Test Excel export includes summary sheet."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_excel(doc, include_summary=True)
        
        df = pd.read_excel(io.BytesIO(result), sheet_name=None)
        # Should have Summary sheet
        sheet_names = [name.lower() for name in df.keys()]
        assert any("summary" in name for name in sheet_names)

    def test_export_excel_with_entities(self):
        """Test Excel export includes entities sheet."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_excel(doc, include_entities=True)
        
        df = pd.read_excel(io.BytesIO(result), sheet_name=None)
        sheet_names = [name.lower() for name in df.keys()]
        assert any("entities" in name for name in sheet_names)

    def test_export_excel_with_raw_text(self):
        """Test Excel export includes raw text sheet."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export_excel(doc, include_raw_text=True)
        
        df = pd.read_excel(io.BytesIO(result), sheet_name=None)
        sheet_names = [name.lower() for name in df.keys()]
        assert any("raw" in name or "text" in name for name in sheet_names)


class TestExporterGeneric:
    """Tests for generic export functionality."""

    def test_export_with_format_json(self):
        """Test export with JSON format."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export(doc, ExportFormat.JSON)
        
        assert isinstance(result, str)
        json.loads(result)  # Should be valid JSON

    def test_export_with_format_csv(self):
        """Test export with CSV format."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export(doc, ExportFormat.CSV)
        
        assert isinstance(result, str)

    def test_export_with_format_excel(self):
        """Test export with Excel format."""
        exporter = Exporter()
        doc = create_test_document()
        
        result = exporter.export(doc, ExportFormat.EXCEL)
        
        assert isinstance(result, bytes)

    def test_export_with_invalid_format(self):
        """Test export with invalid format raises error."""
        exporter = Exporter()
        doc = create_test_document()
        
        with pytest.raises(ValueError):
            exporter.export(doc, "invalid_format")


class TestGetExporter:
    """Tests for exporter singleton."""

    def test_get_exporter_returns_instance(self):
        """Test that get_exporter returns an instance."""
        exporter = get_exporter()
        
        assert exporter is not None
        assert isinstance(exporter, Exporter)

    def test_get_exporter_returns_same_instance(self):
        """Test that get_exporter returns cached instance."""
        e1 = get_exporter()
        e2 = get_exporter()
        
        assert e1 is e2


class TestExporterWithNoSummary:
    """Tests for export when document has no summary."""

    def test_export_json_no_summary(self):
        """Test JSON export when document has no summary."""
        exporter = Exporter()
        doc = create_test_document()
        doc.summary = None
        
        result = exporter.export_json(doc, include_summary=True)
        
        data = json.loads(result)
        assert "summary" not in data

    def test_export_excel_no_summary(self):
        """Test Excel export when document has no summary."""
        exporter = Exporter()
        doc = create_test_document()
        doc.summary = None
        
        result = exporter.export_excel(doc, include_summary=True)
        
        # Should not raise error
        assert isinstance(result, bytes)


class TestExporterConfiguration:
    """Tests for exporter configuration."""

    def test_exporter_uses_settings(self):
        """Test that exporter uses settings configuration."""
        exporter = Exporter()
        
        # Check that settings are loaded
        assert exporter._json_indent >= 0
        assert exporter._csv_delimiter is not None
        assert exporter._sheet_names is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
