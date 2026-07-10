from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class User(BaseEntity):
    __tablename__ = "users"

    full_name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(1024), nullable=True)
    phone = Column(String(50), nullable=True)
    timezone = Column(String(100), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Dialect-agnostic type: JSONB on Postgres, fallback to JSON on SQLite
    preferences = Column(
        JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False
    )

    # Relationships
    owned_organizations = relationship(
        "Organization", back_populates="owner", cascade="all, delete-orphan"
    )
    memberships = relationship(
        "Membership",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Membership.user_id]",
    )
