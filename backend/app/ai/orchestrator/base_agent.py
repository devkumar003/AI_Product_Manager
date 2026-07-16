import contextlib
import time
from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.schemas import AIResponse


@contextlib.asynccontextmanager
async def track_agent_tokens(llm_manager: LLMManager):
    """
    Context manager to track LLM usage metrics (tokens, models, costs)
    during agent execution by dynamically intercepting llm_manager.generate.
    """
    original_generate = llm_manager.generate
    usage_records = []

    async def tracked_generate(*args, **kwargs):
        start_time = time.time()
        response: AIResponse = await original_generate(*args, **kwargs)
        execution_time = time.time() - start_time
        
        usage_records.append({
            "model": response.model,
            "provider": response.provider,
            "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) or 0,
            "completion_tokens": getattr(response.usage, "completion_tokens", 0) or 0,
            "total_tokens": getattr(response.usage, "total_tokens", 0) or 0,
            "estimated_cost": getattr(response.usage, "estimated_cost_usd", 0.0) or 0.0,
            "execution_time": execution_time,
        })
        return response

    llm_manager.generate = tracked_generate
    try:
        yield usage_records
    finally:
        llm_manager.generate = original_generate


class BaseAgent(ABC):
    def __init__(self, llm_manager: LLMManager, telemetry: Any) -> None:
        self.llm_manager = llm_manager
        self.telemetry = telemetry

    @abstractmethod
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        """
        Asynchronously runs the agent workflow.
        Returns the raw dictionary output of the execution.
        """
        pass

    @abstractmethod
    def validate(self, output: dict[str, Any]) -> bool:
        """
        Validates the output structure.
        Returns True if valid, raises an exception or returns False otherwise.
        """
        pass

    @abstractmethod
    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        """
        Saves the output data to database models (documents, insights, planning items)
        and returns a dict of references/IDs to be stored in the workflow context.
        """
        pass
