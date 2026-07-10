from uuid import UUID

from app.models.organization import Organization
from app.models.user import User


def test_organization_crud(client, db):
    """
    Test creating, listing, updating, and deleting organizations.
    """
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "orgtest@example.com",
            "username": "orguser",
            "full_name": "Org User",
            "password": "securepassword123",
        },
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "orgtest@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Org
    create_payload = {
        "name": "New Ventures Corp",
        "slug": "new-ventures",
        "description": "Tech startups incubator",
        "logo": "logo.png",
    }
    create_res = client.post(
        "/api/v1/organizations/", json=create_payload, headers=headers
    )
    assert create_res.status_code == 201
    org_data = create_res.json()
    assert org_data["name"] == "New Ventures Corp"
    assert org_data["slug"] == "new-ventures"

    # List Orgs
    list_res = client.get("/api/v1/organizations/", headers=headers)
    assert list_res.status_code == 200
    orgs = list_res.json()
    # User owns the signup org + new org = 2 total
    assert len(orgs) == 2

    # Update Org
    update_res = client.put(
        f"/api/v1/organizations/{org_data['id']}",
        json={
            "name": "New Ventures Inc",
        },
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Ventures Inc"

    # Delete Org
    del_res = client.delete(f"/api/v1/organizations/{org_data['id']}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["id"] == org_data["id"]

    # Verify soft deleted in DB
    org = db.query(Organization).filter_by(id=UUID(org_data["id"])).first()
    assert org.deleted_at is not None


def test_workspace_crud_and_listing(client, db):
    """
    Test creating and listing workspaces in organization context.
    """
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "wstest@example.com",
            "username": "wsuser",
            "full_name": "Workspace User",
            "password": "securepassword123",
        },
    )

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wstest@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch User Default Org
    user = db.query(User).filter_by(email="wstest@example.com").first()
    org = db.query(Organization).filter_by(owner_id=user.id).first()

    # Create workspace
    ws_payload = {
        "name": "Engineering Team",
        "description": "Tech stuff workspace",
        "icon": "code",
        "color": "#ff0000",
        "visibility": "private",
    }
    create_res = client.post(
        f"/api/v1/workspaces/?org_id={org.id}", json=ws_payload, headers=headers
    )
    assert create_res.status_code == 201
    ws_data = create_res.json()
    assert ws_data["name"] == "Engineering Team"
    assert ws_data["organization_id"] == str(org.id)

    # List Workspaces
    list_res = client.get(f"/api/v1/workspaces/organization/{org.id}", headers=headers)
    assert list_res.status_code == 200
    workspaces = list_res.json()
    # 1 default + 1 engineering = 2 total
    assert len(workspaces) == 2
