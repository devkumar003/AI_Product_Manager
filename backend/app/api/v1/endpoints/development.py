from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.api.v1.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.membership import Membership
from app.services.development import (
    development_engine,
    code_planner,
    quality_engine,
    git_workflow,
    dev_management,
    dev_workspace,
)
from app.schemas.development import (
    PipelineExecutionRequest,
    PipelineExecutionResponse,
    CodePlanResponse,
    GeneratedCodeFileResponse,
    CodeReviewResponse,
    CodeQualityScanResponse,
    RefactoringProposalResponse,
    RefactoringProposalCreate,
    BugReportResponse,
    GitBranchResponse,
    GitBranchCreate,
    GitCommitResponse,
    GitCommitCreate,
    GitPullRequestResponse,
    GitPullRequestCreate,
    ReleasePlanResponse,
    ReleasePlanCreate,
    DeploymentPlanResponse,
    DeploymentPlanCreate,
    SprintUpdateResponse,
    SprintUpdateCreate,
    DeveloperTaskAssignmentResponse,
    DeveloperTaskAssignmentCreate,
    DevelopmentAnalyticsResponse,
)

router = APIRouter()


def check_workspace_access(db: Session, user_id: UUID, workspace_id: UUID):
    """
    Unified inline access control checking workspace membership.
    """
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.workspace_id == workspace_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access permissions for this workspace."
        )


@router.post("/pipelines/execute", response_model=PipelineExecutionResponse)
def execute_pipeline(
    req: PipelineExecutionRequest,
    workspace_id: UUID = Query(...),
    pipeline_type: str = Query(...),  # prd, requirement, architecture, database, backend, frontend, api, unittest, integrationtest, documentation, plan
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    try:
        res = development_engine.execute_development_pipeline(
            db=db,
            workspace_id=workspace_id,
            project_id=req.project_id,
            target_name=req.target_name,
            prompt=req.prompt,
            pipeline_type=pipeline_type,
            options=req.options
        )
        return PipelineExecutionResponse(
            success=res["success"],
            message=res["message"],
            outputs=res
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution crashed: {str(e)}"
        )


@router.post("/plans", response_model=CodePlanResponse)
def create_code_plan(
    title: str = Query(...),
    description: str = Query(...),
    requirements: str = Query(...),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    plan = code_planner.create_plan(db, workspace_id, title, description, requirements)
    return plan


@router.get("/plans", response_model=list[CodePlanResponse])
def get_code_plans(
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return code_planner.get_plans(db, workspace_id)


@router.post("/quality/review", response_model=CodeReviewResponse)
def run_code_review(
    file_path: str = Query(...),
    code_content: str = Query(...),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return quality_engine.review_code(db, workspace_id, file_path, code_content)


@router.post("/quality/scan", response_model=CodeQualityScanResponse)
def run_quality_scan(
    file_path: str = Query(...),
    code_content: str = Query(...),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return quality_engine.scan_quality(db, workspace_id, file_path, code_content)


@router.post("/quality/refactor", response_model=RefactoringProposalResponse)
def propose_refactoring(
    req: RefactoringProposalCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return quality_engine.propose_refactor(
        db, workspace_id, req.file_path, req.original_code, req.rationale
    )


@router.post("/quality/bugs", response_model=BugReportResponse)
def run_bug_scanner(
    file_path: str = Query(...),
    code_content: str = Query(...),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return quality_engine.detect_bugs(db, workspace_id, file_path, code_content)


@router.post("/git/branch", response_model=GitBranchResponse)
def create_git_branch(
    req: GitBranchCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return git_workflow.create_branch(db, workspace_id, req.branch_name, req.source_branch)


@router.post("/git/commit", response_model=GitCommitResponse)
def create_git_commit(
    req: GitCommitCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return git_workflow.commit_changes(
        db, workspace_id, req.branch_id, req.commit_message, req.files_changed
    )


@router.post("/git/pr", response_model=GitPullRequestResponse)
def create_pull_request(
    req: GitPullRequestCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return git_workflow.generate_pull_request(
        db, workspace_id, req.title, req.description or "", req.source_branch, req.target_branch
    )


@router.post("/git/pr/{pr_id}/merge", response_model=GitPullRequestResponse)
def merge_pull_request(
    pr_id: UUID,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    pr = git_workflow.merge_pull_request(db, workspace_id, pr_id)
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pull Request not found."
        )
    return pr


@router.post("/releases", response_model=ReleasePlanResponse)
def create_release_plan(
    req: ReleasePlanCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return dev_management.create_release_plan(
        db, workspace_id, req.version, req.name, req.description or "", req.scope
    )


@router.post("/releases/deploy", response_model=DeploymentPlanResponse)
def deploy_release(
    req: DeploymentPlanCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return dev_management.create_deployment_plan(
        db, workspace_id, req.release_id, req.environment, req.provider
    )


@router.post("/sprints/update", response_model=SprintUpdateResponse)
def create_sprint_update(
    req: SprintUpdateCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return dev_management.create_sprint_update(db, workspace_id, req.sprint_name, req.progress_summary or "")


@router.post("/tasks/assign", response_model=DeveloperTaskAssignmentResponse)
def assign_developer_task(
    req: DeveloperTaskAssignmentCreate,
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return dev_management.assign_developer_task(
        db, workspace_id, req.developer_name, req.planning_item_id, req.assigned_role, req.allocated_hours
    )


@router.get("/analytics", response_model=DevelopmentAnalyticsResponse)
def get_development_analytics(
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    metrics = dev_workspace.get_development_analytics(db, workspace_id)
    return DevelopmentAnalyticsResponse(
        total_lines_generated=metrics["total_lines_generated"],
        quality_score_avg=metrics["quality_score_avg"],
        coverage_rate_avg=metrics["coverage_rate_avg"],
        bug_fix_ratio=metrics["bug_fix_ratio"],
        commits_count=metrics["commits_count"],
        pull_requests_count=metrics["pull_requests_count"],
        active_branches=metrics["active_branches"]
    )


@router.post("/workspace/action")
def run_workspace_sandbox_action(
    file_path: str = Query(...),
    action: str = Query(...),
    workspace_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_workspace_access(db, current_user.id, workspace_id)
    return dev_workspace.execute_workspace_actions(db, workspace_id, file_path, action, {})
