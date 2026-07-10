from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class BackendArchitectInput(BaseModel):
    endpoints_specification: str = Field(..., description="API endpoints definitions")


class BackendArchitect(BaseAgent[BackendArchitectInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "backend_architect"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for designing FastAPI modules, service classes, repository queries, "
            "dependency injection hooks, and validation layers."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Backend Architect Agent. Lay out module patterns, routers, dependencies, and exception handling protocols.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- module_hierarchy: list of dicts (module_name, files)\n"
            "- service_contracts: list of dicts (class_name, method_signatures)\n"
            "- dependency_injection_setup: list of strings\n"
            "- exception_handling_rules: list of strings"
        )
