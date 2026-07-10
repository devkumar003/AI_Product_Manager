"""
Task 8 — Agent Memory Extension

Adds AgentMemory (per-agent execution history) and memory cleanup utilities.
"""

import time
from typing import Any
from app.ai.memory.memory_manager import BaseMemory


class AgentMemory(BaseMemory):
    """
    Per-agent execution memory — stores each agent's prior execution results,
    enabling agents to learn from their own history within a workspace.
    """

    def __init__(self, max_entries_per_agent: int = 50) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._max = max_entries_per_agent

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        entries = self._store.get(key, [])
        if not entries:
            return []
        recent = entries[-5:]
        lines = [f"- [{e.get('timestamp', '')}] {e.get('summary', '')}" for e in recent]
        return [{"role": "system", "content": f"[Agent History for {key}]\n" + "\n".join(lines)}]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        if key not in self._store:
            self._store[key] = []
        entry = data if isinstance(data, dict) else {"content": str(data)}
        entry.setdefault("timestamp", time.time())
        self._store[key].append(entry)
        if len(self._store[key]) > self._max:
            self._store[key] = self._store[key][-self._max:]

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]


class MemoryCleanup:
    """Utility for cleaning up expired or low-relevance memory entries."""

    @staticmethod
    async def cleanup_by_age(memory: BaseMemory, key: str, max_age_seconds: float = 86400) -> int:
        """Remove entries older than max_age_seconds (default 24h)."""
        if not hasattr(memory, "_store"):
            return 0
        store = getattr(memory, "_store", {})
        entries = store.get(key, [])
        if not entries:
            return 0
        now = time.time()
        before = len(entries)
        store[key] = [e for e in entries if now - e.get("timestamp", now) < max_age_seconds]
        return before - len(store[key])

    @staticmethod
    async def cleanup_all(memory: BaseMemory) -> int:
        """Clear all entries from a memory store."""
        if not hasattr(memory, "_store"):
            return 0
        store = getattr(memory, "_store", {})
        count = sum(len(v) if isinstance(v, list) else 1 for v in store.values())
        store.clear()
        return count
