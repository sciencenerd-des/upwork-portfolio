"""
Vector Store Module

Handles embedding generation and vector storage using ChromaDB.
- Generate embeddings via OpenRouter API
- Store chunks in ChromaDB collections
- Semantic search with relevance scoring
- Fallback to sentence-transformers if API unavailable
"""

import os
import logging
from typing import Optional
import hashlib

import httpx

from app.config import get_settings
from app.models import TextChunk

logger = logging.getLogger(__name__)

# Try to import ChromaDB
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available.")

# Try to import sentence-transformers as fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingProvider:
    """
    Generates embeddings using OpenRouter API with fallback to local models.
    """

    # Maximum batch size for embedding API calls to avoid request size limits
    MAX_BATCH_SIZE = 100

    def __init__(self):
        self.settings = get_settings()
        # Use settings instead of os.getenv for consistent configuration
        self._api_key = self.settings.openrouter_api_key
        self._base_url = self.settings.llm.base_url
        self._model = self.settings.llm.embedding_model
        self._dimension = self.settings.vector_store.embedding_dimension

        # Fallback model
        self._local_model = None
        self._use_local = False

        # Reusable HTTP client for connection pooling
        self._http_client: Optional[httpx.Client] = None

        if not self._api_key:
            logger.warning("OPENROUTER_API_KEY not set. Using local embeddings.")
            self._use_local = True
            self._init_local_model()

    def _init_local_model(self) -> None:
        """Initialize local sentence-transformers model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self._local_model = SentenceTransformer('all-MiniLM-L6-v2')
                self._dimension = 384  # MiniLM dimension
                logger.info("Loaded local embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"Failed to load local model: {e}")

    def embed(self, text: str) -> list[float]:
        """Generate embedding for single text."""
        return self.embed_batch([text])[0]

    def _get_http_client(self) -> httpx.Client:
        """Get or create reusable HTTP client for connection pooling."""
        if self._http_client is None:
            self._http_client = httpx.Client(
                timeout=60.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._http_client

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts with automatic batching."""
        if not texts:
            return []

        if self._use_local:
            return self._embed_local(texts)

        try:
            # Batch large requests to avoid API size limits
            if len(texts) <= self.MAX_BATCH_SIZE:
                return self._embed_openrouter(texts)
            else:
                # Process in batches
                all_embeddings = []
                for i in range(0, len(texts), self.MAX_BATCH_SIZE):
                    batch = texts[i:i + self.MAX_BATCH_SIZE]
                    batch_embeddings = self._embed_openrouter(batch)
                    all_embeddings.extend(batch_embeddings)
                return all_embeddings

        except Exception as e:
            logger.warning(f"OpenRouter embedding failed: {e}. Using fallback.")
            self._use_local = True
            if not self._local_model:
                self._init_local_model()
            return self._embed_local(texts)

    def _embed_openrouter(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenRouter API with connection reuse."""
        client = self._get_http_client()
        response = client.post(
            f"{self._base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "input": texts,
            }
        )
        response.raise_for_status()
        data = response.json()

        # Extract embeddings from response
        embeddings = [item["embedding"] for item in data["data"]]
        return embeddings

    def _embed_local(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using local model."""
        if self._local_model is None:
            # Return zero vectors as fallback
            logger.warning("No embedding model available. Using zero vectors.")
            return [[0.0] * self._dimension for _ in texts]

        embeddings = self._local_model.encode(texts, convert_to_tensor=False)
        return [emb.tolist() for emb in embeddings]

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


class VectorStore:
    """
    Vector storage using ChromaDB with embedding support.
    """

    def __init__(self, collection_name: Optional[str] = None):
        self.settings = get_settings()
        self._collection_prefix = self.settings.vector_store.collection_prefix
        self._top_k = self.settings.vector_store.top_k
        self._relevance_threshold = self.settings.vector_store.relevance_threshold

        # Initialize embedding provider
        self._embedding_provider = EmbeddingProvider()

        # Initialize ChromaDB
        self._client = None
        self._collection = None
        self._collection_name = collection_name

        if CHROMADB_AVAILABLE:
            self._init_chromadb()

    def _init_chromadb(self) -> None:
        """Initialize ChromaDB client."""
        try:
            # Use ephemeral (in-memory) client
            self._client = chromadb.Client(ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            ))
            logger.info("Initialized ChromaDB client")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._client = None

    def create_collection(self, doc_id: str) -> bool:
        """Create a new collection for a document."""
        if not self._client:
            return False

        try:
            self._collection_name = f"{self._collection_prefix}_{doc_id}"

            # Delete if exists
            try:
                self._client.delete_collection(self._collection_name)
            except Exception:
                pass

            self._collection = self._client.create_collection(
                name=self._collection_name,
                metadata={"doc_id": doc_id}
            )
            logger.info(f"Created collection: {self._collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def get_collection(self, doc_id: str) -> bool:
        """Get existing collection for a document."""
        if not self._client:
            return False

        try:
            collection_name = f"{self._collection_prefix}_{doc_id}"
            self._collection = self._client.get_collection(collection_name)
            self._collection_name = collection_name
            return True
        except Exception:
            return False

    def add_chunks(self, chunks: list[TextChunk]) -> int:
        """
        Add text chunks to the vector store.

        Args:
            chunks: List of TextChunk objects to add

        Returns:
            Number of chunks added
        """
        if not self._collection or not chunks:
            return 0

        try:
            # Prepare data
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.text for chunk in chunks]
            metadatas = [
                {
                    "page_number": chunk.page_number or 0,
                    "start_char": chunk.start_char or 0,
                    "end_char": chunk.end_char or 0,
                    **chunk.metadata
                }
                for chunk in chunks
            ]

            # Generate embeddings
            embeddings = self._embedding_provider.embed_batch(texts)

            # Add to collection
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            logger.info(f"Added {len(chunks)} chunks to collection")
            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            return 0

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[dict] = None
    ) -> list[dict]:
        """
        Search for relevant chunks.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of results with text, metadata, and score
        """
        if not self._collection:
            return []

        top_k = top_k or self._top_k

        try:
            # Generate query embedding
            query_embedding = self._embedding_provider.embed(query)

            # Build query arguments
            query_args = {
                "query_embeddings": [query_embedding],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"]
            }

            if filter_metadata:
                query_args["where"] = filter_metadata

            # Execute search
            results = self._collection.query(**query_args)

            # Format results
            formatted = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    # Convert distance to similarity score (1 - distance for cosine)
                    distance = results["distances"][0][i] if results["distances"] else 0
                    similarity = 1 - (distance / 2)  # Normalize to 0-1

                    if similarity >= self._relevance_threshold:
                        formatted.append({
                            "text": doc,
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                            "score": similarity,
                            "id": results["ids"][0][i] if results["ids"] else None
                        })

            return formatted

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_collection(self, doc_id: Optional[str] = None) -> bool:
        """Delete a collection."""
        if not self._client:
            return False

        try:
            collection_name = (
                f"{self._collection_prefix}_{doc_id}"
                if doc_id else self._collection_name
            )

            if collection_name:
                self._client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")

                if collection_name == self._collection_name:
                    self._collection = None
                    self._collection_name = None

                return True

        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

        return False

    def get_chunk_count(self) -> int:
        """Get number of chunks in current collection."""
        if not self._collection:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def get_all_chunks(self) -> list[dict]:
        """Get all chunks from current collection."""
        if not self._collection:
            return []

        try:
            results = self._collection.get(include=["documents", "metadatas"])

            chunks = []
            for i, doc in enumerate(results["documents"]):
                chunks.append({
                    "id": results["ids"][i],
                    "text": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })

            return chunks

        except Exception as e:
            logger.error(f"Failed to get chunks: {e}")
            return []


class DocumentVectorStore:
    """
    High-level interface for managing vector stores per document.
    """

    def __init__(self):
        self._stores: dict[str, VectorStore] = {}

    def create_store(self, doc_id: str) -> VectorStore:
        """Create a new vector store for a document."""
        store = VectorStore()
        store.create_collection(doc_id)
        self._stores[doc_id] = store
        return store

    def get_store(self, doc_id: str) -> Optional[VectorStore]:
        """Get vector store for a document."""
        if doc_id in self._stores:
            return self._stores[doc_id]

        # Try to load existing collection
        store = VectorStore()
        if store.get_collection(doc_id):
            self._stores[doc_id] = store
            return store

        return None

    def delete_store(self, doc_id: str) -> bool:
        """Delete vector store for a document."""
        if doc_id in self._stores:
            self._stores[doc_id].delete_collection()
            del self._stores[doc_id]
            return True
        return False

    def index_document(self, doc_id: str, chunks: list[TextChunk]) -> int:
        """
        Index document chunks into vector store.

        Args:
            doc_id: Document identifier
            chunks: List of text chunks to index

        Returns:
            Number of chunks indexed
        """
        store = self.create_store(doc_id)
        return store.add_chunks(chunks)

    def search_document(
        self,
        doc_id: str,
        query: str,
        top_k: Optional[int] = None
    ) -> list[dict]:
        """
        Search for relevant chunks in a document.

        Args:
            doc_id: Document identifier
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant chunks with scores
        """
        store = self.get_store(doc_id)
        if not store:
            return []

        return store.search(query, top_k)


# Singleton instances
_embedding_provider: Optional[EmbeddingProvider] = None
_document_vector_store: Optional[DocumentVectorStore] = None


def get_embedding_provider() -> EmbeddingProvider:
    """Get or create embedding provider instance."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = EmbeddingProvider()
    return _embedding_provider


def get_document_vector_store() -> DocumentVectorStore:
    """Get or create document vector store instance."""
    global _document_vector_store
    if _document_vector_store is None:
        _document_vector_store = DocumentVectorStore()
    return _document_vector_store
