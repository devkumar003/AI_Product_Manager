import json
import time
from typing import Any, AsyncIterator
import httpx
from app.ai.providers.base import BaseProvider
from app.ai.schemas import AIResponse, StreamingToken, TokenUsage


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str | None = None) -> None:
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
    ) -> AIResponse:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        model = config.get("model", "gemini-1.5-pro")
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        sys_inst, contents = self._convert_messages(messages)
        payload: dict[str, Any] = {"contents": contents}
        if sys_inst:
            payload["systemInstruction"] = sys_inst

        payload["generationConfig"] = {
            "temperature": config.get("temperature", 0.7),
            "maxOutputTokens": config.get("max_tokens", 4096),
        }

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                return AIResponse(
                    content="",
                    model=model,
                    provider="gemini",
                    usage=TokenUsage(),
                    latency_ms=(time.time() - start_time) * 1000,
                    success=False,
                    error_message=f"Gemini error: {response.text}",
                )

            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Estimate tokens
            prompt_tokens = sum(self.token_count(msg.get("content", "")) for msg in messages)
            completion_tokens = self.token_count(content)
            cost = self.cost_estimate(prompt_tokens, completion_tokens, model)

            return AIResponse(
                content=content,
                model=model,
                provider="gemini",
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
            raise ValueError("Gemini API Key is not configured.")

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

        async with httpx.AsyncClient(timeout=config.get("timeout", 60.0)) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    yield StreamingToken(
                        token="", done=True, error=f"Gemini Stream failed: {body.decode('utf-8')}"
                    )
                    return

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
                                yield StreamingToken(token=parts[0]["text"])
                        except Exception:
                            continue
                yield StreamingToken(token="", done=True)

    async def embeddings(self, text: str, config: dict[str, Any]) -> list[float]:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        model = config.get("model", "text-embedding-004")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{model}",
            "content": {"parts": [{"text": text}]},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise Exception(f"Gemini Embeddings error: {response.text}")
            return response.json()["embedding"]["values"]

    async def moderation(self, text: str, config: dict[str, Any]) -> bool:
        # Gemini does safety checking natively within completions but we can keyword-scan here
        bad_words = ["unauthorized_injection", "malicious_exploit"]
        return any(word in text.lower() for word in bad_words)

    def token_count(self, text: str) -> int:
        return max(1, len(text) // 4)

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        # Gemini 1.5 Pro pricing: $1.25 / M input, $5.00 / M output
        return (prompt_tokens * 1.25 / 1_000_000) + (completion_tokens * 5.00 / 1_000_000)
