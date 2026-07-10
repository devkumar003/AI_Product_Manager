from uuid import UUID

from sqlalchemy.orm import Session

from app.models.invitation import Invitation
from app.repositories.base import BaseRepository


class InvitationRepository(BaseRepository[Invitation]):
    def get_by_token(self, db: Session, token: str) -> Invitation | None:
        return (
            db.query(self.model)
            .filter(self.model.token == token, self.model.deleted_at.is_(None))
            .first()
        )

    def get_by_email_and_org(
        self, db: Session, *, email: str, org_id: UUID
    ) -> Invitation | None:
        return (
            db.query(self.model)
            .filter(
                self.model.email == email,
                self.model.organization_id == org_id,
                self.model.deleted_at.is_(None),
            )
            .first()
        )

    def get_multi_by_org(
        self, db: Session, *, org_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Invitation]:
        return (
            db.query(self.model)
            .filter(
                self.model.organization_id == org_id,
                self.model.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


invitation_repo = InvitationRepository(Invitation)
