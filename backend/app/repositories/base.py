from datetime import UTC, datetime
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from app.models.base import BaseEntity

ModelType = TypeVar("ModelType", bound=BaseEntity)


class BaseRepository[ModelType: BaseEntity]:
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        """
        Retrieve record by primary key, skipping soft-deleted rows.
        """
        return (
            db.query(self.model)
            .filter(self.model.id == id, self.model.deleted_at.is_(None))
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """
        Retrieve multiple records with pagination, skipping soft-deleted rows.
        """
        return (
            db.query(self.model)
            .filter(self.model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: Any) -> ModelType:
        """
        Persist a new entity record.
        """
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Any) -> ModelType:
        """
        Update fields on an existing entity record.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType | None:
        """
        Hard delete an entity record.
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def soft_remove(self, db: Session, *, id: Any) -> ModelType | None:
        """
        Soft delete an entity record.
        """
        obj = self.get(db, id)
        if obj:
            obj.deleted_at = datetime.now(UTC)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
