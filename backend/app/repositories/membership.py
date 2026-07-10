from uuid import UUID

from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.repositories.base import BaseRepository


class MembershipRepository(BaseRepository[Membership]):
    def get_by_user_and_workspace(
        self, db: Session, *, user_id: UUID, workspace_id: UUID
    ) -> Membership | None:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.workspace_id == workspace_id,
                self.model.deleted_at.is_(None),
            )
            .first()
        )

    def get_multi_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Membership]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id, self.model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_workspace(
        self, db: Session, *, workspace_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Membership]:
        return (
            db.query(self.model)
            .filter(
                self.model.workspace_id == workspace_id,
                self.model.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


membership_repo = MembershipRepository(Membership)
