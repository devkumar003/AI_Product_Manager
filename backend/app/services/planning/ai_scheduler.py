import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.planning import PlanningDependency, PlanningItem

logger = logging.getLogger("app.services.planning.ai_scheduler")


class AIScheduler:
    """
    AI Scheduler. Schedules backlog tasks dynamically based on priority,
    deadlines, task estimations, and topological dependency order.
    """

    async def schedule_tasks(
        self, db: Session, workspace_id: UUID, base_start_date: datetime | None = None
    ) -> list[dict]:
        """
        Schedules all Todo/In Progress tasks for a workspace.
        Resolves the dependency graph and assigns start/end times.
        """
        start_time = base_start_date or datetime.utcnow()

        # 1. Fetch all items (specifically Tasks and Stories)
        tasks = (
            db.query(PlanningItem)
            .filter(
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.type.in_(["Task", "UserStory", "Subtask"]),
                PlanningItem.status.in_(["Todo", "In Progress", "Blocked"]),
                PlanningItem.deleted_at.is_(None),
            )
            .all()
        )

        if not tasks:
            return []

        # Map task ID to task object
        task_map = {t.id: t for t in tasks}

        # 2. Fetch dependencies
        dependencies = (
            db.query(PlanningDependency)
            .filter(
                PlanningDependency.workspace_id == workspace_id,
                PlanningDependency.deleted_at.is_(None),
            )
            .all()
        )

        # Build adjacency lists for topological sort
        adj = {t.id: [] for t in tasks}
        in_degree = {t.id: 0 for t in tasks}

        for dep in dependencies:
            src = dep.source_item_id
            tgt = dep.target_item_id
            # Only consider dependencies between our active tasks
            if src in adj and tgt in adj:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        # 3. Topological Sort (Kahn's Algorithm)
        # We also prioritize by task priority: Critical > High > Medium > Low
        priority_weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

        # Get initial zero in-degree tasks
        zero_in = [tid for tid, deg in in_degree.items() if deg == 0]
        # Sort by priority weight desc
        zero_in.sort(
            key=lambda tid: priority_weights.get(task_map[tid].priority, 2),
            reverse=True,
        )

        ordered_task_ids = []
        while zero_in:
            curr = zero_in.pop(0)
            ordered_task_ids.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    zero_in.append(neighbor)
            # Re-sort zero_in to maintain priority precedence
            zero_in.sort(
                key=lambda tid: priority_weights.get(task_map[tid].priority, 2),
                reverse=True,
            )

        # Handle cycles/unvisited tasks (just append them at the end)
        unvisited = set(task_map.keys()) - set(ordered_task_ids)
        if unvisited:
            logger.warning(
                f"Cycles detected in dependency graph for workspace {workspace_id}. Appending cycle tasks at the end."
            )
            ordered_task_ids.extend(list(unvisited))

        # 4. Schedule times (sequentially for simplicity, assuming 1 parallel development thread)
        # In a real scheduling system, tasks are scheduled across a pool of developers.
        # We can assume a single chronological timeline where tasks are allocated start/end dates.
        current_schedule_time = start_time
        schedule_output = []

        for tid in ordered_task_ids:
            task = task_map[tid]
            est_hours = task.estimated_hours or 4.0  # Default to 4 hours
            # Skip weekends (simplified: assume 8 hours/day execution)
            days_needed = est_hours / 8.0

            task_start = current_schedule_time
            task_end = task_start + timedelta(days=days_needed)

            # Update database metadata with scheduled times
            meta = dict(task.metadata_fields or {})
            meta["scheduled_start"] = task_start.isoformat()
            meta["scheduled_end"] = task_end.isoformat()
            task.metadata_fields = meta
            db.add(task)

            schedule_output.append(
                {
                    "task_id": str(task.id),
                    "title": task.title,
                    "type": task.type,
                    "priority": task.priority,
                    "scheduled_start": task_start.isoformat(),
                    "scheduled_end": task_end.isoformat(),
                    "estimated_hours": est_hours,
                }
            )

            # Advance timeline
            current_schedule_time = task_end

        db.commit()
        return schedule_output
