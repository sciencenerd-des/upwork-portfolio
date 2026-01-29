"""
RAG Q&A Engine Module

Provides question answering with citations using RAG (Retrieval Augmented Generation).
- Retrieve relevant chunks via vector search
- Generate answers using LLM
- Extract source citations
- Handle "not found" gracefully
- Multi-turn conversation support
"""

import json
import logging
import re
from typing import Optional
from datetime import datetime

from app.config import get_settings, get_prompts
from app.models import QARequest, QAResponse, QASource, QAMessage
from src.vector_store import DocumentVectorStore, get_document_vector_store
from src.document_store import get_document_store
from src.summarizer import LLMClient, get_llm_client

logger = logging.getLogger(__name__)


class QAEngine:
    """
    RAG-based question answering engine.
    """

    def __init__(self):
        self.settings = get_settings()
        self.prompts = get_prompts()
        self._llm = get_llm_client()
        self._vector_store = get_document_vector_store()

        self._max_context_chunks = self.settings.qa.max_context_chunks
        self._max_history = self.settings.qa.max_conversation_history
        self._no_answer_response = self.settings.qa.no_answer_response
        self._include_citations = self.settings.qa.include_citations
        self._generate_followup = self.settings.qa.generate_followup_questions

    def answer(
        self,
        doc_id: str,
        question: str,
        conversation_history: Optional[list[QAMessage]] = None,
        include_sources: bool = True
    ) -> QAResponse:
        """
        Answer a question about a document.

        Args:
            doc_id: Document identifier
            question: User's question
            conversation_history: Previous Q&A messages
            include_sources: Whether to include source citations

        Returns:
            QAResponse with answer, sources, and suggested questions

        Raises:
            ValueError: If doc_id or question is invalid
        """
        import time
        start_time = time.time()

        # Input validation
        if not doc_id or not doc_id.strip():
            raise ValueError("Document ID cannot be empty")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        # Check if document exists
        doc_store = get_document_store()
        if not doc_store.document_exists(doc_id):
            raise ValueError(f"Document {doc_id} not found")

        # Retrieve relevant context via vector search
        context_chunks = self._retrieve_context(doc_id, question)

        # If no context from vector search, fall back to lexical/keyword search
        if not context_chunks:
            logger.info(f"No vector context found for doc {doc_id}, trying lexical fallback")
            context_chunks = self._lexical_fallback(doc_id, question)

        # If still no context after fallback, return no context response
        if not context_chunks:
            return self._no_context_response(start_time)

        # Build context string
        context = self._build_context(context_chunks)

        # Format conversation history
        history_str = self._format_history(conversation_history)

        # Generate answer using LLM
        response = self._generate_answer(context, question, history_str)

        if response:
            response.processing_time_ms = int((time.time() - start_time) * 1000)

            # Add sources from retrieved chunks if not in response
            if include_sources and not response.sources:
                response.sources = self._extract_sources_from_chunks(context_chunks)

            return response

        # Fallback response
        return self._fallback_response(context_chunks, question, start_time)

    def _retrieve_context(self, doc_id: str, question: str) -> list[dict]:
        """Retrieve relevant chunks from vector store."""
        try:
            results = self._vector_store.search_document(
                doc_id=doc_id,
                query=question,
                top_k=self._max_context_chunks
            )
            return results
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []

    def _lexical_fallback(self, doc_id: str, question: str) -> list[dict]:
        """
        Fallback to lexical/keyword search when vector retrieval fails.
        Uses stored document chunks with simple keyword matching.
        """
        doc_store = get_document_store()
        doc = doc_store.get_document(doc_id)

        if not doc:
            return []

        # Prepare question keywords (lowercase, filter stopwords)
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "this", "that", "these", "those", "what", "which", "who", "whom",
            "where", "when", "why", "how", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "as", "about", "into", "through", "during",
            "before", "after", "above", "below", "between", "and", "or", "not",
            "it", "its", "i", "me", "my", "you", "your", "he", "she", "we", "they"
        }

        question_lower = question.lower()
        question_words = set(
            w for w in re.findall(r'\b\w+\b', question_lower)
            if w not in stopwords and len(w) > 2
        )

        if not question_words:
            # No meaningful keywords, return empty
            return []

        scored_chunks = []

        # Score each stored chunk by keyword overlap
        for chunk in doc.chunks:
            chunk_text = chunk.text.lower()
            chunk_words = set(re.findall(r'\b\w+\b', chunk_text))

            # Calculate overlap score
            overlap = question_words & chunk_words
            if overlap:
                # Score = number of matching keywords / total question keywords
                score = len(overlap) / len(question_words)
                scored_chunks.append({
                    "text": chunk.text,
                    "metadata": {
                        "page_number": chunk.page_number,
                        "chunk_id": chunk.chunk_id,
                    },
                    "score": score,
                    "overlap_count": len(overlap)
                })

        # Sort by score (descending) and return top-k
        scored_chunks.sort(key=lambda x: (-x["score"], -x["overlap_count"]))

        # Return top chunks that meet a minimum threshold
        min_score_threshold = 0.1  # At least 10% of keywords should match
        results = [
            c for c in scored_chunks[:self._max_context_chunks]
            if c["score"] >= min_score_threshold
        ]

        if results:
            logger.info(f"Lexical fallback found {len(results)} relevant chunks")

        return results

    def _build_context(self, chunks: list[dict]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []

        for i, chunk in enumerate(chunks):
            page_info = ""
            if chunk.get("metadata", {}).get("page_number"):
                page_info = f" (Page {chunk['metadata']['page_number']})"

            context_parts.append(f"[Chunk {i + 1}]{page_info}:\n{chunk['text']}")

        return "\n\n".join(context_parts)

    def _format_history(self, history: Optional[list[QAMessage]]) -> str:
        """Format conversation history for prompt."""
        if not history:
            return ""

        # Keep only recent history
        recent = history[-self._max_history:]

        formatted = []
        for msg in recent:
            role = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")

        return "\n".join(formatted)

    def _generate_answer(
        self,
        context: str,
        question: str,
        history: str
    ) -> Optional[QAResponse]:
        """Generate answer using LLM."""
        system_prompt, user_prompt = self.prompts.format_qa_prompt(
            context=context,
            question=question,
            conversation_history=history,
            no_answer_response=self._no_answer_response
        )

        response_text = self._llm.chat_with_fallback(system_prompt, user_prompt)

        if not response_text:
            return None

        return self._parse_llm_response(response_text)

    def _parse_llm_response(self, response: str) -> QAResponse:
        """Parse LLM response into QAResponse."""
        try:
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # Plain text response
                    return QAResponse(
                        answer=response.strip(),
                        confidence=0.7,
                        sources=[],
                        suggested_questions=[]
                    )

            data = json.loads(json_str)

            # Parse sources
            sources = []
            for src in data.get("sources", []):
                sources.append(QASource(
                    page=src.get("page"),
                    section=src.get("section"),
                    quote=src.get("quote", ""),
                    relevance_score=src.get("relevance_score")
                ))

            return QAResponse(
                answer=data.get("answer", ""),
                confidence=float(data.get("confidence", 0.7)),
                sources=sources,
                suggested_questions=data.get("suggested_questions", [])[:3]
            )

        except json.JSONDecodeError:
            # Return plain text response
            return QAResponse(
                answer=response.strip(),
                confidence=0.6,
                sources=[],
                suggested_questions=[]
            )

    def _extract_sources_from_chunks(self, chunks: list[dict]) -> list[QASource]:
        """Extract source citations from retrieved chunks."""
        sources = []

        for chunk in chunks[:3]:  # Limit to top 3
            metadata = chunk.get("metadata", {})
            text = chunk.get("text", "")

            # Get a relevant quote (first 100 chars)
            quote = text[:100].strip()
            if len(text) > 100:
                quote += "..."

            sources.append(QASource(
                page=metadata.get("page_number"),
                section=metadata.get("section"),
                quote=quote,
                relevance_score=chunk.get("score")
            ))

        return sources

    def _no_context_response(self, start_time: float) -> QAResponse:
        """Return response when no relevant context is found in the document."""
        import time

        return QAResponse(
            answer=self._no_answer_response,
            confidence=0.0,
            sources=[],
            suggested_questions=[
                "What is the main purpose of this document?",
                "What are the key dates mentioned?",
                "What is the total amount?",
            ],
            processing_time_ms=int((time.time() - start_time) * 1000)
        )

    def _fallback_response(
        self,
        chunks: list[dict],
        question: str,
        start_time: float
    ) -> QAResponse:
        """Generate fallback response using keyword matching."""
        import time

        # Simple keyword matching
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))

        best_chunk = None
        best_score = 0

        for chunk in chunks:
            text_lower = chunk.get("text", "").lower()
            text_words = set(re.findall(r'\b\w+\b', text_lower))

            # Calculate overlap
            overlap = len(question_words & text_words)
            if overlap > best_score:
                best_score = overlap
                best_chunk = chunk

        if best_chunk and best_score > 0:
            answer = f"Based on the document, here's relevant information:\n\n{best_chunk['text'][:500]}"
            if len(best_chunk['text']) > 500:
                answer += "..."

            sources = [QASource(
                page=best_chunk.get("metadata", {}).get("page_number"),
                quote=best_chunk['text'][:100]
            )]
        else:
            answer = self._no_answer_response
            sources = []

        return QAResponse(
            answer=answer,
            confidence=0.5 if best_chunk else 0.0,
            sources=sources,
            suggested_questions=[],
            processing_time_ms=int((time.time() - start_time) * 1000)
        )

    def answer_batch(
        self,
        doc_id: str,
        questions: list[str]
    ) -> list[QAResponse]:
        """
        Answer multiple questions about a document.

        Args:
            doc_id: Document identifier
            questions: List of questions

        Returns:
            List of QAResponse objects
        """
        responses = []
        history = []

        for question in questions:
            response = self.answer(doc_id, question, history)
            responses.append(response)

            # Add to history for context
            history.append(QAMessage(role="user", content=question))
            history.append(QAMessage(role="assistant", content=response.answer))

        return responses

    def generate_suggested_questions(self, doc_id: str, context: str = "") -> list[str]:
        """
        Generate suggested questions based on document content.

        Args:
            doc_id: Document identifier
            context: Optional context text

        Returns:
            List of suggested questions
        """
        # If no context provided, get some from vector store
        if not context:
            chunks = self._retrieve_context(doc_id, "summary overview main points")
            if chunks:
                context = " ".join(c.get("text", "")[:200] for c in chunks[:3])

        if not context:
            return [
                "What is the main purpose of this document?",
                "What are the key dates mentioned?",
                "Who are the parties involved?",
            ]

        # Try to generate using LLM
        prompt = f"""Based on this document excerpt, suggest 3-5 specific questions a user might want to ask:

Document excerpt:
{context[:1000]}

Return only the questions, one per line, without numbering."""

        response = self._llm.chat(
            system_prompt="You are a helpful assistant that generates relevant questions.",
            user_prompt=prompt
        )

        if response:
            questions = [q.strip() for q in response.strip().split("\n") if q.strip()]
            return questions[:5]

        # Default questions
        return [
            "What is the main purpose of this document?",
            "What are the key dates mentioned?",
            "What is the total amount?",
            "Who are the parties involved?",
        ]


# Singleton instance
_qa_engine: Optional[QAEngine] = None


def get_qa_engine() -> QAEngine:
    """Get or create Q&A engine instance."""
    global _qa_engine
    if _qa_engine is None:
        _qa_engine = QAEngine()
    return _qa_engine
