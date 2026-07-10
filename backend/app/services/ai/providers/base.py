import abc
from typing import Any, AsyncIterator


class BaseAIProvider(abc.ABC):
    """
    Abstract Base Class for all AI model providers.
    Ensures unified structure for generating and streaming LLM responses.
    """

    @abc.abstractmethod
    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        """
        Generate a complete response from the LLM.
        """
        pass

    @abc.abstractmethod
    def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the LLM, yielding text chunks.
        """
        pass
