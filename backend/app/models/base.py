import uuid

from sqlalchemy import Column, DateTime, Integer, Uuid, func

from app.database.session import Base


class BaseEntity(Base):
    __abstract__ = True

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Uuid, nullable=True)
    updated_by = Column(Uuid, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    __mapper_args__ = {"version_id_col": version}
