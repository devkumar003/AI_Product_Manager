import uuid
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def log(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        description: str,
        workspace_id: uuid.UUID | None = None,
        metadata_json: dict | None = None,
    ) -> Activity:
        db_activity = Activity(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            metadata_json=metadata_json or {},
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    def get_multi_by_workspace(
        self,
        db: Session,
        *,
        workspace_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Activity]:
        return (
            db.query(self.model)
            .filter(self.model.workspace_id == workspace_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


activity_repo = ActivityRepository(Activity)
