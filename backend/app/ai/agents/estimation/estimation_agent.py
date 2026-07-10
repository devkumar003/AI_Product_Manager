from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class EstimationAgentInput(BaseModel):
    task_breakdown: str = Field(..., description="Task breakdown from the Task Generator Agent")
    team_size: int = Field(default=5, description="Number of developers available")


class EstimationAgent(BaseAgent[EstimationAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "estimation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Produces development time estimates, resource cost projections, "
            "complexity assessments, and confidence scoring for project delivery."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Estimation Agent. Estimate development effort, cost, and complexity.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- total_development_hours: int\n"
            "- total_development_weeks: int\n"
            "- estimated_cost_usd: float\n"
            "- resource_requirements: list of dicts (role, count, hours_per_week)\n"
            "- complexity_assessment: string (low, medium, high, very_high)\n"
            "- confidence_score: float (0.0 to 1.0)\n"
            "- phase_estimates: list of dicts (phase, hours, cost_usd)"
        )
