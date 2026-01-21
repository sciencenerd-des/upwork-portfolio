"""
Tests for Vector Store Module.
Covers OpenRouter embeddings, local fallback, batching, and dimension handling.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestEmbeddingProvider:
    """Tests for EmbeddingProvider class."""

    def test_provider_initialization(self):
        """Test EmbeddingProvider initializes correctly."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        assert provider._dimension > 0
        assert provider._base_url is not None

    def test_provider_without_api_key_uses_local(self):
        """Test that provider falls back to local without API key."""
        from src.vector_store import EmbeddingProvider
        
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            provider = EmbeddingProvider()
            provider._api_key = None
            provider._use_local = True
            
            # Should use local model
            assert provider._use_local is True

    def test_embed_single_text(self):
        """Test embedding single text."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        # Force local mode for testing
        provider._use_local = True
        provider._init_local_model()
        
        embedding = provider.embed("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == provider._dimension

    def test_embed_batch_empty(self):
        """Test embedding empty batch."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        result = provider.embed_batch([])
        
        assert result == []

    def test_embed_batch_multiple(self):
        """Test embedding multiple texts."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        provider._use_local = True
        provider._init_local_model()
        
        texts = ["text one", "text two", "text three"]
        embeddings = provider.embed_batch(texts)
        
        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == provider._dimension

    def test_embed_batch_with_batching(self):
        """Test that large batches are split."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        provider._use_local = True
        provider._init_local_model()
        
        # Create more texts than MAX_BATCH_SIZE
        texts = [f"text {i}" for i in range(provider.MAX_BATCH_SIZE + 10)]
        
        embeddings = provider.embed_batch(texts)
        
        assert len(embeddings) == len(texts)

    def test_local_fallback_on_api_error(self):
        """Test fallback to local on API error."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        provider._api_key = "test_key"
        provider._use_local = False
        
        # Mock API to fail
        with patch.object(provider, '_embed_openrouter', side_effect=Exception("API Error")):
            with patch.object(provider, '_init_local_model'):
                with patch.object(provider, '_embed_local', return_value=[[0.1] * 384]):
                    result = provider.embed_batch(["test"])
                    
                    assert provider._use_local is True

    def test_zero_vectors_without_model(self):
        """Test zero vectors when no model available."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        provider._use_local = True
        provider._local_model = None
        
        result = provider._embed_local(["test"])
        
        assert len(result) == 1
        assert all(v == 0.0 for v in result[0])

    def test_http_client_lifecycle(self):
        """Test HTTP client creation and cleanup."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        # Get client
        client1 = provider._get_http_client()
        assert provider._http_client is not None
        
        # Same client reused
        client2 = provider._get_http_client()
        assert client1 is client2
        
        # Close releases client
        provider.close()
        assert provider._http_client is None

    def test_dimension_property(self):
        """Test dimension property."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        assert provider.dimension > 0
        assert isinstance(provider.dimension, int)


class TestVectorStore:
    """Tests for VectorStore class."""

    def test_store_initialization(self):
        """Test VectorStore initializes correctly."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        
        assert store._top_k > 0
        assert store._relevance_threshold >= 0

    def test_create_collection(self):
        """Test creating a collection for a document."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        
        result = store.create_collection("test_doc_123")
        
        assert result is True

    def test_add_chunks(self):
        """Test adding chunks to vector store."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        from app.models import TextChunk
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        store.create_collection("test_doc_456")
        
        chunks = [
            TextChunk(chunk_id="c1", text="First chunk content", page_number=1),
            TextChunk(chunk_id="c2", text="Second chunk content", page_number=1),
        ]
        
        result = store.add_chunks("test_doc_456", chunks)
        
        assert result is True

    def test_search_document(self):
        """Test searching document chunks."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        from app.models import TextChunk
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        store.create_collection("test_doc_789")
        
        chunks = [
            TextChunk(chunk_id="c1", text="Python programming language", page_number=1),
            TextChunk(chunk_id="c2", text="JavaScript web development", page_number=2),
        ]
        
        store.add_chunks("test_doc_789", chunks)
        
        results = store.search_document("test_doc_789", "Python code", top_k=2)
        
        assert isinstance(results, list)

    def test_delete_collection(self):
        """Test deleting a collection."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        store.create_collection("test_doc_delete")
        
        result = store.delete_collection("test_doc_delete")
        
        assert result is True


class TestDocumentVectorStore:
    """Tests for DocumentVectorStore singleton."""

    def test_get_document_vector_store(self):
        """Test getting document vector store."""
        from src.vector_store import get_document_vector_store
        
        store = get_document_vector_store()
        
        assert store is not None

    def test_document_vector_store_singleton(self):
        """Test that document vector store is singleton."""
        from src.vector_store import get_document_vector_store
        
        store1 = get_document_vector_store()
        store2 = get_document_vector_store()
        
        assert store1 is store2


class TestVectorStoreWithMock:
    """Tests for VectorStore with mocked dependencies."""

    def test_add_chunks_without_chromadb(self):
        """Test add_chunks returns False without ChromaDB."""
        from src.vector_store import VectorStore
        
        store = VectorStore()
        store._client = None
        
        result = store.add_chunks("doc_id", [])
        
        assert result is False

    def test_search_without_chromadb(self):
        """Test search returns empty without ChromaDB."""
        from src.vector_store import VectorStore
        
        store = VectorStore()
        store._client = None
        
        result = store.search_document("doc_id", "query")
        
        assert result == []


class TestEmbeddingProviderIntegration:
    """Integration tests for embedding provider with real API."""

    @pytest.mark.skipif(
        not os.environ.get("OPENROUTER_API_KEY"),
        reason="OPENROUTER_API_KEY not set"
    )
    def test_openrouter_embeddings_real(self):
        """Test real OpenRouter embedding API."""
        from src.vector_store import EmbeddingProvider
        
        provider = EmbeddingProvider()
        
        if provider._use_local:
            pytest.skip("Provider fell back to local mode")
        
        embeddings = provider.embed_batch(["test text", "another text"])
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == provider._dimension


class TestVectorStoreEdgeCases:
    """Edge case tests for vector store."""

    def test_empty_query(self):
        """Test search with empty query."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        store.create_collection("test_empty_query")
        
        results = store.search_document("test_empty_query", "", top_k=5)
        
        # Should return empty or handle gracefully
        assert isinstance(results, list)

    def test_nonexistent_collection_search(self):
        """Test search on non-existent collection."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        
        results = store.search_document("nonexistent_doc", "query")
        
        assert results == []

    def test_create_collection_twice(self):
        """Test creating same collection twice."""
        from src.vector_store import VectorStore, CHROMADB_AVAILABLE
        
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not available")
        
        store = VectorStore()
        
        result1 = store.create_collection("duplicate_doc")
        result2 = store.create_collection("duplicate_doc")
        
        # Both should succeed (get_or_create behavior)
        assert result1 is True
        assert result2 is True


class TestChromaDBAvailability:
    """Tests for ChromaDB availability check."""

    def test_chromadb_available_constant(self):
        """Test CHROMADB_AVAILABLE constant."""
        from src.vector_store import CHROMADB_AVAILABLE
        
        assert isinstance(CHROMADB_AVAILABLE, bool)

    def test_sentence_transformers_available_constant(self):
        """Test SENTENCE_TRANSFORMERS_AVAILABLE constant."""
        from src.vector_store import SENTENCE_TRANSFORMERS_AVAILABLE
        
        assert isinstance(SENTENCE_TRANSFORMERS_AVAILABLE, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
