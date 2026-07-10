from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class RoadmapAgentInput(BaseModel):
    features_list: str = Field(..., description="List of targeted MVP features")
    timeline_months: int = Field(default=6, description="Timeline window in months")


class RoadmapAgent(BaseAgent[RoadmapAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "roadmap"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for formulating product release phases, mapping monthly milestones, "
            "and highlighting phase-by-phase feature dependencies."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Roadmap Agent. Establish quarterly and monthly product roadmaps with milestones.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- quarterly_phases: list of dicts (quarter, focus, milestones)\n"
            "- monthly_milestones: list of dicts (month, goals, features)\n"
            "- critical_path_dependencies: list of strings\n"
            "- release_dates: list of dicts (release, version, target)"
        )
