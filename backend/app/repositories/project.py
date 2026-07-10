import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def get_by_slug(
        self, db: Session, *, workspace_id: uuid.UUID, slug: str
    ) -> Project | None:
        return (
            db.query(self.model)
            .filter(
                self.model.workspace_id == workspace_id,
                self.model.slug == slug,
                self.model.deleted_at.is_(None),
            )
            .first()
        )

    def get_multi_by_workspace(
        self,
        db: Session,
        *,
        workspace_id: uuid.UUID,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_desc: bool = False,
    ) -> list[Project]:
        query = db.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.deleted_at.is_(None),
        )

        if search:
            search_filt = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.name.ilike(search_filt),
                    self.model.description.ilike(search_filt),
                    self.model.slug.ilike(search_filt),
                )
            )
        if status:
            query = query.filter(self.model.status == status)
        if priority:
            query = query.filter(self.model.priority == priority)

        # Sorting
        if sort_by and hasattr(self.model, sort_by):
            sort_attr = getattr(self.model, sort_by)
            if sort_desc:
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(self.model.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def duplicate(
        self, db: Session, *, project_id: uuid.UUID, owner_id: uuid.UUID | None = None
    ) -> Project | None:
        original = self.get(db, project_id)
        if not original:
            return None

        # Generate unique slug
        base_slug = f"{original.slug}-copy"
        slug = base_slug
        counter = 1
        while self.get_by_slug(db, workspace_id=original.workspace_id, slug=slug):
            slug = f"{base_slug}-{counter}"
            counter += 1

        duplicated = Project(
            workspace_id=original.workspace_id,
            name=f"{original.name} (Copy)",
            description=original.description,
            slug=slug,
            icon=original.icon,
            color=original.color,
            status="Planning",
            priority=original.priority,
            owner_id=owner_id or original.owner_id,
            archived=False,
        )
        db.add(duplicated)
        db.commit()
        db.refresh(duplicated)
        return duplicated


project_repo = ProjectRepository(Project)
