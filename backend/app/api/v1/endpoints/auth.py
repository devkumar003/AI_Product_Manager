import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.settings import settings
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
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticate username/email and password, setting HttpOnly cookies.
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

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    import secrets
    csrf_token = secrets.token_hex(32)
    response.set_cookie(
        key="XSRF-TOKEN",
        value=csrf_token,
        httponly=False,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
def refresh(
    response: Response,
    request: Request,
    refresh_token: str | None = None,
    db: Session = Depends(get_db)
) -> Token:
    """
    Exchange refresh token for a new access/refresh token pair.
    Supports token from request body/query or cookies.
    """
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
        )

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

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    # Update cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Revoke the current access token by blacklisting it in Redis and clearing cookies.
    """
    from app.core.redis import cache_manager

    token = request.cookies.get("access_token")
    if not token:
        # Fallback to Authorization Header
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]

    if token:
        try:
            payload = decode_token(token)
            # Use token's expiry to calculate remaining TTL for blacklist entry
            exp = payload.get("exp", 0)
            import time
            remaining_ttl = max(int(exp - time.time()), 0)
            if remaining_ttl > 0:
                # Blacklist using the token's sub + exp as a unique key
                blacklist_key = f"token_blacklist:{payload.get('sub')}:{exp}"
                await cache_manager.set(blacklist_key, "revoked", expire_seconds=remaining_ttl)
        except Exception:
            pass  # Token is already invalid/expired

    # Clear HttpOnly and CSRF cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("XSRF-TOKEN")

    # Audit log
    audit_log_repo.log_action(
        db,
        user_id=None,
        action="User Logout",
    )

    return {"message": "Successfully logged out"}
