from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class SecurityAgentInput(BaseModel):
    architecture_overview: str = Field(
        ..., description="Details of tech stack and design decisions"
    )


class SecurityAgent(BaseAgent[SecurityAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "security"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Performs architectural vulnerability sweeps, assessing authentication systems, "
            "evaluating secret credentials storage, and planning dependency scanning profiles."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Security Agent. Draft security guidelines, OWASP controls, and credentials audit criteria.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- security_checklist: list of strings\n"
            "- authentication_review: string\n"
            "- authorization_review: string\n"
            "- owasp_recommendations: list of dicts (id, description, mapping_code)\n"
            "- dependency_scan_strategy: string\n"
            "- secrets_protection_rules: list of strings"
        )
