from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission
from app.models.activity import Activity
from app.models.membership import Membership
from app.repositories.activity import activity_repo
from app.schemas.activity import ActivityResponse

router = APIRouter()


@router.get("/{workspace_id}", response_model=list[ActivityResponse])
def list_workspace_activities(
    workspace_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> list[Activity]:
    return activity_repo.get_multi_by_workspace(
        db,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
    )
