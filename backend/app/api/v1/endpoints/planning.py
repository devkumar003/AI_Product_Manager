from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.membership import Membership
from app.models.user import User
from app.schemas.planning import (
    DependencyResponse,
    ExecutionQueueItemCreate,
    ExecutionQueueItemResponse,
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    MissionResponse,
    PlanningAnalyticsResponse,
    PlanningItemCreate,
    PlanningItemResponse,
    ResourceRequirementResponse,
    ScenarioSimulationCreate,
    ScenarioSimulationResponse,
)
from app.services.planning import (
    ai_scheduler,
    context_compressor,
    dependency_engine,
    execution_queue,
    goal_manager,
    mission_planner,
    planning_analytics,
    planning_engine,
    resource_planner,
    scenario_simulator,
    workspace_intelligence,
)

router = APIRouter()


def _verify_workspace_membership(
    db: Session, user_id: UUID, workspace_id: UUID
) -> None:
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == user_id,
            Membership.workspace_id == workspace_id,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access permission to this workspace",
        )


# ══════════════════════════════════════════════════
# 1. Goal Management System Endpoints
# ══════════════════════════════════════════════════


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    workspace_id: UUID,
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return goal_manager.create_goal(db, workspace_id, goal_in)


@router.get("/goals", response_model=list[GoalResponse])
def list_goals(
    workspace_id: UUID,
    goal_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return goal_manager.list_workspace_goals(db, workspace_id, goal_type)


@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
    workspace_id: UUID,
    goal_id: UUID,
    goal_in: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    goal = goal_manager.update_goal(db, goal_id, goal_in)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    workspace_id: UUID,
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _verify_workspace_membership(db, current_user.id, workspace_id)
    success = goal_manager.delete_goal(db, goal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    from fastapi import Response

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════
# 2. Mission Planner Endpoints
# ══════════════════════════════════════════════════


class MissionPlanGenerateRequest(BaseModel):
    title: str
    goal_ids: list[UUID]


@router.post(
    "/missions", response_model=MissionResponse, status_code=status.HTTP_201_CREATED
)
async def generate_mission_plan(
    workspace_id: UUID,
    req: MissionPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await mission_planner.generate_mission_plan(
            db, workspace_id, req.title, req.goal_ids
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate mission plan: {str(e)}"
        ) from e


@router.get("/missions", response_model=list[MissionResponse])
def list_missions(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return mission_planner.list_workspace_missions(db, workspace_id)


# ══════════════════════════════════════════════════
# 3. Planning Backlog Endpoints
# ══════════════════════════════════════════════════


class BacklogGenerateRequest(BaseModel):
    project_id: UUID | None = None
    vision: str


@router.post("/backlog/generate", response_model=list[PlanningItemResponse])
async def generate_backlog(
    workspace_id: UUID,
    req: BacklogGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await planning_engine.generate_backlog_from_vision(
            db, workspace_id, req.project_id, req.vision
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate backlog: {str(e)}"
        ) from e


@router.get("/backlog/items", response_model=list[PlanningItemResponse])
def list_backlog_items(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return planning_engine.list_workspace_items(db, workspace_id)


@router.post(
    "/backlog/items",
    response_model=PlanningItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_backlog_item(
    workspace_id: UUID,
    item_in: PlanningItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    from app.models.planning import PlanningItem

    item = PlanningItem(
        workspace_id=workspace_id,
        project_id=item_in.project_id,
        parent_id=item_in.parent_id,
        type=item_in.type,
        title=item_in.title,
        description=item_in.description,
        status=item_in.status or "Todo",
        priority=item_in.priority or "Medium",
        estimated_hours=item_in.estimated_hours or 0.0,
        assigned_roles=item_in.assigned_roles,
        metadata_fields=item_in.metadata_fields,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ══════════════════════════════════════════════════
# 4. Dependency Engine Endpoints
# ══════════════════════════════════════════════════


@router.post("/dependencies/detect", response_model=list[DependencyResponse])
async def detect_dependencies(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await dependency_engine.detect_and_save_dependencies(db, workspace_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to detect dependencies: {str(e)}"
        ) from e


@router.get("/dependencies", response_model=list[DependencyResponse])
def list_dependencies(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return dependency_engine.list_dependencies(db, workspace_id)


# ══════════════════════════════════════════════════
# 5. Execution Queue Endpoints
# ══════════════════════════════════════════════════


@router.post("/queue/enqueue", response_model=ExecutionQueueItemResponse)
def enqueue_task(
    workspace_id: UUID,
    task_in: ExecutionQueueItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return execution_queue.enqueue_task(db, workspace_id, task_in)


@router.get("/queue", response_model=list[ExecutionQueueItemResponse])
def list_queue(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return execution_queue.list_queue(db, workspace_id)


# ══════════════════════════════════════════════════
# 6. AI Scheduler Endpoints
# ══════════════════════════════════════════════════


class RunScheduleRequest(BaseModel):
    base_start_date: datetime | None = None


@router.post("/scheduler/schedule")
async def run_ai_scheduler(
    workspace_id: UUID,
    req: RunScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await ai_scheduler.schedule_tasks(db, workspace_id, req.base_start_date)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to schedule tasks: {str(e)}"
        ) from e


# ══════════════════════════════════════════════════
# 7. Scenario Simulation Endpoints
# ══════════════════════════════════════════════════


@router.post("/simulations", response_model=ScenarioSimulationResponse)
async def simulate_scenario(
    workspace_id: UUID,
    req: ScenarioSimulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await scenario_simulator.simulate_scenario(
            db, workspace_id, req.name, req.vision
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run simulation: {str(e)}"
        ) from e


@router.get("/simulations", response_model=list[ScenarioSimulationResponse])
def list_simulations(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return scenario_simulator.list_simulations(db, workspace_id)


# ══════════════════════════════════════════════════
# 8. Resource Planner Endpoints
# ══════════════════════════════════════════════════


@router.post("/resources/epic/{epic_id}", response_model=ResourceRequirementResponse)
async def plan_epic_resources(
    workspace_id: UUID,
    epic_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return await resource_planner.plan_resources_for_epic(db, workspace_id, epic_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to plan epic resources: {str(e)}"
        ) from e


@router.get("/resources", response_model=list[ResourceRequirementResponse])
def list_resource_plans(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return resource_planner.list_workspace_resource_plans(db, workspace_id)


# ══════════════════════════════════════════════════
# 9. Workspace Intelligence & Analytics Endpoints
# ══════════════════════════════════════════════════


@router.get("/intelligence/templates")
def list_templates(current_user: User = Depends(get_current_active_user)) -> Any:
    return workspace_intelligence.get_templates()


class ApplyTemplateRequest(BaseModel):
    project_id: UUID | None = None
    template_key: str


@router.post("/intelligence/templates/apply", response_model=list[PlanningItemResponse])
def apply_template(
    workspace_id: UUID,
    req: ApplyTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    try:
        return workspace_intelligence.apply_template_to_workspace(
            db, workspace_id, req.project_id, req.template_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/intelligence/roadmap")
def get_roadmap(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return workspace_intelligence.get_workspace_roadmap(db, workspace_id)


@router.get("/analytics/latest", response_model=PlanningAnalyticsResponse)
def get_latest_analytics(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    # Calculate fresh analytics first
    planning_analytics.calculate_workspace_analytics(db, workspace_id)
    latest = planning_analytics.get_latest_analytics(db, workspace_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return latest


@router.get("/analytics/history", response_model=list[PlanningAnalyticsResponse])
def get_analytics_history(
    workspace_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    return planning_analytics.get_history(db, workspace_id, limit)


# ══════════════════════════════════════════════════
# 10. Context Compression Endpoints
# ══════════════════════════════════════════════════


class CompressTextRequest(BaseModel):
    text: str
    target_summary_words: int | None = 300


class CompressMessagesRequest(BaseModel):
    messages: list[dict[str, str]]
    target_turns: int | None = 4


@router.post("/compress/text")
async def compress_text(
    req: CompressTextRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    try:
        compressed = await context_compressor.compress_text(
            req.text, req.target_summary_words
        )
        return {"compressed": compressed}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compress context: {str(e)}"
        ) from e


@router.post("/compress/messages")
async def compress_messages(
    req: CompressMessagesRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    try:
        compressed = await context_compressor.compress_messages(
            req.messages, req.target_turns
        )
        return {"compressed_messages": compressed}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compress messages: {str(e)}"
        ) from e
