"""
Task 21 — Prompt Chaining
Task 22 — Workflow Templates

Supports: sequential execution, conditional execution,
parallel agent execution, dynamic agent routing,
and pre-built workflow templates for common product management flows.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine

from app.ai.services.engine_executor import EngineExecutor

logger = logging.getLogger("app.ai.workflows.chaining")


class ChainStep:
    """A single step in a prompt chain."""

    def __init__(
        self,
        engine_name: str,
        input_builder: Callable[[dict[str, Any]], dict[str, Any]],
        output_key: str,
        condition: Callable[[dict[str, Any]], bool] | None = None,
    ) -> None:
        self.engine_name = engine_name
        self.input_builder = input_builder
        self.output_key = output_key
        self.condition = condition  # If set, step only runs when condition returns True


class PromptChain:
    """
    Orchestrates sequential/conditional prompt chain execution.
    Each step's output is stored in a shared context dict and available to subsequent steps.
    """

    def __init__(self, name: str, executor: EngineExecutor) -> None:
        self.name = name
        self.executor = executor
        self.steps: list[ChainStep] = []
        self.parallel_groups: list[list[ChainStep]] = []

    def add_step(self, step: ChainStep) -> "PromptChain":
        self.steps.append(step)
        return self

    def add_parallel_group(self, steps: list[ChainStep]) -> "PromptChain":
        self.parallel_groups.append(steps)
        return self

    async def execute(
        self,
        initial_context: dict[str, Any],
        workspace_id: str = "",
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Run all steps sequentially. Conditional steps are skipped if their condition returns False.
        Parallel groups are awaited concurrently between sequential steps.
        """
        context = dict(initial_context)
        context["_chain_name"] = self.name
        context["_completed_steps"] = []

        # Sequential steps
        for step in self.steps:
            # Check condition
            if step.condition and not step.condition(context):
                logger.info(f"Skipping conditional step '{step.engine_name}' in chain '{self.name}'")
                continue

            logger.info(f"Executing chain step '{step.engine_name}' in '{self.name}'")
            step_input = step.input_builder(context)

            result = await self.executor.execute(
                engine_name=step.engine_name,
                input_data=step_input,
                workspace_id=workspace_id,
                provider=provider,
                model=model,
            )

            context[step.output_key] = result
            context["_completed_steps"].append(step.engine_name)

        # Parallel groups
        for group in self.parallel_groups:
            eligible = [s for s in group if not s.condition or s.condition(context)]

            async def _run(s: ChainStep) -> tuple[str, dict[str, Any]]:
                inp = s.input_builder(context)
                res = await self.executor.execute(
                    engine_name=s.engine_name,
                    input_data=inp,
                    workspace_id=workspace_id,
                    provider=provider,
                    model=model,
                )
                return s.output_key, res

            results = await asyncio.gather(*[_run(s) for s in eligible])
            for key, val in results:
                context[key] = val
                context["_completed_steps"].append(key)

        return context


# ── Task 22: Pre-built Workflow Templates ──

def _json_dump(d: Any) -> str:
    import json
    return json.dumps(d) if isinstance(d, dict) else str(d)


def build_idea_validation_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("idea_validation", executor)
    chain.add_step(ChainStep(
        engine_name="idea_analysis",
        input_builder=lambda ctx: {"idea": ctx["idea"], "additional_context": ctx.get("context", "")},
        output_key="analysis",
    ))
    chain.add_step(ChainStep(
        engine_name="idea_validation",
        input_builder=lambda ctx: {"idea": ctx["idea"], "analysis_summary": _json_dump(ctx.get("analysis", {}))},
        output_key="validation",
    ))
    chain.add_step(ChainStep(
        engine_name="product_discovery",
        input_builder=lambda ctx: {"idea": ctx["idea"], "validation_summary": _json_dump(ctx.get("validation", {}))},
        output_key="discovery",
    ))
    return chain


def build_prd_generation_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("prd_generation", executor)
    chain.add_step(ChainStep(
        engine_name="idea_analysis",
        input_builder=lambda ctx: {"idea": ctx["idea"]},
        output_key="analysis",
    ))
    chain.add_step(ChainStep(
        engine_name="product_discovery",
        input_builder=lambda ctx: {"idea": ctx["idea"], "validation_summary": _json_dump(ctx.get("analysis", {}))},
        output_key="discovery",
    ))
    chain.add_step(ChainStep(
        engine_name="requirement_generator",
        input_builder=lambda ctx: {"product_discovery": _json_dump(ctx.get("discovery", {})), "idea": ctx["idea"]},
        output_key="requirements",
    ))
    chain.add_step(ChainStep(
        engine_name="user_story_generator",
        input_builder=lambda ctx: {"requirements": _json_dump(ctx.get("requirements", {}))},
        output_key="stories",
    ))
    chain.add_step(ChainStep(
        engine_name="prd_generator",
        input_builder=lambda ctx: {
            "idea": ctx["idea"],
            "discovery": _json_dump(ctx.get("discovery", {})),
            "requirements": _json_dump(ctx.get("requirements", {})),
            "stories": _json_dump(ctx.get("stories", {})),
        },
        output_key="prd",
    ))
    return chain


def build_architecture_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("architecture_design", executor)
    chain.add_step(ChainStep(
        engine_name="requirement_generator",
        input_builder=lambda ctx: {"product_discovery": ctx.get("idea", ""), "idea": ctx.get("idea", "")},
        output_key="requirements",
    ))
    chain.add_step(ChainStep(
        engine_name="architecture_generator",
        input_builder=lambda ctx: {"requirements": _json_dump(ctx.get("requirements", {}))},
        output_key="architecture",
    ))
    chain.add_step(ChainStep(
        engine_name="database_generator",
        input_builder=lambda ctx: {
            "architecture": _json_dump(ctx.get("architecture", {})),
            "requirements": _json_dump(ctx.get("requirements", {})),
        },
        output_key="database",
    ))
    chain.add_step(ChainStep(
        engine_name="api_generator",
        input_builder=lambda ctx: {
            "database_schema": _json_dump(ctx.get("database", {})),
            "architecture": _json_dump(ctx.get("architecture", {})),
        },
        output_key="api",
    ))
    return chain


def build_roadmap_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("roadmap_planning", executor)
    chain.add_step(ChainStep(
        engine_name="feature_prioritization",
        input_builder=lambda ctx: {"features": ctx.get("features", ctx.get("idea", "")), "framework": ctx.get("framework", "RICE")},
        output_key="prioritization",
    ))
    chain.add_step(ChainStep(
        engine_name="roadmap_generator",
        input_builder=lambda ctx: {"features": _json_dump(ctx.get("prioritization", {})), "timeline_months": ctx.get("timeline_months", 12)},
        output_key="roadmap",
    ))
    return chain


def build_sprint_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("sprint_planning", executor)
    chain.add_step(ChainStep(
        engine_name="sprint_generator",
        input_builder=lambda ctx: {"roadmap": ctx.get("roadmap_data", ctx.get("idea", "")), "team_size": ctx.get("team_size", 5)},
        output_key="sprint",
    ))
    chain.add_step(ChainStep(
        engine_name="task_breakdown",
        input_builder=lambda ctx: {"sprint_data": _json_dump(ctx.get("sprint", {}))},
        output_key="tasks",
    ))
    return chain


def build_risk_assessment_workflow(executor: EngineExecutor) -> PromptChain:
    chain = PromptChain("risk_assessment", executor)
    chain.add_step(ChainStep(
        engine_name="risk_analysis",
        input_builder=lambda ctx: {"project_context": ctx.get("project_context", ctx.get("idea", ""))},
        output_key="risks",
    ))
    chain.add_step(ChainStep(
        engine_name="cost_estimation",
        input_builder=lambda ctx: {"task_breakdown": _json_dump(ctx.get("risks", {}))},
        output_key="costs",
    ))
    chain.add_step(ChainStep(
        engine_name="timeline_prediction",
        input_builder=lambda ctx: {"task_breakdown": _json_dump(ctx.get("risks", {})), "team_size": ctx.get("team_size", 5)},
        output_key="timeline",
    ))
    return chain


# Registry of all workflow templates
WORKFLOW_TEMPLATES = {
    "idea_validation": build_idea_validation_workflow,
    "prd_generation": build_prd_generation_workflow,
    "architecture_design": build_architecture_workflow,
    "roadmap_planning": build_roadmap_workflow,
    "sprint_planning": build_sprint_workflow,
    "risk_assessment": build_risk_assessment_workflow,
}
