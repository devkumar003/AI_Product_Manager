from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class Document(BaseEntity):
    __tablename__ = "documents"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id = Column(
        Uuid,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(255), nullable=False)
    filename = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=True)
    category = Column(String(100), default="General", nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    status = Column(String(50), default="Draft", nullable=False)
    current_version_number = Column(Integer, default=1, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="documents")
    workspace = relationship("Workspace")
    versions_list = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number.desc()",
    )
