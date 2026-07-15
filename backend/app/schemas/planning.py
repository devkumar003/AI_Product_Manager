from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=500, description="Name of the goal")
    description: str | None = Field(None, max_length=5000, description="Detailed description")
    type: str = Field(..., min_length=1, max_length=50, description="Business, Product, Technical, Sprint, Release")
    status: str | None = Field(
        "Open", max_length=50, description="Open, In Progress, Achieved, Abandoned"
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
    name: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)
    type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)
    progress: float | None = None
    target_date: datetime | None = None


class GoalResponse(GoalBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MissionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field("Planned", max_length=50)
    objectives: list[dict[str, Any]] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    deliverables: list[dict[str, Any]] = Field(default_factory=list)
    execution_plan: dict[str, Any] = Field(default_factory=dict)


class MissionCreate(MissionBase):
    pass


class MissionUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(None, max_length=50)
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
    type: str = Field(..., min_length=1, max_length=50)  # Epic, Feature, UserStory, Task, Subtask
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field("Todo", max_length=50)
    priority: str | None = Field("Medium", max_length=50)
    estimated_hours: float | None = 0.0
    assigned_roles: list[str] = Field(default_factory=list)
    metadata_fields: dict[str, Any] = Field(default_factory=dict)


class PlanningItemCreate(PlanningItemBase):
    project_id: UUID | None = None
    parent_id: UUID | None = None


class PlanningItemUpdate(BaseModel):
    type: str | None = Field(None, max_length=50)
    title: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(None, max_length=50)
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
    name: str = Field(..., min_length=1, max_length=500)
    vision: str = Field(..., min_length=1, max_length=10000)


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
