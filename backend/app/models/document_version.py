from sqlalchemy import Column, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class DocumentVersion(BaseEntity):
    __tablename__ = "document_versions"

    document_id = Column(
        Uuid,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number = Column(Integer, nullable=False)
    filename = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="versions_list")
