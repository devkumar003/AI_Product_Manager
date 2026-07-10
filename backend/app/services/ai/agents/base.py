import logging
from collections.abc import AsyncIterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.ai.utils.json_parser import extract_json_from_text
from app.services.ai.llm_manager import LLMManager
from app.services.ai.memory.base import BaseMemory

logger = logging.getLogger("app.services.ai.agents")

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class AgentConfig(BaseModel):
    model: str = "gpt-4o"
    provider: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    max_retries: int = 3


class BaseAgent(Generic[InputT, OutputT]):
    """
    Standard Base Agent implementing structural configurations, memory bindings,
    and retry-backoff validations.
    """

    def __init__(
        self,
        system_prompt: str,
        prompt_template: str,
        input_schema: type[InputT],
        output_schema: type[OutputT],
        llm_manager: LLMManager,
        config: AgentConfig | None = None,
        memory: BaseMemory | None = None,
        tools: list[Any] | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.prompt_template = prompt_template
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.llm_manager = llm_manager
        self.config = config or AgentConfig()
        self.memory = memory
        self.tools = tools or []

    async def execute(
        self, inputs: InputT, memory_key: str | None = None, **kwargs: Any
    ) -> OutputT:
        """
        Format prompts, query memory adapters, invoke LLMs, validate schema outputs, and save state.
        """
        # Format template
        formatted_user_prompt = self.prompt_template.format(**inputs.model_dump())

        # Compile messages stack
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.memory and memory_key:
            ctx = await self.memory.get_context(memory_key, **kwargs)
            messages.extend(ctx)

        messages.append({"role": "user", "content": formatted_user_prompt})

        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.info(
                    f"Agent execution attempt {attempt + 1}/{self.config.max_retries}"
                )
                response_text = await self.llm_manager.generate(
                    messages=messages,
                    model=self.config.model,
                    provider=self.config.provider,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )

                # Parse JSON string output if output schema is a Pydantic model
                if issubclass(self.output_schema, BaseModel):
                    try:
                        extracted = extract_json_from_text(response_text)
                        parsed_output = self.output_schema.model_validate(extracted)
                    except Exception as parse_err:
                        logger.warning(
                            f"JSON validation failed on attempt {attempt + 1}: {parse_err}"
                        )
                        # Add self-healing feedback to message chain for next retry attempt
                        messages.append({"role": "assistant", "content": response_text})
                        messages.append(
                            {
                                "role": "user",
                                "content": f"Your previous output failed Pydantic schema validation: {parse_err}. Please return ONLY valid JSON strictly adhering to the schema.",
                            }
                        )
                        raise ValueError(
                            f"Model output did not match expected Pydantic schema structure: {parse_err}. Output: {response_text}"
                        )
                else:
                    parsed_output = response_text

                # Save back to memory
                if self.memory and memory_key:
                    await self.memory.store(
                        memory_key,
                        [
                            {"role": "user", "content": formatted_user_prompt},
                            {"role": "assistant", "content": response_text},
                        ],
                    )

                return parsed_output

            except Exception as e:
                last_error = e
                logger.warning(f"Error encountered on attempt {attempt + 1}: {str(e)}")

        raise Exception(
            f"Agent execution failed after {self.config.max_retries} attempts. Last error: {str(last_error)}"
        )

    async def execute_stream(
        self, inputs: InputT, memory_key: str | None = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        Streaming completions gateway with async context loading.
        """
        formatted_user_prompt = self.prompt_template.format(**inputs.model_dump())
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.memory and memory_key:
            ctx = await self.memory.get_context(memory_key, **kwargs)
            messages.extend(ctx)

        messages.append({"role": "user", "content": formatted_user_prompt})

        async for chunk in self.llm_manager.generate_stream(
            messages=messages,
            model=self.config.model,
            provider=self.config.provider,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        ):
            yield chunk
