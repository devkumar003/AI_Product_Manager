
from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class IntegrationPlugin(BaseEntity):
    __tablename__ = "integration_plugins"

    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    plugin_version = Column(String, default="1.0.0", nullable=False)
    plugin_type = Column(
        String, default="OAuth", nullable=False
    )  # OAuth, APIKey, Webhook, MCP
    category = Column(
        String, default="Developer Tools", nullable=False
    )  # Dev, Chat, Email, Calendar, Drive, Design
    settings_schema = Column(
        JSON, nullable=True
    )  # JSON Schema for configuration parameters
    is_active = Column(Boolean, default=True, nullable=False)

    connections = relationship(
        "IntegrationConnection", back_populates="plugin", cascade="all, delete-orphan"
    )


class IntegrationConnection(BaseEntity):
    __tablename__ = "integration_connections"

    workspace_id = Column(Uuid, ForeignKey("workspaces.id"), index=True, nullable=False)
    plugin_id = Column(
        Uuid, ForeignKey("integration_plugins.id"), index=True, nullable=False
    )
    config = Column(JSON, nullable=True)  # Non-sensitive configuration options
    status = Column(
        String, default="Connected", nullable=False
    )  # Connected, Disconnected, Error
    last_sync_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

    plugin = relationship("IntegrationPlugin", back_populates="connections")
    logs = relationship(
        "IntegrationLog", back_populates="connection", cascade="all, delete-orphan"
    )


class EncryptedSecret(BaseEntity):
    __tablename__ = "encrypted_secrets"

    workspace_id = Column(Uuid, ForeignKey("workspaces.id"), index=True, nullable=False)
    secret_key = Column(String, index=True, nullable=False)  # E.g. "github_oauth_token"
    encrypted_value = Column(String, nullable=False)


class MCPServer(BaseEntity):
    __tablename__ = "mcp_servers"

    workspace_id = Column(Uuid, ForeignKey("workspaces.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    headers = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class IntegrationWebhook(BaseEntity):
    __tablename__ = "integration_webhooks"

    workspace_id = Column(Uuid, ForeignKey("workspaces.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of subscribed events
    secret_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class IntegrationLog(BaseEntity):
    __tablename__ = "integration_logs"

    workspace_id = Column(Uuid, ForeignKey("workspaces.id"), index=True, nullable=False)
    connection_id = Column(
        Uuid, ForeignKey("integration_connections.id"), index=True, nullable=True
    )
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)  # Success, Failed
    payload = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)

    connection = relationship("IntegrationConnection", back_populates="logs")
