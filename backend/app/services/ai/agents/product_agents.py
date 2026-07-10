from typing import Type
from pydantic import BaseModel, Field
from app.services.ai.llm_manager import LLMManager
from app.services.ai.agents.base import BaseAgent, AgentConfig
from app.services.ai.memory.base import BaseMemory


# -------------------------------------------------------------
# 1. Product Manager Agent (Refines Raw Idea)
# -------------------------------------------------------------
class IdeaInput(BaseModel):
    idea: str = Field(..., description="Raw product idea from the user")
    target_industry: str = Field("General Tech", description="Target industry vertical")


class RefinedIdeaOutput(BaseModel):
    refined_title: str = Field(..., description="A professional, catchy product name/title")
    refined_description: str = Field(..., description="Detailed, high-clarity summary of the refined idea")
    target_audience: list[str] = Field(..., description="List of primary user segments/personas")
    key_objectives: list[str] = Field(..., description="Key objectives and metrics this product solves")
    feature_milestones: list[str] = Field(..., description="Initial high-level milestones or roadmap items")


class ProductManagerAgent(BaseAgent[IdeaInput, RefinedIdeaOutput]):
    def __init__(
        self,
        llm_manager: LLMManager,
        config: AgentConfig | None = None,
        memory: BaseMemory | None = None,
    ) -> None:
        system_prompt = (
            "You are a Staff Product Manager at an elite software company. "
            "Your goal is to refine raw product ideas into well-structured, professional, "
            "and commercially viable software products. "
            "You must return your output strictly in JSON format matching the specified schema."
        )
        prompt_template = (
            "Refine the following raw product idea:\n"
            "Idea: {idea}\n"
            "Target Industry: {target_industry}\n\n"
            "Provide a professional product title, refined description, target audience segments, "
            "key product objectives, and high-level feature milestones."
        )
        super().__init__(
            system_prompt=system_prompt,
            prompt_template=prompt_template,
            input_schema=IdeaInput,
            output_schema=RefinedIdeaOutput,
            llm_manager=llm_manager,
            config=config,
            memory=memory,
        )


# -------------------------------------------------------------
# 2. PRD Generator Agent (Creates Complete Specs)
# -------------------------------------------------------------
class PRDInput(BaseModel):
    refined_title: str = Field(..., description="Refined product title")
    refined_description: str = Field(..., description="Refined product description")
    target_audience: list[str] = Field(..., description="Target audience segments")
    key_objectives: list[str] = Field(..., description="Key objectives")


class PRDOutput(BaseModel):
    prd_title: str = Field(..., description="Title of the PRD document")
    user_persona: str = Field(..., description="In-depth user persona narrative")
    user_stories: list[str] = Field(..., description="Agile user stories (As a... I want... So that...)")
    functional_requirements: list[str] = Field(..., description="Detailed feature functional requirements")
    technical_constraints: list[str] = Field(..., description="System limits, platform choices, or constraints")


class PRDGeneratorAgent(BaseAgent[PRDInput, PRDOutput]):
    def __init__(
        self,
        llm_manager: LLMManager,
        config: AgentConfig | None = None,
        memory: BaseMemory | None = None,
    ) -> None:
        system_prompt = (
            "You are a Principal Product Owner. Your job is to generate a comprehensive, "
            "production-grade Product Requirement Document (PRD) from a refined product idea. "
            "Write highly specific functional requirements and realistic user stories. "
            "Return the result strictly in JSON matching the specified schema."
        )
        prompt_template = (
            "Write a PRD for the following product:\n"
            "Product Name: {refined_title}\n"
            "Description: {refined_description}\n"
            "Target Audience: {target_audience}\n"
            "Objectives: {key_objectives}\n\n"
            "Formulate detailed user personas, user stories, clear functional requirements, "
            "and technical constraints."
        )
        super().__init__(
            system_prompt=system_prompt,
            prompt_template=prompt_template,
            input_schema=PRDInput,
            output_schema=PRDOutput,
            llm_manager=llm_manager,
            config=config,
            memory=memory,
        )


# -------------------------------------------------------------
# 3. Technical Architect Agent (Creates Design Docs)
# -------------------------------------------------------------
class ArchitectInput(BaseModel):
    prd_title: str = Field(..., description="PRD Title")
    functional_requirements: list[str] = Field(..., description="Functional requirements list")
    technical_constraints: list[str] = Field(..., description="Technical constraints")


class ArchitectureOutput(BaseModel):
    system_description: str = Field(..., description="Overall architecture pattern and system description")
    database_schema_ddl: list[str] = Field(..., description="Mock database schema tables/columns design DDL")
    api_endpoints: list[str] = Field(..., description="REST/GraphQL API endpoints specification")
    deployment_strategy: str = Field(..., description="Docker/Kubernetes orchestration and deployment details")


class TechnicalArchitectAgent(BaseAgent[ArchitectInput, ArchitectureOutput]):
    def __init__(
        self,
        llm_manager: LLMManager,
        config: AgentConfig | None = None,
        memory: BaseMemory | None = None,
    ) -> None:
        system_prompt = (
            "You are a Staff Technical Architect. Your job is to translate product specifications "
            "and functional requirements into a detailed, scalable, clean-architecture software design document. "
            "Output your design document strictly in JSON matching the specified schema."
        )
        prompt_template = (
            "Design the system architecture for the following product:\n"
            "Product Title: {prd_title}\n"
            "Functional Requirements: {functional_requirements}\n"
            "Technical Constraints: {technical_constraints}\n\n"
            "Provide the system description, database schema DDL design, API endpoint definitions, "
            "and deployment strategy."
        )
        super().__init__(
            system_prompt=system_prompt,
            prompt_template=prompt_template,
            input_schema=ArchitectInput,
            output_schema=ArchitectureOutput,
            llm_manager=llm_manager,
            config=config,
            memory=memory,
        )
