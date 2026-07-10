"""
Task 17 — Knowledge Base

Supports: collections, documents, categories, tags, metadata,
relationships, versioning, loading, and search.
"""

import hashlib
import time
from typing import Any

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str = ""
    title: str = Field(...)
    content: str = Field(...)
    category: str = Field(default="general")
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    related_doc_ids: list[str] = Field(default_factory=list)

    def compute_id(self) -> str:
        return hashlib.sha256(
            f"{self.title}:{self.content[:200]}".encode()
        ).hexdigest()[:16]


class KnowledgeCollection(BaseModel):
    name: str
    description: str = ""
    documents: dict[str, KnowledgeDocument] = Field(default_factory=dict)
    categories: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)


class KnowledgeBase:
    """
    In-memory knowledge base supporting collections, documents,
    categorization, tagging, versioning, search, and relationships.
    """

    def __init__(self) -> None:
        self._collections: dict[str, KnowledgeCollection] = {}

    # ── Collection Management ──

    def create_collection(
        self, name: str, description: str = ""
    ) -> KnowledgeCollection:
        if name in self._collections:
            return self._collections[name]
        col = KnowledgeCollection(name=name, description=description)
        self._collections[name] = col
        return col

    def get_collection(self, name: str) -> KnowledgeCollection | None:
        return self._collections.get(name)

    def list_collections(self) -> list[str]:
        return list(self._collections.keys())

    # ── Document Management ──

    def add_document(
        self,
        collection_name: str,
        doc: KnowledgeDocument,
    ) -> KnowledgeDocument:
        col = self._collections.get(collection_name)
        if not col:
            col = self.create_collection(collection_name)

        if not doc.id:
            doc.id = doc.compute_id()

        col.documents[doc.id] = doc
        col.categories.add(doc.category)
        col.tags.update(doc.tags)
        return doc

    def get_document(
        self, collection_name: str, doc_id: str
    ) -> KnowledgeDocument | None:
        col = self._collections.get(collection_name)
        if not col:
            return None
        return col.documents.get(doc_id)

    def update_document(
        self,
        collection_name: str,
        doc_id: str,
        updates: dict[str, Any],
    ) -> KnowledgeDocument | None:
        doc = self.get_document(collection_name, doc_id)
        if not doc:
            return None

        for key, value in updates.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        doc.version += 1
        doc.updated_at = time.time()
        return doc

    def delete_document(self, collection_name: str, doc_id: str) -> bool:
        col = self._collections.get(collection_name)
        if col and doc_id in col.documents:
            del col.documents[doc_id]
            return True
        return False

    # ── Search ──

    def search(
        self,
        query: str,
        collection_name: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        limit: int = 20,
    ) -> list[KnowledgeDocument]:
        results: list[KnowledgeDocument] = []
        query_lower = query.lower()

        targets = (
            [self._collections[collection_name]]
            if collection_name and collection_name in self._collections
            else self._collections.values()
        )

        for col in targets:
            for doc in col.documents.values():
                if category and doc.category != category:
                    continue
                if tags and not set(tags).intersection(doc.tags):
                    continue
                if (
                    query_lower in doc.title.lower()
                    or query_lower in doc.content.lower()
                ):
                    results.append(doc)

        return results[:limit]

    # ── Bulk Operations ──

    def load_documents(
        self, collection_name: str, documents: list[dict[str, Any]]
    ) -> int:
        loaded = 0
        for raw in documents:
            doc = KnowledgeDocument(**raw)
            self.add_document(collection_name, doc)
            loaded += 1
        return loaded

    def get_stats(self) -> dict[str, Any]:
        total_docs = sum(len(c.documents) for c in self._collections.values())
        return {
            "total_collections": len(self._collections),
            "total_documents": total_docs,
            "collections": {
                name: len(col.documents) for name, col in self._collections.items()
            },
        }
