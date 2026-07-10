from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class ResearchAgentInput(BaseModel):
    niche: str = Field(..., description="The industry or market niche to search")


class ResearchAgent(BaseAgent[ResearchAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "market_research"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Performs market analysis, identifying top competitors, comparing feature gaps, "
            "sizing target audiences, and advising pricing levels."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Market Research Agent. Outline the market landscapes, size, and trends.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- market_size_est: string\n"
            "- growth_trends: list of strings\n"
            "- top_competitors: list of dicts (name, features, market_share_tier)\n"
            "- feature_gaps: list of strings\n"
            "- target_personas: list of strings\n"
            "- pricing_benchmarks: list of dicts (tier, rate_usd, description)"
        )
