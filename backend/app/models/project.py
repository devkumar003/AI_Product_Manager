from sqlalchemy import Boolean, Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Project(BaseEntity):
    __tablename__ = "projects"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    slug = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)
    color = Column(String(50), nullable=True)
    status = Column(String(50), default="Planning", nullable=False)
    priority = Column(String(50), default="Medium", nullable=False)
    owner_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    archived = Column(Boolean, default=False, nullable=False)

    # Relationships
    workspace = relationship("Workspace")
    owner = relationship("User")
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )
