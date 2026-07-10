import abc
from typing import Any


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
    Manages session-based chat records, supporting automated prompt window compression.
    """

    def __init__(self, limit: int = 10) -> None:
        self._limit = limit
        self._store: dict[str, list[dict[str, str]]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        history = self._store.get(key, [])
        # Apply automatic memory compression if limits are exceeded
        if len(history) > self._limit:
            history = await self.compress(key, history)
        return history

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        if key not in self._store:
            self._store[key] = []
        turns = data if isinstance(data, list) else [data]
        for turn in turns:
            self._store[key].append(
                {"role": turn.get("role", "user"), "content": turn.get("content", "")}
            )

    async def compress(
        self, key: str, history: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """
        Compresses previous dialogue turns into a consolidated summary system prompt,
        preserving token boundaries.
        """
        keep_turns = history[-4:]  # Retain the most recent 4 messages as raw history
        compress_turns = history[:-4]

        # Simple structural compression summarizing statements
        user_queries = [t["content"] for t in compress_turns if t["role"] == "user"]
        summary = f"Summary of early exchange: User discussed details concerning: {', '.join(user_queries[:3])}."

        compressed = [
            {"role": "system", "content": f"[Conversation Summary] {summary}"}
        ]
        compressed.extend(keep_turns)

        self._store[key] = compressed
        return compressed

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]


class WorkspaceMemory(BaseMemory):
    """
    Manages workspace-scoped project definitions, constraints, and styling frameworks.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        settings = self._store.get(key, {})
        if not settings:
            return []
        context_str = ", ".join(f"{k}: {v}" for k, v in settings.items())
        return [
            {"role": "system", "content": f"[Workspace Setting Context] {context_str}"}
        ]

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        if key not in self._store:
            self._store[key] = {}
        if isinstance(data, dict):
            self._store[key].update(data)

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]


class OrganizationMemory(BaseMemory):
    """
    Manages organization-scoped guidelines, corporate structures, and release criteria.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
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
        if key not in self._store:
            self._store[key] = {}
        if isinstance(data, dict):
            self._store[key].update(data)

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
