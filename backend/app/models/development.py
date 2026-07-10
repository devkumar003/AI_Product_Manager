import uuid
from sqlalchemy import Column, String, Uuid, ForeignKey, Float, DateTime, Integer, JSON, Boolean, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class CodePlan(BaseEntity):
    __tablename__ = "code_plans"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(JSON, default=dict, nullable=False)  # target modules, APIs, schemas
    steps = Column(JSON, default=list, nullable=False)  # execution steps list
    status = Column(String(50), default="Planned", nullable=False)  # Planned, Implementing, Completed, Blocked

    workspace = relationship("Workspace")


class GeneratedCodeFile(BaseEntity):
    __tablename__ = "generated_code_files"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False)  # Backend, Frontend, API, Database, UnitTestCase, IntegrationTestCase, Documentation, PRD, RequirementAnalysis, Architecture
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)  # Python, TypeScript, SQL, Markdown, HTML, CSS
    is_merged = Column(Boolean, default=False, nullable=False)

    workspace = relationship("Workspace")
    project = relationship("Project")


class CodeReview(BaseEntity):
    __tablename__ = "code_reviews"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path = Column(String(512), nullable=False)
    status = Column(String(50), default="Pending", nullable=False)  # Pending, Approved, Requested Changes
    reviewer = Column(String(255), default="AI Agent", nullable=False)
    comments = Column(JSON, default=list, nullable=False)  # Detailed list of review findings
    score = Column(Float, default=100.0, nullable=False)  # Code rating out of 100

    workspace = relationship("Workspace")


class CodeQualityScan(BaseEntity):
    __tablename__ = "code_quality_scans"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    complexity_score = Column(Float, default=0.0, nullable=False)
    duplication_rate = Column(Float, default=0.0, nullable=False)
    test_coverage_est = Column(Float, default=0.0, nullable=False)
    security_vulnerabilities = Column(JSON, default=list, nullable=False)
    style_violations = Column(JSON, default=list, nullable=False)

    workspace = relationship("Workspace")


class RefactoringProposal(BaseEntity):
    __tablename__ = "refactoring_proposals"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path = Column(String(512), nullable=False)
    original_code = Column(Text, nullable=False)
    refactored_code = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    status = Column(String(50), default="Proposed", nullable=False)  # Proposed, Accepted, Rejected

    workspace = relationship("Workspace")


class BugReport(BaseEntity):
    __tablename__ = "bug_reports"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), default="Medium", nullable=False)  # High, Medium, Low
    detected_at = Column(DateTime, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    status = Column(String(50), default="Open", nullable=False)  # Open, Fixing, Fixed, Ignored

    workspace = relationship("Workspace")


class GitBranch(BaseEntity):
    __tablename__ = "git_branches"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_name = Column(String(255), nullable=False)
    source_branch = Column(String(255), default="main", nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Merged, Stale

    workspace = relationship("Workspace")


class GitCommit(BaseEntity):
    __tablename__ = "git_commits"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id = Column(
        Uuid,
        ForeignKey("git_branches.id", ondelete="CASCADE"),
        nullable=False,
    )
    commit_hash = Column(String(40), nullable=False)
    commit_message = Column(String(512), nullable=False)
    author = Column(String(255), default="AI Developer Agent", nullable=False)
    files_changed = Column(JSON, default=list, nullable=False)

    workspace = relationship("Workspace")
    branch = relationship("GitBranch")


class GitPullRequest(BaseEntity):
    __tablename__ = "git_pull_requests"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_branch = Column(String(255), nullable=False)
    target_branch = Column(String(255), default="main", nullable=False)
    status = Column(String(50), default="Open", nullable=False)  # Open, Merged, Closed
    merge_recommendation = Column(String(50), default="Ready", nullable=False)  # Ready, Conflicts, ReviewRequired

    workspace = relationship("Workspace")


class ReleasePlan(BaseEntity):
    __tablename__ = "release_plans"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(String(50), nullable=False)  # e.g., v1.0.0
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    milestones = Column(JSON, default=list, nullable=False)
    scope = Column(JSON, default=list, nullable=False)  # List of planning items/feature IDs
    status = Column(String(50), default="Draft", nullable=False)  # Draft, Scheduled, Released

    workspace = relationship("Workspace")


class DeploymentPlan(BaseEntity):
    __tablename__ = "deployment_plans"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    release_id = Column(
        Uuid,
        ForeignKey("release_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    environment = Column(String(50), default="Production", nullable=False)  # Production, Staging, Dev
    provider = Column(String(50), default="AWS ECS", nullable=False)  # AWS, GCP, Vercel, Docker Swarm
    manifests = Column(JSON, default=dict, nullable=False)  # Kubernetes / Docker compose templates
    steps = Column(JSON, default=list, nullable=False)  # execution script steps
    status = Column(String(50), default="Ready", nullable=False)  # Ready, Deploying, Succeeded, Failed

    workspace = relationship("Workspace")
    release = relationship("ReleasePlan")


class SprintUpdate(BaseEntity):
    __tablename__ = "sprint_updates"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    sprint_name = Column(String(255), nullable=False)
    burn_down_data = Column(JSON, default=dict, nullable=False)
    progress_summary = Column(Text, nullable=True)
    impediments = Column(JSON, default=list, nullable=False)

    workspace = relationship("Workspace")


class DeveloperTaskAssignment(BaseEntity):
    __tablename__ = "developer_task_assignments"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    developer_name = Column(String(255), nullable=False)
    planning_item_id = Column(
        Uuid,
        ForeignKey("planning_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_role = Column(String(100), nullable=False)  # Lead Backend, QA, UI Designer
    allocated_hours = Column(Float, default=0.0, nullable=False)

    workspace = relationship("Workspace")
    planning_item = relationship("PlanningItem")
