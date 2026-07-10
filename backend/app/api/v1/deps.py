from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.permissions import Permission, role_has_permission
from app.core.security import ALGORITHM
from app.core.settings import settings
from app.database.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.organization import org_repo
from app.repositories.user import user_repo
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, access token required",
            )
    except (jwt.JWTError, ValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from err
    user = user_repo.get(db, id=UUID(token_data.sub))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email not verified",
        )
    return current_user


def require_workspace_permission(permission: Permission):
    """
    Dependency factory to check if the user has a specific permission in the workspace
    referenced by the path parameter 'workspace_id'.
    """

    def dependency(
        workspace_id: UUID = Path(...),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> Membership:
        # Check if workspace exists
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == workspace_id, Workspace.deleted_at.is_(None))
            .first()
        )
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
            )

        # Query user membership
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
                detail="User is not a member of this workspace",
            )

        if not role_has_permission(membership.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions within workspace",
            )
        return membership

    return dependency


def require_organization_permission(permission: Permission):
    """
    Dependency factory to check if the user has a specific permission in the organization
    referenced by the path parameter 'org_id'.
    """

    def dependency(
        org_id: UUID = Path(...),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> Organization:
        org = org_repo.get(db, id=org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        # Owners have absolute access
        if org.owner_id == current_user.id:
            return org

        if permission == Permission.ORG_DELETE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the organization owner can perform this action",
            )

        # Check if user has membership in any workspace of this organization
        memberships = (
            db.query(Membership)
            .join(Workspace)
            .filter(
                Membership.user_id == current_user.id,
                Workspace.organization_id == org_id,
                Membership.deleted_at.is_(None),
            )
            .all()
        )
        if not memberships:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization",
            )

        # Verify role permission
        has_perm = False
        for m in memberships:
            if role_has_permission(m.role, permission):
                has_perm = True
                break

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions within organization",
            )
        return org

    return dependency
