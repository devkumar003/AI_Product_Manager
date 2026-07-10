import json
from unittest.mock import AsyncMock, patch
import pytest


from app.ai.schemas import AIResponse, TokenUsage

async def mock_llm_generate(*args, **kwargs):
    return AIResponse(
        content="This is a mock response from the new AI Infrastructure LLM Manager.",
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency_ms=0.0,
        success=True
    )


@patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock)
def test_ai_endpoints_workflow(mock_generate, client, db):
    # Setup mock behavior
    mock_generate.side_effect = mock_llm_generate

    # 1. Sign up and login to retrieve access token
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "ai_new_tester@example.com",
            "username": "ainewtester",
            "full_name": "AI New Tester",
            "password": "securepassword123",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "ai_new_tester@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create organization
    org_res = client.post(
        "/api/v1/organizations/",
        json={"name": "AI Labs", "slug": "ai-labs"},
        headers=headers,
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    # 3. Create workspace
    workspace_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        json={"name": "AI R&D Space", "description": "workspace for ai agents testing", "visibility": "private"},
        headers=headers,
    )
    assert workspace_res.status_code == 201
    workspace_id = workspace_res.json()["id"]

    # 4. Test Unified completions endpoint
    res = client.post(
        "/api/v1/ai/",
        json={
            "workspace_id": workspace_id,
            "user_id": "",  # Automatically populated by router
            "user_message": "Hello, AI infrastructure!",
            "stream": False,
        },
        headers=headers,
    )
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["success"] is True
    assert "new AI Infrastructure" in res_data["content"]

    # 5. Test Unified streaming endpoint
    stream_res = client.post(
        "/api/v1/ai/stream",
        json={
            "workspace_id": workspace_id,
            "user_id": "",
            "user_message": "Please stream this back.",
            "stream": True,
        },
        headers=headers,
    )
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
