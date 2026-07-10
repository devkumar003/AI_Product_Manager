import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.planning import Goal
from app.schemas.planning import GoalCreate, GoalUpdate

logger = logging.getLogger("app.services.planning.goal_manager")


class GoalManager:
    """
    Goal Management System. Manages Goal creation, tracking, status progression, and analytics.
    """

    def create_goal(self, db: Session, workspace_id: UUID, goal_in: GoalCreate) -> Goal:
        goal = Goal(
            workspace_id=workspace_id,
            name=goal_in.name,
            description=goal_in.description,
            type=goal_in.type,
            status=goal_in.status or "Open",
            progress=goal_in.progress or 0.0,
            target_date=goal_in.target_date,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def get_goal(self, db: Session, goal_id: UUID) -> Goal | None:
        return (
            db.query(Goal).filter(Goal.id == goal_id, Goal.deleted_at.is_(None)).first()
        )

    def list_workspace_goals(
        self, db: Session, workspace_id: UUID, goal_type: str | None = None
    ) -> list[Goal]:
        query = db.query(Goal).filter(
            Goal.workspace_id == workspace_id, Goal.deleted_at.is_(None)
        )
        if goal_type:
            query = query.filter(Goal.type == goal_type)
        return query.all()

    def update_goal(
        self, db: Session, goal_id: UUID, goal_in: GoalUpdate
    ) -> Goal | None:
        goal = self.get_goal(db, goal_id)
        if not goal:
            return None

        update_data = goal_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        goal.updated_at = datetime.utcnow()
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def delete_goal(self, db: Session, goal_id: UUID) -> bool:
        goal = self.get_goal(db, goal_id)
        if not goal:
            return False
        goal.deleted_at = datetime.utcnow()
        db.add(goal)
        db.commit()
        return True

    def calculate_progress_from_tasks(
        self,
        db: Session,
        goal_id: UUID,
        completed_tasks_count: int,
        total_tasks_count: int,
    ) -> float:
        """
        Updates a goal's progress based on associated tasks completion rate.
        """
        goal = self.get_goal(db, goal_id)
        if not goal:
            return 0.0

        if total_tasks_count > 0:
            progress = min(100.0, (completed_tasks_count / total_tasks_count) * 100.0)
        else:
            progress = 0.0

        goal.progress = progress
        if progress >= 100.0:
            goal.status = "Achieved"
        elif progress > 0.0 and goal.status == "Open":
            goal.status = "In Progress"

        goal.updated_at = datetime.utcnow()
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return progress
