from sqlalchemy import JSON, Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class WorkspaceInsight(BaseEntity):
    __tablename__ = "workspace_insights"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, default=dict, nullable=False)

    workspace = relationship("Workspace")
