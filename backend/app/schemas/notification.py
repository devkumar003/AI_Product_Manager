from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    type: str = Field("Info", max_length=50)
    title: str = Field(..., max_length=255)
    message: str = Field(..., max_length=1024)
    metadata_json: dict = Field(default_factory=dict)


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationUpdate(BaseModel):
    read: bool | None = None
    archived: bool | None = None
    deleted: bool | None = None


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    read: bool
    archived: bool
    deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
