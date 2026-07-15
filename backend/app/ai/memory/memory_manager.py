import abc
import asyncio
import json
from typing import Any

from app.core.redis import cache_manager


class BaseMemory(abc.ABC):
    """
    Standard interface for all memory stores (conversation, workspace settings, vector).
    """

    @abc.abstractmethod
    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        """Retrieve contextual key-value pairs or message logs."""
        pass

    @abc.abstractmethod
    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        """Cache new metadata records or conversation turns."""
        pass

    @abc.abstractmethod
    async def clear(self, key: str) -> None:
        """Wipe memory records associated with the key."""
        pass


class TemporaryMemory(BaseMemory):
    """
    Volatile, in-memory cache used for transient workflow states.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, str]]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        return self._store.get(key, [])

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        if key not in self._store:
            self._store[key] = []
        if isinstance(data, list):
            self._store[key].extend(data)
        else:
            self._store[key].append(data)

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]


class ConversationMemory(BaseMemory):
    """
    Manages session-based chat records, supporting automated prompt window compression
    and persistent Redis storage.
    """

    def __init__(self, limit: int = 10) -> None:
        self._limit = limit
        self._store: dict[str, list[dict[str, str]]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _get_lock(self, key: str) -> asyncio.Lock:
        """Return a per-key asyncio lock to serialise concurrent writes."""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = f"chat_history:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            history = json.loads(cached) if cached else []
        except Exception:
            history = self._store.get(key, [])

        # Apply automatic memory compression if limits are exceeded
        if len(history) > self._limit:
            history = await self.compress(key, history)
        return history

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        async with self._get_lock(key):
            cache_key = f"chat_history:{key}"
            history = await self.get_context(key)

            turns = data if isinstance(data, list) else [data]
            for turn in turns:
                history.append(
                    {"role": turn.get("role", "user"), "content": turn.get("content", "")}
                )

            try:
                await cache_manager.set(
                    cache_key, json.dumps(history), expire_seconds=86400
                )
            except Exception:
                pass
            self._store[key] = history

    async def compress(
        self, key: str, history: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """
        Compresses previous dialogue turns into a consolidated summary system prompt,
        preserving token boundaries.
        """
        keep_turns = history[-4:]  # Retain the most recent 4 messages as raw history
        compress_turns = history[:-4]

        # Consolidated compression summarizing previous turns
        exchanges = []
        for t in compress_turns:
            role_label = "User" if t["role"] == "user" else "Assistant"
            content_snippet = t["content"][:60].strip() + (
                "..." if len(t["content"]) > 60 else ""
            )
            exchanges.append(f"{role_label}: {content_snippet}")

        summary = "Previous dialog history:\n" + "\n".join(exchanges[:6])
        compressed = [
            {"role": "system", "content": f"[Conversation Summary]\n{summary}"}
        ]
        compressed.extend(keep_turns)

        cache_key = f"chat_history:{key}"
        try:
            await cache_manager.set(
                cache_key, json.dumps(compressed), expire_seconds=86400
            )
        except Exception:
            pass
        self._store[key] = compressed
        return compressed

    async def clear(self, key: str) -> None:
        cache_key = f"chat_history:{key}"
        try:
            await cache_manager.delete(cache_key)
        except Exception:
            pass
        if key in self._store:
            del self._store[key]


class WorkspaceMemory(BaseMemory):
    """
    Manages workspace-scoped project definitions, constraints, and styling frameworks.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = f"workspace_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            settings = json.loads(cached) if cached else {}
        except Exception:
            settings = self._store.get(key, {})

        if not settings:
            return []
        context_str = ", ".join(f"{k}: {v}" for k, v in settings.items())
        return [
            {"role": "system", "content": f"[Workspace Setting Context] {context_str}"}
        ]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = f"workspace_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            settings = json.loads(cached) if cached else {}
        except Exception:
            settings = self._store.get(key, {})

        if isinstance(data, dict):
            settings.update(data)

        try:
            await cache_manager.set(
                cache_key, json.dumps(settings), expire_seconds=86400
            )
        except Exception:
            pass
        self._store[key] = settings

    async def clear(self, key: str) -> None:
        cache_key = f"workspace_memory:{key}"
        try:
            await cache_manager.delete(cache_key)
        except Exception:
            pass
        if key in self._store:
            del self._store[key]


class OrganizationMemory(BaseMemory):
    """
    Manages organization-scoped guidelines, corporate structures, and release criteria.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        cache_key = f"org_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            guidelines = json.loads(cached) if cached else {}
        except Exception:
            guidelines = self._store.get(key, {})

        if not guidelines:
            return []
        lines = [f"- {k}: {v}" for k, v in guidelines.items()]
        return [
            {
                "role": "system",
                "content": "[Organization Brand Standards]\n" + "\n".join(lines),
            }
        ]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        cache_key = f"org_memory:{key}"
        try:
            cached = await cache_manager.get(cache_key)
            guidelines = json.loads(cached) if cached else {}
        except Exception:
            guidelines = self._store.get(key, {})

        if isinstance(data, dict):
            guidelines.update(data)

        try:
            await cache_manager.set(
                cache_key, json.dumps(guidelines), expire_seconds=86400
            )
        except Exception:
            pass
        self._store[key] = guidelines

    async def clear(self, key: str) -> None:
        cache_key = f"org_memory:{key}"
        try:
            await cache_manager.delete(cache_key)
        except Exception:
            pass
        if key in self._store:
            del self._store[key]
