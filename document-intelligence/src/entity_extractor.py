"""Entity extraction using pragmatic regex heuristics."""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any

DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s*\d{4}|"
    r"\d{4}-\d{2}-\d{2})\b",
    re.IGNORECASE,
)
AMOUNT_PATTERN = re.compile(
    r"(?:[$€₹]\s?\d[\d,]*(?:\.\d{2})?|\b\d[\d,]*(?:\.\d{2})\s?(?:USD|EUR|INR|GBP)\b)",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b")
IDENTIFIER_PATTERN = re.compile(
    r"\b(?:Invoice|Contract|PO|Purchase Order|Agreement|Report)\s*(?:#|No\.?|Number)?\s*([A-Z0-9-]{4,})\b",
    re.IGNORECASE,
)
PERSON_PATTERN = re.compile(
    r"\b(?:Signed by|Prepared by|Approved by|Contact)\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})"
)
ORG_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z&,. ]+\s(?:Inc\.?|LLC|Ltd\.?|Corp\.?|Corporation|Company|Co\.?))\b"
)


def _unique_matches(values: list[str], limit: int = 10) -> list[str]:
    deduped = OrderedDict((value.strip(), None) for value in values if value.strip())
    return list(deduped.keys())[:limit]


def _build_items(values: list[str], label: str, confidence: float) -> list[dict[str, Any]]:
    return [{"value": value, "label": label, "confidence": confidence} for value in values]


def extract_entities(text: str) -> dict[str, list[dict[str, Any]]]:
    """Extract entities used in invoices, contracts, and reports."""
    dates = _unique_matches(DATE_PATTERN.findall(text), limit=12)
    amounts = _unique_matches(AMOUNT_PATTERN.findall(text), limit=12)
    emails = _unique_matches(EMAIL_PATTERN.findall(text), limit=12)
    phones = _unique_matches(PHONE_PATTERN.findall(text), limit=12)
    identifiers = _unique_matches(IDENTIFIER_PATTERN.findall(text), limit=12)
    persons = _unique_matches(PERSON_PATTERN.findall(text), limit=10)
    organizations = _unique_matches(ORG_PATTERN.findall(text), limit=10)

    return {
        "dates": _build_items(dates, "Date", 0.93),
        "amounts": _build_items(amounts, "Amount", 0.95),
        "organizations": _build_items(organizations, "Organization", 0.88),
        "persons": _build_items(persons, "Person", 0.86),
        "emails": _build_items(emails, "Email", 0.99),
        "phones": _build_items(phones, "Phone", 0.9),
        "identifiers": _build_items(identifiers, "Identifier", 0.91),
    }
