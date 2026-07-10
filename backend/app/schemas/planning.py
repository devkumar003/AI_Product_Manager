from typing import Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GoalBase(BaseModel):
    name: str = Field(..., description="Name of the goal")
    description: Optional[str] = Field(None, description="Detailed description")
    type: str = Field(..., description="Business, Product, Technical, Sprint, Release")
    status: Optional[str] = Field("Open", description="Open, In Progress, Achieved, Abandoned")
    progress: Optional[float] = Field(0.0, description="Progress percentage from 0.0 to 100.0")
    target_date: Optional[datetime] = Field(None, description="Target date for goal completion")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    target_date: Optional[datetime] = None


class GoalResponse(GoalBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Planned"
    objectives: list[dict[str, Any]] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    deliverables: list[dict[str, Any]] = Field(default_factory=list)
    execution_plan: dict[str, Any] = Field(default_factory=dict)


class MissionCreate(MissionBase):
    pass


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    objectives: Optional[list[dict[str, Any]]] = None
    milestones: Optional[list[dict[str, Any]]] = None
    deliverables: Optional[list[dict[str, Any]]] = None
    execution_plan: Optional[dict[str, Any]] = None


class MissionResponse(MissionBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PlanningItemBase(BaseModel):
    type: str  # Epic, Feature, UserStory, Task, Subtask
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Todo"
    priority: Optional[str] = "Medium"
    estimated_hours: Optional[float] = 0.0
    assigned_roles: list[str] = Field(default_factory=list)
    metadata_fields: dict[str, Any] = Field(default_factory=dict)


class PlanningItemCreate(PlanningItemBase):
    project_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None


class PlanningItemUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[float] = None
    assigned_roles: Optional[list[str]] = None
    metadata_fields: Optional[dict[str, Any]] = None
    parent_id: Optional[UUID] = None


class PlanningItemResponse(PlanningItemBase):
    id: UUID
    workspace_id: UUID
    project_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    priority: Optional[int] = 0
    scheduled_at: Optional[datetime] = None
    max_retries: Optional[int] = 3


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
    run_at: Optional[datetime] = None
    error_log: Optional[str] = None
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
    epic_id: Optional[UUID] = None
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
