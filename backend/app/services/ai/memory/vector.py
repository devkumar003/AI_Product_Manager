import math
from typing import Any
from app.services.ai.memory.base import BaseMemory


class VectorMemory(BaseMemory):
    """
    Local high-performance vector similarity matching memory adapter using pure Python math.
    Enables storing text chunks with embeddings and performing cosine-similarity searches.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}

    def _simulated_embedding(self, text: str) -> list[float]:
        """
        Generates a deterministic, normalized mock embedding vector of 128 dimensions.
        """
        dimensions = 128
        vec = [0.0] * dimensions
        for idx, char in enumerate(text[:dimensions]):
            vec[idx] = float(ord(char) * (idx + 1))
        h = hash(text)
        for i in range(dimensions):
            vec[i] += float(h % (i + 7))

        # Normalize vector
        magnitude = math.sqrt(sum(x * x for x in vec))
        if magnitude > 0:
            vec = [x / magnitude for x in vec]
        return vec

    async def get_context(self, key: str, **kwargs: Any) -> list[dict[str, str]]:
        """
        Query memory key for top_k similar text snippets matching a query text.
        """
        query = kwargs.get("query", "")
        top_k = kwargs.get("top_k", 3)
        if not query or key not in self._store:
            return []

        query_vec = self._simulated_embedding(query)
        candidates = self._store[key]

        scored = []
        for cand in candidates:
            cand_vec = cand["vector"]
            # Cosine similarity of two normalized vectors is the dot product
            similarity = sum(q * c for q, c in zip(query_vec, cand_vec))
            scored.append((similarity, cand))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, cand in scored[:top_k]:
            results.append(
                {
                    "role": "system",
                    "content": f"[Knowledge Snippet] (Relevance: {score:.2f}) {cand['text']}",
                }
            )
        return results

    async def store(self, key: str, data: Any, **kwargs: Any) -> None:
        """
        Store text snippets under memory key.
        """
        if key not in self._store:
            self._store[key] = []

        items = data if isinstance(data, list) else [data]

        for item in items:
            text = ""
            metadata = {}
            if isinstance(item, dict):
                text = item.get("text", "")
                metadata = item.get("metadata", {})
            elif isinstance(item, str):
                text = item

            if not text:
                continue

            vec = self._simulated_embedding(text)
            self._store[key].append(
                {"text": text, "vector": vec, "metadata": metadata}
            )

    async def clear(self, key: str) -> None:
        if key in self._store:
            del self._store[key]
        return None
