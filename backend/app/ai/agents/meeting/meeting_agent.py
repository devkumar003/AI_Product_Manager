from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class MeetingAgentInput(BaseModel):
    meeting_transcript: str = Field(..., description="Raw text transcript of the project meeting")


class MeetingAgent(BaseAgent[MeetingAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "meeting"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Architecture blueprint for parses, summary extractions, action-item tracking, "
            "and decisions tracking from raw team audio transcripts."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Meeting Agent. Process transcripts and map requirements, assignments, and decision logs.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- meeting_summary: string\n"
            "- action_items: list of dicts (task, owner, timeline_estimate)\n"
            "- requirements_highlighted: list of strings\n"
            "- decision_tracker: list of dicts (decision, context, status)"
        )
