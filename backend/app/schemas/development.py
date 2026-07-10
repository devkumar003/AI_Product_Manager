from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


# -------------------------------------------------------------
# Code Plan Schemas
# -------------------------------------------------------------
class CodePlanBase(BaseModel):
    title: str
    description: str | None = None
    scope: dict[str, Any] = {}
    steps: list[str] = []
    status: str = "Planned"


class CodePlanCreate(CodePlanBase):
    pass


class CodePlanResponse(CodePlanBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Generated Code File Schemas
# -------------------------------------------------------------
class GeneratedCodeFileBase(BaseModel):
    file_path: str
    file_type: str  # Backend, Frontend, API, Database, UnitTestCase, IntegrationTestCase, Documentation, PRD, RequirementAnalysis, Architecture
    content: str
    language: str
    is_merged: bool = False


class GeneratedCodeFileCreate(GeneratedCodeFileBase):
    project_id: UUID | None = None


class GeneratedCodeFileResponse(GeneratedCodeFileBase):
    id: UUID
    workspace_id: UUID
    project_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Code Review Schemas
# -------------------------------------------------------------
class CodeReviewBase(BaseModel):
    file_path: str
    status: str = "Pending"
    reviewer: str = "AI Agent"
    comments: list[dict[str, Any]] = []
    score: float = 100.0


class CodeReviewCreate(CodeReviewBase):
    pass


class CodeReviewResponse(CodeReviewBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Code Quality Schemas
# -------------------------------------------------------------
class CodeQualityScanBase(BaseModel):
    complexity_score: float = 0.0
    duplication_rate: float = 0.0
    test_coverage_est: float = 0.0
    security_vulnerabilities: list[dict[str, Any]] = []
    style_violations: list[dict[str, Any]] = []


class CodeQualityScanResponse(CodeQualityScanBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Refactoring Schemas
# -------------------------------------------------------------
class RefactoringProposalBase(BaseModel):
    file_path: str
    original_code: str
    refactored_code: str
    rationale: str
    status: str = "Proposed"


class RefactoringProposalCreate(RefactoringProposalBase):
    pass


class RefactoringProposalResponse(RefactoringProposalBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Bug Detection & Fix Schemas
# -------------------------------------------------------------
class BugReportBase(BaseModel):
    title: str
    description: str | None = None
    severity: str = "Medium"
    suggested_fix: str | None = None
    status: str = "Open"


class BugReportCreate(BugReportBase):
    detected_at: datetime


class BugReportResponse(BugReportBase):
    id: UUID
    workspace_id: UUID
    detected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Git Workflow Schemas
# -------------------------------------------------------------
class GitBranchBase(BaseModel):
    branch_name: str
    source_branch: str = "main"
    status: str = "Active"


class GitBranchCreate(GitBranchBase):
    pass


class GitBranchResponse(GitBranchBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GitCommitBase(BaseModel):
    commit_hash: str | None = None
    commit_message: str
    author: str = "AI Developer Agent"
    files_changed: list[str] = []


class GitCommitCreate(GitCommitBase):
    branch_id: UUID


class GitCommitResponse(GitCommitBase):
    id: UUID
    workspace_id: UUID
    branch_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GitPullRequestBase(BaseModel):
    title: str
    description: str | None = None
    source_branch: str
    target_branch: str = "main"
    status: str = "Open"
    merge_recommendation: str = "Ready"


class GitPullRequestCreate(GitPullRequestBase):
    pass


class GitPullRequestResponse(GitPullRequestBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Management & Sprints Schemas
# -------------------------------------------------------------
class ReleasePlanBase(BaseModel):
    version: str
    name: str
    description: str | None = None
    milestones: list[dict[str, Any]] = []
    scope: list[UUID] = []
    status: str = "Draft"


class ReleasePlanCreate(ReleasePlanBase):
    pass


class ReleasePlanResponse(ReleasePlanBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DeploymentPlanBase(BaseModel):
    environment: str = "Production"
    provider: str = "AWS ECS"
    manifests: dict[str, Any] = {}
    steps: list[str] = []
    status: str = "Ready"


class DeploymentPlanCreate(DeploymentPlanBase):
    release_id: UUID


class DeploymentPlanResponse(DeploymentPlanBase):
    id: UUID
    workspace_id: UUID
    release_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SprintUpdateBase(BaseModel):
    sprint_name: str
    burn_down_data: dict[str, Any] = {}
    progress_summary: str | None = None
    impediments: list[str] = []


class SprintUpdateCreate(SprintUpdateBase):
    pass


class SprintUpdateResponse(SprintUpdateBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DeveloperTaskAssignmentBase(BaseModel):
    developer_name: str
    planning_item_id: UUID
    assigned_role: str
    allocated_hours: float = 0.0


class DeveloperTaskAssignmentCreate(DeveloperTaskAssignmentBase):
    pass


class DeveloperTaskAssignmentResponse(DeveloperTaskAssignmentBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Combined UI & Sandbox Pipeline Requests
# -------------------------------------------------------------
class PipelineExecutionRequest(BaseModel):
    project_id: UUID | None = None
    target_name: str  # e.g., "AI ProductOS Backend"
    prompt: str  # Custom instruction or requirements context
    options: dict[str, Any] = {}


class PipelineExecutionResponse(BaseModel):
    success: bool
    message: str
    outputs: dict[str, Any] = {}


class DevelopmentAnalyticsResponse(BaseModel):
    total_lines_generated: int
    quality_score_avg: float
    coverage_rate_avg: float
    bug_fix_ratio: float
    commits_count: int
    pull_requests_count: int
    active_branches: list[str]
