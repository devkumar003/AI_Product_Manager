import abc
import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.ai.config.config import ModelSettings
from app.ai.core.llm_manager import LLMManager
from app.ai.exceptions import ProviderException, ValidationException
from app.ai.memory.memory_manager import (
    ConversationMemory,
    OrganizationMemory,
    WorkspaceMemory,
)
from app.ai.prompts.prompt_manager import PromptManager
from app.ai.schemas import StreamingToken
from app.ai.telemetry.metrics import TelemetryRegistry
from app.ai.tools.tool_framework import ToolExecutor, ToolRegistry

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseAgent(Generic[InputT, OutputT], abc.ABC):
    """
    Standard Base Agent specification conforming to Task 1.
    All platform agents (CEO, Product Manager, technical architects, etc.) inherit from this.
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        prompt_manager: PromptManager,
        tool_registry: ToolRegistry,
        telemetry: TelemetryRegistry,
        input_schema: type[InputT] | None = None,
        output_schema: type[OutputT] | None = None,
        default_settings: ModelSettings | None = None,
    ) -> None:
        # Core Components
        self.llm = llm_manager
        self.prompt_manager = prompt_manager
        self.tool_registry = tool_registry
        self.tool_executor = ToolExecutor(tool_registry)
        self.telemetry = telemetry

        # Memory Manager references
        self.conversation_memory = ConversationMemory()
        self.workspace_memory = WorkspaceMemory()
        self.organization_memory = OrganizationMemory()

        # Resolve schemas if they are not passed
        if input_schema is None or output_schema is None:
            for base in getattr(self.__class__, "__orig_bases__", []):
                if hasattr(base, "__origin__") and base.__origin__ is BaseAgent:
                    args = getattr(base, "__args__", [])
                    if len(args) >= 2:
                        if input_schema is None:
                            input_schema = args[0]
                        if output_schema is None:
                            output_schema = args[1]

            # Fallbacks if inspection fails
            if input_schema is None:
                input_schema = BaseModel
            if output_schema is None:
                from app.ai.schemas import AgentResponse

                output_schema = AgentResponse

        # Schema Validation references
        self.input_schema = input_schema
        self.output_schema = output_schema

        # Configuration Settings
        self.settings = default_settings or ModelSettings(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=4096,
            retry_count=3,
            timeout=60.0,
        )

        # Logging Setup
        self.logger = logging.getLogger(f"app.ai.agents.{self.name}")

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name identifier of the agent."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Agent version string."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Agent responsibilities description."""
        pass

    @abc.abstractmethod
    def get_system_instructions(self) -> str:
        """Raw system instruction template containing variable substitution format."""
        pass

    async def execute(
        self,
        workspace_id: str,
        user_id: str,
        input_data: InputT,
        variables: dict[str, Any] | None = None,
    ) -> OutputT:
        """
        Runs the agent execution loop:
        1. Validate inputs (Pydantic validation).
        2. Load system instruction prompts.
        3. Retrieve context memories.
        4. Execute LLM completions request with retry limits.
        5. Validate output structure against schema constraints.
        6. Record performance telemetry metrics.
        """
        start_time = time.time()
        vars_dict = variables or {}

        # 1. Input Validation (Pydantic parsing)
        try:
            self.logger.info(f"Validating input for agent '{self.name}'")
            validated_input = self.input_schema(**input_data.model_dump())
        except Exception as e:
            self.logger.error(
                f"Input validation failed for agent '{self.name}': {str(e)}"
            )
            raise ValidationException(
                f"Invalid input provided to agent '{self.name}': {str(e)}"
            )

        # Prompt Injection Protection
        from app.ai.utils.security import AISecurityManager
        AISecurityManager.verify_prompt_injection(validated_input.model_dump_json())

        # 2. System Prompts Preparation
        system_base = self.get_system_instructions()

        # Auto-append validation rules demanding output formatting matching the target schema
        schema_json = json.dumps(self.output_schema.model_json_schema())
        system_prompt = (
            f"{system_base}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. You must respond ONLY with a single JSON block matching this schema:\n"
            f"{schema_json}\n"
            f"2. Never include extra text, comments, markdown notes, or code wrappers outside of the JSON block.\n"
            f"3. Make sure the output is valid JSON before responding."
        )

        # Interpolate variables if prompt template is registered in Manager
        try:
            self.prompt_manager.register_prompt(
                name=f"agent_{self.name}",
                template=system_prompt,
                category="agent",
                version=self.version,
            )
            compiled_instructions = self.prompt_manager.interpolate(
                name=f"agent_{self.name}", variables=vars_dict, version=self.version
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to interpolate prompt variables, using raw system instructions: {str(e)}"
            )
            compiled_instructions = system_prompt

        # 3. Memory Retrieval
        session_id = f"{workspace_id}:{user_id}"
        history = await self.conversation_memory.get_context(session_id)
        workspace_ctx = await self.workspace_memory.get_context(workspace_id)
        org_ctx = await self.organization_memory.get_context(workspace_id)

        # Assemble messages payload
        messages = [{"role": "system", "content": compiled_instructions}]
        messages.extend(workspace_ctx)
        messages.extend(org_ctx)
        messages.extend(history)
        messages.append({"role": "user", "content": validated_input.model_dump_json()})

        # 4. Model Invocation with self-healing retry loop
        max_validation_attempts = 3
        current_messages = list(messages)
        content = ""
        response = None

        for attempt in range(1, max_validation_attempts + 1):
            try:
                self.logger.info(
                    f"Invoking LLM for agent '{self.name}' using model '{self.settings.model}' (Attempt {attempt}/{max_validation_attempts})"
                )
                response = await self.llm.generate(
                    messages=current_messages,
                    provider=None,  # Auto-routes down priority list
                    model=self.settings.model,
                    temperature=self.settings.temperature if attempt == 1 else 0.1,
                    max_tokens=self.settings.max_tokens,
                    retry_count=1,
                    timeout=self.settings.timeout,
                    use_cache=False if attempt > 1 else True,  # Bypass cache on retry
                )

                # 5. Output Validation (conforming response to schema)
                content = response.content.strip()
                parsed_json = self._parse_json_content(content)
                validated_output = self.output_schema(**parsed_json)
                break
            except Exception as e:
                self.logger.warning(
                    f"Output validation failed for agent '{self.name}' on attempt {attempt}: {str(e)}"
                )
                if attempt == max_validation_attempts:
                    if isinstance(e, (ValidationException, json.JSONDecodeError, ValueError)):
                        raise ValidationException(
                            message=f"Agent '{self.name}' output failed target schema after {max_validation_attempts} attempts: {str(e)}",
                            details={"raw_content": content, "error": str(e)},
                        )
                    raise e

                # Append repair instructions to message chain
                current_messages.append({"role": "assistant", "content": content})
                current_messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous response failed target schema validation with error: '{str(e)}'. "
                        "Please correct the response and return ONLY valid JSON matching the schema. "
                        "Do not include any conversational filler, notes, or markdown fences except standard JSON."
                    )
                })

        # Save turns to Conversation Memory
        await self.conversation_memory.store(
            session_id,
            [
                {"role": "user", "content": validated_input.model_dump_json()},
                {"role": "assistant", "content": content},
            ],
        )

        # 6. Record Telemetry Metrics
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_request(
            workspace_id=workspace_id,
            provider=response.provider if response else "unknown",
            model=response.model if response else "unknown",
            tokens=response.usage.total_tokens if (response and response.usage) else 0,
            cost=response.usage.estimated_cost_usd if (response and response.usage) else 0.0,
            latency_ms=latency,
            success=True,
        )

        return validated_output

    async def execute_stream(
        self,
        workspace_id: str,
        user_id: str,
        input_data: InputT,
    ) -> AsyncIterator[StreamingToken]:
        """
        Executes raw token streaming.
        Note: Output schema structures validation cannot be enforced on raw streaming chunks in real time.
        """
        # Prompt Injection Protection
        from app.ai.utils.security import AISecurityManager
        AISecurityManager.verify_prompt_injection(input_data.model_dump_json())

        system_base = self.get_system_instructions()
        messages = [
            {"role": "system", "content": system_base},
            {"role": "user", "content": input_data.model_dump_json()},
        ]

        async for chunk in self.llm.stream(
            messages=messages,
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            timeout=self.settings.timeout,
        ):
            yield chunk

    def _parse_json_content(self, text: str) -> dict[str, Any]:
        from app.ai.utils.json_parser import extract_json_from_text
        try:
            return extract_json_from_text(text)
        except Exception as e:
            raise ValidationException(
                message=f"Failed to parse agent output content as valid JSON structure: {str(e)}",
                details={"raw_content": text},
            )
