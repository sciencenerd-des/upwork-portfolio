"""
Summarization Module

Generates document summaries using LLM with fallback options.
- Primary: Claude via OpenRouter
- Fallback: GPT-4 via OpenRouter
- Basic fallback: Extractive summarization
"""

import os
import json
import logging
import re
from typing import Optional
from collections import Counter

import httpx

from app.config import get_settings, get_prompts
from app.models import DocumentSummary, DocumentType

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM client using OpenRouter API.
    """

    def __init__(self):
        self.settings = get_settings()
        # Use settings instead of os.getenv for consistent configuration
        self._api_key = self.settings.openrouter_api_key
        self._base_url = self.settings.llm.base_url
        self._primary_model = self.settings.llm.primary_model
        self._fallback_model = self.settings.llm.fallback_model
        self._max_tokens = self.settings.llm.max_tokens
        self._temperature = self.settings.llm.temperature
        self._timeout = self.settings.llm.timeout_seconds
        # Reusable HTTP client for connection pooling
        self._http_client: Optional[httpx.Client] = None

    def _get_http_client(self) -> httpx.Client:
        """Get or create reusable HTTP client for connection pooling."""
        if self._http_client is None:
            self._http_client = httpx.Client(
                timeout=self._timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._http_client

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        Send chat request to LLM.

        Args:
            system_prompt: System message
            user_prompt: User message
            model: Model to use (default: primary model)

        Returns:
            LLM response text or None if failed
        """
        if not self._api_key:
            logger.warning("OPENROUTER_API_KEY not set")
            return None

        model = model or self._primary_model

        try:
            client = self._get_http_client()
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://document-intelligence.local",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": self._max_tokens,
                    "temperature": self._temperature,
                }
            )
            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"LLM request failed: {e}")

        return None

    def chat_with_fallback(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Send chat request with automatic fallback to secondary model.
        """
        # Try primary model
        response = self.chat(system_prompt, user_prompt, self._primary_model)
        if response:
            return response

        logger.info(f"Primary model failed, trying fallback: {self._fallback_model}")

        # Try fallback model
        return self.chat(system_prompt, user_prompt, self._fallback_model)


class Summarizer:
    """
    Document summarization using LLM with fallback to extractive methods.
    """

    def __init__(self):
        self.settings = get_settings()
        self.prompts = get_prompts()
        self._llm = LLMClient()
        self._min_points = self.settings.summarization.min_key_points
        self._max_points = self.settings.summarization.max_key_points

    def summarize(self, text: str, word_count: int = 0, page_count: int = 0) -> DocumentSummary:
        """
        Generate document summary.

        Args:
            text: Document text to summarize
            word_count: Document word count (for metadata)
            page_count: Document page count (for metadata)

        Returns:
            DocumentSummary object
        """
        if not text.strip():
            return self._empty_summary(word_count, page_count)

        # Truncate text if too long (keep under token limit)
        max_chars = 15000  # Roughly 4000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "...[truncated]"

        # Try LLM summarization
        summary = self._llm_summarize(text)

        if summary:
            summary.word_count = word_count
            summary.page_count = page_count
            return summary

        # Fallback to extractive summarization
        logger.info("Using extractive summarization fallback")
        return self._extractive_summarize(text, word_count, page_count)

    def _llm_summarize(self, text: str) -> Optional[DocumentSummary]:
        """Generate summary using LLM."""
        system_prompt, user_prompt = self.prompts.format_summarization_prompt(
            document_text=text,
            min_points=self._min_points,
            max_points=self._max_points
        )

        response = self._llm.chat_with_fallback(system_prompt, user_prompt)

        if not response:
            return None

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response

            data = json.loads(json_str)

            # Map document type
            doc_type_str = data.get("document_type", "unknown").lower()
            doc_type = self._map_document_type(doc_type_str)

            return DocumentSummary(
                document_type=doc_type,
                executive_summary=data.get("executive_summary", data.get("summary", "")),
                key_points=data.get("key_points", [])[:self._max_points]
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Try to extract information from plain text
            return self._parse_plain_text_response(response)

    def _parse_plain_text_response(self, response: str) -> Optional[DocumentSummary]:
        """Try to extract summary from plain text response."""
        lines = response.strip().split("\n")

        doc_type = DocumentType.UNKNOWN
        summary = ""
        key_points = []

        for line in lines:
            line_lower = line.lower().strip()

            # Look for document type
            if "document type" in line_lower or "type:" in line_lower:
                doc_type = self._map_document_type(line)

            # Look for summary
            elif "summary" in line_lower and ":" in line:
                summary = line.split(":", 1)[1].strip()

            # Look for key points (bullet points)
            elif line.strip().startswith(("-", "*", "•", "1.", "2.", "3.")):
                point = re.sub(r'^[-*•\d.)\s]+', '', line).strip()
                if point:
                    key_points.append(point)

        if summary or key_points:
            return DocumentSummary(
                document_type=doc_type,
                executive_summary=summary,
                key_points=key_points[:self._max_points]
            )

        return None

    def _map_document_type(self, type_str: str) -> DocumentType:
        """Map string to DocumentType enum."""
        type_lower = type_str.lower()

        if "invoice" in type_lower:
            return DocumentType.INVOICE
        elif "contract" in type_lower or "agreement" in type_lower:
            return DocumentType.CONTRACT
        elif "receipt" in type_lower:
            return DocumentType.RECEIPT
        elif "report" in type_lower:
            return DocumentType.REPORT
        elif "letter" in type_lower:
            return DocumentType.LETTER
        elif "resume" in type_lower or "cv" in type_lower:
            return DocumentType.RESUME
        elif "legal" in type_lower:
            return DocumentType.LEGAL
        else:
            return DocumentType.UNKNOWN

    def _extractive_summarize(
        self,
        text: str,
        word_count: int,
        page_count: int
    ) -> DocumentSummary:
        """
        Generate extractive summary when LLM is unavailable.

        Uses sentence scoring based on:
        - Position (early sentences weighted higher)
        - Length (medium-length preferred)
        - Keyword frequency
        """
        sentences = self._split_sentences(text)

        if not sentences:
            return self._empty_summary(word_count, page_count)

        # Score sentences
        scored = self._score_sentences(sentences, text)

        # Select top sentences for summary
        top_sentences = sorted(scored, key=lambda x: x[1], reverse=True)[:3]

        # Sort by original order for coherence
        top_sentences.sort(key=lambda x: sentences.index(x[0]))

        summary_text = " ".join(s[0] for s in top_sentences)

        # Extract key points (next best sentences)
        remaining = sorted(scored, key=lambda x: x[1], reverse=True)[3:3 + self._max_points]
        key_points = [s[0] for s in remaining if len(s[0]) > 20]

        # Detect document type from patterns
        doc_type = self._detect_document_type(text)

        return DocumentSummary(
            document_type=doc_type,
            executive_summary=summary_text[:500],
            key_points=key_points,
            word_count=word_count,
            page_count=page_count
        )

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    def _score_sentences(self, sentences: list[str], full_text: str) -> list[tuple[str, float]]:
        """Score sentences for extractive summarization."""
        # Get word frequencies
        words = re.findall(r'\b\w+\b', full_text.lower())
        word_freq = Counter(words)

        # Remove common stopwords from consideration
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "must", "shall",
                     "of", "in", "to", "for", "on", "with", "at", "by", "from",
                     "as", "into", "through", "during", "before", "after", "above",
                     "below", "between", "under", "again", "further", "then", "once",
                     "and", "but", "or", "nor", "so", "yet", "both", "either",
                     "neither", "not", "only", "own", "same", "than", "too", "very",
                     "just", "can", "this", "that", "these", "those", "it", "its"}

        for sw in stopwords:
            word_freq.pop(sw, None)

        scored = []

        for i, sentence in enumerate(sentences):
            score = 0.0

            # Position score (first sentences get bonus)
            position_score = max(0, 1.0 - (i / len(sentences)) * 0.5)
            score += position_score * 2

            # Length score (prefer medium length)
            word_count = len(sentence.split())
            if 10 <= word_count <= 30:
                score += 1.5
            elif 5 <= word_count <= 50:
                score += 0.5

            # Keyword score
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            keyword_score = sum(word_freq.get(w, 0) for w in sentence_words if w not in stopwords)
            score += keyword_score * 0.01

            # Bonus for sentences with numbers/dates
            if re.search(r'\d+', sentence):
                score += 0.5

            scored.append((sentence, score))

        return scored

    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect document type from content patterns."""
        text_lower = text.lower()
        patterns = self.prompts.document_type_patterns

        scores = {}

        for doc_type, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[doc_type] = score

        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] >= 2:
                return self._map_document_type(best_type)

        return DocumentType.UNKNOWN

    def _empty_summary(self, word_count: int, page_count: int) -> DocumentSummary:
        """Return empty summary for empty documents."""
        return DocumentSummary(
            document_type=DocumentType.UNKNOWN,
            executive_summary="No content available for summarization.",
            key_points=[],
            word_count=word_count,
            page_count=page_count
        )


# Singleton instances
_llm_client: Optional[LLMClient] = None
_summarizer: Optional[Summarizer] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def get_summarizer() -> Summarizer:
    """Get or create summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer
