from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class DevOpsAgentInput(BaseModel):
    tech_stack: str = Field(..., description="Stack details from tech architect")


class DevOpsAgent(BaseAgent[DevOpsAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "devops"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for formulating containerization blueprints, creating CI/CD workflows, "
            "and outlining metrics monitoring, backup, and high-availability plans."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the DevOps Agent. Define dockerfiles, deployment actions, scaling limits, and backup guidelines.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- docker_strategy: dict of (base_image, multi_stage_builds, volumes)\n"
            "- cicd_pipeline_steps: list of strings\n"
            "- monitoring_framework: string (e.g. Prometheus, Grafana)\n"
            "- backup_and_recovery_plan: string\n"
            "- high_availability_setup: string"
        )
