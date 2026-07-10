import logging
from typing import Any

from app.services.ai.agents.product_agents import (
    ArchitectInput,
    IdeaInput,
    PRDGeneratorAgent,
    PRDInput,
    ProductManagerAgent,
    TechnicalArchitectAgent,
)
from app.services.ai.llm_manager import LLMManager, llm_manager
from app.services.ai.memory.conversation import ConversationMemory
from app.services.ai.memory.workspace import WorkspaceMemory

logger = logging.getLogger("app.services.ai.orchestrator")


class AIOrchestrator:
    """
    Coordinates multi-agent workflows E2E:
    Idea Refiner (Product Manager) -> Product Specs (PRD Generator) -> Design Docs (Technical Architect)
    """

    def __init__(self, llm_manager: LLMManager) -> None:
        self.llm_manager = llm_manager

        # Initialize independent memory components
        self.workspace_memory = WorkspaceMemory()
        self.conversation_memory = ConversationMemory()

        # Instantiate agents with workspace memory context
        self.pm_agent = ProductManagerAgent(
            llm_manager=self.llm_manager, memory=self.workspace_memory
        )
        self.prd_agent = PRDGeneratorAgent(
            llm_manager=self.llm_manager, memory=self.workspace_memory
        )
        self.architect_agent = TechnicalArchitectAgent(
            llm_manager=self.llm_manager, memory=self.workspace_memory
        )

    async def run_product_generation_flow(
        self,
        raw_idea: str,
        workspace_id: str,
        industry: str = "General Tech",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Runs the full E2E generation pipeline.
        """
        logger.info(
            f"Running E2E product generation flow for workspace: {workspace_id}"
        )

        # Step 1: PM Agent refines raw idea
        pm_input = IdeaInput(idea=raw_idea, target_industry=industry)
        refined_idea = await self.pm_agent.execute(pm_input, memory_key=workspace_id)

        # Store intermediate state in Workspace Memory
        await self.workspace_memory.store(
            workspace_id,
            {
                "refined_title": refined_idea.refined_title,
                "refined_description": refined_idea.refined_description,
                "target_audience": ", ".join(refined_idea.target_audience),
            },
        )

        # Step 2: PRD Agent creates comprehensive requirement document
        prd_input = PRDInput(
            refined_title=refined_idea.refined_title,
            refined_description=refined_idea.refined_description,
            target_audience=refined_idea.target_audience,
            key_objectives=refined_idea.key_objectives,
        )
        prd_document = await self.prd_agent.execute(prd_input, memory_key=workspace_id)

        # Store PRD details in Workspace Memory
        await self.workspace_memory.store(
            workspace_id, {"prd_title": prd_document.prd_title}
        )

        # Step 3: Architect Agent generates design specs
        architect_input = ArchitectInput(
            prd_title=prd_document.prd_title,
            functional_requirements=prd_document.functional_requirements,
            technical_constraints=prd_document.technical_constraints,
        )
        architecture_design = await self.architect_agent.execute(
            architect_input, memory_key=workspace_id
        )

        # Return consolidated results
        return {
            "refined_idea": refined_idea.model_dump(),
            "prd": prd_document.model_dump(),
            "architecture": architecture_design.model_dump(),
        }


ai_orchestrator = AIOrchestrator(llm_manager)
