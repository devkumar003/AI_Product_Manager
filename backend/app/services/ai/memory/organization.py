import json
from typing import Any
from app.core.redis import cache_manager
from app.services.ai.memory.base import BaseMemory


class OrganizationMemory(BaseMemory):
    """
    Manages organization-wide templates, rules, and constraints for AI features.
    """

    def __init__(self, prefix: str = "ai:org") -> None:
        self.prefix = prefix

    def _make_key(self, organization_id: str) -> str:
        return f"{self.prefix}:{organization_id}"

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = self._make_key(key)
        raw = cache_manager.get(cache_key)
        if not raw:
            return []
        try:
            data = json.loads(raw)
            context = []
            for k, v in data.items():
                context.append(
                    {"role": "system", "content": f"[Organization Memory] {k}: {v}"}
                )
            return context
        except Exception:
            return []

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = self._make_key(key)
        raw = cache_manager.get(cache_key)
        existing = {}
        if raw:
            try:
                existing = json.loads(raw)
            except Exception:
                pass

        if isinstance(data, dict):
            existing.update(data)

        # Cache organization configuration details
        cache_manager.set(cache_key, json.dumps(existing), expire_seconds=31536000)

    async def clear(self, key: str) -> None:
        cache_key = self._make_key(key)
        cache_manager.delete(cache_key)
