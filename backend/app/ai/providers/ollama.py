import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.ai.providers.base import BaseProvider
from app.ai.schemas import AIResponse, StreamingToken, TokenUsage


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/api"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AIResponse:
        model = config.get("model", "llama3")
        start_time = time.time()
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": config.get("temperature", 0.7),
            },
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            response = await client.post(f"{self.url}/chat", json=payload)
            if response.status_code != 200:
                return AIResponse(
                    content="",
                    model=model,
                    provider="ollama",
                    usage=TokenUsage(),
                    latency_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error_message=f"Ollama error: {response.text}",
                )

            data = response.json()
            content = data["message"]["content"]

            prompt_tokens = sum(
                self.token_count(msg.get("content", "")) for msg in messages
            )
            completion_tokens = self.token_count(content)

            return AIResponse(
                content=content,
                model=model,
                provider="ollama",
                usage=TokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    estimated_cost_usd=0.0,
                ),
                latency_ms=(time.time() - start_time) * 1000,
                success=True,
            )

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[StreamingToken]:
        model = config.get("model", "llama3")
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": config.get("temperature", 0.7),
            },
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            async with client.stream(
                "POST", f"{self.url}/chat", json=payload
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    yield StreamingToken(
                        token="",
                        done=True,
                        error=f"Ollama Stream failed: {body.decode('utf-8')}",
                    )
                    return

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield StreamingToken(token=content)
                        if data.get("done", False):
                            break
                    except Exception:
                        continue
                yield StreamingToken(token="", done=True)

    async def embeddings(self, text: str, config: dict[str, Any]) -> list[float]:
        model = config.get("model", "all-minilm")
        payload = {
            "model": model,
            "prompt": text,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.url}/embeddings", json=payload)
            if response.status_code != 200:
                raise Exception(f"Ollama Embeddings error: {response.text}")
            return response.json()["embedding"]

    async def moderation(self, text: str, config: dict[str, Any]) -> bool:
        # Local keyword checking
        bad_words = ["unauthorized_injection", "malicious_exploit"]
        return any(word in text.lower() for word in bad_words)

    def token_count(self, text: str) -> int:
        return max(1, len(text) // 4)

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # Local model operations are free of usage cost
        return 0.0
