import asyncio
import json
from typing import Any, AsyncIterator
import httpx
from app.services.ai.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Chat Completion API integration.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        if not self.api_key:
            from app.core.settings import settings
            if settings.ENVIRONMENT in ("testing", "development"):
                response_format = config.get("response_format")
                if response_format and response_format.get("type") == "json_object":
                    return '{"score": 90.0, "comments": [{"line": 1, "issue": "Simulated check", "severity": "Info"}]}'
                return "Simulated LLM response content for development and testing verification."
            raise ValueError("OpenAI API key is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": config.get("model", "gpt-4o"),
            "messages": messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.status_code != 200:
                raise Exception(
                    f"OpenAI generation failed: Status {response.status_code} - {response.text}"
                )
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        if not self.api_key:
            from app.core.settings import settings
            if settings.ENVIRONMENT in ("testing", "development"):
                simulated_text = (
                    "Simulated live streaming response from AI ProductOS Autonomous Agent.\n\n"
                    "### 🚀 Key Observations & Recommendations:\n"
                    "1. **Strategic Alignment**: The feature strongly aligns with user retention goals.\n"
                    "2. **Technical Feasibility**: Clean architectural separation enables rapid delivery.\n"
                    "3. **Execution Plan**: Recommend breaking into 2 sprint milestones with automated verification."
                )
                for word in simulated_text.split(" "):
                    yield word + " "
                    await asyncio.sleep(0.02)
                return
            raise ValueError("OpenAI API key is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": config.get("model", "gpt-4o"),
            "messages": messages,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4096),
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", self.url, headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(
                        f"OpenAI stream setup failed: Status {response.status_code} - {body.decode('utf-8')}"
                    )

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            choice = data.get("choices", [{}])[0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
