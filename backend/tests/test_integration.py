import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def auth_headers(client: TestClient):
    # Register & Login
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "integration_tester@example.com",
            "username": "inttester",
            "full_name": "Integration Tester",
            "password": "securepwd123",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "integration_tester@example.com", "password": "securepwd123"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def workspace_id(client: TestClient, auth_headers: dict):
    # Org
    org_res = client.post(
        "/api/v1/organizations/",
        json={"name": "Integration Corp", "slug": "int-corp"},
        headers=auth_headers,
    )
    org_id = org_res.json()["id"]

    # Workspace
    ws_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        json={"name": "Integration Workspace"},
        headers=auth_headers,
    )
    return ws_res.json()["id"]


def test_plugins_and_connections_flow(client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. List Plugins (verify seeded)
    res = client.get(
        "/api/v1/integration/plugins",
        headers=auth_headers,
    )
    assert res.status_code == 200
    plugins = res.json()
    assert len(plugins) >= 5
    
    # Get a plugin slug (e.g. 'github')
    github_plugin = next(p for p in plugins if p["slug"] == "github")
    assert github_plugin is not None
    plugin_id = github_plugin["id"]

    # 2. Disable Plugin
    res_disable = client.post(
        f"/api/v1/integration/plugins/{plugin_id}/disable",
        headers=auth_headers,
    )
    assert res_disable.status_code == 200
    assert res_disable.json()["is_active"] is False

    # 3. Enable Plugin
    res_enable = client.post(
        f"/api/v1/integration/plugins/{plugin_id}/enable",
        headers=auth_headers,
    )
    assert res_enable.status_code == 200
    assert res_enable.json()["is_active"] is True

    # 4. Create manual connection
    res_conn = client.post(
        f"/api/v1/integration/connections?workspace_id={workspace_id}",
        json={
            "plugin_id": plugin_id,
            "config": {"account_owner": "test_owner"}
        },
        headers=auth_headers,
    )
    assert res_conn.status_code == 200
    conn_id = res_conn.json()["id"]

    # 5. List Connections
    res_list = client.get(
        f"/api/v1/integration/connections?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 6. Disconnect connection
    res_disc = client.delete(
        f"/api/v1/integration/connections/{conn_id}?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_disc.status_code == 204


def test_oauth_flow_and_api_proxies(client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. Get Authorize URL
    res_url = client.get(
        "/api/v1/integration/oauth/authorize?provider=github",
        headers=auth_headers,
    )
    assert res_url.status_code == 200
    assert "url" in res_url.json()

    # 2. Exchange Code
    res_exchange = client.post(
        f"/api/v1/integration/oauth/exchange?workspace_id={workspace_id}",
        json={
            "code": "test_auth_code_123",
            "redirect_uri": "http://localhost:3000/dashboard/integrations",
            "provider": "github"
        },
        headers=auth_headers,
    )
    assert res_exchange.status_code == 200
    assert res_exchange.json()["access_token"] == "mock_github_access_token_val_12345"

    # 3. Test Proxy API calls (GitHub, Jira, Slack)
    res_repos = client.get(
        f"/api/v1/integration/github/repos?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_repos.status_code == 200
    assert len(res_repos.json()) >= 2

    res_jira = client.get(
        f"/api/v1/integration/jira/projects?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_jira.status_code == 200
    assert len(res_jira.json()) >= 1

    res_slack = client.post(
        f"/api/v1/integration/slack/post?workspace_id={workspace_id}&channel=general&text=test",
        headers=auth_headers,
    )
    assert res_slack.status_code == 200
    assert "ts" in res_slack.json()


def test_mcp_servers_flow(client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. Register MCP Server
    res_reg = client.post(
        f"/api/v1/integration/mcp?workspace_id={workspace_id}",
        json={
            "name": "Local Filesystem Tools",
            "url": "http://localhost:8080/mcp",
            "headers": {"Authorization": "Bearer local_token"}
        },
        headers=auth_headers,
    )
    assert res_reg.status_code == 200
    server_id = res_reg.json()["id"]

    # 2. List MCP Servers
    res_list = client.get(
        f"/api/v1/integration/mcp?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Discover Tools
    res_tools = client.get(
        f"/api/v1/integration/mcp/{server_id}/tools?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_tools.status_code == 200
    assert "tools" in res_tools.json()

    # 4. Call Tool
    res_call = client.post(
        f"/api/v1/integration/mcp/{server_id}/call?workspace_id={workspace_id}",
        json={
            "tool_name": "web_search",
            "arguments": {"query": "Next.js 15"}
        },
        headers=auth_headers,
    )
    assert res_call.status_code == 200
    assert "status" in res_call.json()

    # 5. Delete MCP Server
    res_del = client.delete(
        f"/api/v1/integration/mcp/{server_id}?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_del.status_code == 204


def test_webhooks_and_logs(client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. Register Webhook
    res_reg = client.post(
        f"/api/v1/integration/webhooks?workspace_id={workspace_id}",
        json={
            "name": "Slack Dispatcher Event",
            "target_url": "https://hooks.slack.com/services/test",
            "events": ["planning.milestone_completed", "document.created"],
            "secret_token": "whsec_customtoken_1"
        },
        headers=auth_headers,
    )
    assert res_reg.status_code == 200
    wh_id = res_reg.json()["id"]

    # 2. List Webhooks
    res_list = client.get(
        f"/api/v1/integration/webhooks?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Trigger Webhook Event
    res_trig = client.post(
        f"/api/v1/integration/webhooks/trigger?workspace_id={workspace_id}",
        json={
            "event": "document.created",
            "payload": {"document_id": "doc_123", "title": "Product Specs"}
        },
        headers=auth_headers,
    )
    assert res_trig.status_code == 200
    assert res_trig.json()["subscribers_triggered"] >= 1

    # 4. Fetch Integration Logs
    res_logs = client.get(
        f"/api/v1/integration/logs?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_logs.status_code == 200
    assert len(res_logs.json()) >= 1

    # 5. Delete Webhook
    res_del = client.delete(
        f"/api/v1/integration/webhooks/{wh_id}?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_del.status_code == 204
