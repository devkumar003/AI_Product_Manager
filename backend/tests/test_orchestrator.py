import json
import uuid
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.ai.schemas import AIResponse, TokenUsage


async def mock_llm_generate(*args, **kwargs):
    return AIResponse(
        content=json.dumps({
            # Discovery / Validation mockup
            "analysis": {"market_trends": ["AI Product Management is growing"]},
            "validation": {
                "pestle_markdown": "Political: Stable\nEconomic: Good",
                "swot_markdown": "Strengths: AI\nWeaknesses: None"
            },
            "discovery": {"personas": [{"name": "Product Manager"}]},
            # PRD / Requirements mockup
            "prd": "Product Specs content",
            "requirements": {"functional": ["Auth", "Dashboard"]},
            "stories": {"stories": [{"title": "As a User...", "description": "I want to log in", "priority": "High"}]},
            # Planning mockup
            "sprint": {"sprint_goal": "MVP"},
            "tasks": {"tasks": [{"title": "Setup DB", "description": "Create SQLite instance", "priority": "High"}]},
            # Roadmap mockup
            "prioritization": {"framework": "RICE"},
            "roadmap": "Roadmap timeline content",
            # Engineering mockup
            "architecture": "Architecture details",
            "database": "DB schema details",
            "api": "API route specs",
            # Risks / assessment mockup
            "risks": {"identified_risks": ["Resource shortage"]},
            "costs": {"cost_forecast": "Buffer needed"},
            "timeline": {"timeline_prediction": "Estimated 2 months"}
        }),
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, estimated_cost_usd=0.01),
        latency_ms=10.0,
        success=True,
    )


@patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock)
def test_orchestrator_workflow_endpoints(mock_generate, client: TestClient, db: Session):
    mock_generate.side_effect = mock_llm_generate

    # 1. Sign up and login
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "orch_tester@example.com",
            "username": "orchtester",
            "full_name": "Orchestration Tester",
            "password": "securepassword123",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "orch_tester@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create organization
    org_res = client.post(
        "/api/v1/organizations/",
        json={"name": "Orchestrator Labs", "slug": "orch-labs"},
        headers=headers,
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    # 3. Create workspace
    workspace_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        json={
            "name": "Orch Space",
            "description": "workspace for orchestrator testing",
            "visibility": "private",
        },
        headers=headers,
    )
    assert workspace_res.status_code == 201
    workspace_id = workspace_res.json()["id"]

    # 4. Create project
    project_res = client.post(
        f"/api/v1/projects/{workspace_id}",
        json={
            "name": "Orchestrator Test Project",
            "description": "A startup idea to test orchestrator",
        },
        headers=headers,
    )
    assert project_res.status_code == 201
    proj_data = project_res.json()
    project_id = proj_data["id"]
    execution_id = proj_data["workflow_id"]
    assert execution_id is not None

    # 6. Check workflow status
    status_res = client.get(
        f"/api/v1/orchestrator/status/{execution_id}",
        headers=headers,
    )
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["id"] == execution_id

    # 7. Cancel workflow
    cancel_res = client.post(
        f"/api/v1/orchestrator/cancel/{execution_id}",
        headers=headers,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "success"

    # 8. Check status after cancel
    status_res = client.get(
        f"/api/v1/orchestrator/status/{execution_id}",
        headers=headers,
    )
    assert status_res.json()["status"] == "cancelled"

    # 9. Test retry/resume workflow stage
    retry_res = client.post(
        f"/api/v1/orchestrator/retry/{execution_id}",
        headers=headers,
    )
    assert retry_res.status_code == 200
    assert retry_res.json()["status"] == "processing"
