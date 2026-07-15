from sqlalchemy import Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class ChatMessage(BaseEntity):
    __tablename__ = "chat_messages"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sender = Column(String(50), nullable=False)  # 'user' or 'assistant'
    message = Column(String(8192), nullable=False)

    workspace = relationship("Workspace")
    user = relationship("User")
    project = relationship("Project")
