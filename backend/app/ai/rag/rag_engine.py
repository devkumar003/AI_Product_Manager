"""
Task 18 — RAG Foundation

Provider-independent RAG layer with:
- Vector store abstraction (future: FAISS, ChromaDB, Pinecone, Qdrant, Milvus)
- Embedding service abstraction
- Document chunking with metadata
- Hybrid retrieval (keyword + semantic)
- Document indexing pipeline
"""

import math
import hashlib
import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger("app.ai.rag")


# ── Chunking ──

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] = Field(default_factory=list)
    token_count: int = 0


def chunk_text(
    text: str,
    document_id: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    metadata: dict[str, Any] | None = None,
) -> list[DocumentChunk]:
    """Split text into overlapping chunks with metadata."""
    chunks: list[DocumentChunk] = []
    words = text.split()
    idx = 0
    chunk_num = 0

    while idx < len(words):
        end = min(idx + chunk_size, len(words))
        chunk_text_str = " ".join(words[idx:end])
        chunk_id = hashlib.sha256(f"{document_id}:{chunk_num}".encode()).hexdigest()[:12]
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text_str,
                metadata={**(metadata or {}), "chunk_index": chunk_num},
                token_count=max(1, len(chunk_text_str) // 4),
            )
        )
        chunk_num += 1
        idx += chunk_size - chunk_overlap

    return chunks


# ── Embedding Service Abstraction ──

class BaseEmbeddingService:
    """Abstract embedding provider. Subclass for OpenAI, Gemini, local models."""

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(t) for t in texts]


class LocalEmbeddingService(BaseEmbeddingService):
    """
    Pure-Python deterministic embedding for development/testing.
    Produces 128-dimensional normalized vectors from character frequencies.
    """

    def __init__(self, dimensions: int = 128) -> None:
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        for i, ch in enumerate(text.encode("utf-8")):
            vec[ch % self.dimensions] += float(ch) * (i + 1)
        magnitude = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / magnitude for v in vec]


class LLMEmbeddingService(BaseEmbeddingService):
    """Routes through LLM Manager for provider embeddings (OpenAI, Gemini, Ollama)."""

    def __init__(self, llm_manager: Any) -> None:
        self.llm = llm_manager

    async def embed(self, text: str) -> list[float]:
        return await self.llm.embeddings(text)


# ── Vector Store Abstraction ──

class BaseVectorStore:
    """Abstract vector store. Subclass for FAISS, ChromaDB, Pinecone, Qdrant, Milvus."""

    async def upsert(self, chunks: list[DocumentChunk]) -> int:
        raise NotImplementedError

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[DocumentChunk]:
        raise NotImplementedError

    async def delete(self, document_id: str) -> int:
        raise NotImplementedError


class InMemoryVectorStore(BaseVectorStore):
    """In-memory vector store for development. Uses cosine similarity."""

    def __init__(self) -> None:
        self._store: list[DocumentChunk] = []

    async def upsert(self, chunks: list[DocumentChunk]) -> int:
        for chunk in chunks:
            # Replace existing chunk if same id
            self._store = [c for c in self._store if c.chunk_id != chunk.chunk_id]
            self._store.append(chunk)
        return len(chunks)

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[DocumentChunk]:
        scored = []
        for chunk in self._store:
            if not chunk.embedding:
                continue
            score = self._cosine_similarity(query_embedding, chunk.embedding)
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    async def delete(self, document_id: str) -> int:
        before = len(self._store)
        self._store = [c for c in self._store if c.document_id != document_id]
        return before - len(self._store)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a)) or 1.0
        mag_b = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (mag_a * mag_b)


# ── RAG Retriever ──

class RAGRetriever:
    """
    Hybrid retriever combining vector similarity search with keyword filtering.
    """

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_service: BaseEmbeddingService,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def index_document(
        self,
        document_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        chunk_size: int = 512,
    ) -> int:
        """Chunk, embed, and store a document."""
        chunks = chunk_text(content, document_id, chunk_size=chunk_size, metadata=metadata)
        for chunk in chunks:
            chunk.embedding = await self.embedding_service.embed(chunk.content)
        return await self.vector_store.upsert(chunks)

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        keyword_filter: str | None = None,
    ) -> list[DocumentChunk]:
        """Retrieve relevant chunks using semantic similarity + optional keyword filter."""
        query_embedding = await self.embedding_service.embed(query)
        results = await self.vector_store.search(query_embedding, top_k=top_k * 2)

        if keyword_filter:
            kw = keyword_filter.lower()
            results = [c for c in results if kw in c.content.lower()]

        return results[:top_k]

    async def delete_document(self, document_id: str) -> int:
        return await self.vector_store.delete(document_id)
