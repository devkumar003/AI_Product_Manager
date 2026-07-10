from pydantic import BaseModel, Field

from app.ai.agents.base import BaseAgent
from app.ai.schemas import AgentResponse


class FrontendArchitectInput(BaseModel):
    screen_list: str = Field(..., description="Screen catalog list or UX guidelines")


class FrontendArchitect(BaseAgent[FrontendArchitectInput, AgentResponse]):
    @property
    def name(self) -> str:
        return "frontend_architect"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return (
            "Responsible for designing Next.js folder layouts, setting up Zustand state stores, "
            "mapping component hierarchies, and outlining custom React hooks."
        )

    def get_system_instructions(self) -> str:
        return (
            "You are the Frontend Architect Agent. Define Next.js App Router structures, component patterns, and state bindings.\n"
            "Under the 'result' key of the AgentResponse, output:\n"
            "- nextjs_directory_tree: string\n"
            "- key_components: list of dicts (name, page_route, type)\n"
            "- state_stores: list of dicts (name, actions, state_variables)\n"
            "- custom_hooks: list of dicts (name, signature, purpose)\n"
            "- theme_tailwind_tokens: dict of (fonts, colors, spacing)"
        )
