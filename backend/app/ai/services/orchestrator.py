import logging
import time
import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.ai.agents.analytics import AnalyticsAgent
from app.ai.agents.api_architect import APIArchitect
from app.ai.agents.backend_architect import BackendArchitect
from app.ai.agents.business_analyst import BAAgent

# Agent imports — all 24 agents
from app.ai.agents.CEO import CEOAgent
from app.ai.agents.communication import AgentCommunicationBus
from app.ai.agents.database_architect import DBArchitect
from app.ai.agents.devops import DevOpsAgent
from app.ai.agents.documentation import DocumentationAgent
from app.ai.agents.estimation import EstimationAgent
from app.ai.agents.frontend_architect import FrontendArchitect
from app.ai.agents.knowledge import KnowledgeAgent
from app.ai.agents.market_research import ResearchAgent
from app.ai.agents.meeting import MeetingAgent
from app.ai.agents.priority import PriorityAgent
from app.ai.agents.product_manager import PMAgent
from app.ai.agents.qa import QAAgent
from app.ai.agents.review import ReviewAgent
from app.ai.agents.risk import RiskAgent
from app.ai.agents.roadmap import RoadmapAgent
from app.ai.agents.security import SecurityAgent
from app.ai.agents.sprint import SprintAgent
from app.ai.agents.task import TaskAgent
from app.ai.agents.technical_architect import TechArchitect
from app.ai.agents.ux_designer import UXAgent
from app.ai.core.llm_manager import LLMManager
from app.ai.exceptions import AIException, ValidationException
from app.ai.memory.memory_manager import (
    ConversationMemory,
    OrganizationMemory,
    WorkspaceMemory,
)
from app.ai.prompts.prompt_manager import PromptManager
from app.ai.registry.agent_registry import AgentRegistry
from app.ai.schemas import (
    AgentResponse,
    AIRequest,
    AIResponse,
    StreamingToken,
    TokenUsage,
)
from app.ai.telemetry.metrics import TelemetryRegistry
from app.ai.tools.tool_framework import ToolRegistry
from app.ai.utils.security import AISecurityManager

logger = logging.getLogger("app.ai.orchestrator")


class AIOrchestrator:
    """
    Unified entry point for all AI capabilities in AI ProductOS.

    Request Flow:
        User -> AI Endpoint -> AI Orchestrator -> Agent Registry
             -> Selected Agent -> LLM Manager -> Provider -> Response

    Supports two modes:
        1. Chat mode (no agent_name): direct LLM completion via prompt templates
        2. Agent mode (agent_name specified): routed through the full agent pipeline
    """

    def __init__(self) -> None:
        # Core infrastructure singletons
        self.llm_manager = LLMManager()
        self.agent_registry = AgentRegistry()
        self.prompt_manager = PromptManager()
        self.tool_registry = ToolRegistry()
        self.telemetry = TelemetryRegistry()
        self.communication_bus = AgentCommunicationBus()

        # Core Memory adapters
        self.conversation_memory = ConversationMemory()
        self.workspace_memory = WorkspaceMemory()
        self.organization_memory = OrganizationMemory()

        self._load_default_prompts()
        self._register_all_agents()

    # ──────────────────────────────────────────────
    # Initialization
    # ──────────────────────────────────────────────

    def _load_default_prompts(self) -> None:
        self.prompt_manager.register_prompt(
            name="chat_assistant",
            template=(
                "You are AI ProductOS Conversational Assistant.\n"
                "Help the user plan specs, review requirements, and coordinate product milestones.\n"
                "System instructions:\n"
                "{{AUDIT_RULES}}\n"
                "{{SECURITY_SANDBOX}}"
            ),
            category="system",
        )

    def _register_all_agents(self) -> None:
        """Instantiate and register every agent with shared infrastructure references."""
        agent_classes = [
            CEOAgent,
            PMAgent,
            BAAgent,
            ResearchAgent,
            UXAgent,
            TechArchitect,
            DBArchitect,
            APIArchitect,
            BackendArchitect,
            FrontendArchitect,
            RoadmapAgent,
            SprintAgent,
            TaskAgent,
            QAAgent,
            SecurityAgent,
            DevOpsAgent,
            AnalyticsAgent,
            MeetingAgent,
            DocumentationAgent,
            KnowledgeAgent,
            ReviewAgent,
            EstimationAgent,
            RiskAgent,
            PriorityAgent,
        ]

        for agent_cls in agent_classes:
            # Instantiate with shared infrastructure — each agent uses the
            # same LLM manager, prompt manager, tool registry, and telemetry
            instance = agent_cls(
                llm_manager=self.llm_manager,
                prompt_manager=self.prompt_manager,
                tool_registry=self.tool_registry,
                telemetry=self.telemetry,
            )

            self.agent_registry.register(
                name=instance.name,
                agent_class=agent_cls,
                version=instance.version,
                description=instance.description,
            )

            # Store the live instance for execution routing
            self.agent_registry._agents[instance.name]["instance"] = instance

        logger.info(
            f"Registered {len(agent_classes)} agents in the Agent Registry: "
            f"{[a.name.fget(a) if hasattr(a.name, 'fget') else 'unknown' for a in agent_classes]}"
        )

    def _get_agent_instance(self, agent_name: str) -> Any:
        """Retrieve a live agent instance from the registry."""
        entry = self.agent_registry._agents.get(agent_name)
        if not entry or "instance" not in entry:
            raise AIException(
                message=f"Agent '{agent_name}' is not registered or has no active instance.",
                details={"available_agents": list(self.agent_registry._agents.keys())},
            )
        return entry["instance"]

    # ──────────────────────────────────────────────
    # Agent-mode execution
    # ──────────────────────────────────────────────

    async def execute_agent(
        self,
        agent_name: str,
        workspace_id: str,
        user_id: str,
        input_data: dict[str, Any],
    ) -> AgentResponse:
        """
        Execute a specific agent by name. The agent handles its own prompt
        construction, LLM routing, retry logic, and output validation.
        """
        agent = self._get_agent_instance(agent_name)

        # Build input using the agent's own input schema
        try:
            validated_input = agent.input_schema(**input_data)
        except Exception as e:
            raise ValidationException(
                message=f"Invalid input for agent '{agent_name}': {str(e)}",
                details={"input_data": input_data},
            )

        result = await agent.execute(
            workspace_id=workspace_id,
            user_id=user_id,
            input_data=validated_input,
        )

        return result

    # ──────────────────────────────────────────────
    # Chat-mode execution (existing behaviour)
    # ──────────────────────────────────────────────

    async def execute_request(self, req: AIRequest) -> AIResponse:
        """
        Main execution point for standard/non-streaming completions requests.
        If req.agent_name is specified, routes through the agent pipeline.
        Otherwise falls through to direct chat completion.
        """
        # If an agent name is specified, route through agent execution
        if req.agent_name:
            agent_result = await self.execute_agent(
                agent_name=req.agent_name,
                workspace_id=req.workspace_id,
                user_id=req.user_id,
                input_data={"idea": req.user_message, **req.prompt_variables},
            )
            # Wrap AgentResponse into AIResponse for consistent API contract
            return AIResponse(
                content=agent_result.model_dump_json(),
                model="agent:" + req.agent_name,
                provider="orchestrator",
                usage=TokenUsage(),
                latency_ms=0.0,
                success=True,
            )

        # ── Standard chat completion path ──
        start_time = time.time()

        # 1. Security Check: Prompt Injection Scan
        AISecurityManager.verify_prompt_injection(req.user_message)
        sanitized_input = AISecurityManager.sanitize_input(req.user_message)

        # 2. Context & Memory Loading (Concurrent)
        session_id = f"{req.workspace_id}:{req.user_id}"
        
        workspace_ctx, org_ctx, conversation_history = await asyncio.gather(
            self.workspace_memory.get_context(req.workspace_id),
            self.organization_memory.get_context(req.workspace_id),
            self.conversation_memory.get_context(session_id)
        )

        # 4. Prompt loading & interpolation
        prompt_name = req.prompt_name or "chat_assistant"
        try:
            system_prompt = self.prompt_manager.interpolate(
                prompt_name, req.prompt_variables
            )
        except Exception:
            system_prompt = self.prompt_manager.get_prompt("chat_assistant").template

        if req.system_prompt_override:
            system_prompt += f"\n\nAdditional instruction: {req.system_prompt_override}"

        # 5. Build standard messages payload
        messages = [{"role": "system", "content": system_prompt}]
        for ctx in workspace_ctx + org_ctx:
            messages.append(ctx)
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": sanitized_input})

        # 6. Provider/Model Selection
        provider = req.provider_override
        model = req.model_override

        # 7. Execution through LLM routing gateway
        try:
            logger.info(
                f"Orchestrator routing query to LLM. Provider: {provider}, Model: {model}"
            )
            res = await self.llm_manager.generate(
                messages=messages,
                provider=provider,
                model=model,
                temperature=req.temperature_override or 0.7,
            )

            masked_content = AISecurityManager.mask_secrets(res.content)
            res.content = masked_content

            # 8. Save execution turns to Conversation Memory
            await self.conversation_memory.store(
                session_id,
                [
                    {"role": "user", "content": sanitized_input},
                    {"role": "assistant", "content": masked_content},
                ],
            )

            # 9. Record Telemetry Metrics
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_request(
                workspace_id=req.workspace_id,
                provider=res.provider,
                model=res.model,
                tokens=res.usage.total_tokens,
                cost=res.usage.estimated_cost_usd,
                latency_ms=latency,
                success=True,
            )

            return res

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_request(
                workspace_id=req.workspace_id,
                provider=provider or "unknown",
                model=model or "unknown",
                tokens=0,
                cost=0.0,
                latency_ms=latency,
                success=False,
            )
            logger.exception("AI request execution failed in orchestrator pipeline.")
            raise AIException(
                message=f"Orchestrator failed to process execution: {str(e)}"
            )

    async def execute_stream(self, req: AIRequest) -> AsyncIterator[StreamingToken]:
        """
        Main execution point for real-time tokens streaming.
        """
        AISecurityManager.verify_prompt_injection(req.user_message)
        sanitized_input = AISecurityManager.sanitize_input(req.user_message)

        session_id = f"{req.workspace_id}:{req.user_id}"
        conversation_history = await self.conversation_memory.get_context(session_id)

        prompt_name = req.prompt_name or "chat_assistant"
        try:
            system_prompt = self.prompt_manager.interpolate(
                prompt_name, req.prompt_variables
            )
        except Exception:
            system_prompt = self.prompt_manager.get_prompt("chat_assistant").template

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": sanitized_input})

        provider = req.provider_override
        model = req.model_override

        try:
            async for token in self.llm_manager.stream(
                messages=messages,
                provider=provider,
                model=model,
                temperature=req.temperature_override or 0.7,
            ):
                yield token
        except Exception as e:
            yield StreamingToken(token="", done=True, error=str(e))

    # ──────────────────────────────────────────────
    # Registry inspection helpers
    # ──────────────────────────────────────────────

    def list_agents(self) -> list[dict[str, Any]]:
        """Return metadata for all registered agents."""
        return [
            {
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "status": meta.status,
                "health": meta.health,
            }
            for meta in self.agent_registry.list_agents()
        ]
