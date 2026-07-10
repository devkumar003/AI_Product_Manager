"""
Task 2 — Multi-Agent Collaboration Chain

Full sequential agent pipeline: CEO → BA → PM → ... → Reviewer → Final
Supports sequential, parallel, conditional, and dynamic routing.
"""

import asyncio
import logging
import time
from typing import Any

logger = logging.getLogger("app.ai.agents.collaboration")


class AgentCollaborationChain:
    """
    Orchestrates multi-agent collaboration where each agent receives
    the accumulated context from all prior agents in the chain.
    """

    # Default sequential pipeline order
    DEFAULT_PIPELINE = [
        "ceo",
        "business_analyst",
        "product_manager",
        "market_research",
        "technical_architect",
        "database_architect",
        "api_architect",
        "backend_architect",
        "frontend_architect",
        "ux_designer",
        "qa",
        "security",
        "devops",
        "documentation",
        "analytics",
        "review",
    ]

    def __init__(self, orchestrator: Any) -> None:
        self.orchestrator = orchestrator

    async def execute_sequential(
        self,
        pipeline: list[str] | None = None,
        workspace_id: str = "",
        user_id: str = "",
        initial_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute agents sequentially, passing accumulated context."""
        agents = pipeline or self.DEFAULT_PIPELINE
        context: dict[str, Any] = dict(initial_input or {})
        results: dict[str, Any] = {}
        start = time.time()

        for agent_name in agents:
            try:
                agent_input = {"idea": context.get("idea", ""), **context}
                result = await self.orchestrator.execute_agent(
                    agent_name=agent_name,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    input_data=agent_input,
                )
                results[agent_name] = (
                    result.model_dump() if hasattr(result, "model_dump") else result
                )
                context[f"{agent_name}_output"] = results[agent_name]
                logger.info(f"Agent '{agent_name}' completed in chain")
            except Exception as e:
                logger.error(f"Agent '{agent_name}' failed in chain: {e}")
                results[agent_name] = {"status": "failed", "error": str(e)}

        return {
            "pipeline": agents,
            "results": results,
            "total_agents": len(agents),
            "completed": sum(
                1
                for r in results.values()
                if isinstance(r, dict) and r.get("status") != "failed"
            ),
            "total_time_ms": (time.time() - start) * 1000,
        }

    async def execute_parallel(
        self,
        agent_names: list[str],
        workspace_id: str = "",
        user_id: str = "",
        shared_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute multiple agents in parallel with the same input."""
        shared = dict(shared_input or {})

        async def _run(name: str) -> tuple[str, Any]:
            try:
                result = await self.orchestrator.execute_agent(
                    agent_name=name,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    input_data={"idea": shared.get("idea", ""), **shared},
                )
                return name, (
                    result.model_dump() if hasattr(result, "model_dump") else result
                )
            except Exception as e:
                return name, {"status": "failed", "error": str(e)}

        results = await asyncio.gather(*[_run(n) for n in agent_names])
        return {name: result for name, result in results}

    async def execute_conditional(
        self,
        pipeline: list[dict[str, Any]],
        workspace_id: str = "",
        user_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute agents conditionally. Each step is:
        {"agent": "name", "condition": callable(context) -> bool}
        """
        ctx = dict(context or {})
        results: dict[str, Any] = {}

        for step in pipeline:
            agent_name = step["agent"]
            condition = step.get("condition")

            if condition and not condition(ctx):
                logger.info(f"Skipping agent '{agent_name}' — condition not met")
                results[agent_name] = {"status": "skipped"}
                continue

            try:
                result = await self.orchestrator.execute_agent(
                    agent_name=agent_name,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    input_data={"idea": ctx.get("idea", ""), **ctx},
                )
                dump = result.model_dump() if hasattr(result, "model_dump") else result
                results[agent_name] = dump
                ctx[f"{agent_name}_output"] = dump
            except Exception as e:
                results[agent_name] = {"status": "failed", "error": str(e)}

        return results
