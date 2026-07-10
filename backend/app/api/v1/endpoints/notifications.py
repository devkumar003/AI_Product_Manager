from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.notification import Notification
from app.repositories.notification import notification_repo
from app.schemas.notification import NotificationResponse, NotificationUpdate

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    include_archived: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Notification]:
    return notification_repo.get_multi_by_user(
        db,
        user_id=current_user.id,
        unread_only=unread_only,
        include_archived=include_archived,
        skip=skip,
        limit=limit,
    )


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    count = notification_repo.mark_all_read(db, user_id=current_user.id)
    return {"message": f"Successfully marked {count} notifications as read"}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Notification:
    notification = notification_repo.get(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/{notification_id}/archive", response_model=NotificationResponse)
def archive_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Notification:
    notification = notification_repo.get(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.archived = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}", response_model=NotificationResponse)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Notification:
    notification = notification_repo.get(db, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.deleted = True
    db_obj = notification_repo.soft_remove(db, id=notification_id)
    return db_obj
