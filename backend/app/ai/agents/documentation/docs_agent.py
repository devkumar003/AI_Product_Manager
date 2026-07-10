from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class DocumentationAgentInput(BaseModel):
    architecture_overview: str = Field(..., description="Details of project directories and APIs")


class DocumentationAgent(BaseAgent[DocumentationAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "documentation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for building project README blocks, formatting developer setups, "
            "authoring OpenAPI files, and drafting release notes."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Documentation Agent. Author README markdown pages, API schemas, change lists, and release summaries.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- readme_content: string\n"
            "- developer_setup_guide: string\n"
            "- api_documentation: string\n"
            "- architecture_documentation: string\n"
            "- release_notes: string"
        )
