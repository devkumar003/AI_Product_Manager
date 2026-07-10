import abc
from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel, Field


class WorkflowContext(BaseModel):
    """
    Mutable state context carried throughout workflow execution stages.
    """

    workspace_id: str
    user_id: str
    state: dict[str, Any] = Field(default_factory=dict)
    telemetry: list[dict[str, Any]] = Field(default_factory=list)


class WorkflowStep(abc.ABC):
    """
    Abstract step in an agent chain or decision tree.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abc.abstractmethod
    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """Execute step and return the updated context."""
        pass


class ActionStep(WorkflowStep):
    """
    A step that executes an arbitrary async handler function.
    """

    def __init__(
        self,
        name: str,
        handler: Callable[[WorkflowContext], Coroutine[Any, Any, WorkflowContext]],
    ) -> None:
        super().__init__(name)
        self.handler = handler

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        return await self.handler(context)


class DecisionNode(WorkflowStep):
    """
    Conditional branching step that routes execution to path A or path B.
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[WorkflowContext], bool],
        true_step: WorkflowStep,
        false_step: WorkflowStep,
    ) -> None:
        super().__init__(name)
        self.condition = condition
        self.true_step = true_step
        self.false_step = false_step

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        decision = self.condition(context)
        context.telemetry.append(
            {"step": self.name, "branch_taken": "true" if decision else "false"}
        )
        if decision:
            return await self.true_step.run(context)
        return await self.false_step.run(context)


class WorkflowEngine:
    """
    Executes chains of actions, supporting dynamic branching and future LangGraph bindings.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.steps: list[WorkflowStep] = []

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)

    async def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Run all steps sequentially, accumulating outputs and logging timeline trace."""
        context.telemetry.append({"workflow": self.name, "event": "execution_started"})

        for step in self.steps:
            try:
                context = await step.run(context)
            except Exception as e:
                context.telemetry.append({"step": step.name, "error": str(e)})
                raise e

        context.telemetry.append(
            {"workflow": self.name, "event": "execution_completed"}
        )
        return context
