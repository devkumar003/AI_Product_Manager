from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


# ══════════════════════════════════════════════════
# Plugin Schemas
# ══════════════════════════════════════════════════

class IntegrationPluginBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    plugin_version: str = "1.0.0"
    plugin_type: str = "OAuth"
    category: str = "Developer Tools"
    settings_schema: Optional[Dict[str, Any]] = None
    is_active: bool = True


class IntegrationPluginCreate(IntegrationPluginBase):
    pass


class IntegrationPluginUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    plugin_version: Optional[str] = None
    plugin_type: Optional[str] = None
    category: Optional[str] = None
    settings_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


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
    config: Optional[Dict[str, Any]] = None
    status: str = "Connected"


class IntegrationConnectionCreate(IntegrationConnectionBase):
    pass


class IntegrationConnectionUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class IntegrationConnectionResponse(IntegrationConnectionBase):
    id: UUID
    workspace_id: UUID
    last_sync_at: Optional[datetime] = None
    error_message: Optional[str] = None
    plugin: Optional[IntegrationPluginResponse] = None
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
    headers: Optional[Dict[str, str]] = None
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
    arguments: Dict[str, Any] = {}


# ══════════════════════════════════════════════════
# Webhook Schemas
# ══════════════════════════════════════════════════

class IntegrationWebhookBase(BaseModel):
    name: str
    target_url: str
    events: List[str]
    is_active: bool = True


class IntegrationWebhookCreate(IntegrationWebhookBase):
    secret_token: Optional[str] = None


class IntegrationWebhookResponse(IntegrationWebhookBase):
    id: UUID
    workspace_id: UUID
    secret_token: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════
# Log Schemas
# ══════════════════════════════════════════════════

class IntegrationLogResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    connection_id: Optional[UUID] = None
    action: str
    status: str
    payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
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
    payload: Dict[str, Any]
