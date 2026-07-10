from sqlalchemy import Boolean, Column, ForeignKey, String, Uuid, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Notification(BaseEntity):
    __tablename__ = "notifications"

    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(String(50), default="Info", nullable=False) # Info, Warning, Error, Success
    title = Column(String(255), nullable=False)
    message = Column(String(1024), nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User")
