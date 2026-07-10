import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.services.ai.providers.base import BaseAIProvider


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API integration.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _convert_messages(
        self, messages: list[dict[str, str]]
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        system_instruction = None
        contents = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = {"parts": [{"text": content}]}
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({"role": gemini_role, "parts": [{"text": content}]})
        return system_instruction, contents

    async def generate(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> str:
        if not self.api_key:
            from app.core.settings import settings

            if settings.ENVIRONMENT in ("testing", "development"):
                return "Simulated Gemini LLM response content for development and testing verification."
            raise ValueError("Gemini API key is not configured.")

        model = config.get("model", "gemini-1.5-pro")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        sys_inst, contents = self._convert_messages(messages)
        payload: dict[str, Any] = {"contents": contents}
        if sys_inst:
            payload["systemInstruction"] = sys_inst

        payload["generationConfig"] = {
            "temperature": config.get("temperature", 0.7),
            "maxOutputTokens": config.get("max_tokens", 4096),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(
                    f"Gemini generation failed: Status {response.status_code} - {response.text}"
                )
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_stream(
        self, messages: list[dict[str, str]], config: dict[str, Any]
    ) -> AsyncIterator[str]:
        if not self.api_key:
            from app.core.settings import settings

            if settings.ENVIRONMENT in ("testing", "development"):
                yield "Simulated Gemini stream chunk"
                return
            raise ValueError("Gemini API key is not configured.")

        model = config.get("model", "gemini-1.5-pro")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={self.api_key}"

        sys_inst, contents = self._convert_messages(messages)
        payload: dict[str, Any] = {"contents": contents}
        if sys_inst:
            payload["systemInstruction"] = sys_inst

        payload["generationConfig"] = {
            "temperature": config.get("temperature", 0.7),
            "maxOutputTokens": config.get("max_tokens", 4096),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(
                        f"Gemini stream setup failed: Status {response.status_code} - {body.decode('utf-8')}"
                    )

                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            data = json.loads(data_str)
                            parts = (
                                data.get("candidates", [{}])[0]
                                .get("content", {})
                                .get("parts", [])
                            )
                            if parts and "text" in parts[0]:
                                yield parts[0]["text"]
                        except Exception:
                            continue
