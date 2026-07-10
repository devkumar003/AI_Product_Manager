from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class RiskAgentInput(BaseModel):
    project_summary: str = Field(
        ..., description="Combined project context from prior agents"
    )


class RiskAgent(BaseAgent[RiskAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "risk"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Identifies and catalogues technical, business, schedule, budget, "
            "and dependency risks with mitigation plans for each."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Risk Agent. Identify project risks and propose mitigation strategies.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- technical_risks: list of dicts (risk, probability, impact, mitigation)\n"
            "- business_risks: list of dicts (risk, probability, impact, mitigation)\n"
            "- schedule_risks: list of dicts (risk, probability, impact, mitigation)\n"
            "- budget_risks: list of dicts (risk, probability, impact, mitigation)\n"
            "- dependency_risks: list of dicts (risk, probability, impact, mitigation)\n"
            "- overall_risk_score: string (low, medium, high, critical)"
        )
