import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.planning import ExecutionQueueItem
from app.schemas.planning import ExecutionQueueItemCreate

logger = logging.getLogger("app.services.planning.execution_queue")


class ExecutionQueue:
    """
    Execution Queue. Supports task queuing with priority, scheduled execution,
    delayed execution, and retry handling.
    """

    def enqueue_task(
        self, db: Session, workspace_id: UUID, task_in: ExecutionQueueItemCreate
    ) -> ExecutionQueueItem:
        scheduled_at = task_in.scheduled_at or datetime.utcnow()
        item = ExecutionQueueItem(
            workspace_id=workspace_id,
            task_name=task_in.task_name,
            payload=task_in.payload,
            priority=task_in.priority or 0,
            status="Pending",
            retry_count=0,
            max_retries=task_in.max_retries or 3,
            scheduled_at=scheduled_at,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def fetch_next_executable(self, db: Session) -> list[ExecutionQueueItem]:
        """
        Retrieves items that are due or overdue, sorted by priority (highest first) and scheduled date.
        """
        now = datetime.utcnow()
        return (
            db.query(ExecutionQueueItem)
            .filter(
                ExecutionQueueItem.status.in_(["Pending", "Delayed"]),
                ExecutionQueueItem.scheduled_at <= now,
                ExecutionQueueItem.deleted_at.is_(None),
            )
            .order_by(
                ExecutionQueueItem.priority.desc(),
                ExecutionQueueItem.scheduled_at.asc(),
            )
            .all()
        )

    def mark_running(self, db: Session, item_id: UUID, workspace_id: UUID | None = None) -> bool:
        query = db.query(ExecutionQueueItem).filter(ExecutionQueueItem.id == item_id)
        if workspace_id:
            query = query.filter(ExecutionQueueItem.workspace_id == workspace_id)
        item = query.first()
        if not item:
            return False
        item.status = "Running"
        item.run_at = datetime.utcnow()
        db.add(item)
        db.commit()
        return True

    def mark_success(self, db: Session, item_id: UUID, workspace_id: UUID | None = None) -> bool:
        query = db.query(ExecutionQueueItem).filter(ExecutionQueueItem.id == item_id)
        if workspace_id:
            query = query.filter(ExecutionQueueItem.workspace_id == workspace_id)
        item = query.first()
        if not item:
            return False
        item.status = "Succeeded"
        db.add(item)
        db.commit()
        return True

    def mark_failed(self, db: Session, item_id: UUID, error_msg: str, workspace_id: UUID | None = None) -> bool:
        query = db.query(ExecutionQueueItem).filter(ExecutionQueueItem.id == item_id)
        if workspace_id:
            query = query.filter(ExecutionQueueItem.workspace_id == workspace_id)
        item = query.first()
        if not item:
            return False

        item.retry_count += 1
        item.error_log = error_msg

        if item.retry_count >= item.max_retries:
            item.status = "Failed"
            logger.error(
                f"Execution queue task {item.task_name} ({item.id}) failed permanently: {error_msg}"
            )
        else:
            # Backoff for retry: delay execution by 5 minutes * retry_count
            item.status = "Delayed"
            item.scheduled_at = datetime.utcnow() + timedelta(
                minutes=5 * item.retry_count
            )
            logger.warning(
                f"Execution queue task {item.task_name} ({item.id}) failed. Retrying at {item.scheduled_at}"
            )

        db.add(item)
        db.commit()
        return True

    def list_queue(self, db: Session, workspace_id: UUID) -> list[ExecutionQueueItem]:
        return (
            db.query(ExecutionQueueItem)
            .filter(
                ExecutionQueueItem.workspace_id == workspace_id,
                ExecutionQueueItem.deleted_at.is_(None),
            )
            .order_by(ExecutionQueueItem.scheduled_at.desc())
            .all()
        )
