from sqlalchemy import JSON, Column, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class SimulatedIntegrationAsset(BaseEntity):
    __tablename__ = "simulated_integration_assets"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(100), nullable=False, index=True)  # 'github', 'slack', etc.
    asset_type = Column(String(100), nullable=False, index=True)  # 'repository', 'channel', etc.
    name = Column(String(255), nullable=False)
    payload = Column(JSON, default=dict, nullable=False)

    workspace = relationship("Workspace")
