from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace


def test_invitation_lifecycle(client, db):
    """
    Test generating invitation, acceptance validation, and member role assignment.
    """
    # 1. Signup inviter
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "inviter@example.com",
            "username": "inviter",
            "full_name": "Inviter User",
            "password": "securepassword123",
        },
    )

    # Login inviter
    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "inviter@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch Inviter's Org & Workspace
    inviter_user = db.query(User).filter_by(email="inviter@example.com").first()
    org = db.query(Organization).filter_by(owner_id=inviter_user.id).first()
    workspace = db.query(Workspace).filter_by(organization_id=org.id).first()

    # 2. Issue Invitation
    invite_res = client.post(
        f"/api/v1/invitations/?org_id={org.id}",
        json={
            "email": "invitee@example.com",
            "role": "Product Manager",
            "workspace_id": str(workspace.id),
        },
        headers=headers,
    )
    assert invite_res.status_code == 201
    invite_data = invite_res.json()
    invite_token = invite_data["token"]
    assert invite_data["role"] == "Product Manager"
    assert invite_data["status"] == "pending"

    # 3. Accept before signup (should fail)
    accept_fail_res = client.post(f"/api/v1/invitations/{invite_token}/accept")
    assert accept_fail_res.status_code == 400
    assert "Please sign up first" in accept_fail_res.json()["detail"]

    # 4. Signup invitee
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "invitee@example.com",
            "username": "invitee",
            "full_name": "Invitee User",
            "password": "securepassword123",
        },
    )

    # 5. Accept after signup
    accept_success_res = client.post(f"/api/v1/invitations/{invite_token}/accept")
    assert accept_success_res.status_code == 200

    # 6. Verify memberships
    invitee_user = db.query(User).filter_by(email="invitee@example.com").first()
    membership = (
        db.query(Membership)
        .filter_by(user_id=invitee_user.id, workspace_id=workspace.id)
        .first()
    )
    assert membership is not None
    assert membership.role == "Product Manager"

    # Verify invitation marked accepted
    invitation = db.query(Invitation).filter_by(token=invite_token).first()
    assert invitation.status == "accepted"
