from sqlalchemy import Column, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Membership(BaseEntity):
    __tablename__ = "memberships"

    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(50), default="Viewer", nullable=False)
    joined_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    invited_by = Column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships - explicitly declare user_id as the primary FK link
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    workspace = relationship("Workspace", back_populates="memberships")
