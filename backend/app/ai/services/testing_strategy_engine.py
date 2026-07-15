"""
Testing Strategy Engine — Generates comprehensive QA plans
covering unit, integration, E2E, performance, and security testing.
"""

from typing import Any

from pydantic import BaseModel, Field


class TestingStrategyInput(BaseModel):
    project_description: str = Field(
        ..., description="Description of the project or feature to test"
    )
    tech_stack: str = Field(
        default="", description="Technology stack details"
    )
    test_focus: str = Field(
        default="comprehensive",
        description="Focus area: comprehensive, unit, integration, e2e, performance, security",
    )


class TestSuiteItem(BaseModel):
    test_name: str = Field(..., description="Test case name")
    test_type: str = Field(
        ..., description="unit, integration, e2e, performance, security"
    )
    description: str = Field(..., description="What this test validates")
    priority: str = Field(default="medium", description="low, medium, high, critical")
    setup_requirements: str = Field(default="", description="Setup/fixtures needed")


class TestingStrategyOutput(BaseModel):
    strategy_summary: str = Field(
        ..., description="Overview of the testing strategy"
    )
    test_pyramid_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Recommended test count by layer (unit, integration, e2e)",
    )
    test_suites: list[TestSuiteItem] = Field(
        default_factory=list, description="Detailed test cases"
    )
    tools_recommended: list[str] = Field(
        default_factory=list,
        description="Recommended testing tools and frameworks",
    )
    coverage_targets: dict[str, str] = Field(
        default_factory=dict,
        description="Coverage targets by category (e.g., line: 80%, branch: 70%)",
    )
    ci_cd_integration: list[str] = Field(
        default_factory=list,
        description="CI/CD pipeline integration steps for tests",
    )
    non_functional_tests: list[str] = Field(
        default_factory=list,
        description="Non-functional test recommendations (load, stress, chaos)",
    )


TESTING_STRATEGY_PROMPT = (
    "You are the Testing Strategy Engine of AI ProductOS.\n"
    "Generate a comprehensive QA and testing plan for the described project.\n"
    "Include:\n"
    "- Test pyramid breakdown (unit, integration, E2E counts)\n"
    "- Detailed test suites with names, types, descriptions, and priorities\n"
    "- Recommended testing tools and frameworks\n"
    "- Coverage targets by category\n"
    "- CI/CD integration steps\n"
    "- Non-functional testing recommendations (load, stress, security, chaos)\n"
    "Return JSON matching the TestingStrategyOutput schema."
)
