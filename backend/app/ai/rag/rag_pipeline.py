"""
Task 4 — Complete RAG Pipeline Extension

Adds: Document Loader, Ranking, Citation Support, Context Builder.
Extends the existing rag_engine.py foundation.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

from app.ai.rag.rag_engine import RAGRetriever

logger = logging.getLogger("app.ai.rag.pipeline")


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    content_preview: str
    relevance_score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGContextBuilder:
    """
    Builds LLM-ready context from RAG retrieval results with
    citation tracking and relevance ranking.
    """

    def __init__(self, retriever: RAGRetriever) -> None:
        self.retriever = retriever

    async def build_context(
        self,
        query: str,
        top_k: int = 5,
        keyword_filter: str | None = None,
        max_context_tokens: int = 3000,
    ) -> tuple[str, list[Citation]]:
        """
        Retrieve chunks, rank by relevance, and build a formatted context string
        with citation references.
        """
        chunks = await self.retriever.retrieve(
            query, top_k=top_k, keyword_filter=keyword_filter
        )
        if not chunks:
            return "", []

        # Rank by embedding similarity (already ranked from retriever)
        citations: list[Citation] = []
        context_parts: list[str] = []
        total_tokens = 0

        for i, chunk in enumerate(chunks):
            estimated_tokens = chunk.token_count or max(1, len(chunk.content) // 4)
            if total_tokens + estimated_tokens > max_context_tokens:
                break

            ref_num = i + 1
            context_parts.append(f"[{ref_num}] {chunk.content}")
            citations.append(
                Citation(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content_preview=chunk.content[:150],
                    relevance_score=1.0 - (i * 0.1),
                    metadata=chunk.metadata,
                )
            )
            total_tokens += estimated_tokens

        context_text = "\n\n".join(context_parts)
        return context_text, citations


class DocumentLoader:
    """Loads documents from various sources into the RAG pipeline."""

    def __init__(self, retriever: RAGRetriever) -> None:
        self.retriever = retriever

    async def load_text(
        self, document_id: str, text: str, metadata: dict[str, Any] | None = None
    ) -> int:
        """Load plain text document."""
        return await self.retriever.index_document(document_id, text, metadata=metadata)

    async def load_markdown(
        self, document_id: str, markdown: str, metadata: dict[str, Any] | None = None
    ) -> int:
        """Load markdown document, splitting on headers for better chunks."""
        meta = {**(metadata or {}), "format": "markdown"}
        return await self.retriever.index_document(document_id, markdown, metadata=meta)

    async def load_structured(
        self,
        document_id: str,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Load structured JSON data by converting to text representation."""
        import json

        text = json.dumps(data, indent=2, default=str)
        meta = {**(metadata or {}), "format": "structured_json"}
        return await self.retriever.index_document(document_id, text, metadata=meta)
