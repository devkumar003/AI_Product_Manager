import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.services.ai.providers.base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    """
    Ollama local API integration.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/api/chat"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        payload = {
            "model": config.get("model", "llama3"),
            "messages": messages,
            "options": {
                "temperature": config.get("temperature", 0.7),
            },
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.url, json=payload)
            if response.status_code != 200:
                raise Exception(
                    f"Ollama generation failed: Status {response.status_code} - {response.text}"
                )
            result = response.json()
            return result["message"]["content"]

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        payload = {
            "model": config.get("model", "llama3"),
            "messages": messages,
            "options": {
                "temperature": config.get("temperature", 0.7),
            },
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", self.url, json=payload) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(
                        f"Ollama stream setup failed: Status {response.status_code} - {body.decode('utf-8')}"
                    )

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done", False):
                            break
                    except Exception:
                        continue
