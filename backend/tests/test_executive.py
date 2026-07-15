from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def auth_headers(client: TestClient, db: Session):
    """
    Creates a test user and returns request auth headers.
    """
    email = f"exec_{uuid4().hex}@productos.com"
    username = f"exec_{uuid4().hex}"

    # 1. Sign up user
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "username": username,
            "password": "testpassword123",
            "full_name": "Executive Officer",
        },
    )
    assert signup_res.status_code == 201

    # 2. Login user
    login_res = client.post(
        "/api/v1/auth/login", data={"username": email, "password": "testpassword123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create organization & workspace
    org_res = client.post(
        "/api/v1/organizations/",
        headers=headers,
        json={"name": "Exec Corp", "slug": f"exec-corp-{uuid4().hex[:8]}"},
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    ws_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        headers=headers,
        json={"name": "Executive Boardroom", "color": "#1e3a8a"},
    )
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
        "budget": 250000.0,
    }
    res = client.post(
        f"/api/v1/executive/ceo/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload,
    )
    assert res.status_code == 200
    data = res.json()
    assert "strategy_data" in data
    assert "financials" in data
    assert len(data["recommendations"]) > 0

    # 2. Get CEO reports
    list_res = client.get(
        f"/api/v1/executive/ceo/reports?workspace_id={ws_id}", headers=headers
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_cto_executive_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Generate CTO Report
    req_payload = {
        "product_spec": "A real-time collaborative code editor using WebSockets and CRDTs.",
        "preferred_cloud": "GCP",
        "compliance_needs": ["HIPAA", "SOC2"],
    }
    res = client.post(
        f"/api/v1/executive/cto/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload,
    )
    assert res.status_code == 200
    data = res.json()
    assert "architecture_review" in data
    assert "security_devops" in data
    assert "health_metrics" in data

    # 2. Get CTO reports
    list_res = client.get(
        f"/api/v1/executive/cto/reports?workspace_id={ws_id}", headers=headers
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_coo_executive_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Generate COO Report
    req_payload = {
        "sprint_name": "Sprint 8 - WebSockets Integration",
        "team_members": ["Alice", "Bob", "Charlie", "David"],
        "total_budget": 80000.0,
    }
    res = client.post(
        f"/api/v1/executive/coo/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload,
    )
    assert res.status_code == 200
    data = res.json()
    assert "resource_capacity" in data
    assert "delivery_monitoring" in data
    assert len(data["notification_center"]) > 0

    # 2. Get COO reports
    list_res = client.get(
        f"/api/v1/executive/coo/reports?workspace_id={ws_id}", headers=headers
    )
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_export_endpoints(client: TestClient, auth_headers):
    headers, ws_id = auth_headers
    report_id = uuid4()

    # 1. Test PDF export
    pdf_res = client.get(
        f"/api/v1/executive/export/pdf?report_id={report_id}&report_type=ceo&workspace_id={ws_id}",
        headers=headers,
    )
    assert pdf_res.status_code == 200
    assert pdf_res.json()["success"] is True

    # 2. Test PPT export
    ppt_res = client.get(
        f"/api/v1/executive/export/ppt?report_id={report_id}&report_type=cto&workspace_id={ws_id}",
        headers=headers,
    )
    assert ppt_res.status_code == 200
    assert ppt_res.json()["success"] is True


def test_download_report_idor_protection(client: TestClient, auth_headers, db: Session):
    from uuid import UUID
    headers, ws_id = auth_headers


    # 1. Generate a real CEO report
    req_payload = {
        "product_idea": "Build a secure medical records storage and sync platform.",
        "target_industry": "Healthcare Tech",
        "competitors": ["Epic Systems", "Cerner"],
        "budget": 250000.0,
    }
    res = client.post(
        f"/api/v1/executive/ceo/report?workspace_id={ws_id}",
        headers=headers,
        json=req_payload,
    )
    assert res.status_code == 200
    report_id = res.json()["id"]

    # 2. Owner can download PDF and PPT (no workspace_id parameter needed or supplied)
    pdf_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers=headers,
    )
    assert pdf_res.status_code == 200

    ppt_res = client.get(
        f"/api/v1/executive/download/ppt/{report_id}",
        headers=headers,
    )
    assert ppt_res.status_code == 200

    # 3. Create another user (different tenant)
    other_email = f"exec_{uuid4().hex}@productos.com"
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": other_email,
            "username": f"exec_{uuid4().hex}",
            "password": "testpassword123",
            "full_name": "Other Tenant",
        },
    )
    other_login_res = client.post(
        "/api/v1/auth/login", data={"username": other_email, "password": "testpassword123"}
    )
    other_token = other_login_res.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Accessing the owner's report using other tenant headers must return 404
    other_pdf_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers=other_headers,
    )
    assert other_pdf_res.status_code == 404

    # 4. Random UUID returns 404
    random_id = str(uuid4())
    random_res = client.get(
        f"/api/v1/executive/download/pdf/{random_id}",
        headers=headers,
    )
    assert random_res.status_code == 404

    # 5. Malformed UUID returns 422 (FastAPI path validation)
    malformed_res = client.get(
        "/api/v1/executive/download/pdf/invalid-uuid-string",
        headers=headers,
    )
    assert malformed_res.status_code == 422

    # 6. Unauthorized request (no token) returns 401
    client.cookies.clear()
    unauth_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
    )
    assert unauth_res.status_code == 401

    # 7. Expired JWT returns 401 or 403 depending on application auth config
    client.cookies.clear()
    expired_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers={"Authorization": "Bearer invalid_expired_jwt_token"},
    )
    assert expired_res.status_code in (401, 403)


    # 8. Duplicate active memberships: adding a duplicate membership shouldn't break the query
    from app.models.membership import Membership
    from app.models.user import User
    current_user_db = db.query(User).filter(User.full_name == "Executive Officer").first()
    if current_user_db:
        dup_mem = Membership(
            id=uuid4(),
            user_id=current_user_db.id,
            workspace_id=UUID(ws_id),
        )
        db.add(dup_mem)
        db.commit()

        dup_res = client.get(
            f"/api/v1/executive/download/pdf/{report_id}",
            headers=headers,
        )
        assert dup_res.status_code == 200

        # Clean up duplicate membership
        db.delete(dup_mem)
        db.commit()

    # 9. Concurrent downloads simulation
    import concurrent.futures
    def fetch_pdf():
        return client.get(f"/api/v1/executive/download/pdf/{report_id}", headers=headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_pdf) for _ in range(5)]
        results = [f.result() for f in futures]
    for r in results:
        assert r.status_code == 200

    # 10. Archived workspace returns 404
    from app.models.workspace import Workspace
    from uuid import UUID
    workspace_db = db.query(Workspace).filter(Workspace.id == UUID(ws_id)).first()
    workspace_db.archived = True
    db.add(workspace_db)
    db.commit()

    archived_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers=headers,
    )
    assert archived_res.status_code == 404

    # Restore archived workspace state
    workspace_db.archived = False
    db.add(workspace_db)
    db.commit()

    # 11. Revoked membership returns 404
    # Delete the user's active membership to simulate revocation
    user_mem = db.query(Membership).filter(
        Membership.workspace_id == UUID(ws_id),
        Membership.deleted_at.is_(None)
    ).first()
    
    from datetime import datetime, UTC
    user_mem.deleted_at = datetime.now(UTC)
    db.add(user_mem)
    db.commit()

    revoked_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers=headers,
    )
    assert revoked_res.status_code == 404

    # Restore membership
    user_mem.deleted_at = None
    db.add(user_mem)
    db.commit()

    # 12. Soft-deleted report returns 404
    from app.models.executive import CEOReport
    db_report = db.query(CEOReport).filter(CEOReport.id == UUID(report_id)).first()
    db_report.deleted_at = datetime.now(UTC)
    db.add(db_report)
    db.commit()

    deleted_res = client.get(
        f"/api/v1/executive/download/pdf/{report_id}",
        headers=headers,
    )
    assert deleted_res.status_code == 404


