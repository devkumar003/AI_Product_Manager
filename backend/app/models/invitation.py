from sqlalchemy import Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Invitation(BaseEntity):
    __tablename__ = "invitations"

    organization_id = Column(
        Uuid,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
    )
    email = Column(String(255), nullable=False)
    role = Column(String(50), default="Viewer", nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, accepted, rejected, expired
    expires_at = Column(DateTime(timezone=True), nullable=False)
    invited_by = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    workspace = relationship("Workspace", back_populates="invitations")
    sender = relationship("User", foreign_keys=[invited_by])
