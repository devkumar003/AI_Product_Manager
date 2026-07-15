"""Add foreign key indexes

Revision ID: 93b22cf9bc42
Revises: f8f213eee413
Create Date: 2026-07-14 02:22:00.000000

"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93b22cf9bc42"
down_revision: str | Sequence[str] | None = "f8f213eee413"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: Add indexes on foreign key columns."""
    # 1. Workspaces
    op.create_index(op.f("ix_workspaces_organization_id"), "workspaces", ["organization_id"], unique=False)

    # 2. Projects
    op.create_index(op.f("ix_projects_workspace_id"), "projects", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_projects_owner_id"), "projects", ["owner_id"], unique=False)

    # 3. Goals
    op.create_index(op.f("ix_goals_workspace_id"), "goals", ["workspace_id"], unique=False)

    # 4. Missions
    op.create_index(op.f("ix_missions_workspace_id"), "missions", ["workspace_id"], unique=False)

    # 5. Planning Items
    op.create_index(op.f("ix_planning_items_workspace_id"), "planning_items", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_planning_items_project_id"), "planning_items", ["project_id"], unique=False)
    op.create_index(op.f("ix_planning_items_parent_id"), "planning_items", ["parent_id"], unique=False)

    # 6. Planning Dependencies
    op.create_index(op.f("ix_planning_dependencies_workspace_id"), "planning_dependencies", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_planning_dependencies_source_item_id"), "planning_dependencies", ["source_item_id"], unique=False)
    op.create_index(op.f("ix_planning_dependencies_target_item_id"), "planning_dependencies", ["target_item_id"], unique=False)

    # 7. Execution Queue
    op.create_index(op.f("ix_execution_queue_workspace_id"), "execution_queue", ["workspace_id"], unique=False)

    # 8. Scenario Simulations
    op.create_index(op.f("ix_scenario_simulations_workspace_id"), "scenario_simulations", ["workspace_id"], unique=False)

    # 9. Resource Requirements
    op.create_index(op.f("ix_resource_requirements_workspace_id"), "resource_requirements", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_resource_requirements_epic_id"), "resource_requirements", ["epic_id"], unique=False)

    # 10. Planning Analytics
    op.create_index(op.f("ix_planning_analytics_workspace_id"), "planning_analytics", ["workspace_id"], unique=False)

    # 11. Documents
    op.create_index(op.f("ix_documents_workspace_id"), "documents", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_documents_project_id"), "documents", ["project_id"], unique=False)

    # 12. Document Versions
    op.create_index(op.f("ix_document_versions_document_id"), "document_versions", ["document_id"], unique=False)

    # 13. Reports
    op.create_index(op.f("ix_ceo_reports_workspace_id"), "ceo_reports", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_cto_reports_workspace_id"), "cto_reports", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_coo_reports_workspace_id"), "coo_reports", ["workspace_id"], unique=False)

    # 14. Invitations
    op.create_index(op.f("ix_invitations_organization_id"), "invitations", ["organization_id"], unique=False)
    op.create_index(op.f("ix_invitations_workspace_id"), "invitations", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_invitations_invited_by"), "invitations", ["invited_by"], unique=False)

    # 15. Memberships
    op.create_index(op.f("ix_memberships_user_id"), "memberships", ["user_id"], unique=False)
    op.create_index(op.f("ix_memberships_workspace_id"), "memberships", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_memberships_invited_by"), "memberships", ["invited_by"], unique=False)

    # 16. Notifications
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    # 17. Organizations
    op.create_index(op.f("ix_organizations_owner_id"), "organizations", ["owner_id"], unique=False)

    # 18. Chat Messages
    op.create_index(op.f("ix_chat_messages_project_id"), "chat_messages", ["project_id"], unique=False)

    # 19. Activities
    op.create_index(op.f("ix_activities_workspace_id"), "activities", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_activities_user_id"), "activities", ["user_id"], unique=False)

    # 20. Token Usage
    op.create_index(op.f("ix_ai_token_usage_workspace_id"), "ai_token_usage", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_ai_token_usage_user_id"), "ai_token_usage", ["user_id"], unique=False)

    # 21. Audit Logs
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)

    # 22. Code Plans
    op.create_index(op.f("ix_code_plans_workspace_id"), "code_plans", ["workspace_id"], unique=False)

    # 23. Generated Code Files
    op.create_index(op.f("ix_generated_code_files_workspace_id"), "generated_code_files", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_generated_code_files_project_id"), "generated_code_files", ["project_id"], unique=False)

    # 24. Code Reviews
    op.create_index(op.f("ix_code_reviews_workspace_id"), "code_reviews", ["workspace_id"], unique=False)

    # 25. Code Quality Scans
    op.create_index(op.f("ix_code_quality_scans_workspace_id"), "code_quality_scans", ["workspace_id"], unique=False)

    # 26. Refactoring Proposals
    op.create_index(op.f("ix_refactoring_proposals_workspace_id"), "refactoring_proposals", ["workspace_id"], unique=False)

    # 27. Bug Reports
    op.create_index(op.f("ix_bug_reports_workspace_id"), "bug_reports", ["workspace_id"], unique=False)

    # 28. Git Branches
    op.create_index(op.f("ix_git_branches_workspace_id"), "git_branches", ["workspace_id"], unique=False)

    # 29. Git Commits
    op.create_index(op.f("ix_git_commits_workspace_id"), "git_commits", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_git_commits_branch_id"), "git_commits", ["branch_id"], unique=False)

    # 30. Git Pull Requests
    op.create_index(op.f("ix_git_pull_requests_workspace_id"), "git_pull_requests", ["workspace_id"], unique=False)

    # 31. Release Plans
    op.create_index(op.f("ix_release_plans_workspace_id"), "release_plans", ["workspace_id"], unique=False)

    # 32. Deployment Plans
    op.create_index(op.f("ix_deployment_plans_workspace_id"), "deployment_plans", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_deployment_plans_release_id"), "deployment_plans", ["release_id"], unique=False)

    # 33. Sprint Updates
    op.create_index(op.f("ix_sprint_updates_workspace_id"), "sprint_updates", ["workspace_id"], unique=False)

    # 34. Developer Task Assignments
    op.create_index(op.f("ix_developer_task_assignments_workspace_id"), "developer_task_assignments", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_developer_task_assignments_planning_item_id"), "developer_task_assignments", ["planning_item_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema: Drop all added indexes."""
    op.drop_index(op.f("ix_developer_task_assignments_planning_item_id"), table_name="developer_task_assignments")
    op.drop_index(op.f("ix_developer_task_assignments_workspace_id"), table_name="developer_task_assignments")
    op.drop_index(op.f("ix_sprint_updates_workspace_id"), table_name="sprint_updates")
    op.drop_index(op.f("ix_deployment_plans_release_id"), table_name="deployment_plans")
    op.drop_index(op.f("ix_deployment_plans_workspace_id"), table_name="deployment_plans")
    op.drop_index(op.f("ix_release_plans_workspace_id"), table_name="release_plans")
    op.drop_index(op.f("ix_git_pull_requests_workspace_id"), table_name="git_pull_requests")
    op.drop_index(op.f("ix_git_commits_branch_id"), table_name="git_commits")
    op.drop_index(op.f("ix_git_commits_workspace_id"), table_name="git_commits")
    op.drop_index(op.f("ix_git_branches_workspace_id"), table_name="git_branches")
    op.drop_index(op.f("ix_bug_reports_workspace_id"), table_name="bug_reports")
    op.drop_index(op.f("ix_refactoring_proposals_workspace_id"), table_name="refactoring_proposals")
    op.drop_index(op.f("ix_code_quality_scans_workspace_id"), table_name="code_quality_scans")
    op.drop_index(op.f("ix_code_reviews_workspace_id"), table_name="code_reviews")
    op.drop_index(op.f("ix_generated_code_files_project_id"), table_name="generated_code_files")
    op.drop_index(op.f("ix_generated_code_files_workspace_id"), table_name="generated_code_files")
    op.drop_index(op.f("ix_code_plans_workspace_id"), table_name="code_plans")
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_ai_token_usage_user_id"), table_name="ai_token_usage")
    op.drop_index(op.f("ix_ai_token_usage_workspace_id"), table_name="ai_token_usage")
    op.drop_index(op.f("ix_activities_user_id"), table_name="activities")
    op.drop_index(op.f("ix_activities_workspace_id"), table_name="activities")
    op.drop_index(op.f("ix_chat_messages_project_id"), table_name="chat_messages")
    op.drop_index(op.f("ix_organizations_owner_id"), table_name="organizations")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_memberships_invited_by"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_workspace_id"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_user_id"), table_name="memberships")
    op.drop_index(op.f("ix_invitations_invited_by"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_workspace_id"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_organization_id"), table_name="invitations")
    op.drop_index(op.f("ix_coo_reports_workspace_id"), table_name="coo_reports")
    op.drop_index(op.f("ix_cto_reports_workspace_id"), table_name="cto_reports")
    op.drop_index(op.f("ix_ceo_reports_workspace_id"), table_name="ceo_reports")
    op.drop_index(op.f("ix_document_versions_document_id"), table_name="document_versions")
    op.drop_index(op.f("ix_documents_project_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_workspace_id"), table_name="documents")
    op.drop_index(op.f("ix_planning_analytics_workspace_id"), table_name="planning_analytics")
    op.drop_index(op.f("ix_resource_requirements_epic_id"), table_name="resource_requirements")
    op.drop_index(op.f("ix_resource_requirements_workspace_id"), table_name="resource_requirements")
    op.drop_index(op.f("ix_scenario_simulations_workspace_id"), table_name="scenario_simulations")
    op.drop_index(op.f("ix_execution_queue_workspace_id"), table_name="execution_queue")
    op.drop_index(op.f("ix_planning_dependencies_target_item_id"), table_name="planning_dependencies")
    op.drop_index(op.f("ix_planning_dependencies_source_item_id"), table_name="planning_dependencies")
    op.drop_index(op.f("ix_planning_dependencies_workspace_id"), table_name="planning_dependencies")
    op.drop_index(op.f("ix_planning_items_parent_id"), table_name="planning_items")
    op.drop_index(op.f("ix_planning_items_project_id"), table_name="planning_items")
    op.drop_index(op.f("ix_planning_items_workspace_id"), table_name="planning_items")
    op.drop_index(op.f("ix_missions_workspace_id"), table_name="missions")
    op.drop_index(op.f("ix_goals_workspace_id"), table_name="goals")
    op.drop_index(op.f("ix_projects_owner_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_workspace_id"), table_name="projects")
    op.drop_index(op.f("ix_workspaces_organization_id"), table_name="workspaces")
