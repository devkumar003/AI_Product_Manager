import asyncio
import logging
import hashlib
import json
from collections.abc import AsyncIterator
import httpx

from app.ai.exceptions import ProviderException
from app.ai.providers import (
    BaseProvider,
    ClaudeProvider,
    DeepSeekProvider,
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    OpenAIProvider,
)
from app.ai.schemas import AIResponse, StreamingToken
from app.core.settings import settings
from app.core.redis import cache_manager

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
            "ollama": OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL or "http://localhost:11434"
            ),
        }

    def _get_provider_priority(self, requested: str | None = None) -> list[str]:
        # Filter providers dynamically by presence of API keys
        configured = []
        if settings.OPENAI_API_KEY:
            configured.append("openai")
        if settings.ANTHROPIC_API_KEY:
            configured.append("claude")
        if settings.GEMINI_API_KEY:
            configured.append("gemini")
        if settings.GROQ_API_KEY:
            configured.append("groq")
        if settings.DEEPSEEK_API_KEY:
            configured.append("deepseek")
        # Ollama is local, always configured
        configured.append("ollama")

        # Order priority: requested provider first, if configured.
        if requested and requested in self.providers:
            if requested in configured:
                return [requested] + [p for p in configured if p != requested]
            else:
                # If requested provider is not configured, fall back to configured ones
                return configured
        return configured if configured else ["gemini"]

    def _get_cache_key(
        self,
        messages: list[dict[str, str]],
        provider: str | None,
        model: str | None,
        temperature: float,
    ) -> str:
        payload = {
            "messages": messages,
            "provider": provider,
            "model": model,
            "temperature": temperature,
        }
        dumped = json.dumps(payload, sort_keys=True)
        hashed = hashlib.sha256(dumped.encode()).hexdigest()
        return f"llm_cache:{hashed}"

    async def generate(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        retry_count: int = 3,
        timeout: float = 60.0,
        use_cache: bool = True,
    ) -> AIResponse:
        cache_key = self._get_cache_key(messages, provider, model, temperature)
        if use_cache:
            try:
                cached_data = await cache_manager.get(cache_key)
                if cached_data:
                    logger.info("LLM cache hit!")
                    data = json.loads(cached_data)
                    return AIResponse(**data)
            except Exception as ce:
                logger.warning(f"Failed to check LLM cache: {ce}")

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
                        if use_cache:
                            try:
                                await cache_manager.set(
                                    cache_key,
                                    res.model_dump_json(),
                                    expire_seconds=3600,
                                )
                            except Exception as ce:
                                logger.warning(f"Failed to set LLM cache: {ce}")
                        return res
                    else:
                        logger.warning(
                            f"Provider {p_name} returned failure: {res.error_message}"
                        )
                        last_error = Exception(res.error_message)
                except (asyncio.TimeoutError, httpx.TimeoutException) as te:
                    logger.warning(
                        f"Timeout error on {p_name} generate (attempt {attempt}): {str(te)}"
                    )
                    last_error = te
                    # On timeout, back off slightly faster
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(
                        f"Error on {p_name} generate (attempt {attempt}): {str(e)}"
                    )
                    last_error = e
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)

            logger.error(
                f"Provider {p_name} completely failed after {retry_count} retries. Falling back..."
            )

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
                    async for token in fallback_provider.generate_stream(
                        messages, config
                    ):
                        yield token
                except Exception as fe:
                    yield StreamingToken(
                        token="",
                        done=True,
                        error=f"Fallback streaming also failed: {str(fe)}",
                    )
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
