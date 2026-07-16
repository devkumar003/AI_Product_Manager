import asyncio
import logging
import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.ai.core.llm_manager import LLMManager
from app.ai.telemetry.metrics import TelemetryRegistry
from app.ai.orchestrator.base_agent import track_agent_tokens
from app.ai.orchestrator.agents import (
    DiscoveryAgent,
    RequirementsAgent,
    PlanningAgent,
    RoadmapAgent,
    EngineeringAgent,
    ReportAgent,
)
from app.models.orchestrator import AIWorkflowExecution, AIWorkflowStep
from app.models.project import Project

logger = logging.getLogger("app.ai.orchestrator.service")

STAGES = ["discovery", "requirements", "planning", "roadmap", "engineering", "reports"]

AGENT_MAP = {
    "discovery": DiscoveryAgent,
    "requirements": RequirementsAgent,
    "planning": PlanningAgent,
    "roadmap": RoadmapAgent,
    "engineering": EngineeringAgent,
    "reports": ReportAgent,
}

STAGE_PROGRESS = {
    "discovery": 0.15,
    "requirements": 0.35,
    "planning": 0.55,
    "roadmap": 0.70,
    "engineering": 0.85,
    "reports": 1.0,
}


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.active_connections.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.active_connections:
            self.active_connections.remove(q)

    async def broadcast(self, message: Dict[str, Any]):
        for q in self.active_connections:
            await q.put(message)


pubsub_manager = ConnectionManager()


class AIOrchestrationService:
    def __init__(self) -> None:
        self.llm_manager = LLMManager()
        self.telemetry = TelemetryRegistry()
        self._running_tasks: Dict[uuid.UUID, asyncio.Task] = {}
        self.max_retries = 3
        self.stage_timeout = 300.0  # 5 minutes timeout per stage
        self.max_token_limit = 500000

    def start_workflow_task(self, execution_id: uuid.UUID):
        """Starts the workflow execution as an asynchronous task."""
        if execution_id in self._running_tasks:
            logger.info(f"Workflow task {execution_id} is already running.")
            return
        
        task = asyncio.create_task(self._execute_workflow(execution_id))
        self._running_tasks[execution_id] = task
        task.add_done_callback(lambda t: self._running_tasks.pop(execution_id, None))

    async def trigger_workflow(
        self,
        db: Session,
        project_id: uuid.UUID,
        workspace_id: uuid.UUID,
        name: str,
        description: str,
    ) -> AIWorkflowExecution:
        """Triggers a new Master AI Orchestrator workflow."""
        # Check if there is an active execution running
        existing = db.query(AIWorkflowExecution).filter(
            AIWorkflowExecution.project_id == project_id,
            AIWorkflowExecution.status.in_(["pending", "processing"]),
            AIWorkflowExecution.deleted_at.is_(None)
        ).first()

        if existing:
            raise ValueError("An active AI workflow is already running for this project.")

        execution = AIWorkflowExecution(
            id=uuid.uuid4(),
            project_id=project_id,
            workspace_id=workspace_id,
            current_stage="discovery",
            status="pending",
            progress=0.0,
            context_json={
                "name": name,
                "description": description,
                "workspace_id": str(workspace_id),
                "project_id": str(project_id),
            },
            retry_count=0,
            require_human_review=False
        )
        db.add(execution)

        # Update Project state
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.generation_status = "pending"
            project.generation_progress = 0.0
            project.workflow_id = execution.id

        db.commit()
        db.refresh(execution)

        # Transition status to processing and start background task
        execution.status = "processing"
        execution.started_at = datetime.utcnow()
        db.commit()

        self.start_workflow_task(execution.id)
        return execution

    async def cancel_workflow(self, db: Session, execution_id: uuid.UUID) -> None:
        """Cancels a running workflow execution."""
        execution = db.query(AIWorkflowExecution).filter(
            AIWorkflowExecution.id == execution_id,
            AIWorkflowExecution.deleted_at.is_(None)
        ).first()

        if not execution:
            raise ValueError("Workflow execution not found.")

        execution.status = "cancelled"
        execution.completed_at = datetime.utcnow()

        project = db.query(Project).filter(Project.id == execution.project_id).first()
        if project:
            project.generation_status = "cancelled"

        # Cancel any active running asyncio task
        if execution_id in self._running_tasks:
            self._running_tasks[execution_id].cancel()

        db.commit()
        
        await pubsub_manager.broadcast({
            "workflow_id": str(execution_id),
            "project_id": str(execution.project_id),
            "status": "cancelled",
            "progress": execution.progress,
            "current_stage": execution.current_stage
        })

    async def retry_workflow_stage(self, db: Session, execution_id: uuid.UUID) -> AIWorkflowExecution:
        """Retries a failed workflow execution starting from the last failed stage."""
        execution = db.query(AIWorkflowExecution).filter(
            AIWorkflowExecution.id == execution_id,
            AIWorkflowExecution.deleted_at.is_(None)
        ).first()

        if not execution:
            raise ValueError("Workflow execution not found.")

        if execution.status not in ["failed", "cancelled"]:
            raise ValueError("Only failed or cancelled workflows can be retried.")

        execution.status = "processing"
        execution.failure_reason = None
        execution.started_at = datetime.utcnow()

        project = db.query(Project).filter(Project.id == execution.project_id).first()
        if project:
            project.generation_status = "processing"

        db.commit()

        self.start_workflow_task(execution.id)
        return execution

    async def recover_interrupted_workflows(self) -> None:
        """Recovers and resumes all workflows that were interrupted by a server shutdown/restart."""
        db = SessionLocal()
        try:
            interrupted = db.query(AIWorkflowExecution).filter(
                AIWorkflowExecution.status == "processing",
                AIWorkflowExecution.deleted_at.is_(None)
            ).all()

            for execution in interrupted:
                logger.info(f"Recovering and resuming interrupted workflow execution: {execution.id}")
                self.start_workflow_task(execution.id)
        except Exception as e:
            logger.exception(f"Failed to recover interrupted workflows: {e}")
        finally:
            db.close()

    async def _execute_workflow(self, execution_id: uuid.UUID) -> None:
        """Internal runner that executes the sequential steps of a workflow."""
        db = SessionLocal()
        try:
            execution = db.query(AIWorkflowExecution).filter(AIWorkflowExecution.id == execution_id).first()
            if not execution or execution.status != "processing":
                return

            context = dict(execution.context_json)
            completed_stages = []
            
            # Determine resume checkpoint
            if execution.checkpoint_reached:
                if execution.checkpoint_reached in STAGES:
                    idx = STAGES.index(execution.checkpoint_reached)
                    completed_stages = STAGES[:idx + 1]

            logger.info(f"Starting workflow execution {execution_id}. Completed stages: {completed_stages}")

            for stage in STAGES:
                # 1. Check cancellation before each stage
                db.refresh(execution)
                if execution.status == "cancelled":
                    logger.info(f"Workflow {execution_id} was cancelled. Aborting stage {stage}.")
                    return

                if stage in completed_stages:
                    logger.info(f"Skipping completed stage: {stage}")
                    continue

                # 2. Update current stage and progress
                execution.current_stage = stage
                execution.progress = STAGE_PROGRESS[stage]
                
                project = db.query(Project).filter(Project.id == execution.project_id).first()
                if project:
                    project.generation_status = "processing"
                    project.generation_progress = STAGE_PROGRESS[stage]

                db.commit()

                # Broadcast progress update
                await pubsub_manager.broadcast({
                    "workflow_id": str(execution_id),
                    "project_id": str(execution.project_id),
                    "status": "processing",
                    "progress": execution.progress,
                    "current_stage": stage
                })

                # 3. Initialize or retrieve the workflow step record
                step = db.query(AIWorkflowStep).filter(
                    AIWorkflowStep.workflow_id == execution_id,
                    AIWorkflowStep.agent_name == stage
                ).first()

                if not step:
                    step = AIWorkflowStep(
                        id=uuid.uuid4(),
                        workflow_id=execution_id,
                        agent_name=stage,
                        status="running",
                        input_context=context,
                        output_data={},
                        retry_count=0,
                        started_at=datetime.utcnow()
                    )
                    db.add(step)
                else:
                    step.status = "running"
                    step.started_at = datetime.utcnow()
                    step.failure_reason = None
                db.commit()

                # 4. Check limits: maximum retries
                if step.retry_count >= self.max_retries:
                    raise ValueError(f"Stage '{stage}' exceeded maximum retries limit.")

                # 5. Instantiate and execute the Agent with timeout protection
                agent_cls = AGENT_MAP[stage]
                agent = agent_cls(self.llm_manager, self.telemetry)

                try:
                    async with track_agent_tokens(self.llm_manager) as usage_records:
                        # Timeout protection wrapper
                        output = await asyncio.wait_for(
                            agent.execute(context, db),
                            timeout=self.stage_timeout
                        )
                        agent.validate(output)
                        save_result = await agent.save_output(output, context, db)

                        # Update step record on success
                        step.status = "completed"
                        step.output_data = save_result
                        step.completed_at = datetime.utcnow()

                        # Apply token tracking metrics
                        if usage_records:
                            step.model_used = usage_records[0]["model"]
                            step.input_tokens = sum(r["prompt_tokens"] for r in usage_records)
                            step.output_tokens = sum(r["completion_tokens"] for r in usage_records)
                            step.total_tokens = sum(r["total_tokens"] for r in usage_records)
                            step.execution_time = sum(r["execution_time"] for r in usage_records)
                            step.estimated_cost = sum(r["estimated_cost"] for r in usage_records)

                            # Validate maximum token limit
                            total_workflow_tokens = db.query(
                                sa_func_sum(AIWorkflowStep.total_tokens)
                            ).filter(AIWorkflowStep.workflow_id == execution_id).scalar() or 0
                            
                            if total_workflow_tokens > self.max_token_limit:
                                raise ValueError("Workflow exceeded maximum token usage limit.")

                        db.commit()

                        # Update global execution context and checkpoint
                        context = {**context, **save_result}
                        execution.context_json = context
                        execution.checkpoint_reached = stage
                        db.commit()

                except Exception as stage_err:
                    logger.exception(f"Error executing stage {stage} in workflow {execution_id}")
                    step.status = "failed"
                    step.retry_count += 1
                    step.failure_reason = str(stage_err)
                    step.completed_at = datetime.utcnow()
                    
                    execution.status = "failed"
                    execution.failure_reason = f"Stage '{stage}' failed: {str(stage_err)}"
                    
                    if project:
                        project.generation_status = "failed"
                        
                    db.commit()

                    # Broadcast failed state
                    await pubsub_manager.broadcast({
                        "workflow_id": str(execution_id),
                        "project_id": str(execution.project_id),
                        "status": "failed",
                        "progress": execution.progress,
                        "current_stage": stage,
                        "failure_reason": execution.failure_reason
                    })
                    return

            # 6. Mark workflow as fully completed
            execution.status = "completed"
            execution.progress = 1.0
            execution.completed_at = datetime.utcnow()

            if project:
                project.generation_status = "completed"
                project.generation_progress = 1.0

            db.commit()

            # Broadcast completion update
            await pubsub_manager.broadcast({
                "workflow_id": str(execution_id),
                "project_id": str(execution.project_id),
                "status": "completed",
                "progress": 1.0,
                "current_stage": "reports"
            })

        except Exception as e:
            logger.exception(f"Unhandled error in workflow loop execution: {e}")
        finally:
            db.close()


# SQLAlchemy sum helper
def sa_func_sum(col):
    from sqlalchemy import func
    return func.sum(col)


orchestration_service = AIOrchestrationService()
