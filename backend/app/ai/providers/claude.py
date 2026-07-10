import json
import time
from typing import Any, AsyncIterator
import httpx
from app.ai.providers.base import BaseProvider
from app.ai.schemas import AIResponse, StreamingToken, TokenUsage


class ClaudeProvider(BaseProvider):
    def __init__(self, api_key: str | None = None) -> None:
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
    ) -> AIResponse:
        if not self.api_key:
            raise ValueError("Anthropic API Key is not configured.")

        model = config.get("model", "claude-3-5-sonnet-20241022")
        start_time = time.time()
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system, converted_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": model,
            "messages": converted_messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.status_code != 200:
                return AIResponse(
                    content="",
                    model=model,
                    provider="claude",
                    usage=TokenUsage(),
                    latency_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error_message=f"Claude error: {response.text}",
                )

            data = response.json()
            content = data["content"][0]["text"]
            usage_data = data.get("usage", {})
            prompt_tokens = usage_data.get("input_tokens", 0)
            completion_tokens = usage_data.get("output_tokens", 0)
            cost = self.cost_estimate(prompt_tokens, completion_tokens, model)

            return AIResponse(
                content=content,
                model=model,
                provider="claude",
                usage=TokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    estimated_cost_usd=cost,
                ),
                latency_ms=(time.time() - start_time) * 1000,
                success=True,
            )

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        if not self.api_key:
            raise ValueError("Anthropic API Key is not configured.")

        model = config.get("model", "claude-3-5-sonnet-20241022")
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system, converted_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": model,
            "messages": converted_messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": True,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            async with client.stream(
                "POST", self.url, headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    yield StreamingToken(
                        token="", done=True, error=f"Claude Stream failed: {body.decode('utf-8')}"
                    )
                    return

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
                                    yield StreamingToken(token=delta.get("text", ""))
                            except Exception:
                                continue
                yield StreamingToken(token="", done=True)

    async def embeddings(self, text: str, config: dict[str, Any]) -> list[float]:
        # Claude does not officially offer a native embeddings model. Expose mock/error fallback:
        raise NotImplementedError("Anthropic Claude does not support embeddings API natively.")

    async def moderation(self, text: str, config: dict[str, Any]) -> bool:
        bad_words = ["unauthorized_injection", "malicious_exploit"]
        return any(word in text.lower() for word in bad_words)

    def token_count(self, text: str) -> int:
        return max(1, len(text) // 4)

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # Claude 3.5 Sonnet: $3.00 / M input, $15.00 / M output
        return (prompt_tokens * 3.00 / 1_000_000) + (completion_tokens * 15.00 / 1_000_000)
