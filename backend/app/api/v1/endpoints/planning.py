from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
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
    PlanningItemUpdate,
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
import logging

logger = logging.getLogger("app.api.planning")

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
    goal = goal_manager.update_goal(db, goal_id, goal_in, workspace_id)
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
    success = goal_manager.delete_goal(db, goal_id, workspace_id)
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
    vision: str = Field(..., min_length=1, max_length=10000)


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


@router.put("/backlog/items/{item_id}", response_model=PlanningItemResponse)
def update_backlog_item(
    workspace_id: UUID,
    item_id: UUID,
    item_in: PlanningItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    from app.models.planning import PlanningItem
    
    item = db.query(PlanningItem).filter(
        PlanningItem.id == item_id,
        PlanningItem.workspace_id == workspace_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Planning item not found")
        
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
        
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/backlog/items/{item_id}/acceptance-criteria")
async def generate_acceptance_criteria(
    workspace_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    from app.models.planning import PlanningItem
    from app.services.ai.llm_manager import LLMManager
    
    item = db.query(PlanningItem).filter(PlanningItem.id == item_id, PlanningItem.workspace_id == workspace_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Planning item not found")
        
    llm = LLMManager()
    prompt = (
        "You are an expert Agile Product Manager.\n"
        f"Generate precise 'Given-When-Then' Acceptance Criteria for this user story:\n"
        f"Title: {item.title}\n"
        f"Description: {item.description}\n"
        "Provide 2-3 standard Given-When-Then scenarios. Return plain text formatted nicely."
    )
    criteria_text = await llm.generate(
        messages=[{"role": "user", "content": prompt}],
        model="gemini-1.5-pro",
        provider="gemini",
    )
    
    if not item.metadata_fields:
        item.metadata_fields = {}
    
    meta = dict(item.metadata_fields)
    meta["acceptance_criteria"] = criteria_text
    item.metadata_fields = meta
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {"acceptance_criteria": criteria_text}


@router.post("/backlog/items/{item_id}/wireframe")
async def generate_wireframe(
    workspace_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    _verify_workspace_membership(db, current_user.id, workspace_id)
    from app.models.planning import PlanningItem
    from app.services.ai.llm_manager import LLMManager
    
    item = db.query(PlanningItem).filter(PlanningItem.id == item_id, PlanningItem.workspace_id == workspace_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Planning item not found")
        
    llm = LLMManager()
    prompt = (
        "You are a Senior UX/UI Architect.\n"
        f"Generate UX Wireframe Suggestions / layout recommendation for this user story / feature:\n"
        f"Title: {item.title}\n"
        f"Description: {item.description}\n"
        "Provide structural UI recommendations (e.g. Header, Sidebar, Canvas, Settings drawer layout structure). Return plain text formatted nicely."
    )
    wireframe_text = await llm.generate(
        messages=[{"role": "user", "content": prompt}],
        model="gemini-1.5-pro",
        provider="gemini",
    )
    
    if not item.metadata_fields:
        item.metadata_fields = {}
        
    meta = dict(item.metadata_fields)
    meta["wireframe_suggestions"] = wireframe_text
    item.metadata_fields = meta
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {"wireframe_suggestions": wireframe_text}


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


# ══════════════════════════════════════════════════
# 11. Standalone Intelligence Suite Endpoints
# ══════════════════════════════════════════════════

class MarketResearchResponse(BaseModel):
    industry: str
    pestle: str
    swot: str

class CompetitorMatrixResponse(BaseModel):
    competitors: list[str]
    matrix_markdown: str

class CostEstimateResponse(BaseModel):
    total_developers: int
    total_qa: int
    total_designers: int
    monthly_infra_cost: float
    monthly_ai_cost: float
    total_monthly_burn: float
    forecast_3yr_markdown: str

class RiskMatrixItem(BaseModel):
    category: str
    severity: str
    description: str
    mitigation: str

class RiskAnalysisResponse(BaseModel):
    overall_status: str
    risks: list[RiskMatrixItem]


from fastapi import Query
from app.models.insight import WorkspaceInsight

@router.post("/intelligence/market-research", response_model=MarketResearchResponse)
async def generate_market_research(
    workspace_id: UUID,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _verify_workspace_membership(db, current_user.id, workspace_id)
    
    if not refresh:
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "market_research",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        if existing:
            return MarketResearchResponse(**existing.payload)

    from app.models.workspace import Workspace
    from app.services.executive.ceo import ceo_service
    
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    idea = ws.description if ws and ws.description else f"A product named {ws.name}"
    
    pestle_res = ceo_service.run_pestle_analysis(idea)
    swot_res = ceo_service.run_swot_analysis(idea)
    
    payload = {
        "industry": "Technology & SaaS",
        "pestle": pestle_res.get("pestle_markdown", "PESTLE details"),
        "swot": swot_res.get("swot_markdown", "SWOT details")
    }

    # Persist or update cache
    existing = db.query(WorkspaceInsight).filter(
        WorkspaceInsight.workspace_id == workspace_id,
        WorkspaceInsight.category == "market_research",
        WorkspaceInsight.deleted_at.is_(None)
    ).first()
    if existing:
        existing.payload = payload
        db.add(existing)
    else:
        new_insight = WorkspaceInsight(
            workspace_id=workspace_id,
            category="market_research",
            payload=payload
        )
        db.add(new_insight)
    db.commit()
    
    return MarketResearchResponse(**payload)


@router.post("/intelligence/competitor-analysis", response_model=CompetitorMatrixResponse)
async def generate_competitor_analysis(
    workspace_id: UUID,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _verify_workspace_membership(db, current_user.id, workspace_id)
    
    if not refresh:
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "competitor_analysis",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        if existing:
            return CompetitorMatrixResponse(**existing.payload)

    from app.models.workspace import Workspace
    from app.services.executive.ceo import ceo_service
    
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    idea = ws.description if ws and ws.description else f"A product named {ws.name}"
    
    competitor_list = ["Competitor A", "Competitor B", "Competitor C"]
    comp_res = ceo_service.run_competitor_intelligence(idea, competitor_list)
    
    payload = {
        "competitors": comp_res.get("competitor_names", competitor_list),
        "matrix_markdown": comp_res.get("competitor_matrix_markdown", "Competitor matrix details.")
    }

    # Persist or update cache
    existing = db.query(WorkspaceInsight).filter(
        WorkspaceInsight.workspace_id == workspace_id,
        WorkspaceInsight.category == "competitor_analysis",
        WorkspaceInsight.deleted_at.is_(None)
    ).first()
    if existing:
        existing.payload = payload
        db.add(existing)
    else:
        new_insight = WorkspaceInsight(
            workspace_id=workspace_id,
            category="competitor_analysis",
            payload=payload
        )
        db.add(new_insight)
    db.commit()
    
    return CompetitorMatrixResponse(**payload)


@router.post("/intelligence/cost-estimation", response_model=CostEstimateResponse)
async def generate_cost_estimation(
    workspace_id: UUID,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _verify_workspace_membership(db, current_user.id, workspace_id)
    
    if not refresh:
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "cost_estimation",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        if existing:
            return CostEstimateResponse(**existing.payload)

    from app.models.planning import PlanningItem
    from app.services.planning.resource_planner import ResourcePlanner
    from app.services.executive.ceo import ceo_service
    
    epics = db.query(PlanningItem).filter(
        PlanningItem.workspace_id == workspace_id,
        PlanningItem.type == "Epic",
        PlanningItem.deleted_at.is_(None)
    ).all()
    
    planner = ResourcePlanner()
    
    total_dev = 0
    total_qa = 0
    total_des = 0
    monthly_infra = 0.0
    monthly_ai = 0.0
    
    for epic in epics:
        try:
            req = planner.get_epic_resource_plan(db, epic.id)
            if not req:
                req = await planner.plan_resources_for_epic(db, workspace_id, epic.id)
            
            total_dev += req.developer_count
            total_qa += req.qa_count
            total_des += req.designer_count
            monthly_infra += req.infra_cost_est
            monthly_ai += req.ai_cost_est
        except Exception:
            pass
            
    if total_dev == 0:
        total_dev = 4
        total_qa = 1
        total_des = 1
        monthly_infra = 250.0
        monthly_ai = 150.0
        
    dev_salary = total_dev * 8000.0
    qa_salary = total_qa * 6000.0
    des_salary = total_des * 6000.0
    headcount_cost = dev_salary + qa_salary + des_salary
    total_burn = headcount_cost + monthly_infra + monthly_ai
    
    from app.models.workspace import Workspace
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    idea = ws.description if ws and ws.description else f"A product named {ws.name}"
    forecast_res = ceo_service.run_revenue_forecast(idea, total_burn * 12)
    
    payload = {
        "total_developers": total_dev,
        "total_qa": total_qa,
        "total_designers": total_des,
        "monthly_infra_cost": monthly_infra,
        "monthly_ai_cost": monthly_ai,
        "total_monthly_burn": total_burn,
        "forecast_3yr_markdown": forecast_res.get("forecast_markdown", "Three-year forecast details.")
    }

    # Persist or update cache
    existing = db.query(WorkspaceInsight).filter(
        WorkspaceInsight.workspace_id == workspace_id,
        WorkspaceInsight.category == "cost_estimation",
        WorkspaceInsight.deleted_at.is_(None)
    ).first()
    if existing:
        existing.payload = payload
        db.add(existing)
    else:
        new_insight = WorkspaceInsight(
            workspace_id=workspace_id,
            category="cost_estimation",
            payload=payload
        )
        db.add(new_insight)
    db.commit()
    
    return CostEstimateResponse(**payload)


@router.post("/intelligence/risk-analysis", response_model=RiskAnalysisResponse)
async def generate_risk_analysis(
    workspace_id: UUID,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _verify_workspace_membership(db, current_user.id, workspace_id)
    
    if not refresh:
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "risk_analysis",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        if existing:
            return RiskAnalysisResponse(**existing.payload)

    from app.models.workspace import Workspace
    from app.services.ai.llm_manager import LLMManager
    import json
    
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    idea = ws.description if ws and ws.description else f"A product named {ws.name}"
    
    llm = LLMManager()
    prompt = (
        "You are an expert Chief Risk Officer and Operations Advisor.\n"
        f"Perform a comprehensive risk analysis for this business/product idea: '{idea}'.\n"
        "Identify 4 major risks across: 'Strategic', 'Technical', 'Timeline', and 'Financial' categories.\n"
        "Define the Severity (High, Medium, Low), detailed Description, and clear Mitigation steps for each risk.\n"
        "Respond in JSON format only with a list under 'risks' key, each risk having: "
        "'category', 'severity', 'description', and 'mitigation'."
    )
    
    try:
        res = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            model="gemini-1.5-pro",
            provider="gemini"
        )
        content = res.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        data = json.loads(content)
        risks = data.get("risks", [])
    except Exception as e:
        logger.warning(f"Failed to generate risks with LLM, using fallbacks: {e}")
        risks = [
            {"category": "Strategic", "severity": "Medium", "description": "Market adoption could be slower than anticipated due to competition.", "mitigation": "Launch early beta programs to secure user feedback."},
            {"category": "Technical", "severity": "High", "description": "Complex multi-agent orchestration latency could affect user experience.", "mitigation": "Implement smart caching and provider priority routing."},
            {"category": "Timeline", "severity": "Medium", "description": "Aggressive roadmap deadlines might cause quality regression.", "mitigation": "Adopt automated unit/integration testing gates."},
            {"category": "Financial", "severity": "Low", "description": "LLM API usage costs could scale faster than premium subscription revenues.", "mitigation": "Implement token usage tracking and quota limits per workspace."}
        ]
        
    risk_objects = [RiskMatrixItem(**r) for r in risks]
    
    high_count = sum(1 for r in risks if r.get("severity") == "High")
    status_str = "Critical Risk" if high_count >= 2 else "Elevated Risk" if high_count == 1 else "Normal Operations"
    
    payload = {
        "overall_status": status_str,
        "risks": [r.model_dump() for r in risk_objects]
    }

    # Persist or update cache
    existing = db.query(WorkspaceInsight).filter(
        WorkspaceInsight.workspace_id == workspace_id,
        WorkspaceInsight.category == "risk_analysis",
        WorkspaceInsight.deleted_at.is_(None)
    ).first()
    if existing:
        existing.payload = payload
        db.add(existing)
    else:
        new_insight = WorkspaceInsight(
            workspace_id=workspace_id,
            category="risk_analysis",
            payload=payload
        )
        db.add(new_insight)
    db.commit()
    
    return RiskAnalysisResponse(
        overall_status=status_str,
        risks=risk_objects
    )
