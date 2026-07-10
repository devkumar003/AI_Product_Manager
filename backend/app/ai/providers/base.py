import abc
from typing import Any, AsyncIterator
from app.ai.schemas import AIResponse, StreamingToken


class BaseProvider(abc.ABC):
    """
    Standard interface for all LLM Providers (OpenAI, Gemini, Claude, Groq, DeepSeek, Ollama).
    Never exposes provider-specific parameters or structures to upper layers.
    """

    @abc.abstractmethod
    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AIResponse:
        """Execute a synchronous completion request."""
        pass

    @abc.abstractmethod
    def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        """Execute a streaming completion request, yielding individual tokens."""
        pass

    @abc.abstractmethod
    async def embeddings(self, text: str, config: dict[str, Any]) -> list[float]:
        """Generate high-dimensional vector embeddings for a given text snippet."""
        pass

    @abc.abstractmethod
    async def moderation(self, text: str, config: dict[str, Any]) -> bool:
        """Perform content moderation filter checks. Returns True if flagged, False otherwise."""
        pass

    @abc.abstractmethod
    def token_count(self, text: str) -> int:
        """Retrieve total token count for a text string."""
        pass

    @abc.abstractmethod
    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        """Calculate the USD cost of a completion call based on standard pricing models."""
        pass
