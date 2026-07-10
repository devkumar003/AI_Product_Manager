from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class PriorityAgentInput(BaseModel):
    features_list: str = Field(
        ..., description="List of features with descriptions to prioritize"
    )
    framework: str = Field(
        default="RICE",
        description="Prioritization framework: MoSCoW, RICE, ICE, or value_vs_effort",
    )


class PriorityAgent(BaseAgent[PriorityAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "priority"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Scores and ranks features using industry-standard prioritization frameworks "
            "including MoSCoW, RICE, ICE, and Value vs. Effort matrices."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Priority Agent. Apply the requested prioritization framework to the feature list.\n"
            "Support the following frameworks:\n"
            "- MoSCoW: Must Have, Should Have, Could Have, Won't Have\n"
            "- RICE: Reach * Impact * Confidence / Effort\n"
            "- ICE: Impact * Confidence * Ease\n"
            "- Value vs Effort: value_score / effort_score\n\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- framework_used: string\n"
            "- ranked_features: list of dicts (feature_name, score, tier, rationale)\n"
            "- priority_matrix: dict mapping tier_name to list of feature_names\n"
            "- top_3_recommendations: list of strings"
        )
