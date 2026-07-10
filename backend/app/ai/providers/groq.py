from typing import Any, AsyncIterator
from app.ai.providers.openai import OpenAIProvider
from app.ai.schemas import AIResponse, StreamingToken


class GroqProvider(OpenAIProvider):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key=api_key)
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AIResponse:
        if "model" not in config:
            config = {**config, "model": "llama3-8b-8192"}
        response = await super().generate(messages, config)
        response.provider = "groq"
        return response

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        if "model" not in config:
            config = {**config, "model": "llama3-8b-8192"}
        async for token in super().generate_stream(messages, config):
            yield token

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # Groq currently offers very low cost or free tier usage. Let's return 0.0 or a nominal rate:
        return 0.0
