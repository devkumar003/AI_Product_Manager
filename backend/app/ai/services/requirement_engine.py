"""
Task 4 — Requirement Generator
Task 5 — User Story Generator
Task 6 — PRD Generator
"""

from typing import Any
from pydantic import BaseModel, Field


# ── Task 4: Requirement Generator ──

class RequirementInput(BaseModel):
    product_discovery: str = Field(..., description="Product discovery output")
    idea: str = Field(default="", description="Original idea for context")


class RequirementOutput(BaseModel):
    business_requirements: list[dict[str, Any]] = Field(default_factory=list)
    functional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    non_functional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    system_requirements: list[str] = Field(default_factory=list)
    security_requirements: list[str] = Field(default_factory=list)
    performance_requirements: list[dict[str, Any]] = Field(default_factory=list)
    accessibility_requirements: list[str] = Field(default_factory=list)
    compliance_requirements: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


REQUIREMENT_PROMPT = (
    "You are the Requirement Generator of AI ProductOS.\n"
    "Generate exhaustive requirements across all categories: business, functional,\n"
    "non-functional, system, security, performance, accessibility, compliance.\n"
    "Each functional requirement should be a dict with id, title, description, priority, acceptance_criteria.\n"
    "Each non-functional requirement should include category, requirement, metric, target.\n"
    "Return JSON matching RequirementOutput schema."
)


# ── Task 5: User Story Generator ──

class UserStoryInput(BaseModel):
    requirements: str = Field(..., description="Requirements output for story decomposition")


class UserStory(BaseModel):
    epic: str
    feature: str
    story_id: str
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str]
    edge_cases: list[str]
    definition_of_done: list[str]
    priority: str
    points: int


class UserStoryOutput(BaseModel):
    epics: list[dict[str, Any]] = Field(default_factory=list)
    features: list[dict[str, Any]] = Field(default_factory=list)
    stories: list[UserStory] = Field(default_factory=list)


USER_STORY_PROMPT = (
    "You are the User Story Generator of AI ProductOS.\n"
    "Decompose requirements into Agile user stories following the standard format:\n"
    "As a [role], I want [capability], so that [benefit].\n"
    "Group stories under Epics and Features.\n"
    "Include acceptance criteria, edge cases, and definition of done for each story.\n"
    "Return JSON matching UserStoryOutput schema."
)


# ── Task 6: PRD Generator ──

class PRDInput(BaseModel):
    idea: str = Field(..., description="Product idea")
    discovery: str = Field(default="", description="Product discovery data")
    requirements: str = Field(default="", description="Requirements data")
    stories: str = Field(default="", description="User stories data")


class PRDOutput(BaseModel):
    executive_summary: str = Field(...)
    objectives: list[str] = Field(default_factory=list)
    background: str = Field(...)
    problem_statement: str = Field(...)
    business_goals: list[str] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)
    personas: list[dict[str, Any]] = Field(default_factory=list)
    functional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    non_functional_requirements: list[dict[str, Any]] = Field(default_factory=list)
    architecture_summary: str = Field(...)
    feature_list: list[dict[str, Any]] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    release_plan: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    appendix: str = Field(default="")


PRD_PROMPT = (
    "You are the PRD Generator of AI ProductOS.\n"
    "Generate a complete, export-ready Product Requirements Document.\n"
    "Include every section: executive summary, objectives, background, problem statement,\n"
    "business goals, target users, personas, functional/non-functional requirements,\n"
    "architecture summary, feature list, success metrics, KPIs, dependencies, release plan,\n"
    "risks, and appendix.\n"
    "Be exhaustive and professional. This should read like a real enterprise PRD.\n"
    "Return JSON matching PRDOutput schema."
)
