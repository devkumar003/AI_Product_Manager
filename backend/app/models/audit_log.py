from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class AuditLog(BaseEntity):
    __tablename__ = "audit_logs"

    user_id = Column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(512), nullable=True)

    # Dialect-agnostic type: JSONB on Postgres, fallback to JSON on SQLite
    payload = Column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )

    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User")
