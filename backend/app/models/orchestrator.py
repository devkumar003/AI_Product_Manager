from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class AIWorkflowExecution(BaseEntity):
    __tablename__ = "ai_workflow_executions"

    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_stage = Column(String(100), nullable=True)
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed, awaiting_review, cancelled
    progress = Column(Float, default=0.0, nullable=False)
    context_json = Column(JSON, default=dict, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    failure_reason = Column(String(4096), nullable=True)
    require_human_review = Column(Boolean, default=False, nullable=False)
    checkpoint_reached = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
    steps = relationship(
        "AIWorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="AIWorkflowStep.started_at.asc()",
    )


class AIWorkflowStep(BaseEntity):
    __tablename__ = "ai_workflow_steps"

    workflow_id = Column(
        Uuid,
        ForeignKey("ai_workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_name = Column(String(100), nullable=False, index=True)
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, running, completed, failed, cancelled
    input_context = Column(JSON, default=dict, nullable=False)
    output_data = Column(JSON, default=dict, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    failure_reason = Column(String(4096), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # AI tracking metrics
    model_used = Column(String(100), nullable=True)
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    execution_time = Column(Float, default=0.0, nullable=False)
    estimated_cost = Column(Float, default=0.0, nullable=False)

    # Relationships
    workflow = relationship("AIWorkflowExecution", back_populates="steps")
