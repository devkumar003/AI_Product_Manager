from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class CEOAgentInput(BaseModel):
    idea: str = Field(..., description="The seed product idea or business concept")
    target_audience: str = Field(
        default="General Developers / Enterprises",
        description="Primary targeted audience",
    )
    monetization: str = Field(
        default="SaaS Subscription", description="Proposed revenue model"
    )


class CEOAgent(BaseAgent[CEOAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "ceo"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for business vision, product strategy, market direction, "
            "revenue strategy, SWOT analysis, and high-level KPIs."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the CEO Agent. Your role is to define the product vision, SWOT, revenue, and KPIs.\n"
            "Analyze the seed idea and target audience to generate a cohesive business strategy.\n"
            "Return a JSON object matching the AgentResponse schema. Under the 'result' key, include:\n"
            "- product_vision: string\n"
            "- business_vision: string\n"
            "- market_direction: string\n"
            "- revenue_strategy: string\n"
            "- growth_strategy: string\n"
            "- swot_analysis: dict of (strengths, weaknesses, opportunities, threats)\n"
            "- key_goals: list of strings\n"
            "- kpis: list of strings"
        )
