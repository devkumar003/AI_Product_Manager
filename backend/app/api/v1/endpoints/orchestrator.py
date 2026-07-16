import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.orchestrator import AIWorkflowExecution, AIWorkflowStep
from app.ai.orchestrator.service import orchestration_service, pubsub_manager

router = APIRouter()
logger = logging.getLogger("app.api.v1.endpoints.orchestrator")


# ── Pydantic Schemas ──

class TriggerWorkflowRequest(BaseModel):
    project_id: UUID
    workspace_id: UUID
    name: str
    description: str


class WorkflowStepResponse(BaseModel):
    id: UUID
    agent_name: str
    status: str
    retry_count: int
    failure_reason: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_used: Optional[str] = None
    input_tokens: int
    output_tokens: int
    total_tokens: int
    execution_time: float
    estimated_cost: float

    class Config:
        from_attributes = True


class WorkflowExecutionResponse(BaseModel):
    id: UUID
    project_id: UUID
    workspace_id: UUID
    current_stage: Optional[str] = None
    status: str
    progress: float
    retry_count: int
    failure_reason: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    checkpoint_reached: Optional[str] = None
    steps: List[WorkflowStepResponse] = []

    class Config:
        from_attributes = True


# ── Endpoints ──

@router.post("/trigger", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
async def trigger_workflow(
    payload: TriggerWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Triggers the Master AI Orchestrator workflow for a project."""
    try:
        execution = await orchestration_service.trigger_workflow(
            db=db,
            project_id=payload.project_id,
            workspace_id=payload.workspace_id,
            name=payload.name,
            description=payload.description
        )
        return execution
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        logger.exception("Failed to trigger workflow")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger workflow: {str(e)}"
        )


@router.post("/cancel/{execution_id}", status_code=status.HTTP_200_OK)
async def cancel_workflow(
    execution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancels a running workflow execution."""
    try:
        await orchestration_service.cancel_workflow(db=db, execution_id=execution_id)
        return {"status": "success", "message": "Workflow cancellation requested."}
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        logger.exception("Failed to cancel workflow")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )


@router.post("/retry/{execution_id}", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def retry_workflow(
    execution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retries a failed or cancelled workflow execution from the last checkpoint."""
    try:
        execution = await orchestration_service.retry_workflow_stage(db=db, execution_id=execution_id)
        return execution
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        logger.exception("Failed to retry workflow")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry workflow: {str(e)}"
        )


@router.get("/status/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_status(
    execution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves the full status and metric summary of a workflow execution."""
    execution = db.query(AIWorkflowExecution).filter(
        AIWorkflowExecution.id == execution_id,
        AIWorkflowExecution.deleted_at.is_(None)
    ).first()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found."
        )

    return execution


@router.get("/stream/{project_id}")
async def stream_workflow_progress(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
):
    """Streams live workflow progress updates via Server-Sent Events (SSE)."""
    async def event_generator():
        q = pubsub_manager.subscribe()
        logger.info(f"Client subscribed to SSE updates for project {project_id}")
        try:
            while True:
                msg = await q.get()
                if msg.get("project_id") == str(project_id):
                    yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.CancelledError:
            logger.info(f"Client connection closed for project {project_id}")
        finally:
            pubsub_manager.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
