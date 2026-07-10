from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_organization_permission,
)
from app.core.permissions import Permission
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.organization import org_repo
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)

router = APIRouter()


@router.post(
    "/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED
)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Organization:
    """
    Create a new organization, check unique slug, assign creator as Owner,
    and provision one default workspace automatically.
    """
    # Check duplicate slug
    existing = org_repo.get_by_slug(db, slug=org_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this slug already exists.",
        )

    db_org = Organization(
        name=org_in.name,
        slug=org_in.slug,
        description=org_in.description,
        logo=org_in.logo,
        owner_id=current_user.id,
        plan="free",
        status="active",
    )
    db.add(db_org)
    db.flush()

    # Automatically create a default Workspace
    db_workspace = Workspace(
        organization_id=db_org.id,
        name="General Workspace",
        description="Default workspace created automatically.",
        icon="layout",
        color="#6366f1",
        visibility="private",
        archived=False,
    )
    db.add(db_workspace)
    db.flush()

    # Map membership as Owner
    db_membership = Membership(
        user_id=current_user.id,
        workspace_id=db_workspace.id,
        role="Owner",
    )
    db.add(db_membership)
    db.commit()
    db.refresh(db_org)

    return db_org


@router.get("/", response_model=list[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Organization]:
    """
    List all organizations owned by the user or where the user is a workspace member.
    """
    owned = (
        db.query(Organization)
        .filter(
            Organization.owner_id == current_user.id,
            Organization.deleted_at.is_(None),
        )
        .all()
    )

    joined = (
        db.query(Organization)
        .join(Workspace)
        .join(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Organization.owner_id != current_user.id,
            Organization.deleted_at.is_(None),
            Membership.deleted_at.is_(None),
        )
        .all()
    )

    return list(set(owned + joined))


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    org: Organization = Depends(require_organization_permission(Permission.ORG_READ)),
) -> Organization:
    """
    Get organization details by primary key ID.
    """
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: UUID,
    org_in: OrganizationUpdate,
    db: Session = Depends(get_db),
    org: Organization = Depends(require_organization_permission(Permission.ORG_WRITE)),
) -> Organization:
    """
    Update organization parameters.
    """
    if org_in.slug and org_in.slug != org.slug:
        existing = org_repo.get_by_slug(db, slug=org_in.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An organization with this slug already exists.",
            )

    updated_org = org_repo.update(db, db_obj=org, obj_in=org_in)
    return updated_org


@router.delete("/{org_id}", response_model=OrganizationResponse)
def delete_organization(
    org_id: UUID,
    db: Session = Depends(get_db),
    org: Organization = Depends(require_organization_permission(Permission.ORG_DELETE)),
) -> Organization:
    """
    Soft delete an organization.
    """
    soft_deleted = org_repo.soft_remove(db, id=org_id)
    if not soft_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return soft_deleted
