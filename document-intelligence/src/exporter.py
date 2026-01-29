"""
Export Module

Exports document data to various formats.
- JSON: Structured format with all data
- CSV: Flattened entities for spreadsheet import
- Excel: Formatted workbook with multiple sheets
"""

import io
import json
import csv
import logging
import re
from datetime import datetime
from pathlib import PurePath
from typing import Optional, Union

import pandas as pd

from app.config import get_settings
from app.models import (
    ProcessedDocument,
    DocumentSummary,
    ExtractedEntities,
    ExportFormat,
)

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    Removes directory components and dangerous characters.
    """
    # Normalize path separators (handle both Unix and Windows paths)
    filename = filename.replace('\\', '/')

    # Remove any directory components (Unix and Windows)
    filename = PurePath(filename).name

    # Remove potentially dangerous characters
    filename = re.sub(r'[^\w\-.]', '_', filename)

    # Remove leading dots and underscores
    filename = filename.lstrip('._')

    # Ensure it's not empty
    if not filename:
        filename = 'export'

    return filename


class Exporter:
    """
    Exports document data to JSON, CSV, and Excel formats.
    """

    def __init__(self):
        self.settings = get_settings()
        self._json_indent = self.settings.export.json_indent
        self._csv_delimiter = self.settings.export.csv_delimiter
        self._sheet_names = self.settings.export.excel_sheet_names

    def export(
        self,
        document: ProcessedDocument,
        format: ExportFormat,
        include_summary: bool = True,
        include_entities: bool = True,
        include_raw_text: bool = False
    ) -> Union[str, bytes]:
        """
        Export document data to specified format.

        Args:
            document: ProcessedDocument to export
            format: Export format (json, csv, excel)
            include_summary: Include document summary
            include_entities: Include extracted entities
            include_raw_text: Include raw text content

        Returns:
            String for JSON/CSV, bytes for Excel
        """
        if format == ExportFormat.JSON:
            return self.export_json(
                document, include_summary, include_entities, include_raw_text
            )
        elif format == ExportFormat.CSV:
            return self.export_csv(document)
        elif format == ExportFormat.EXCEL:
            return self.export_excel(
                document, include_summary, include_entities, include_raw_text
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")

    # =========================================================================
    # JSON Export
    # =========================================================================

    def export_json(
        self,
        document: ProcessedDocument,
        include_summary: bool = True,
        include_entities: bool = True,
        include_raw_text: bool = False
    ) -> str:
        """Export document data to JSON format."""
        data = {
            "metadata": {
                "doc_id": document.metadata.doc_id,
                "filename": document.metadata.filename,
                "file_type": document.metadata.file_type,
                "file_size_bytes": document.metadata.file_size_bytes,
                "page_count": document.metadata.page_count,
                "upload_time": document.metadata.upload_time.isoformat(),
                "is_scanned": document.metadata.is_scanned,
                "processing_status": document.status.value,
            },
            "export_time": datetime.utcnow().isoformat(),
        }

        if include_summary and document.summary:
            data["summary"] = {
                "document_type": document.summary.document_type.value,
                "executive_summary": document.summary.executive_summary,
                "key_points": document.summary.key_points,
                "word_count": document.summary.word_count,
                "page_count": document.summary.page_count,
            }

        if include_entities:
            data["entities"] = self._entities_to_dict(document.entities)

        if include_raw_text:
            data["raw_text"] = document.raw_text
            data["pages"] = [
                {
                    "page_number": p.page_number,
                    "text": p.text,
                    "is_scanned": p.is_scanned,
                    "ocr_confidence": p.ocr_confidence,
                }
                for p in document.pages
            ]

        return json.dumps(data, indent=self._json_indent, ensure_ascii=False)

    def _entities_to_dict(self, entities: ExtractedEntities) -> dict:
        """Convert ExtractedEntities to dictionary."""
        return {
            "dates": [
                {
                    "value": e.value,
                    "parsed_date": e.parsed_date.isoformat() if e.parsed_date else None,
                    "confidence": e.confidence,
                    "page_number": e.page_number,
                }
                for e in entities.dates
            ],
            "amounts": [
                {
                    "value": e.value,
                    "numeric_value": e.numeric_value,
                    "currency": e.currency,
                    "confidence": e.confidence,
                    "page_number": e.page_number,
                }
                for e in entities.amounts
            ],
            "persons": [
                {
                    "value": e.value,
                    "confidence": e.confidence,
                    "page_number": e.page_number,
                }
                for e in entities.persons
            ],
            "organizations": [
                {
                    "value": e.value,
                    "confidence": e.confidence,
                    "page_number": e.page_number,
                }
                for e in entities.organizations
            ],
            "emails": [{"value": e.value, "confidence": e.confidence} for e in entities.emails],
            "phones": [{"value": e.value, "confidence": e.confidence} for e in entities.phones],
            "invoice_numbers": [{"value": e.value, "confidence": e.confidence} for e in entities.invoice_numbers],
            "gstins": [{"value": e.value, "confidence": e.confidence} for e in entities.gstins],
            "pans": [{"value": e.value, "confidence": e.confidence} for e in entities.pans],
            "total_count": entities.total_count,
        }

    # =========================================================================
    # CSV Export
    # =========================================================================

    def export_csv(self, document: ProcessedDocument) -> str:
        """
        Export entities to CSV format (flattened).
        Each entity is a row with type, value, confidence.
        """
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self._csv_delimiter)

        # Header
        writer.writerow([
            "entity_type",
            "value",
            "confidence",
            "page_number",
            "additional_info"
        ])

        # Dates
        for e in document.entities.dates:
            writer.writerow([
                "date",
                e.value,
                e.confidence,
                e.page_number or "",
                f"parsed: {e.parsed_date.isoformat() if e.parsed_date else ''}"
            ])

        # Amounts
        for e in document.entities.amounts:
            writer.writerow([
                "amount",
                e.value,
                e.confidence,
                e.page_number or "",
                f"numeric: {e.numeric_value}, currency: {e.currency}"
            ])

        # Persons
        for e in document.entities.persons:
            writer.writerow([
                "person",
                e.value,
                e.confidence,
                e.page_number or "",
                e.label or ""
            ])

        # Organizations
        for e in document.entities.organizations:
            writer.writerow([
                "organization",
                e.value,
                e.confidence,
                e.page_number or "",
                e.label or ""
            ])

        # Emails
        for e in document.entities.emails:
            writer.writerow(["email", e.value, e.confidence, "", ""])

        # Phones
        for e in document.entities.phones:
            writer.writerow(["phone", e.value, e.confidence, "", ""])

        # Invoice numbers
        for e in document.entities.invoice_numbers:
            writer.writerow(["invoice_number", e.value, e.confidence, "", ""])

        # GSTINs
        for e in document.entities.gstins:
            writer.writerow(["gstin", e.value, e.confidence, "", ""])

        # PANs
        for e in document.entities.pans:
            writer.writerow(["pan", e.value, e.confidence, "", ""])

        return output.getvalue()

    # =========================================================================
    # Excel Export
    # =========================================================================

    def export_excel(
        self,
        document: ProcessedDocument,
        include_summary: bool = True,
        include_entities: bool = True,
        include_raw_text: bool = False
    ) -> bytes:
        """
        Export document data to Excel format with multiple sheets.
        """
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            if include_summary and document.summary:
                self._write_summary_sheet(writer, document)

            # Entities sheet
            if include_entities:
                self._write_entities_sheet(writer, document)

            # Raw text sheet (optional)
            if include_raw_text:
                self._write_text_sheet(writer, document)

        output.seek(0)
        return output.read()

    def _write_summary_sheet(
        self,
        writer: pd.ExcelWriter,
        document: ProcessedDocument
    ) -> None:
        """Write summary sheet to Excel."""
        sheet_name = self._sheet_names.get("summary", "Summary")

        summary_data = []

        # Metadata
        summary_data.append(["Document Information", ""])
        summary_data.append(["Filename", document.metadata.filename])
        summary_data.append(["Pages", document.metadata.page_count])
        summary_data.append(["File Size", f"{document.metadata.file_size_bytes / 1024:.1f} KB"])
        summary_data.append(["Scanned", "Yes" if document.metadata.is_scanned else "No"])
        summary_data.append(["", ""])

        if document.summary:
            summary_data.append(["Document Summary", ""])
            summary_data.append(["Document Type", document.summary.document_type.value])
            summary_data.append(["Executive Summary", document.summary.executive_summary])
            summary_data.append(["", ""])
            summary_data.append(["Key Points", ""])

            for i, point in enumerate(document.summary.key_points, 1):
                summary_data.append([f"  {i}.", point])

        df = pd.DataFrame(summary_data, columns=["Field", "Value"])
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    def _write_entities_sheet(
        self,
        writer: pd.ExcelWriter,
        document: ProcessedDocument
    ) -> None:
        """Write entities sheet to Excel."""
        sheet_name = self._sheet_names.get("entities", "Entities")

        rows = []

        # Dates
        for e in document.entities.dates:
            rows.append({
                "Type": "Date",
                "Value": e.value,
                "Confidence": f"{e.confidence:.0%}",
                "Page": e.page_number or "",
                "Details": f"Parsed: {e.parsed_date.strftime('%Y-%m-%d') if e.parsed_date else 'N/A'}"
            })

        # Amounts
        for e in document.entities.amounts:
            rows.append({
                "Type": "Amount",
                "Value": e.value,
                "Confidence": f"{e.confidence:.0%}",
                "Page": e.page_number or "",
                "Details": f"{e.currency} {e.numeric_value:,.2f}" if e.numeric_value else ""
            })

        # Persons
        for e in document.entities.persons:
            rows.append({
                "Type": "Person",
                "Value": e.value,
                "Confidence": f"{e.confidence:.0%}",
                "Page": e.page_number or "",
                "Details": e.label or ""
            })

        # Organizations
        for e in document.entities.organizations:
            rows.append({
                "Type": "Organization",
                "Value": e.value,
                "Confidence": f"{e.confidence:.0%}",
                "Page": e.page_number or "",
                "Details": e.label or ""
            })

        # Other entities
        for e in document.entities.emails:
            rows.append({"Type": "Email", "Value": e.value, "Confidence": f"{e.confidence:.0%}", "Page": "", "Details": ""})

        for e in document.entities.phones:
            rows.append({"Type": "Phone", "Value": e.value, "Confidence": f"{e.confidence:.0%}", "Page": "", "Details": ""})

        for e in document.entities.invoice_numbers:
            rows.append({"Type": "Invoice #", "Value": e.value, "Confidence": f"{e.confidence:.0%}", "Page": "", "Details": ""})

        for e in document.entities.gstins:
            rows.append({"Type": "GSTIN", "Value": e.value, "Confidence": f"{e.confidence:.0%}", "Page": "", "Details": ""})

        for e in document.entities.pans:
            rows.append({"Type": "PAN", "Value": e.value, "Confidence": f"{e.confidence:.0%}", "Page": "", "Details": ""})

        if rows:
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # Empty sheet with headers
            df = pd.DataFrame(columns=["Type", "Value", "Confidence", "Page", "Details"])
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def _write_text_sheet(
        self,
        writer: pd.ExcelWriter,
        document: ProcessedDocument
    ) -> None:
        """Write raw text sheet to Excel."""
        sheet_name = self._sheet_names.get("raw_text", "Raw Text")

        rows = []
        for page in document.pages:
            rows.append({
                "Page": page.page_number,
                "Text": page.text[:32000],  # Excel cell limit
                "Scanned": "Yes" if page.is_scanned else "No",
                "OCR Confidence": f"{page.ocr_confidence:.0%}" if page.ocr_confidence else "N/A"
            })

        if rows:
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # =========================================================================
    # Selective Export
    # =========================================================================

    def export_entities_only(
        self,
        entities: ExtractedEntities,
        format: ExportFormat
    ) -> Union[str, bytes]:
        """Export only entities without full document."""
        if format == ExportFormat.JSON:
            data = {
                "entities": self._entities_to_dict(entities),
                "export_time": datetime.utcnow().isoformat(),
            }
            return json.dumps(data, indent=self._json_indent, ensure_ascii=False)

        elif format == ExportFormat.CSV:
            # Create temporary document for CSV export
            from app.models import ProcessedDocument, DocumentMetadata, DocumentStatus

            temp_doc = ProcessedDocument(
                metadata=DocumentMetadata(
                    doc_id="temp",
                    filename="entities_export",
                    file_size_bytes=0,
                    file_type=".json",
                    page_count=0
                ),
                status=DocumentStatus.COMPLETED,
                raw_text="",
                pages=[],
                chunks=[],
                entities=entities
            )
            return self.export_csv(temp_doc)

        else:
            raise ValueError(f"Unsupported format for entities export: {format}")

    def export_summary_only(
        self,
        summary: DocumentSummary,
        format: ExportFormat
    ) -> str:
        """Export only summary."""
        if format == ExportFormat.JSON:
            data = {
                "summary": {
                    "document_type": summary.document_type.value,
                    "executive_summary": summary.executive_summary,
                    "key_points": summary.key_points,
                    "word_count": summary.word_count,
                    "page_count": summary.page_count,
                },
                "export_time": datetime.utcnow().isoformat(),
            }
            return json.dumps(data, indent=self._json_indent, ensure_ascii=False)

        elif format == ExportFormat.CSV:
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(["Field", "Value"])
            writer.writerow(["Document Type", summary.document_type.value])
            writer.writerow(["Executive Summary", summary.executive_summary])
            writer.writerow(["Word Count", summary.word_count])
            writer.writerow(["Page Count", summary.page_count])
            writer.writerow(["", ""])
            writer.writerow(["Key Points", ""])

            for i, point in enumerate(summary.key_points, 1):
                writer.writerow([f"Point {i}", point])

            return output.getvalue()

        else:
            raise ValueError(f"Unsupported format for summary export: {format}")


# Singleton instance
_exporter: Optional[Exporter] = None


def get_exporter() -> Exporter:
    """Get or create exporter instance."""
    global _exporter
    if _exporter is None:
        _exporter = Exporter()
    return _exporter
