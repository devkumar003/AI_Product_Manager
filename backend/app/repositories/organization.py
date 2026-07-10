from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def get_by_slug(self, db: Session, slug: str) -> Organization | None:
        return (
            db.query(self.model)
            .filter(self.model.slug == slug, self.model.deleted_at.is_(None))
            .first()
        )

    def get_multi_by_owner(
        self, db: Session, *, owner_id: str, skip: int = 0, limit: int = 100
    ) -> list[Organization]:
        return (
            db.query(self.model)
            .filter(self.model.owner_id == owner_id, self.model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )


org_repo = OrganizationRepository(Organization)
