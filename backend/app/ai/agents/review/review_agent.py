from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class ReviewAgentInput(BaseModel):
    agent_outputs: str = Field(..., description="JSON string of all prior agent outputs to review")


class ReviewAgent(BaseAgent[ReviewAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "review"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Cross-validates outputs from all other agents, checking for consistency, "
            "missing fields, duplicate features, and dependency conflicts."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Review Agent. You receive the combined outputs of every other agent "
            "and perform a thorough cross-validation.\n"
            "Check for:\n"
            "- Consistency across agent outputs\n"
            "- Missing fields or incomplete sections\n"
            "- Duplicate features listed by multiple agents\n"
            "- Dependency conflicts between architecture, database, and API designs\n"
            "- Alignment between business strategy and technical implementation\n\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- consistency_score: float (0.0 to 1.0)\n"
            "- missing_items: list of dicts (agent_name, missing_field, severity)\n"
            "- duplicates_found: list of dicts (item, found_in_agents)\n"
            "- dependency_conflicts: list of dicts (conflict, agents_involved, recommendation)\n"
            "- alignment_notes: list of strings"
        )
