from collections.abc import AsyncIterator
from typing import Any

from app.ai.providers.openai import OpenAIProvider
from app.ai.schemas import AIResponse, StreamingToken


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key=api_key)
        self.base_url = "https://api.deepseek.com"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AIResponse:
        if "model" not in config:
            config = {**config, "model": "deepseek-chat"}
        response = await super().generate(messages, config)
        response.provider = "deepseek"
        return response

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        if "model" not in config:
            config = {**config, "model": "deepseek-chat"}
        async for token in super().generate_stream(messages, config):
            yield token

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # DeepSeek pricing: $0.14 / M input tokens, $0.28 / M output tokens
        return (prompt_tokens * 0.14 / 1_000_000) + (
            completion_tokens * 0.28 / 1_000_000
        )
