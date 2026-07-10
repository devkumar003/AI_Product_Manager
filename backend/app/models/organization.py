from sqlalchemy import Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Organization(BaseEntity):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(1024), nullable=True)
    logo = Column(String(1024), nullable=True)
    owner_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan = Column(String(50), default="free", nullable=False)
    status = Column(String(50), default="active", nullable=False)

    # Relationships
    owner = relationship("User", back_populates="owned_organizations")
    workspaces = relationship(
        "Workspace", back_populates="organization", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation", back_populates="organization", cascade="all, delete-orphan"
    )
