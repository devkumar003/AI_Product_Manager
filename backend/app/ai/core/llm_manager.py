import asyncio
import logging
from typing import Any, AsyncIterator
from app.core.settings import settings
from app.ai.providers import (
    BaseProvider,
    OpenAIProvider,
    GeminiProvider,
    ClaudeProvider,
    GroqProvider,
    DeepSeekProvider,
    OllamaProvider,
)
from app.ai.schemas import AIResponse, StreamingToken
from app.ai.exceptions import ProviderException

logger = logging.getLogger("app.ai.llm_manager")


class LLMManager:
    """
    Unified LLM Routing Gateway. Exposes generate, stream, embeddings, moderation,
    token_count, and cost_estimate methods. Never exposes provider-specific configurations.
    """

    def __init__(self) -> None:
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        self.providers: dict[str, BaseProvider] = {
            "openai": OpenAIProvider(api_key=settings.OPENAI_API_KEY),
            "gemini": GeminiProvider(api_key=settings.GEMINI_API_KEY),
            "claude": ClaudeProvider(api_key=settings.ANTHROPIC_API_KEY),
            "groq": GroqProvider(api_key=settings.GROQ_API_KEY),
            "deepseek": DeepSeekProvider(api_key=settings.DEEPSEEK_API_KEY),
            "ollama": OllamaProvider(base_url=settings.OLLAMA_BASE_URL or "http://localhost:11434"),
        }

    def _get_provider_priority(self, requested: str | None = None) -> list[str]:
        default_order = ["openai", "claude", "gemini", "groq", "deepseek", "ollama"]
        if requested and requested in self.providers:
            # Place requested provider first, followed by others as fallbacks
            return [requested] + [p for p in default_order if p != requested]
        return default_order

    async def generate(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        retry_count: int = 3,
        timeout: float = 60.0,
    ) -> AIResponse:
        priority_chain = self._get_provider_priority(provider)
        last_error = None

        for p_name in priority_chain:
            target_provider = self.providers[p_name]
            config = {
                "model": model or self._get_default_model(p_name),
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": timeout,
            }

            # Retry loop for the specific provider
            for attempt in range(1, retry_count + 1):
                try:
                    logger.info(
                        f"Attempting generate via {p_name} (Attempt {attempt}/{retry_count}) using model {config['model']}"
                    )
                    res = await target_provider.generate(messages, config)
                    if res.success:
                        return res
                    else:
                        logger.warning(f"Provider {p_name} returned failure: {res.error_message}")
                        last_error = Exception(res.error_message)
                except Exception as e:
                    logger.warning(f"Error on {p_name} generate (attempt {attempt}): {str(e)}")
                    last_error = e
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)

            logger.error(f"Provider {p_name} completely failed after {retry_count} retries. Falling back...")

        raise ProviderException(
            message=f"All configured AI Providers failed to generate a response. Last error: {str(last_error)}",
            details={"last_error": str(last_error)},
        )

    async def stream(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 60.0,
    ) -> AsyncIterator[StreamingToken]:
        priority_chain = self._get_provider_priority(provider)
        target_name = priority_chain[0]
        target_provider = self.providers[target_name]

        config = {
            "model": model or self._get_default_model(target_name),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }

        try:
            async for token in target_provider.generate_stream(messages, config):
                yield token
        except Exception as e:
            logger.error(f"Stream generation failed for {target_name}: {str(e)}")
            # For stream cancellation/failure, attempt fallback synchronously
            if len(priority_chain) > 1:
                fallback_name = priority_chain[1]
                logger.info(f"Attempting streaming fallback to {fallback_name}...")
                fallback_provider = self.providers[fallback_name]
                config["model"] = self._get_default_model(fallback_name)
                try:
                    async for token in fallback_provider.generate_stream(messages, config):
                        yield token
                except Exception as fe:
                    yield StreamingToken(token="", done=True, error=f"Fallback streaming also failed: {str(fe)}")
            else:
                yield StreamingToken(token="", done=True, error=str(e))

    async def embeddings(
        self, text: str, provider: str = "openai", model: str | None = None
    ) -> list[float]:
        target = self.providers.get(provider, self.providers["openai"])
        config = {"model": model or "text-embedding-3-small"}
        return await target.embeddings(text, config)

    async def moderation(self, text: str, provider: str = "openai") -> bool:
        target = self.providers.get(provider, self.providers["openai"])
        return await target.moderation(text, {})

    def token_count(self, text: str, provider: str = "openai") -> int:
        target = self.providers.get(provider, self.providers["openai"])
        return target.token_count(text)

    def cost_estimate(
        self, prompt_tokens: int, completion_tokens: int, provider: str, model: str
    ) -> float:
        target = self.providers.get(provider, self.providers["openai"])
        return target.cost_estimate(prompt_tokens, completion_tokens, model)

    def _get_default_model(self, provider: str) -> str:
        defaults = {
            "openai": "gpt-4o",
            "gemini": "gemini-1.5-pro",
            "claude": "claude-3-5-sonnet-20241022",
            "groq": "llama3-8b-8192",
            "deepseek": "deepseek-chat",
            "ollama": "llama3",
        }
        return defaults.get(provider, "gpt-4o")
