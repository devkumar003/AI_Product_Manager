from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class PMAgentInput(BaseModel):
    strategy_summary: str = Field(..., description="Strategy summary from CEO Agent")
    priority_focus: str = Field(
        default="MVP Features", description="Focus of prioritization"
    )


class PMAgent(BaseAgent[PMAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "product_manager"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for feature planning, scoping, roadmap phases, "
            "prioritizing backlogs, and feature dependency mapping."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Product Manager Agent. Your role is to plan features and dependencies.\n"
            "Under the 'result' key of the AgentResponse, output a structured product plan:\n"
            "- features: list of dicts (name, description, priority, dependencies)\n"
            "- scope_boundary: list of in_scope and out_of_scope items\n"
            "- release_milestones: list of dicts (phase, version, target_features)"
        )
