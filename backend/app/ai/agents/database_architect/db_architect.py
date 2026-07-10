from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class DBArchitectInput(BaseModel):
    tech_stack: str = Field(..., description="Stack details, primarily DB type")
    requirements: str = Field(
        ..., description="Details on features requiring data persistency"
    )


class DBArchitect(BaseAgent[DBArchitectInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "database_architect"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for formulating relational/non-relational schemas, listing database entities, "
            "mapping relationship keys, configuring indexes, and planning migrations."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Database Architect Agent. Create schema designs and normalization setups.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- entities: list of dicts (name, attributes, primary_key)\n"
            "- relationships: list of dicts (from_entity, to_entity, cardinality)\n"
            "- indexes: list of dicts (table, fields, type)\n"
            "- migration_strategy: string\n"
            "- query_optimization_tips: list of strings"
        )
