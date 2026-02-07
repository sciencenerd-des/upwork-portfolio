"""End-to-end document processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.document_loader import load_document
from src.entity_extractor import extract_entities
from src.summarizer import generate_summary, key_points
from src.text_processor import chunk_text, clean_text


@dataclass(slots=True)
class ProcessedDocument:
    document_id: str
    filename: str
    page_count: int
    word_count: int
    processing_mode: str
    summary: str
    key_points: list[str]
    text: str
    text_preview: str
    entities: dict[str, list[dict[str, object]]]
    chunks: list[str]
    suggested_questions: list[str]
    created_at: str

    def response_payload(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "filename": self.filename,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "processing_mode": self.processing_mode,
            "summary": self.summary,
            "key_points": self.key_points,
            "text_preview": self.text_preview,
            "entities": self.entities,
            "suggested_questions": self.suggested_questions,
            "created_at": self.created_at,
        }


def _generate_suggested_questions(
    filename: str, entities: dict[str, list[dict[str, object]]]
) -> list[str]:
    questions = [
        f"What is the main purpose of {filename}?",
        "What are the most important dates and deadlines?",
        "Which monetary values look most critical?",
    ]

    if entities.get("organizations"):
        questions.append("Which organizations are involved in this document?")
    if entities.get("persons"):
        questions.append("Who signed or approved this document?")

    return questions[:5]


def run_pipeline(file_bytes: bytes, filename: str) -> ProcessedDocument:
    loaded = load_document(file_bytes=file_bytes, filename=filename)
    cleaned = clean_text(loaded.text)

    if not cleaned:
        raise ValueError("No readable text found after processing.")

    chunks = chunk_text(cleaned)
    entities = extract_entities(cleaned)
    summary = generate_summary(cleaned)
    points = key_points(cleaned)
    word_count = len(cleaned.split())

    return ProcessedDocument(
        document_id=loaded.document_id,
        filename=loaded.filename,
        page_count=loaded.page_count,
        word_count=word_count,
        processing_mode="OCR" if loaded.used_ocr else "Native Text Extraction",
        summary=summary,
        key_points=points,
        text=cleaned,
        text_preview=cleaned[:1400],
        entities=entities,
        chunks=chunks,
        suggested_questions=_generate_suggested_questions(loaded.filename, entities),
        created_at=datetime.now(timezone.utc).isoformat(),
    )
