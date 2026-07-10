import asyncio
import logging
import threading
from collections.abc import AsyncIterator
from typing import Any

from app.ai.core.llm_manager import LLMManager as CoreLLMManager
from app.core.settings import settings

logger = logging.getLogger("app.services.ai.llm_manager")


class LLMResponse(str):
    """
    Backward-compatible string subclass that exposes a .content property.
    """

    def __new__(cls, content: str):
        return super().__new__(cls, content)

    @property
    def content(self) -> str:
        return str(self)


def run_sync(coro: Any) -> Any:
    """
    Safely executes an async coroutine synchronously from any context.
    Prevents thread-pool deadlocks and loop attachment conflicts when called inside an running event loop.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        result_container = []
        error_container = []

        def _worker():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                res = new_loop.run_until_complete(coro)
                result_container.append(res)
            except Exception as e:
                error_container.append(e)
            finally:
                new_loop.close()

        thread = threading.Thread(target=_worker)
        thread.start()
        thread.join()

        if error_container:
            raise error_container[0]
        return result_container[0]
    else:
        return asyncio.run(coro)


class LLMManager:
    """
    Refactored Service-layer LLM Manager. Bridges legacy service calls to the enterprise-grade
    app.ai.core.llm_manager.LLMManager, adding intelligent reasoning model routing and cross-provider failover.
    """

    def __init__(self) -> None:
        self.core_manager = CoreLLMManager()

    def _resolve_provider_name(self, provider: str | None, model: str) -> str:
        if provider:
            p_name = provider.lower()
            if p_name in self.core_manager.providers:
                return p_name
            logger.warning(
                f"Unknown provider '{provider}' requested. Falling back to auto-detection."
            )

        m_lower = model.lower()
        if m_lower.startswith(
            ("gpt-", "o1", "o3", "ft:gpt", "dall-e", "text-embedding")
        ):
            if not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY:
                return "gemini"
            return "openai"
        elif m_lower.startswith("gemini-"):
            return "gemini"
        elif m_lower.startswith("claude-"):
            return "claude"
        elif m_lower.startswith("deepseek-"):
            return "deepseek"
        elif m_lower.startswith(("groq/", "llama3", "mixtral", "gemma")):
            return "groq"
        elif (
            "llama" in m_lower
            or "mistral" in m_lower
            or "phi" in m_lower
            or m_lower.startswith("ollama/")
        ):
            return "ollama"
        else:
            if not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY:
                return "gemini"
            return "openai"

    async def generate(
        self,
        messages: list[dict[str, str]] | None = None,
        model: str = "gpt-4o",
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Unified generation gateway delegating to CoreLLMManager for retry and cross-provider failover.
        """
        prompt = kwargs.pop("prompt", None)
        system_prompt = kwargs.pop("system_prompt", None)
        config = kwargs.pop("config", None)
        if config:
            if hasattr(config, "model"):
                model = config.model or model
            if hasattr(config, "provider"):
                provider = config.provider or provider
            if hasattr(config, "temperature"):
                temperature = config.temperature or temperature
            if hasattr(config, "max_tokens"):
                max_tokens = config.max_tokens or max_tokens

        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if prompt:
                messages.append({"role": "user", "content": prompt})

        if not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY:
            if model in ("gpt-4o", "gpt-4", "gpt-3.5-turbo") or not provider:
                model = "gemini-1.5-pro"
                provider = "gemini"

        resolved_provider = self._resolve_provider_name(provider, model)

        try:
            res = await self.core_manager.generate(
                messages=messages,
                provider=resolved_provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return LLMResponse(res.content)
        except Exception as e:
            logger.error(f"CoreLLMManager generation failed: {str(e)}")
            raise e

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4o",
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Unified streaming generation gateway.
        """
        if not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY:
            if model in ("gpt-4o", "gpt-4", "gpt-3.5-turbo") or not provider:
                model = "gemini-1.5-pro"
                provider = "gemini"

        resolved_provider = self._resolve_provider_name(provider, model)

        async def _generator():
            async for token_obj in self.core_manager.stream(
                messages=messages,
                provider=resolved_provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                if token_obj.error:
                    logger.error(f"Streaming error encountered: {token_obj.error}")
                    raise Exception(token_obj.error)
                if token_obj.token:
                    yield token_obj.token

        return _generator()

    def generate_sync(
        self,
        messages: list[dict[str, str]] | None = None,
        model: str = "gpt-4o",
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> LLMResponse:
        return run_sync(
            self.generate(
                messages=messages,
                model=model,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        )


llm_manager = LLMManager()
