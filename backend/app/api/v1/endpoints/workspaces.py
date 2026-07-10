from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission, role_has_permission
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace import workspace_repo
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    org_id: UUID,
    workspace_in: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Workspace:
    """
    Create a workspace inside an organization. Creator must have
    workspace write permissions in that organization.
    """
    # Verify organization exists
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

    # Authorization Check
    is_owner = org.owner_id == current_user.id
    has_admin_membership = False
    if not is_owner:
        # Check if they are Admin in any workspace of this organization
        membership = (
            db.query(Membership)
            .join(Workspace)
            .filter(
                Membership.user_id == current_user.id,
                Workspace.organization_id == org_id,
                Membership.deleted_at.is_(None),
            )
            .first()
        )
        if membership and role_has_permission(
            membership.role, Permission.WORKSPACE_WRITE
        ):
            has_admin_membership = True

    if not is_owner and not has_admin_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create workspace in this organization",
        )

    db_workspace = Workspace(
        organization_id=org_id,
        name=workspace_in.name,
        description=workspace_in.description,
        icon=workspace_in.icon,
        color=workspace_in.color,
        visibility=workspace_in.visibility,
        archived=False,
    )
    db.add(db_workspace)
    db.flush()

    # Map creator as Owner of this workspace
    db_membership = Membership(
        user_id=current_user.id,
        workspace_id=db_workspace.id,
        role="Owner",
    )
    db.add(db_membership)
    db.commit()
    db.refresh(db_workspace)

    return db_workspace


@router.get("/organization/{org_id}", response_model=list[WorkspaceResponse])
def list_workspaces(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Workspace]:
    """
    List workspaces in an organization where the user has memberships.
    """
    # Verify membership or ownership of the organization
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

    if org.owner_id == current_user.id:
        return (
            db.query(Workspace)
            .filter(Workspace.organization_id == org_id, Workspace.deleted_at.is_(None))
            .all()
        )

    workspaces = (
        db.query(Workspace)
        .join(Membership)
        .filter(
            Workspace.organization_id == org_id,
            Membership.user_id == current_user.id,
            Workspace.deleted_at.is_(None),
            Membership.deleted_at.is_(None),
        )
        .all()
    )
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> Workspace:
    """
    Get workspace details.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: UUID,
    workspace_in: WorkspaceUpdate,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Workspace:
    """
    Rename or edit workspace details.
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    updated_workspace = workspace_repo.update(db, db_obj=workspace, obj_in=workspace_in)
    return updated_workspace


@router.delete("/{workspace_id}", response_model=WorkspaceResponse)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_DELETE)
    ),
) -> Workspace:
    """
    Soft delete a workspace.
    """
    soft_deleted = workspace_repo.soft_remove(db, id=workspace_id)
    if not soft_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return soft_deleted


@router.post("/{workspace_id}/switch")
def switch_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Switch active workspace, persisting the active workspace ID in user preferences.
    """
    # Verify membership
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == workspace_id,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    # Persist active workspace in preferences JSON
    updated_prefs = {
        **current_user.preferences,
        "active_workspace_id": str(workspace_id),
    }
    current_user.preferences = updated_prefs
    db.add(current_user)
    db.commit()

    return {
        "message": "Switched active workspace successfully",
        "active_workspace_id": str(workspace_id),
    }
