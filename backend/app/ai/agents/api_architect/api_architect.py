from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class APIArchitectInput(BaseModel):
    entities_definition: str = Field(..., description="DB entity lists or architecture summaries")


class APIArchitect(BaseAgent[APIArchitectInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "api_architect"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for cataloging system endpoints, defining request/response models, "
            "versioning structures, and handling errors."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the API Architect Agent. Map REST/WebSocket API endpoints, authentication models, and pagination rules.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- endpoints: list of dicts (path, method, summary, request_body_schema, response_schema)\n"
            "- auth_strategy: string\n"
            "- error_format: dict representing generic API error responses\n"
            "- pagination_defaults: dict of (limit, offset_param, cursor_param)"
        )
