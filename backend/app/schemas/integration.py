from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

# ══════════════════════════════════════════════════
# Plugin Schemas
# ══════════════════════════════════════════════════


class IntegrationPluginBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    plugin_version: str = "1.0.0"
    plugin_type: str = "OAuth"
    category: str = "Developer Tools"
    settings_schema: dict[str, Any] | None = None
    is_active: bool = True


class IntegrationPluginCreate(IntegrationPluginBase):
    pass


class IntegrationPluginUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    plugin_version: str | None = None
    plugin_type: str | None = None
    category: str | None = None
    settings_schema: dict[str, Any] | None = None
    is_active: bool | None = None


class IntegrationPluginResponse(IntegrationPluginBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# Connection Schemas
# ══════════════════════════════════════════════════


class IntegrationConnectionBase(BaseModel):
    plugin_id: UUID
    config: dict[str, Any] | None = None
    status: str = "Connected"


class IntegrationConnectionCreate(IntegrationConnectionBase):
    pass


class IntegrationConnectionUpdate(BaseModel):
    config: dict[str, Any] | None = None
    status: str | None = None
    error_message: str | None = None


class IntegrationConnectionResponse(IntegrationConnectionBase):
    id: UUID
    workspace_id: UUID
    last_sync_at: datetime | None = None
    error_message: str | None = None
    plugin: IntegrationPluginResponse | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# MCP Schemas
# ══════════════════════════════════════════════════


class MCPServerBase(BaseModel):
    name: str
    url: str
    headers: dict[str, str] | None = None
    is_active: bool = True


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerResponse(MCPServerBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MCPToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = {}


# ══════════════════════════════════════════════════
# Webhook Schemas
# ══════════════════════════════════════════════════


class IntegrationWebhookBase(BaseModel):
    name: str
    target_url: str
    events: list[str]
    is_active: bool = True


class IntegrationWebhookCreate(IntegrationWebhookBase):
    secret_token: str | None = None


class IntegrationWebhookResponse(IntegrationWebhookBase):
    id: UUID
    workspace_id: UUID
    secret_token: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# Log Schemas
# ══════════════════════════════════════════════════


class IntegrationLogResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    connection_id: UUID | None = None
    action: str
    status: str
    payload: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# Operations Request Schemas
# ══════════════════════════════════════════════════


class OAuthExchangeRequest(BaseModel):
    code: str
    redirect_uri: str
    provider: str


class WebhookTriggerRequest(BaseModel):
    event: str
    payload: dict[str, Any]
