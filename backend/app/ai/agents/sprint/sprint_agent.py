from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class SprintAgentInput(BaseModel):
    roadmap_milestones: str = Field(..., description="Details of current roadmap milestones")
    team_velocity: int = Field(default=30, description="Estimated story points per sprint")


class SprintAgent(BaseAgent[SprintAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "sprint"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for sprint planning, formulating sprint goals, calculating team capacities, "
            "and picking sprint backlog cards."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Sprint Agent. Conduct sprint planners, outline sprint goals, and allocate capacity.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- sprint_goal: string\n"
            "- capacity_allocation: dict of (development_pts, qa_pts, design_pts)\n"
            "- sprint_backlog: list of dicts (title, points, category)\n"
            "- velocity_estimate: int\n"
            "- duration_weeks: int"
        )
