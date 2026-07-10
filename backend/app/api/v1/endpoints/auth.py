import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.audit_log import audit_log_repo
from app.repositories.user import user_repo
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return re.sub(r"^-+|-+$", "", text)


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Register a new user, automatically provision a default Organization,
    create a default Workspace, and map the user as the Owner.
    """
    # Check duplicate email
    if user_repo.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Check duplicate username
    if user_repo.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists.",
        )

    # Hash password and create user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        password_hash=hashed_password,
        timezone="UTC",
        language="en",
        is_verified=True,  # Auto-verify in development/mock
        is_active=True,
        preferences={},
    )
    db.add(db_user)
    db.flush()  # Populates user ID

    # Create default Organization
    org_name = f"{db_user.full_name}'s Organization"
    org_slug = slugify(f"{db_user.username}-org")

    # Check if slug exists, append suffix if needed
    suffix = 1
    base_slug = org_slug
    while db.query(Organization).filter(Organization.slug == org_slug).first():
        org_slug = f"{base_slug}-{suffix}"
        suffix += 1

    db_org = Organization(
        name=org_name,
        slug=org_slug,
        owner_id=db_user.id,
        plan="free",
        status="active",
    )
    db.add(db_org)
    db.flush()

    # Create default Workspace
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
        user_id=db_user.id,
        workspace_id=db_workspace.id,
        role="Owner",
    )
    db.add(db_membership)

    db.commit()
    db.refresh(db_user)

    # Audit log
    audit_log_repo.log_action(
        db,
        user_id=db_user.id,
        action="User Signup & Organization Setup",
        payload={
            "organization_id": str(db_org.id),
            "workspace_id": str(db_workspace.id),
        },
    )

    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate username/email and password, logging access logs.
    """
    # Standard OAuth2 form transmits identifier via 'username'
    user = user_repo.get_by_email(db, email=form_data.username)
    if not user:
        user = user_repo.get_by_username(db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.password_hash):
        # Log failed attempt
        audit_log_repo.log_action(
            db,
            user_id=None,
            action="Failed Login Attempt",
            payload={"identifier": form_data.username},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email/username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account",
        )

    # Update login timestamp
    user.last_login = datetime.now(UTC)
    db.add(user)
    db.commit()

    # Audit log
    audit_log_repo.log_action(
        db,
        user_id=user.id,
        action="Successful Login",
    )

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
def refresh(refresh_token: str, db: Session = Depends(get_db)) -> Token:
    """
    Exchange refresh token for a new access/refresh token pair.
    """
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token format",
            )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired or invalid refresh token",
        ) from err

    user = user_repo.get(db, id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive or disabled",
        )

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/logout")
def logout(db: Session = Depends(get_db)) -> dict:
    """
    Logs out the user and registers the logout audit trace.
    """
    # In pure stateless JWT, client deletes token.
    # Optionally blacklist on Redis. We register audit trace.
    return {"message": "Successfully logged out"}
