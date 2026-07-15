from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Goal(BaseEntity):
    __tablename__ = "goals"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(2048), nullable=True)
    type = Column(
        String(50), nullable=False
    )  # Business, Product, Technical, Sprint, Release
    status = Column(
        String(50), default="Open", nullable=False
    )  # Open, In Progress, Achieved, Abandoned
    progress = Column(Float, default=0.0, nullable=False)
    target_date = Column(DateTime, nullable=True)

    # Relationships
    workspace = relationship("Workspace")


class Mission(BaseEntity):
    __tablename__ = "missions"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    description = Column(String(2048), nullable=True)
    status = Column(
        String(50), default="Planned", nullable=False
    )  # Planned, Executing, Completed, Cancelled
    objectives = Column(
        JSON, default=list, nullable=False
    )  # List of target goals / objectives
    milestones = Column(
        JSON, default=list, nullable=False
    )  # Milestones list with dates
    deliverables = Column(JSON, default=list, nullable=False)  # Deliverables list
    execution_plan = Column(
        JSON, default=dict, nullable=False
    )  # Step by step execution steps

    workspace = relationship("Workspace")


class PlanningItem(BaseEntity):
    __tablename__ = "planning_items"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id = Column(
        Uuid,
        ForeignKey("planning_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    type = Column(String(50), nullable=False)  # Epic, Feature, UserStory, Task, Subtask
    title = Column(String(255), nullable=False)
    description = Column(String(4096), nullable=True)
    status = Column(
        String(50), default="Todo", nullable=False
    )  # Todo, In Progress, Blocked, Done
    priority = Column(
        String(50), default="Medium", nullable=False
    )  # Critical, High, Medium, Low
    estimated_hours = Column(Float, default=0.0, nullable=False)
    assigned_roles = Column(
        JSON, default=list, nullable=False
    )  # e.g., ["Frontend", "Backend"]
    metadata_fields = Column(
        JSON, default=dict, nullable=False
    )  # e.g., acceptance criteria

    # Self-referential relationship
    parent = relationship(
        "PlanningItem", remote_side="PlanningItem.id", backref="children"
    )
    workspace = relationship("Workspace")
    project = relationship("Project")


class PlanningDependency(BaseEntity):
    __tablename__ = "planning_dependencies"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_item_id = Column(
        Uuid,
        ForeignKey("planning_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_item_id = Column(
        Uuid,
        ForeignKey("planning_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dependency_type = Column(
        String(50), default="Blocker", nullable=False
    )  # Blocker, API, Database, Infrastructure, Task

    workspace = relationship("Workspace")
    source_item = relationship("PlanningItem", foreign_keys=[source_item_id])
    target_item = relationship("PlanningItem", foreign_keys=[target_item_id])


class ExecutionQueueItem(BaseEntity):
    __tablename__ = "execution_queue"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_name = Column(String(255), nullable=False)
    payload = Column(JSON, default=dict, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher is higher priority
    status = Column(
        String(50), default="Pending", nullable=False
    )  # Pending, Running, Succeeded, Failed, Delayed
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    run_at = Column(DateTime, nullable=True)
    error_log = Column(String(4096), nullable=True)

    workspace = relationship("Workspace")


class ScenarioSimulation(BaseEntity):
    __tablename__ = "scenario_simulations"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    vision = Column(String(4096), nullable=False)
    best_case_timeline = Column(JSON, default=dict, nullable=False)
    worst_case_timeline = Column(JSON, default=dict, nullable=False)
    average_case_timeline = Column(JSON, default=dict, nullable=False)
    budget_impact = Column(JSON, default=dict, nullable=False)
    timeline_impact = Column(JSON, default=dict, nullable=False)

    workspace = relationship("Workspace")


class ResourceRequirement(BaseEntity):
    __tablename__ = "resource_requirements"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    epic_id = Column(
        Uuid,
        ForeignKey("planning_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    developer_count = Column(Integer, default=0, nullable=False)
    qa_count = Column(Integer, default=0, nullable=False)
    designer_count = Column(Integer, default=0, nullable=False)
    infra_cost_est = Column(Float, default=0.0, nullable=False)
    ai_cost_est = Column(Float, default=0.0, nullable=False)
    duration_weeks = Column(Integer, default=0, nullable=False)

    workspace = relationship("Workspace")
    epic = relationship("PlanningItem")


class PlanningAnalytics(BaseEntity):
    __tablename__ = "planning_analytics"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    accuracy_rate = Column(Float, default=0.0, nullable=False)
    completion_rate = Column(Float, default=0.0, nullable=False)
    execution_efficiency = Column(Float, default=0.0, nullable=False)
    total_delays_hours = Column(Float, default=0.0, nullable=False)
    measured_at = Column(DateTime, nullable=False)

    workspace = relationship("Workspace")
