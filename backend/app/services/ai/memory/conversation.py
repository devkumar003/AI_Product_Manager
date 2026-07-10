import json
from typing import Any
from app.core.redis import cache_manager
from app.services.ai.memory.base import BaseMemory


class ConversationMemory(BaseMemory):
    """
    Manages conversational memory/chat history for AI agents.
    """

    def __init__(self, prefix: str = "ai:chat") -> None:
        self.prefix = prefix

    def _make_key(self, session_id: str) -> str:
        return f"{self.prefix}:{session_id}"

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        limit = kwargs.get("limit", 20)
        cache_key = self._make_key(key)
        raw = cache_manager.get(cache_key)
        if not raw:
            return []
        try:
            messages = json.loads(raw)
            return messages[-limit:]
        except Exception:
            return []

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = self._make_key(key)
        existing = await self.get_context(key, limit=1000)

        if isinstance(data, list):
            existing.extend(data)
        elif isinstance(data, dict):
            existing.append(data)

        # Persist history (86400 seconds = 24 hours expiry)
        cache_manager.set(cache_key, json.dumps(existing), expire_seconds=86400)

    async def clear(self, key: str) -> None:
        cache_key = self._make_key(key)
        cache_manager.delete(cache_key)
