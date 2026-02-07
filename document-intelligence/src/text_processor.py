"""Text cleaning and chunking helpers."""

from __future__ import annotations

import re

STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "is",
    "are",
    "was",
    "were",
    "to",
    "of",
    "for",
    "on",
    "in",
    "with",
    "at",
    "from",
    "by",
    "this",
    "that",
    "it",
    "as",
    "be",
    "has",
    "have",
}


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sentence_split(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9]+", text)]
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def chunk_text(text: str, max_chars: int = 900, overlap_chars: int = 120) -> list[str]:
    """Chunk text into overlapping windows to support retrieval."""
    if not text:
        return []

    sentences = sentence_split(text)
    if not sentences:
        return [text[:max_chars]]

    built: list[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            built.append(current)
        overlap = current[-overlap_chars:].strip() if current else ""
        current = f"{overlap} {sentence}".strip()

    if current:
        built.append(current)

    return built
