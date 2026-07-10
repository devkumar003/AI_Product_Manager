"""
Task 10 — Roadmap Generator
Task 11 — Sprint Generator
Task 12 — Task Breakdown Engine
Task 13 — Feature Prioritization Engine
"""

from typing import Any
from pydantic import BaseModel, Field


# ── Task 10: Roadmap Generator ──

class RoadmapInput(BaseModel):
    features: str = Field(..., description="Feature list with priorities")
    timeline_months: int = Field(default=12, description="Planning horizon")


class RoadmapOutput(BaseModel):
    vision_roadmap: str = Field(...)
    quarterly_roadmap: list[dict[str, Any]] = Field(default_factory=list)
    monthly_roadmap: list[dict[str, Any]] = Field(default_factory=list)
    release_roadmap: list[dict[str, Any]] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    feature_timeline: list[dict[str, Any]] = Field(default_factory=list)
    dependencies: list[dict[str, Any]] = Field(default_factory=list)


ROADMAP_PROMPT = (
    "You are the Roadmap Generator of AI ProductOS.\n"
    "Create a multi-layered roadmap: vision, quarterly, monthly, and release.\n"
    "Include milestones with target dates, feature timelines, and dependency chains.\n"
    "Return JSON matching RoadmapOutput schema."
)


# ── Task 11: Sprint Generator ──

class SprintInput(BaseModel):
    roadmap: str = Field(..., description="Roadmap data for sprint decomposition")
    team_size: int = Field(default=5)
    sprint_duration_weeks: int = Field(default=2)


class SprintOutput(BaseModel):
    sprint_goals: list[str] = Field(default_factory=list)
    sprint_planning: list[dict[str, Any]] = Field(default_factory=list)
    sprint_capacity: dict[str, Any] = Field(default_factory=dict)
    velocity_estimate: int = Field(default=30)
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    subtasks: list[dict[str, Any]] = Field(default_factory=list)
    assignments: list[dict[str, Any]] = Field(default_factory=list)


SPRINT_PROMPT = (
    "You are the Sprint Generator of AI ProductOS.\n"
    "Plan sprints from the roadmap: goals, capacity allocation, velocity,\n"
    "task decomposition, subtasks, and developer assignments.\n"
    "Return JSON matching SprintOutput schema."
)


# ── Task 12: Task Breakdown Engine ──

class TaskBreakdownInput(BaseModel):
    sprint_data: str = Field(..., description="Sprint planning data")


class TaskItem(BaseModel):
    id: str
    type: str  # epic, story, task, subtask
    parent_id: str = ""
    title: str
    description: str
    estimate_hours: float = 0
    priority: str = "medium"
    assignee: str = ""
    checklist: list[str] = Field(default_factory=list)


class TaskBreakdownOutput(BaseModel):
    epics: list[TaskItem] = Field(default_factory=list)
    stories: list[TaskItem] = Field(default_factory=list)
    tasks: list[TaskItem] = Field(default_factory=list)
    subtasks: list[TaskItem] = Field(default_factory=list)
    total_estimate_hours: float = 0


TASK_BREAKDOWN_PROMPT = (
    "You are the Task Breakdown Engine of AI ProductOS.\n"
    "Decompose sprint items into a full hierarchy: Epic → Story → Task → Subtask.\n"
    "Each item should have id, type, parent_id, title, description, estimate_hours,\n"
    "priority, assignee suggestion, and checklist items.\n"
    "Return JSON matching TaskBreakdownOutput schema."
)


# ── Task 13: Feature Prioritization Engine ──

class PrioritizationInput(BaseModel):
    features: str = Field(..., description="Feature list to prioritize")
    framework: str = Field(default="RICE", description="MoSCoW, RICE, ICE, WSJF, value_vs_effort")


class PrioritizedFeature(BaseModel):
    feature_name: str
    score: float
    tier: str
    rationale: str
    framework_breakdown: dict[str, Any] = Field(default_factory=dict)


class PrioritizationOutput(BaseModel):
    framework_used: str = Field(...)
    ranked_features: list[PrioritizedFeature] = Field(default_factory=list)
    priority_matrix: dict[str, list[str]] = Field(default_factory=dict)
    top_recommendations: list[str] = Field(default_factory=list)


PRIORITIZATION_PROMPT = (
    "You are the Feature Prioritization Engine of AI ProductOS.\n"
    "Apply the requested prioritization framework to rank features.\n"
    "Supported frameworks:\n"
    "- MoSCoW: Must / Should / Could / Won't\n"
    "- RICE: Reach × Impact × Confidence / Effort\n"
    "- ICE: Impact × Confidence × Ease\n"
    "- WSJF: Cost of Delay / Job Duration\n"
    "- Value vs Effort: value_score / effort_score\n"
    "Show the breakdown for each feature.\n"
    "Return JSON matching PrioritizationOutput schema."
)
