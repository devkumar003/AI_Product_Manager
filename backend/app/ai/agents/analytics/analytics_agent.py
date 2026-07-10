from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class AnalyticsAgentInput(BaseModel):
    product_vision: str = Field(..., description="Core product goals and target metrics")


class AnalyticsAgent(BaseAgent[AnalyticsAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "analytics"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for formulating measurement frameworks, establishing North Star goals, "
            "and outlining telemetry specifications for user retention and system performance."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Analytics Agent. Build analytics configurations, retention indices, and core business telemetry charts.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- north_star_metric: string\n"
            "- business_kpis: list of strings\n"
            "- product_metrics: list of strings\n"
            "- adoption_metrics: list of strings\n"
            "- retention_metrics: list of strings\n"
            "- tracking_setup_rec: string"
        )
