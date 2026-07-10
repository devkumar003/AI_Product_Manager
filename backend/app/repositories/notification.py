import uuid
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def get_multi_by_user(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        unread_only: bool = False,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Notification]:
        query = db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.deleted == False,
            self.model.deleted_at.is_(None),
        )

        if unread_only:
            query = query.filter(self.model.read == False)
        if not include_archived:
            query = query.filter(self.model.archived == False)

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def mark_all_read(self, db: Session, *, user_id: uuid.UUID) -> int:
        count = (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.read == False,
                self.model.deleted == False,
                self.model.deleted_at.is_(None),
            )
            .update({"read": True}, synchronize_session=False)
        )
        db.commit()
        return count


notification_repo = NotificationRepository(Notification)
