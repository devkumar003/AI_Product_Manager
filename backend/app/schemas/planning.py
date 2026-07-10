from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GoalBase(BaseModel):
    name: str = Field(..., description="Name of the goal")
    description: str | None = Field(None, description="Detailed description")
    type: str = Field(..., description="Business, Product, Technical, Sprint, Release")
    status: str | None = Field(
        "Open", description="Open, In Progress, Achieved, Abandoned"
    )
    progress: float | None = Field(
        0.0, description="Progress percentage from 0.0 to 100.0"
    )
    target_date: datetime | None = Field(
        None, description="Target date for goal completion"
    )


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    type: str | None = None
    status: str | None = None
    progress: float | None = None
    target_date: datetime | None = None


class GoalResponse(GoalBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MissionBase(BaseModel):
    title: str
    description: str | None = None
    status: str | None = "Planned"
    objectives: list[dict[str, Any]] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    deliverables: list[dict[str, Any]] = Field(default_factory=list)
    execution_plan: dict[str, Any] = Field(default_factory=dict)


class MissionCreate(MissionBase):
    pass


class MissionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    objectives: list[dict[str, Any]] | None = None
    milestones: list[dict[str, Any]] | None = None
    deliverables: list[dict[str, Any]] | None = None
    execution_plan: dict[str, Any] | None = None


class MissionResponse(MissionBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PlanningItemBase(BaseModel):
    type: str  # Epic, Feature, UserStory, Task, Subtask
    title: str
    description: str | None = None
    status: str | None = "Todo"
    priority: str | None = "Medium"
    estimated_hours: float | None = 0.0
    assigned_roles: list[str] = Field(default_factory=list)
    metadata_fields: dict[str, Any] = Field(default_factory=dict)


class PlanningItemCreate(PlanningItemBase):
    project_id: UUID | None = None
    parent_id: UUID | None = None


class PlanningItemUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    estimated_hours: float | None = None
    assigned_roles: list[str] | None = None
    metadata_fields: dict[str, Any] | None = None
    parent_id: UUID | None = None


class PlanningItemResponse(PlanningItemBase):
    id: UUID
    workspace_id: UUID
    project_id: UUID | None = None
    parent_id: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DependencyCreate(BaseModel):
    source_item_id: UUID
    target_item_id: UUID
    dependency_type: str = "Blocker"  # Blocker, API, Database, Infrastructure, Task


class DependencyResponse(DependencyCreate):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionQueueItemCreate(BaseModel):
    task_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int | None = 0
    scheduled_at: datetime | None = None
    max_retries: int | None = 3


class ExecutionQueueItemResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    task_name: str
    payload: dict[str, Any]
    priority: int
    status: str
    retry_count: int
    max_retries: int
    scheduled_at: datetime
    run_at: datetime | None = None
    error_log: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScenarioSimulationCreate(BaseModel):
    name: str
    vision: str


class ScenarioSimulationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    vision: str
    best_case_timeline: dict[str, Any]
    worst_case_timeline: dict[str, Any]
    average_case_timeline: dict[str, Any]
    budget_impact: dict[str, Any]
    timeline_impact: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResourceRequirementCreate(BaseModel):
    epic_id: UUID | None = None
    developer_count: int = 0
    qa_count: int = 0
    designer_count: int = 0
    infra_cost_est: float = 0.0
    ai_cost_est: float = 0.0
    duration_weeks: int = 0


class ResourceRequirementResponse(ResourceRequirementCreate):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanningAnalyticsResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    accuracy_rate: float
    completion_rate: float
    execution_efficiency: float
    total_delays_hours: float
    measured_at: datetime

    model_config = ConfigDict(from_attributes=True)
