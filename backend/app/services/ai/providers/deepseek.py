from collections.abc import AsyncIterator
from typing import Any

from app.services.ai.providers.openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """
    DeepSeek OpenAI-compatible Chat Completions API integration.
    """

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key=api_key)
        self.url = "https://api.deepseek.com/chat/completions"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        if "model" not in config:
            config = {**config, "model": "deepseek-chat"}
        return await super().generate(messages, config)

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        if "model" not in config:
            config = {**config, "model": "deepseek-chat"}
        async for chunk in super().generate_stream(messages, config):
            yield chunk
