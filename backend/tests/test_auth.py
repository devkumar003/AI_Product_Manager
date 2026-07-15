from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace


def test_signup_success(client, db):
    """
    Test that signup provisions user, organization, workspace, and owner role.
    """
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "securepassword123",
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data

    # Verify db state
    user = db.query(User).filter_by(email="test@example.com").first()
    assert user is not None

    org = db.query(Organization).filter_by(owner_id=user.id).first()
    assert org is not None
    assert org.name == "Test User's Organization"

    workspace = db.query(Workspace).filter_by(organization_id=org.id).first()
    assert workspace is not None
    assert workspace.name == "General Workspace"

    membership = (
        db.query(Membership)
        .filter_by(user_id=user.id, workspace_id=workspace.id)
        .first()
    )
    assert membership is not None
    assert membership.role == "Owner"


def test_signup_duplicate(client):
    """
    Test duplicate signup fields validation.
    """
    payload = {
        "email": "dup@example.com",
        "username": "dupuser",
        "full_name": "Duplicate User",
        "password": "securepassword123",
    }
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    # Duplicate email
    res2 = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "dup@example.com",
            "username": "dupuser2",
            "full_name": "Duplicate User 2",
            "password": "securepassword123",
        },
    )
    assert res2.status_code == 400

    # Duplicate username
    res3 = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "dup3@example.com",
            "username": "dupuser",
            "full_name": "Duplicate User 3",
            "password": "securepassword123",
        },
    )
    assert res3.status_code == 400


def test_login_success(client):
    """
    Test user authentication login.
    """
    signup_payload = {
        "email": "login@example.com",
        "username": "loginuser",
        "full_name": "Login User",
        "password": "securepassword123",
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    # Login
    login_data = {
        "username": "login@example.com",
        "password": "securepassword123",
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_profile_and_workspace_switch(client, db):
    """
    Test reading user profile, updating, and switching workspace context.
    """
    signup_payload = {
        "email": "profile@example.com",
        "username": "profileuser",
        "full_name": "Profile User",
        "password": "securepassword123",
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "profile@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch profile
    profile_res = client.get("/api/v1/users/me", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "profile@example.com"

    # Get user default workspace
    user = db.query(User).filter_by(email="profile@example.com").first()
    org = db.query(Organization).filter_by(owner_id=user.id).first()
    workspace = db.query(Workspace).filter_by(organization_id=org.id).first()

    # Switch workspace
    switch_res = client.post(
        f"/api/v1/workspaces/{workspace.id}/switch", headers=headers
    )
    assert switch_res.status_code == 200
    assert switch_res.json()["active_workspace_id"] == str(workspace.id)

    # Re-verify profile active workspace
    profile_res2 = client.get("/api/v1/users/me", headers=headers)
    assert profile_res2.json()["preferences"]["active_workspace_id"] == str(
        workspace.id
    )


def test_cookie_and_csrf_auth(client, db):
    """
    Test HttpOnly cookies authentication and CSRF token protection.
    """
    signup_payload = {
        "email": "cookie_test@example.com",
        "username": "cookieuser",
        "full_name": "Cookie User",
        "password": "securepassword123",
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    # 1. Login to get cookies
    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "cookie_test@example.com",
            "password": "securepassword123",
        },
    )
    assert login_res.status_code == 200
    
    # Verify cookies are set in the response
    assert "access_token" in login_res.cookies
    assert "refresh_token" in login_res.cookies
    assert "XSRF-TOKEN" in login_res.cookies

    # Clear current client credentials from headers to force using cookies
    if "Authorization" in client.headers:
        del client.headers["Authorization"]

    # 2. Access protected GET route using cookies (should succeed without CSRF check since it's GET)
    profile_res = client.get("/api/v1/users/me")
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "cookie_test@example.com"

    # Get user default workspace
    user = db.query(User).filter_by(email="cookie_test@example.com").first()
    org = db.query(Organization).filter_by(owner_id=user.id).first()
    workspace = db.query(Workspace).filter_by(organization_id=org.id).first()

    # 3. Access protected POST route (workspace switch) using cookies WITHOUT CSRF (should fail with 403)
    switch_res = client.post(f"/api/v1/workspaces/{workspace.id}/switch")
    assert switch_res.status_code == 403
    assert "CSRF token validation failed" in switch_res.json()["detail"]

    # 4. Access protected POST route with WRONG CSRF token (should fail with 403)
    bad_headers = {"X-XSRF-TOKEN": "wrong-token-value"}
    switch_res = client.post(
        f"/api/v1/workspaces/{workspace.id}/switch",
        headers=bad_headers
    )
    assert switch_res.status_code == 403

    # 5. Access protected POST route with CORRECT CSRF token (should succeed)
    csrf_token = login_res.cookies["XSRF-TOKEN"]
    good_headers = {"X-XSRF-TOKEN": csrf_token}
    switch_res = client.post(
        f"/api/v1/workspaces/{workspace.id}/switch",
        headers=good_headers
    )
    assert switch_res.status_code == 200
    assert switch_res.json()["active_workspace_id"] == str(workspace.id)

