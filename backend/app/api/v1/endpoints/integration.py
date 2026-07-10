import logging
from uuid import UUID
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.integration import IntegrationLog
from app.schemas.integration import (
    IntegrationPluginResponse,
    IntegrationConnectionResponse,
    IntegrationConnectionCreate,
    IntegrationConnectionUpdate,
    MCPServerResponse,
    MCPServerCreate,
    MCPToolCallRequest,
    IntegrationWebhookResponse,
    IntegrationWebhookCreate,
    IntegrationLogResponse,
    OAuthExchangeRequest,
    WebhookTriggerRequest,
)
from app.services.integration import (
    plugin_manager,
    oauth_manager,
    mcp_service,
    webhook_engine,
    api_manager,
)

logger = logging.getLogger("app.api.v1.endpoints.integration")
router = APIRouter()


# ══════════════════════════════════════════════════
# Plugins & Connections
# ══════════════════════════════════════════════════

@router.get("/plugins", response_model=List[IntegrationPluginResponse])
def list_plugins(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Exposes all seeded plugins in the system."""
    return plugin_manager.list_plugins(db, active_only=False)


@router.post("/plugins/{id}/enable", response_model=IntegrationPluginResponse)
def enable_plugin(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    plugin = plugin_manager.enable_plugin(db, id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.post("/plugins/{id}/disable", response_model=IntegrationPluginResponse)
def disable_plugin(id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    plugin = plugin_manager.disable_plugin(db, id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return plugin


@router.get("/connections", response_model=List[IntegrationConnectionResponse])
def list_connections(
    workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Lists all active connections in a workspace."""
    from app.models.integration import IntegrationConnection
    return db.query(IntegrationConnection).filter(
        IntegrationConnection.workspace_id == workspace_id
    ).all()


@router.post("/connections", response_model=IntegrationConnectionResponse)
def create_connection(
    workspace_id: UUID,
    payload: IntegrationConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Creates a connection manually (e.g. for API key or webhook plugins)."""
    return plugin_manager.create_connection(db, workspace_id, payload.plugin_id, payload.config)


@router.delete("/connections/{id}")
def disconnect_connection(
    id: UUID,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Disconnects and sets the connection state to Disconnected."""
    success = plugin_manager.disconnect_connection(db, workspace_id, id)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════
# OAuth Endpoints
# ══════════════════════════════════════════════════

@router.get("/oauth/authorize")
def get_oauth_authorize_url(
    provider: str,
    client_id: str = "default_client_id",
    redirect_uri: str = "http://localhost:3000/dashboard/integrations",
    current_user: User = Depends(get_current_active_user)
):
    """Generates the external authorization redirect URL."""
    url = oauth_manager.get_authorize_url(provider, client_id, redirect_uri)
    return {"url": url}


@router.post("/oauth/exchange")
def oauth_exchange_code(
    workspace_id: UUID,
    payload: OAuthExchangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Exchanges code for access tokens."""
    return oauth_manager.exchange_code_for_tokens(
        db, workspace_id, payload.provider, payload.code, payload.redirect_uri
    )


# ══════════════════════════════════════════════════
# Model Context Protocol (MCP) Endpoints
# ══════════════════════════════════════════════════

@router.get("/mcp", response_model=List[MCPServerResponse])
def list_mcp_servers(
    workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return mcp_service.list_mcp_servers(db, workspace_id)


@router.post("/mcp", response_model=MCPServerResponse)
def register_mcp_server(
    workspace_id: UUID,
    payload: MCPServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return mcp_service.register_mcp_server(
        db, workspace_id, payload.name, payload.url, payload.headers
    )


@router.delete("/mcp/{id}")
def delete_mcp_server(
    id: UUID,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = mcp_service.delete_mcp_server(db, workspace_id, id)
    if not success:
        raise HTTPException(status_code=404, detail="MCP Server not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/mcp/{id}/tools")
async def discover_mcp_tools(
    id: UUID,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    tools = await mcp_service.discover_tools(db, workspace_id, id)
    return {"tools": tools}


@router.post("/mcp/{id}/call")
async def execute_mcp_tool(
    id: UUID,
    workspace_id: UUID,
    payload: MCPToolCallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await mcp_service.execute_tool(
        db, workspace_id, id, payload.tool_name, payload.arguments
    )


# ══════════════════════════════════════════════════
# Webhooks Endpoints
# ══════════════════════════════════════════════════

@router.get("/webhooks", response_model=List[IntegrationWebhookResponse])
def list_webhooks(
    workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return webhook_engine.list_webhooks(db, workspace_id)


@router.post("/webhooks", response_model=IntegrationWebhookResponse)
def register_webhook(
    workspace_id: UUID,
    payload: IntegrationWebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return webhook_engine.register_webhook(
        db, workspace_id, payload.name, payload.target_url, payload.events, payload.secret_token
    )


@router.delete("/webhooks/{id}")
def delete_webhook(
    id: UUID,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = webhook_engine.delete_webhook(db, workspace_id, id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/webhooks/trigger")
async def trigger_webhook_event(
    workspace_id: UUID,
    payload: WebhookTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    count = await webhook_engine.trigger_event(db, workspace_id, payload.event, payload.payload)
    return {"status": "dispatched", "subscribers_triggered": count}


# ══════════════════════════════════════════════════
# Audit Logs Endpoints
# ══════════════════════════════════════════════════

@router.get("/logs", response_model=List[IntegrationLogResponse])
def get_integration_logs(
    workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return db.query(IntegrationLog).filter(
        IntegrationLog.workspace_id == workspace_id
    ).order_by(IntegrationLog.created_at.desc()).limit(100).all()


# ══════════════════════════════════════════════════
# Connectors / Providers APIs Proxies
# ══════════════════════════════════════════════════

@router.get("/github/repos")
async def github_repos(workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await api_manager.github_get_repositories(db, workspace_id)


@router.get("/github/branches")
async def github_branches(
    workspace_id: UUID, repo: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await api_manager.github_get_branches(db, workspace_id, repo)


@router.get("/github/commits")
async def github_commits(
    workspace_id: UUID, repo: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await api_manager.github_get_commits(db, workspace_id, repo)


@router.get("/github/prs")
async def github_prs(
    workspace_id: UUID, repo: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await api_manager.github_get_pull_requests(db, workspace_id, repo)


@router.get("/jira/projects")
async def jira_projects(workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await api_manager.jira_get_projects(db, workspace_id)


@router.get("/jira/issues")
async def jira_issues(
    workspace_id: UUID, project_key: str = "PROD", db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await api_manager.jira_get_issues(db, workspace_id, project_key)


@router.get("/notion/databases")
async def notion_databases(workspace_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await api_manager.notion_get_databases(db, workspace_id)


@router.post("/slack/post")
async def slack_post(
    workspace_id: UUID, channel: str, text: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await api_manager.slack_post_message(db, workspace_id, channel, text)
