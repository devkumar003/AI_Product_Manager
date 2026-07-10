import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.ai.schemas import AIResponse, TokenUsage


@pytest.fixture
def auth_headers(client: TestClient):
    # Register & Login
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "planner@example.com",
            "username": "planner",
            "full_name": "Planner Agent",
            "password": "securepwd123",
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "planner@example.com", "password": "securepwd123"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def workspace_id(client: TestClient, auth_headers: dict):
    # Org
    org_res = client.post(
        "/api/v1/organizations/",
        json={"name": "Plan Corp", "slug": "plan-corp"},
        headers=auth_headers,
    )
    org_id = org_res.json()["id"]

    # Workspace
    ws_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        json={"name": "Engineering Workspace"},
        headers=auth_headers,
    )
    return ws_res.json()["id"]


async def mock_llm_generate(*args, **kwargs):
    return AIResponse(
        content='{"epics": [{"title": "Epic Test", "description": "Mock description", "priority": "High", "estimated_hours": 10.0, "assigned_roles": ["Dev"], "features": []}]}',
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency_ms=0.0,
        success=True
    )


@patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock)
def test_goal_crud_workflow(mock_generate, client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. Create Goal
    res = client.post(
        f"/api/v1/planning/goals?workspace_id={workspace_id}",
        json={
            "name": "Establish AI Foundation",
            "description": "Define multi-agent infrastructure goals",
            "type": "Technical",
            "status": "Open",
            "progress": 0.0,
        },
        headers=auth_headers,
    )
    assert res.status_code == 201
    goal_id = res.json()["id"]

    # 2. List Goals
    res_list = client.get(
        f"/api/v1/planning/goals?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 3. Update Goal
    res_up = client.put(
        f"/api/v1/planning/goals/{goal_id}?workspace_id={workspace_id}",
        json={"progress": 25.0, "status": "In Progress"},
        headers=auth_headers,
    )
    assert res_up.status_code == 200
    assert res_up.json()["progress"] == 25.0

    # 4. Delete Goal
    res_del = client.delete(
        f"/api/v1/planning/goals/{goal_id}?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_del.status_code == 204


@patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock)
def test_backlog_and_scheduler_workflow(mock_generate, client: TestClient, auth_headers: dict, workspace_id: str):
    mock_generate.side_effect = mock_llm_generate

    # 1. Generate Backlog from vision
    res = client.post(
        f"/api/v1/planning/backlog/generate?workspace_id={workspace_id}",
        json={"vision": "Create a simple calendar app for scheduling tasks"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 2. Run AI Scheduler
    res_sched = client.post(
        f"/api/v1/planning/scheduler/schedule?workspace_id={workspace_id}",
        json={},
        headers=auth_headers,
    )
    assert res_sched.status_code == 200


@patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock)
def test_simulations_and_resource_planner(mock_generate, client: TestClient, auth_headers: dict, workspace_id: str):
    # Mock return for simulation
    mock_generate.return_value = AIResponse(
        content='{"best_case_timeline": {"duration_weeks": 4}, "worst_case_timeline": {"duration_weeks": 12}, "average_case_timeline": {"duration_weeks": 7}, "budget_impact": {}, "timeline_impact": {}}',
        model="gpt-4o",
        provider="openai",
        usage=TokenUsage(),
        latency_ms=0.0,
        success=True
    )

    # 1. Run simulation
    res_sim = client.post(
        f"/api/v1/planning/simulations?workspace_id={workspace_id}",
        json={"name": "Simulated Release", "vision": "Deploy mobile payments"},
        headers=auth_headers,
    )
    assert res_sim.status_code == 200
    assert "best_case_timeline" in res_sim.json()


def test_templates_and_roadmap(client: TestClient, auth_headers: dict, workspace_id: str):
    # 1. Get Templates
    res_t = client.get(
        "/api/v1/planning/intelligence/templates",
        headers=auth_headers,
    )
    assert res_t.status_code == 200
    assert "SaaS" in res_t.json()

    # 2. Apply Template
    res_apply = client.post(
        f"/api/v1/planning/intelligence/templates/apply?workspace_id={workspace_id}",
        json={"template_key": "SaaS"},
        headers=auth_headers,
    )
    assert res_apply.status_code == 200
    assert len(res_apply.json()) > 0

    # 3. Get Roadmap
    res_roadmap = client.get(
        f"/api/v1/planning/intelligence/roadmap?workspace_id={workspace_id}",
        headers=auth_headers,
    )
    assert res_roadmap.status_code == 200
    assert "roadmap" in res_roadmap.json()
