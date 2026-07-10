import abc
from typing import Any, Callable, Type
from pydantic import BaseModel, Field


class BaseTool(abc.ABC):
    """
    Abstract class for all tools available to LLM models during agent execution loops.
    """

    def __init__(self, name: str, description: str, args_schema: Type[BaseModel]) -> None:
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abc.abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Run the tool logic with validated arguments."""
        pass

    def get_openai_metadata(self) -> dict[str, Any]:
        """Convert the tool signature to OpenAI function call specifications."""
        schema = self.args_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }


class ToolRegistry:
    """
    Registry for tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_openai_tools_metadata(self) -> list[dict[str, Any]]:
        return [tool.get_openai_metadata() for tool in self._tools.values()]


class ToolExecutor:
    """
    Validates arguments and executes registered tools safely.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    async def execute(self, tool_name: str, raw_arguments: dict[str, Any]) -> Any:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' is not registered.")

        # Validate arguments using Pydantic model
        try:
            validated_args = tool.args_schema(**raw_arguments)
        except Exception as e:
            raise ValueError(f"Arguments validation failed for tool '{tool_name}': {str(e)}")

        try:
            return await tool.execute(**validated_args.model_dump())
        except Exception as e:
            raise RuntimeError(f"Execution of tool '{tool_name}' failed: {str(e)}")


# -------------------------------------------------------------
# Interface descriptors for future tools (TASK 9 requirements)
# -------------------------------------------------------------

class WebSearchArgs(BaseModel):
    query: str = Field(..., description="The query to search the web for")


class WebSearchTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            name="web_search",
            description="Perform a search on the web to retrieve live content.",
            args_schema=WebSearchArgs,
        )

    async def execute(self, query: str) -> Any:
        raise NotImplementedError("Web search tool execution is not implemented yet.")


class DatabaseArgs(BaseModel):
    query: str = Field(..., description="SQL query to execute against the PostgreSQL database")


class DatabaseTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            name="database_query",
            description="Query the internal relational database using SQL.",
            args_schema=DatabaseArgs,
        )

    async def execute(self, query: str) -> Any:
        raise NotImplementedError("Database query tool execution is not implemented yet.")


class CalculatorArgs(BaseModel):
    expression: str = Field(..., description="Math expression to calculate, e.g. '2 + 2 * 7'")


class CalculatorTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="Perform simple mathematical calculations.",
            args_schema=CalculatorArgs,
        )

    async def execute(self, expression: str) -> Any:
        raise NotImplementedError("Calculator tool execution is not implemented yet.")
