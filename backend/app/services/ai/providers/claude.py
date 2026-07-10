import json
from typing import Any, AsyncIterator
import httpx
from app.services.ai.providers.base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """
    Anthropic Claude Messages API integration.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.url = "https://api.anthropic.com/v1/messages"

    def _convert_messages(
        self, messages: list[dict[str, str]]
    ) -> tuple[str | None, list[dict[str, str]]]:
        system_content = None
        converted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_content = content
            else:
                converted.append(
                    {
                        "role": "assistant" if role == "assistant" else "user",
                        "content": content,
                    }
                )
        return system_content, converted

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        if not self.api_key:
            from app.core.settings import settings
            if settings.ENVIRONMENT in ("testing", "development"):
                return "Simulated Claude LLM response content for development and testing verification."
            raise ValueError("Anthropic API key is not configured.")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system, converted_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": config.get("model", "claude-3-5-sonnet-20241022"),
            "messages": converted_messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.status_code != 200:
                raise Exception(
                    f"Claude generation failed: Status {response.status_code} - {response.text}"
                )
            result = response.json()
            return result["content"][0]["text"]

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        if not self.api_key:
            from app.core.settings import settings
            if settings.ENVIRONMENT in ("testing", "development"):
                yield "Simulated Claude stream chunk"
                return
            raise ValueError("Anthropic API key is not configured.")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system, converted_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": config.get("model", "claude-3-5-sonnet-20241022"),
            "messages": converted_messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": True,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", self.url, headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(
                        f"Claude stream setup failed: Status {response.status_code} - {body.decode('utf-8')}"
                    )

                event_name = None
                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    if line.startswith("event: "):
                        event_name = line[7:].strip()
                    elif line.startswith("data: "):
                        data_str = line[6:].strip()
                        if event_name == "content_block_delta":
                            try:
                                data = json.loads(data_str)
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                            except Exception:
                                continue
