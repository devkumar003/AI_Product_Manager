"""
Acceptance Criteria Engine — Generates Given-When-Then acceptance criteria
for user stories, features, and epics.
"""

from pydantic import BaseModel, Field


class AcceptanceCriteriaInput(BaseModel):
    user_story: str = Field(..., description="The user story or feature description")
    additional_context: str = Field(
        default="", description="Optional context like personas, constraints, or domain"
    )


class AcceptanceCriterionItem(BaseModel):
    scenario: str = Field(..., description="Scenario name/title")
    given: str = Field(..., description="Given precondition")
    when: str = Field(..., description="When action/trigger")
    then: str = Field(..., description="Then expected outcome")


class AcceptanceCriteriaOutput(BaseModel):
    user_story_summary: str = Field(..., description="Restated user story summary")
    criteria: list[AcceptanceCriterionItem] = Field(
        default_factory=list, description="List of GWT acceptance criteria"
    )
    edge_cases: list[str] = Field(
        default_factory=list, description="Edge cases and negative scenarios"
    )
    definition_of_done: list[str] = Field(
        default_factory=list, description="Definition of done checklist"
    )


ACCEPTANCE_CRITERIA_PROMPT = (
    "You are the Acceptance Criteria Engine of AI ProductOS.\n"
    "Generate precise, testable Given-When-Then (GWT) acceptance criteria for the provided user story.\n"
    "Include:\n"
    "- 3-5 standard GWT scenarios covering the happy path\n"
    "- 2-3 edge cases and negative scenarios\n"
    "- A clear Definition of Done checklist\n"
    "Return JSON matching the AcceptanceCriteriaOutput schema."
)
