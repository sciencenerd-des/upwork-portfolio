"""
Tests for Summarizer Module.
Covers LLM path (real OpenRouter) and extractive fallback.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestLLMClient:
    """Tests for LLMClient class."""

    def test_client_initialization_without_key(self):
        """Test LLMClient initializes without API key."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            from src.summarizer import LLMClient
            
            client = LLMClient()
            assert client._api_key is None or client._api_key == ""

    def test_client_initialization_with_key(self):
        """Test LLMClient initializes with API key from settings."""
        from src.summarizer import LLMClient
        from app.config import get_settings
        
        settings = get_settings()
        client = LLMClient()
        
        # Should use settings value
        assert client._api_key == settings.openrouter_api_key

    def test_chat_without_api_key_returns_none(self):
        """Test that chat returns None without API key."""
        from src.summarizer import LLMClient
        
        client = LLMClient()
        client._api_key = None
        
        result = client.chat("system", "user")
        assert result is None

    def test_http_client_reuse(self):
        """Test that HTTP client is reused."""
        from src.summarizer import LLMClient
        
        client = LLMClient()
        
        http1 = client._get_http_client()
        http2 = client._get_http_client()
        
        assert http1 is http2

    def test_close_releases_client(self):
        """Test that close releases HTTP client."""
        from src.summarizer import LLMClient
        
        client = LLMClient()
        _ = client._get_http_client()
        
        assert client._http_client is not None
        
        client.close()
        
        assert client._http_client is None


class TestSummarizer:
    """Tests for Summarizer class."""

    def test_summarizer_initialization(self):
        """Test Summarizer initializes correctly."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        assert summarizer._min_points >= 1
        assert summarizer._max_points >= summarizer._min_points

    def test_summarize_empty_text(self):
        """Test summarizing empty text returns empty summary."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        result = summarizer.summarize("")
        
        assert result is not None
        assert result.executive_summary == ""
        assert result.key_points == []

    def test_summarize_whitespace_text(self):
        """Test summarizing whitespace-only text."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        result = summarizer.summarize("   \n\t  ")
        
        assert result is not None
        assert result.executive_summary == ""

    def test_extractive_summarize(self):
        """Test extractive summarization fallback."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        text = """
        Invoice Number: INV-2024-001
        Date: January 15, 2024
        
        This is an invoice for services rendered. The total amount due is $5,000.
        
        Payment is due within 30 days. Please remit payment to the address below.
        
        Thank you for your business. We appreciate your continued partnership.
        """
        
        result = summarizer._extractive_summarize(text, word_count=50, page_count=1)
        
        assert result is not None
        assert len(result.executive_summary) > 0
        assert len(result.key_points) >= 1

    def test_summarize_with_metadata(self):
        """Test summarize includes word and page count."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        result = summarizer.summarize("Test content", word_count=100, page_count=2)
        
        assert result.word_count == 100
        assert result.page_count == 2

    def test_summarize_long_text_truncation(self):
        """Test that long text is truncated before summarization."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        # Create a very long text
        long_text = "This is a test sentence. " * 5000
        
        # Should not raise an error
        result = summarizer.summarize(long_text)
        
        assert result is not None


class TestDocumentTypeDetection:
    """Tests for document type detection in summarizer."""

    def test_detect_invoice_type(self):
        """Test detection of invoice document type."""
        from src.summarizer import Summarizer
        from app.models import DocumentType
        
        summarizer = Summarizer()
        
        text = "Invoice Number: INV-001 Amount Due: $500 Payment Terms: Net 30"
        
        result = summarizer._extractive_summarize(text, 10, 1)
        
        # Should detect as invoice
        assert result.document_type == DocumentType.INVOICE

    def test_detect_contract_type(self):
        """Test detection of contract document type."""
        from src.summarizer import Summarizer
        from app.models import DocumentType
        
        summarizer = Summarizer()
        
        text = "This Agreement is entered into between Party A and Party B. Terms and conditions apply."
        
        result = summarizer._extractive_summarize(text, 10, 1)
        
        # Should detect as contract
        assert result.document_type == DocumentType.CONTRACT

    def test_detect_receipt_type(self):
        """Test detection of receipt document type."""
        from src.summarizer import Summarizer
        from app.models import DocumentType
        
        summarizer = Summarizer()
        
        text = "Receipt for payment received. Thank you for your purchase. Total: $100"
        
        result = summarizer._extractive_summarize(text, 10, 1)
        
        # Should detect as receipt
        assert result.document_type == DocumentType.RECEIPT


class TestKeyPointExtraction:
    """Tests for key point extraction."""

    def test_extract_key_points_from_text(self):
        """Test extracting key points from text."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        text = """
        First important point about the document.
        
        Second key finding from the analysis.
        
        Third significant observation noted.
        
        Fourth relevant detail to consider.
        """
        
        result = summarizer._extractive_summarize(text, 50, 1)
        
        assert len(result.key_points) >= 1
        assert len(result.key_points) <= summarizer._max_points

    def test_key_points_limit(self):
        """Test that key points respect max limit."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        # Create text with many sentences
        text = ". ".join([f"Point number {i} is important" for i in range(20)]) + "."
        
        result = summarizer._extractive_summarize(text, 100, 1)
        
        assert len(result.key_points) <= summarizer._max_points


class TestSummarizerIntegration:
    """Integration tests for summarizer with real API (if available)."""

    @pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not set"
    )
    def test_llm_summarize_real(self):
        """Test LLM summarization with real API."""
        from src.summarizer import Summarizer
        
        summarizer = Summarizer()
        
        text = """
        This document outlines the quarterly financial results for Q4 2024.
        Total revenue reached $10 million, representing a 15% increase year-over-year.
        Operating expenses were $6 million, resulting in a net profit of $4 million.
        Key growth drivers included new product launches and market expansion.
        """
        
        result = summarizer.summarize(text, word_count=50, page_count=1)
        
        assert result is not None
        assert len(result.executive_summary) > 0
        assert len(result.key_points) >= summarizer._min_points


class TestGetSummarizer:
    """Tests for summarizer singleton."""

    def test_get_summarizer_returns_instance(self):
        """Test that get_summarizer returns an instance."""
        from src.summarizer import get_summarizer
        
        summarizer = get_summarizer()
        
        assert summarizer is not None

    def test_get_summarizer_returns_same_instance(self):
        """Test that get_summarizer returns cached instance."""
        from src.summarizer import get_summarizer
        
        s1 = get_summarizer()
        s2 = get_summarizer()
        
        assert s1 is s2


class TestLLMClientWithMock:
    """Tests for LLMClient with mocked responses."""

    def test_chat_success(self):
        """Test successful chat with mocked response."""
        from src.summarizer import LLMClient
        
        client = LLMClient()
        client._api_key = "test_key"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(client, '_get_http_client') as mock_http:
            mock_http_client = MagicMock()
            mock_http_client.post.return_value = mock_response
            mock_http.return_value = mock_http_client
            
            result = client.chat("system prompt", "user prompt")
            
            assert result == "Test response"

    def test_chat_with_fallback(self):
        """Test chat with fallback on primary failure."""
        from src.summarizer import LLMClient
        
        client = LLMClient()
        client._api_key = "test_key"
        
        # First call fails, second succeeds
        call_count = [0]
        
        def mock_post(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Primary failed")
            
            response = MagicMock()
            response.json.return_value = {
                "choices": [{"message": {"content": "Fallback response"}}]
            }
            response.raise_for_status = MagicMock()
            return response
        
        with patch.object(client, '_get_http_client') as mock_http:
            mock_http_client = MagicMock()
            mock_http_client.post = mock_post
            mock_http.return_value = mock_http_client
            
            result = client.chat_with_fallback("system", "user")
            
            assert result == "Fallback response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
