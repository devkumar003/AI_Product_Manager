from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class TechArchitectInput(BaseModel):
    requirements_summary: str = Field(..., description="Business Analyst requirements details")
    platform_type: str = Field(default="SaaS Web Application", description="Type of system architecture")


class TechArchitect(BaseAgent[TechArchitectInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "technical_architect"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for proposing technology stack recommendations, defining backend/frontend architectures, "
            "and outlining caching, deployment, and scalability strategies."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Technical Architect Agent. Detail project blueprints, stacks, security guidelines, and directory layouts.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- architecture_recommendation: string (e.g. monolithic, microservices)\n"
            "- technology_stack: dict of (frontend, backend, database, cache, broker)\n"
            "- deployment_design: string\n"
            "- caching_strategy: string\n"
            "- scalability_parameters: list of strings\n"
            "- security_recommendations: list of strings\n"
            "- folder_blueprint: string"
        )
