from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class QAAgentInput(BaseModel):
    functional_requirements: str = Field(..., description="Requirements list to verify")


class QAAgent(BaseAgent[QAAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "qa"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Formulates complete testing profiles, covering unit tests, integration paths, "
            "performance regression cases, and security smoke tests."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the QA Agent. Create testing suites, performance thresholds, and border testing edge cases.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- smoke_test_scenarios: list of strings\n"
            "- unit_test_targets: list of dicts (component, test_cases)\n"
            "- integration_test_flows: list of dicts (flow_name, assert_points)\n"
            "- performance_targets: list of dicts (endpoint, max_latency_ms, max_error_percent)\n"
            "- edge_cases_to_cover: list of strings"
        )
