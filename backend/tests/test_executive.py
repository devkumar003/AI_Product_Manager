import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

@pytest.fixture
def auth_headers(client: TestClient, db: Session):
    """
    Creates a test user and returns request auth headers.
    """
    email = f"exec_{uuid4().hex}@productos.com"
    username = f"exec_{uuid4().hex}"
    
    # 1. Sign up user
    signup_res = client.post("/api/v1/auth/signup", json={
        "email": email,
        "username": username,
        "password": "testpassword123",
        "full_name": "Executive Officer"
    })
    assert signup_res.status_code == 201

    # 2. Login user
    login_res = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "testpassword123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create organization & workspace
    org_res = client.post("/api/v1/organizations/", headers=headers, json={
        "name": "Exec Corp",
        "slug": f"exec-corp-{uuid4().hex[:8]}"
    })
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    ws_res = client.post(f"/api/v1/workspaces/?org_id={org_id}", headers=headers, json={
        "name": "Executive Boardroom",
        "color": "#1e3a8a"
    })
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # Switch active workspace
    switch_res = client.post(f"/api/v1/workspaces/{ws_id}/switch", headers=headers)
    assert switch_res.status_code == 200

    return headers, ws_id


def test_ceo_executive_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Generate CEO Report
    req_payload = {
        "product_idea": "Build a secure medical records storage and sync platform.",
        "target_industry": "Healthcare Tech",
        "competitors": ["Epic Systems", "Cerner"],
        "budget": 250000.0
    }
    res = client.post(
        f"/api/v1/executive/ceo/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload
    )
    assert res.status_code == 200
    data = res.json()
    assert "strategy_data" in data
    assert "financials" in data
    assert len(data["recommendations"]) > 0

    # 2. Get CEO reports
    list_res = client.get(f"/api/v1/executive/ceo/reports?workspace_id={ws_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_cto_executive_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Generate CTO Report
    req_payload = {
        "product_spec": "A real-time collaborative code editor using WebSockets and CRDTs.",
        "preferred_cloud": "GCP",
        "compliance_needs": ["HIPAA", "SOC2"]
    }
    res = client.post(
        f"/api/v1/executive/cto/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload
    )
    assert res.status_code == 200
    data = res.json()
    assert "architecture_review" in data
    assert "security_devops" in data
    assert "health_metrics" in data

    # 2. Get CTO reports
    list_res = client.get(f"/api/v1/executive/cto/reports?workspace_id={ws_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_coo_executive_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Generate COO Report
    req_payload = {
        "sprint_name": "Sprint 8 - WebSockets Integration",
        "team_members": ["Alice", "Bob", "Charlie", "David"],
        "total_budget": 80000.0
    }
    res = client.post(
        f"/api/v1/executive/coo/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload
    )
    assert res.status_code == 200
    data = res.json()
    assert "resource_capacity" in data
    assert "delivery_monitoring" in data
    assert len(data["notification_center"]) > 0

    # 2. Get COO reports
    list_res = client.get(f"/api/v1/executive/coo/reports?workspace_id={ws_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_export_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers
    report_id = uuid4()

    # 1. Test PDF export
    pdf_res = client.get(
        f"/api/v1/executive/export/pdf?report_id={report_id}&report_type=ceo&workspace_id={ws_id}",
        headers=headers
    )
    assert pdf_res.status_code == 200
    assert pdf_res.json()["success"] is True

    # 2. Test PPT export
    ppt_res = client.get(
        f"/api/v1/executive/export/ppt?report_id={report_id}&report_type=cto&workspace_id={ws_id}",
        headers=headers
    )
    assert ppt_res.status_code == 200
    assert ppt_res.json()["success"] is True
