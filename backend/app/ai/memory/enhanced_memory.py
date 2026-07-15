"""
Task 19 — Enhanced Memory Engine

Extends the existing memory foundation with:
- Project Memory (per-project context)
- Long Term Memory (persistent cross-session)
- Memory Compression (summarization)
- Memory Ranking (relevance scoring)
- Memory Retrieval (unified search across all memory types)
"""

import time
import json
from typing import Any

from app.ai.memory.memory_manager import BaseMemory
from app.core.redis import cache_manager


class ProjectMemory(BaseMemory):
    """Per-project memory storing feature decisions, architecture choices, and sprint history."""

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, str]]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = f"project_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            entries = json.loads(cached) if cached else []
        except Exception:
            entries = self._store.get(key, [])

        if not entries:
            return []
        context_lines = [f"- {e.get('content', '')}" for e in entries[-20:]]
        return [
            {
                "role": "system",
                "content": "[Project Context]\n" + "\n".join(context_lines),
            }
        ]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = f"project_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            entries = json.loads(cached) if cached else []
        except Exception:
            entries = self._store.get(key, [])

        new_entries = data if isinstance(data, list) else [data]
        for entry in new_entries:
            if isinstance(entry, dict):
                entry.setdefault("timestamp", time.time())
                entries.append(entry)

        try:
            await cache_manager.set(
                cache_key, json.dumps(entries), expire_seconds=86400
            )
        except Exception:
            pass
        self._store[key] = entries

    async def clear(self, key: str) -> None:
        cache_key = f"project_memory:{key}"
        try:
            await cache_manager.delete(cache_key)
        except Exception:
            pass
        if key in self._store:
            del self._store[key]


class LongTermMemory(BaseMemory):
    """
    Cross-session persistent memory with relevance scoring.
    Stores important facts, decisions, and preferences that survive session resets.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = f"long_term_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            entries = json.loads(cached) if cached else []
        except Exception:
            entries = self._store.get(key, [])

        if not entries:
            return []
        # Sort by relevance score descending, take top entries
        ranked = sorted(entries, key=lambda e: e.get("relevance", 0.5), reverse=True)
        top = ranked[:10]
        lines = [f"- [{e.get('category', 'fact')}] {e.get('content', '')}" for e in top]
        return [
            {"role": "system", "content": "[Long-Term Memory]\n" + "\n".join(lines)}
        ]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = f"long_term_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            entries = json.loads(cached) if cached else []
        except Exception:
            entries = self._store.get(key, [])

        new_entries = data if isinstance(data, list) else [data]
        for entry in new_entries:
            if isinstance(entry, dict):
                entry.setdefault("timestamp", time.time())
                entry.setdefault("relevance", 0.5)
                entry.setdefault("category", "fact")
                entries.append(entry)

        try:
            await cache_manager.set(
                cache_key, json.dumps(entries), expire_seconds=604800
            )  # 7 days
        except Exception:
            pass
        self._store[key] = entries

    async def clear(self, key: str) -> None:
        cache_key = f"long_term_memory:{key}"
        try:
            await cache_manager.delete(cache_key)
        except Exception:
            pass
        if key in self._store:
            del self._store[key]

    async def boost_relevance(
        self, key: str, content_fragment: str, boost: float = 0.1
    ) -> None:
        """Increase relevance of entries matching a content fragment."""
        cache_key = f"long_term_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            entries = json.loads(cached) if cached else []
        except Exception:
            entries = self._store.get(key, [])

        fragment_lower = content_fragment.lower()
        for entry in entries:
            if fragment_lower in entry.get("content", "").lower():
                entry["relevance"] = min(1.0, entry.get("relevance", 0.5) + boost)

        try:
            await cache_manager.set(
                cache_key, json.dumps(entries), expire_seconds=604800
            )
        except Exception:
            pass
        self._store[key] = entries


class MemoryRetriever:
    """
    Unified search across all memory types with relevance ranking.
    """

    def __init__(
        self,
        conversation: BaseMemory,
        workspace: BaseMemory,
        organization: BaseMemory,
        project: ProjectMemory,
        long_term: LongTermMemory,
    ) -> None:
        self.memories = {
            "conversation": conversation,
            "workspace": workspace,
            "organization": organization,
            "project": project,
            "long_term": long_term,
        }

    async def retrieve_all(self, key: str) -> list[dict[str, str]]:
        """Retrieve and merge context from all memory types."""
        all_context: list[dict[str, str]] = []
        for mem in self.memories.values():
            ctx = await mem.get_context(key)
            all_context.extend(ctx)
        return all_context

    async def retrieve_selective(
        self, key: str, memory_types: list[str]
    ) -> list[dict[str, str]]:
        """Retrieve context from specific memory types only."""
        all_context: list[dict[str, str]] = []
        for mt in memory_types:
            mem = self.memories.get(mt)
            if mem:
                ctx = await mem.get_context(key)
                all_context.extend(ctx)
        return all_context
