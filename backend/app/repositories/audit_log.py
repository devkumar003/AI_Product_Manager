from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def log_action(
        self,
        db: Session,
        *,
        user_id: UUID | None,
        action: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        payload: dict | None = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            payload=payload or {},
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    def get_multi_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.deleted_at.is_(None))
            .order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


audit_log_repo = AuditLogRepository(AuditLog)
