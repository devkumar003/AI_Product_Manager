import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.invitation import invitation_repo
from app.repositories.user import user_repo
from app.schemas.invitation import InvitationCreate, InvitationResponse

router = APIRouter()


@router.post(
    "/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED
)
def create_invitation(
    org_id: UUID,
    invite_in: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Invitation:
    """
    Generate and send a workspace/organization invitation.
    """
    # Verify organization ownership or admin rights
    org = (
        db.query(Organization)
        .filter(Organization.id == org_id, Organization.deleted_at.is_(None))
        .first()
    )
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Creator must be owner of the organization
    if org.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can issue invitations",
        )

    # Verify workspace belongs to organization if provided
    if invite_in.workspace_id:
        workspace = (
            db.query(Workspace)
            .filter(
                Workspace.id == invite_in.workspace_id,
                Workspace.organization_id == org_id,
                Workspace.deleted_at.is_(None),
            )
            .first()
        )
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace does not exist in this organization",
            )

    # Check if duplicate pending invite exists
    existing = invitation_repo.get_by_email_and_org(
        db, email=invite_in.email, org_id=org_id
    )
    if (
        existing
        and existing.status == "pending"
        and existing.expires_at.replace(tzinfo=None)
        > datetime.now(UTC).replace(tzinfo=None)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending invitation already exists for this email address.",
        )

    # Generate secure 32 byte url-safe token
    invite_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=7)  # 7 days validity

    db_invite = Invitation(
        organization_id=org_id,
        workspace_id=invite_in.workspace_id,
        email=invite_in.email,
        role=invite_in.role,
        token=invite_token,
        status="pending",
        expires_at=expires_at,
        invited_by=current_user.id,
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)

    # Note: Email transmission service interface would be called here
    return db_invite


@router.get("/{token}", response_model=InvitationResponse)
def get_invitation_details(token: str, db: Session = Depends(get_db)) -> Invitation:
    """
    Fetch details of an invitation by secure token.
    """
    invite = invitation_repo.get_by_token(db, token=token)
    if not invite or invite.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired.",
        )
    return invite


@router.post("/{token}/accept")
def accept_invitation(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Accept an invitation using its secure token. The accepting user's email
    must match the invitation email and they must be registered.
    """
    invite = invitation_repo.get_by_token(db, token=token)
    if not invite or invite.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is invalid or has already been processed.",
        )

    if invite.expires_at.replace(tzinfo=None) < datetime.now(UTC).replace(tzinfo=None):
        invite.status = "expired"
        db.add(invite)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation has expired.",
        )

    # Check if user is registered
    user = user_repo.get_by_email(db, email=invite.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No registered user matches the invitation email. Please sign up first.",
        )

    # Determine workspace membership mapping
    # If a specific workspace was invited to:
    workspaces_to_join = []
    if invite.workspace_id:
        workspaces_to_join.append(invite.workspace_id)
    else:
        # Join all public workspaces or default workspace of the organization
        default_ws = (
            db.query(Workspace)
            .filter(
                Workspace.organization_id == invite.organization_id,
                Workspace.deleted_at.is_(None),
            )
            .first()
        )
        if default_ws:
            workspaces_to_join.append(default_ws.id)

    # Create memberships
    for ws_id in workspaces_to_join:
        # Check if already a member
        existing_member = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.workspace_id == ws_id,
                Membership.deleted_at.is_(None),
            )
            .first()
        )
        if not existing_member:
            db_membership = Membership(
                user_id=user.id,
                workspace_id=ws_id,
                role=invite.role,
                invited_by=invite.invited_by,
            )
            db.add(db_membership)

    # Mark invitation as accepted
    invite.status = "accepted"
    db.add(invite)
    db.commit()

    return {"message": "Invitation accepted successfully. Memberships provisioned."}


@router.post("/{token}/reject")
def reject_invitation(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Reject an invitation, marking its status as rejected.
    """
    invite = invitation_repo.get_by_token(db, token=token)
    if not invite or invite.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is invalid or has already been processed.",
        )

    invite.status = "rejected"
    db.add(invite)
    db.commit()

    return {"message": "Invitation rejected."}
