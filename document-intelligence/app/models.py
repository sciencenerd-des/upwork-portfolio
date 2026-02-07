"""Pydantic models for API contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProcessResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    word_count: int
    processing_mode: str
    summary: str
    key_points: list[str]
    text_preview: str
    entities: dict[str, list[dict[str, Any]]]
    suggested_questions: list[str]
    created_at: str


class QARequest(BaseModel):
    document_id: str = Field(min_length=4)
    question: str = Field(min_length=3)


class QAResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
