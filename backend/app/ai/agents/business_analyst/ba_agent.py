from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class BAAgentInput(BaseModel):
    product_plan: str = Field(..., description="Product plan output from PM Agent")


class BAAgent(BaseAgent[BAAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "business_analyst"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for formulating detailed business, functional, and non-functional requirements "
            "as well as business rules, constraints, and acceptance criteria."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Business Analyst Agent. Detail user requirements and business rules.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- problem_statement: string\n"
            "- business_requirements: list of strings\n"
            "- functional_requirements: list of dicts (id, description, source_feature)\n"
            "- non_functional_requirements: list of dicts (category, requirement, metric)\n"
            "- business_rules: list of strings\n"
            "- assumptions_and_constraints: list of strings\n"
            "- acceptance_criteria: list of dicts (requirement_id, rule)"
        )
