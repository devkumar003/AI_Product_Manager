from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import user_repo
from app.schemas.user import (
    UserPasswordUpdate,
    UserPreferencesUpdate,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get profile details of the current authenticated user.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Update profile details (first name, last name, phone, language, timezone).
    """
    updated_user = user_repo.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user


@router.patch("/me/preferences", response_model=UserResponse)
def update_preferences_me(
    preferences_in: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Update json preference object properties.
    """
    # Merge existing preferences
    updated_prefs = {**current_user.preferences, **preferences_in.preferences}
    updated_user = user_repo.update(
        db, db_obj=current_user, obj_in={"preferences": updated_prefs}
    )
    return updated_user


@router.patch("/me/avatar", response_model=UserResponse)
def update_avatar_me(
    avatar_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Directly update user avatar url string.
    """
    updated_user = user_repo.update(
        db, db_obj=current_user, obj_in={"avatar_url": avatar_url}
    )
    return updated_user


@router.patch("/me/password")
def update_password_me(
    password_in: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Update user password, verifying matching old credentials value first.
    """
    if not verify_password(password_in.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password.",
        )
    hashed_new = get_password_hash(password_in.new_password)
    user_repo.update(db, db_obj=current_user, obj_in={"password_hash": hashed_new})
    return {"message": "Password updated successfully."}
