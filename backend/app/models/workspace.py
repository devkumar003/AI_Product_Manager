from sqlalchemy import Boolean, Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Workspace(BaseEntity):
    __tablename__ = "workspaces"

    organization_id = Column(
        Uuid,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    icon = Column(String(255), nullable=True)
    color = Column(String(50), nullable=True)
    visibility = Column(String(50), default="private", nullable=False)
    archived = Column(Boolean, default=False, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="workspaces")
    memberships = relationship(
        "Membership", back_populates="workspace", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation", back_populates="workspace", cascade="all, delete-orphan"
    )
