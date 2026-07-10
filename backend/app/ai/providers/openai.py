import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.ai.providers.base import BaseProvider
from app.ai.schemas import AIResponse, StreamingToken, TokenUsage


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AIResponse:
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured.")

        model = config.get("model", "gpt-4o")
        start_time = time.time()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            if response.status_code != 200:
                return AIResponse(
                    content="",
                    model=model,
                    provider="openai",
                    usage=TokenUsage(),
                    latency_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error_message=f"OpenAI error: {response.text}",
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage_data = data.get("usage", {})
            prompt_tokens = usage_data.get("prompt_tokens", 0)
            completion_tokens = usage_data.get("completion_tokens", 0)
            total_tokens = usage_data.get("total_tokens", 0)
            cost = self.cost_estimate(prompt_tokens, completion_tokens, model)

            return AIResponse(
                content=content,
                model=model,
                provider="openai",
                usage=TokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=cost,
                ),
                latency_ms=(time.time() - start_time) * 1000,
                success=True,
            )

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured.")

        model = config.get("model", "gpt-4o")
        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    yield StreamingToken(
                        token="",
                        done=True,
                        error=f"OpenAI Stream failed: {body.decode('utf-8')}",
                    )
                    return

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            yield StreamingToken(token="", done=True)
                            break
                        try:
                            data = json.loads(data_str)
                            choice = data.get("choices", [{}])[0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield StreamingToken(token=content)
                        except Exception:
                            continue

    async def embeddings(self, text: str, config: dict[str, Any]) -> list[float]:
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.get("model", "text-embedding-3-small"),
            "input": text,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings", headers=headers, json=payload
            )
            if response.status_code != 200:
                raise Exception(f"OpenAI Embeddings error: {response.text}")
            return response.json()["data"][0]["embedding"]

    async def moderation(self, text: str, config: dict[str, Any]) -> bool:
        if not self.api_key:
            # Fallback to keyword scan if API key is not present
            return any(
                bad in text.lower()
                for bad in ["unauthorized_injection", "malicious_exploit"]
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"input": text}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/moderations", headers=headers, json=payload
            )
            if response.status_code != 200:
                return False
            results = response.json().get("results", [{}])[0]
            return bool(results.get("flagged", False))

    def token_count(self, text: str) -> int:
        # Standard token heuristic estimation
        return max(1, len(text) // 4)

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # gpt-4o pricing: $5.00 / M input, $15.00 / M output
        if "gpt-4" in model:
            return (prompt_tokens * 5.00 / 1_000_000) + (
                completion_tokens * 15.00 / 1_000_000
            )
        # gpt-3.5 pricing: $0.50 / M input, $1.50 / M output
        return (prompt_tokens * 0.50 / 1_000_000) + (
            completion_tokens * 1.50 / 1_000_000
        )
