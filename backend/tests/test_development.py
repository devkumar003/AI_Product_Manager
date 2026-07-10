import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

@pytest.fixture
def auth_headers(client: TestClient, db: Session):
    """
    Creates a test user and returns request auth headers.
    """
    email = f"dev_{uuid4().hex}@productos.com"
    username = f"dev_{uuid4().hex}"
    
    # 1. Sign up user
    signup_res = client.post("/api/v1/auth/signup", json={
        "email": email,
        "username": username,
        "password": "testpassword123",
        "full_name": "Developer Agent"
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
        "name": "Dev Labs",
        "slug": f"dev-labs-{uuid4().hex[:8]}"
    })
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    ws_res = client.post(f"/api/v1/workspaces/?org_id={org_id}", headers=headers, json={
        "name": "Phase 3 Dev Space",
        "color": "#4f46e5"
    })
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # Refresh current user's active workspace by switching
    switch_res = client.post(f"/api/v1/workspaces/{ws_id}/switch", headers=headers)
    assert switch_res.status_code == 200

    return headers, ws_id


def test_code_planning_and_pipelines(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Execute Code Planning Pipeline
    req_payload = {
        "target_name": "AI ProductOS Billing",
        "prompt": "Create stripe charging hooks and billing history views.",
        "options": {"requirements": "Support charge.succeeded and customer.subscription.deleted"}
    }
    res = client.post(
        f"/api/v1/development/pipelines/execute?workspace_id={ws_id}&pipeline_type=plan",
        headers=headers,
        json=req_payload
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "plan_id" in data["outputs"]
    assert len(data["outputs"]["steps"]) > 0

    # 2. Retrieve plans
    plans_res = client.get(f"/api/v1/development/plans?workspace_id={ws_id}", headers=headers)
    assert plans_res.status_code == 200
    assert len(plans_res.json()) >= 1

    # 3. Execute PRD generation pipeline
    prd_res = client.post(
        f"/api/v1/development/pipelines/execute?workspace_id={ws_id}&pipeline_type=prd",
        headers=headers,
        json=req_payload
    )
    assert prd_res.status_code == 200
    assert prd_res.json()["success"] is True
    assert "PRD" in prd_res.json()["outputs"]["file_path"]


def test_quality_scans_and_reviews(client: TestClient, auth_headers):
    headers, ws_id = auth_headers
    file_path = "backend/app/controllers/billing.py"
    code = (
        "def charge_customer(amount):\n"
        "    if amount <= 0:\n"
        "        raise ValueError('Invalid amount')\n"
        "    print('Charging amount:', amount)\n"
        "    return True\n"
    )

    # 1. Run quality review
    review_res = client.post(
        "/api/v1/development/quality/review",
        params={"workspace_id": ws_id, "file_path": file_path, "code_content": code},
        headers=headers
    )
    assert review_res.status_code == 200
    review_data = review_res.json()
    assert review_data["score"] > 0
    assert len(review_data["comments"]) >= 0

    # 2. Run quality scan
    scan_res = client.post(
        "/api/v1/development/quality/scan",
        params={"workspace_id": ws_id, "file_path": file_path, "code_content": code},
        headers=headers
    )
    assert scan_res.status_code == 200
    assert scan_res.json()["complexity_score"] > 0

    # 3. Run bug detection
    bug_res = client.post(
        "/api/v1/development/quality/bugs",
        params={"workspace_id": ws_id, "file_path": file_path, "code_content": code},
        headers=headers
    )
    assert bug_res.status_code == 200
    assert "Bug" in bug_res.json()["title"]


def test_git_workflow_simulation(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Create branch
    branch_res = client.post(
        f"/api/v1/development/git/branch?workspace_id={ws_id}",
        headers=headers,
        json={"branch_name": "feature/stripe-billing", "source_branch": "main"}
    )
    if branch_res.status_code != 200:
        print("BRANCH RES FAILED DETAILS:", branch_res.json())
    assert branch_res.status_code == 200
    branch_id = branch_res.json()["id"]

    # 2. Commit changes
    commit_res = client.post(
        f"/api/v1/development/git/commit?workspace_id={ws_id}",
        headers=headers,
        json={
            "branch_id": branch_id,
            "commit_message": "feat: wire Stripe Webhook handler endpoints",
            "files_changed": ["backend/app/controllers/billing.py"]
        }
    )
    assert commit_res.status_code == 200
    assert "commit_hash" in commit_res.json()

    # 3. Create pull request
    pr_res = client.post(
        f"/api/v1/development/git/pr?workspace_id={ws_id}",
        headers=headers,
        json={
            "title": "Integrate Stripe Billing API hooks",
            "description": "Sets up subscription models and webhooks logic.",
            "source_branch": "feature/stripe-billing",
            "target_branch": "main"
        }
    )
    assert pr_res.status_code == 200
    pr_id = pr_res.json()["id"]
    assert pr_res.json()["merge_recommendation"] in ["Ready", "Conflicts", "ReviewRequired"]

    # 4. Merge pull request
    merge_res = client.post(
        f"/api/v1/development/git/pr/{pr_id}/merge?workspace_id={ws_id}",
        headers=headers
    )
    assert merge_res.status_code == 200
    assert merge_res.json()["status"] == "Merged"


def test_development_management_and_analytics(client: TestClient, auth_headers):
    headers, ws_id = auth_headers

    # 1. Create Release plan
    release_res = client.post(
        f"/api/v1/development/releases?workspace_id={ws_id}",
        headers=headers,
        json={
            "version": "v1.2.0",
            "name": "Stripe Integration Launch",
            "description": "Billing module complete",
            "scope": []
        }
    )
    assert release_res.status_code == 200
    release_id = release_res.json()["id"]

    # 2. Deploy Release plan
    deploy_res = client.post(
        f"/api/v1/development/releases/deploy?workspace_id={ws_id}",
        headers=headers,
        json={
            "release_id": release_id,
            "environment": "Production",
            "provider": "AWS ECS"
        }
    )
    assert deploy_res.status_code == 200
    assert deploy_res.json()["status"] == "Ready"

    # 3. Sprint update
    sprint_res = client.post(
        f"/api/v1/development/sprints/update?workspace_id={ws_id}",
        headers=headers,
        json={
            "sprint_name": "Sprint 4 - Payment Integration",
            "progress_summary": "Active implementation of subscription billing plans."
        }
    )
    assert sprint_res.status_code == 200
    assert sprint_res.json()["sprint_name"] == "Sprint 4 - Payment Integration"

    # 4. Development Analytics Dashboard query
    analytics_res = client.get(f"/api/v1/development/analytics?workspace_id={ws_id}", headers=headers)
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert data["commits_count"] >= 0
    assert data["quality_score_avg"] > 0
