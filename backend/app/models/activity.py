from sqlalchemy import JSON, Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Activity(BaseEntity):
    __tablename__ = "activities"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
    )
    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(
        String(100), nullable=False
    )  # e.g. project_created, document_uploaded, login, logout, etc.
    entity_type = Column(
        String(50), nullable=False
    )  # e.g. project, document, user, workspace
    entity_id = Column(Uuid, nullable=True)
    description = Column(String(1024), nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace")
