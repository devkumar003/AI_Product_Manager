from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class TaskAgentInput(BaseModel):
    sprint_backlog: str = Field(..., description="Selected backlog items from Sprint Agent")


class TaskAgent(BaseAgent[TaskAgentInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "task_generator"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Deconstructs high-level feature requirements into Epics, User Stories, sub-tasks, "
            "developer assignments, estimates, and checklists."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Task Generator Agent. Breakdown backlogs into stories, developer subtasks, and check lists.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- epic: string\n"
            "- stories: list of dicts (id, title, user_role, capability, acceptance_criteria)\n"
            "- developer_tasks: list of dicts (id, story_id, title, estimate_hours, checklist, role_assigned)"
        )
