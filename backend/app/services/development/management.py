import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.development import (
    DeploymentPlan,
    DeveloperTaskAssignment,
    ReleasePlan,
    SprintUpdate,
)
from app.services.ai.agents.base import AgentConfig
from app.services.ai.llm_manager import llm_manager

logger = logging.getLogger("app.services.development.management")


class DevelopmentManagement:
    def create_release_plan(
        self,
        db: Session,
        workspace_id: UUID,
        version: str,
        name: str,
        description: str,
        scope: list[UUID],
    ) -> ReleasePlan:
        """
        Release Planning Engine.
        """
        logger.info(f"Generating Release Plan: {version}")

        # Invoke LLM to outline milestones and release notes
        prompt = (
            f"Generate release milestones and changelog schema for release version '{version}' named '{name}':\n"
            f"Description: {description}\n"
            f"Scope item count: {len(scope)}\n\n"
            f"Provide list of milestones with timeline goals."
        )
        try:
            res = llm_manager.generate_sync(
                prompt=prompt,
                system_prompt="You are a Product Release Planner.",
                config=AgentConfig(temperature=0.3),
            )
            notes = res.content
        except Exception:
            notes = "Initial build release notes."

        milestones = [
            {"phase": "Beta Launch", "due": "2 weeks", "scope": "Core Features"},
            {
                "phase": "Bug Fix & Hardening",
                "due": "3 weeks",
                "scope": "Test coverage improvement",
            },
            {
                "phase": "Production deploy",
                "due": "4 weeks",
                "scope": "Cloud migration",
            },
        ]

        release = ReleasePlan(
            workspace_id=workspace_id,
            version=version,
            name=name,
            description=description + f"\n\nMilestones Summary:\n{notes}",
            milestones=milestones,
            scope=scope,
            status="Draft",
        )
        db.add(release)
        db.commit()
        db.refresh(release)
        return release

    def create_deployment_plan(
        self,
        db: Session,
        workspace_id: UUID,
        release_id: UUID,
        environment: str,
        provider: str,
    ) -> DeploymentPlan:
        """
        Deployment Planning Engine.
        """
        logger.info(
            f"Creating Deployment Plan for release: {release_id} in {environment}"
        )

        # Generate docker compose / kubernetes stubs
        manifests = {
            "docker-compose.yaml": (
                "version: '3.8'\n"
                "services:\n"
                "  backend:\n"
                "    image: productos-backend:latest\n"
                "    ports:\n"
                "      - '8000:8000'\n"
                "    environment:\n"
                "      - DATABASE_URL=postgresql://user:pass@db:5432/db\n"
                "  frontend:\n"
                "    image: productos-frontend:latest\n"
                "    ports:\n"
                "      - '3000:3000'\n"
            )
        }

        plan = DeploymentPlan(
            workspace_id=workspace_id,
            release_id=release_id,
            environment=environment,
            provider=provider,
            manifests=manifests,
            steps=[
                "Build docker containers for production target.",
                "Execute DB migrations and seeding.",
                "Verify API health checkpoints.",
                "Toggle route proxy target to new containers.",
            ],
            status="Ready",
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    def create_sprint_update(
        self, db: Session, workspace_id: UUID, sprint_name: str, progress_summary: str
    ) -> SprintUpdate:
        """
        Sprint Update Engine.
        """
        logger.info(f"Publishing Sprint update for: {sprint_name}")

        burn_down = {
            "total_story_points": 40,
            "completed_story_points": 24,
            "days_remaining": 6,
            "daily_history": [40, 38, 35, 30, 24],
        }

        update = SprintUpdate(
            workspace_id=workspace_id,
            sprint_name=sprint_name,
            burn_down_data=burn_down,
            progress_summary=progress_summary,
            impediments=["Dependencies on external Slack notification webhook setup"],
        )
        db.add(update)
        db.commit()
        db.refresh(update)
        return update

    def assign_developer_task(
        self,
        db: Session,
        workspace_id: UUID,
        developer_name: str,
        planning_item_id: UUID,
        assigned_role: str,
        allocated_hours: float,
    ) -> DeveloperTaskAssignment:
        """
        Developer Task Assignment Engine.
        """
        logger.info(f"Assigning {developer_name} to planning item {planning_item_id}")

        assignment = DeveloperTaskAssignment(
            workspace_id=workspace_id,
            developer_name=developer_name,
            planning_item_id=planning_item_id,
            assigned_role=assigned_role,
            allocated_hours=allocated_hours,
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment


dev_management = DevelopmentManagement()
