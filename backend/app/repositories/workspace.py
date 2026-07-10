from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    def get_multi_by_org(
        self, db: Session, *, org_id: str, skip: int = 0, limit: int = 100
    ) -> list[Workspace]:
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


workspace_repo = WorkspaceRepository(Workspace)
