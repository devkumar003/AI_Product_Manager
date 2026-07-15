"""
Wireframe Suggestions Engine — Generates structured UI/UX layout blueprints
for features, screens, and user flows.
"""

from typing import Any

from pydantic import BaseModel, Field


class WireframeInput(BaseModel):
    feature_description: str = Field(
        ..., description="The feature or screen to design"
    )
    target_platform: str = Field(
        default="web", description="Target platform: web, mobile, desktop"
    )
    design_system: str = Field(
        default="modern dark", description="Design system style preference"
    )


class ScreenLayout(BaseModel):
    screen_name: str = Field(..., description="Screen/page name")
    purpose: str = Field(..., description="Purpose of this screen")
    layout_structure: str = Field(
        ..., description="Layout structure description (e.g., sidebar + main content)"
    )
    components: list[str] = Field(
        default_factory=list, description="UI components on this screen"
    )
    interactions: list[str] = Field(
        default_factory=list, description="Key user interactions"
    )
    responsive_notes: str = Field(
        default="", description="Responsive design considerations"
    )


class WireframeOutput(BaseModel):
    feature_summary: str = Field(..., description="Summary of the feature being designed")
    screens: list[ScreenLayout] = Field(
        default_factory=list, description="Screen-by-screen wireframe layouts"
    )
    navigation_flow: list[str] = Field(
        default_factory=list, description="User navigation flow steps"
    )
    design_recommendations: list[str] = Field(
        default_factory=list, description="Design best practices and recommendations"
    )
    accessibility_notes: list[str] = Field(
        default_factory=list, description="Accessibility (a11y) considerations"
    )


WIREFRAME_PROMPT = (
    "You are the UX Wireframe Engine of AI ProductOS.\n"
    "Generate detailed, structured wireframe suggestions for the provided feature.\n"
    "For each screen provide:\n"
    "- Screen name and purpose\n"
    "- Layout structure (header, sidebar, main content, modals, etc.)\n"
    "- Key UI components (buttons, forms, cards, tables, etc.)\n"
    "- User interactions and responsive design notes\n"
    "Also provide navigation flow, design recommendations, and accessibility notes.\n"
    "Return JSON matching the WireframeOutput schema."
)
