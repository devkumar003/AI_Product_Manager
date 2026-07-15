import asyncio
import threading
from typing import Any
import logging

from app.ai.core.llm_manager import LLMManager as CoreLLMManager

logger = logging.getLogger("app.utils.llm_wrapper")

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

class AgentConfig:
    def __init__(self, temperature: float = 0.7, max_tokens: int = 4096, model: str = None, provider: str = None):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.provider = provider

class LLMResponse(str):
    """
    Backward-compatible string subclass that exposes a .content property.
    """
    def __new__(cls, content: str):
        return super().__new__(cls, content)

    @property
    def content(self) -> str:
        return str(self)

class LegacyLLMWrapper:
    def __init__(self):
        self.core_manager = CoreLLMManager()

    def generate_sync(
        self,
        prompt: str = None,
        system_prompt: str = None,
        messages: list[dict[str, str]] = None,
        temperature: float = 0.7,
        config: AgentConfig = None,
        **kwargs
    ) -> LLMResponse:
        if config:
            temperature = config.temperature

        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if prompt:
                messages.append({"role": "user", "content": prompt})

        try:
            res = run_sync(
                self.core_manager.generate(
                    messages=messages,
                    temperature=temperature
                )
            )
            return LLMResponse(res.content)
        except Exception as e:
            logger.error(f"LegacyLLMWrapper generation failed: {str(e)}")
            raise e

llm_manager = LegacyLLMWrapper()
