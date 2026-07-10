from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    action: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID | None = None
    description: str = Field(..., max_length=1024)
    metadata_json: dict = Field(default_factory=dict)


class ActivityCreate(ActivityBase):
    workspace_id: UUID | None = None
    user_id: UUID


class ActivityResponse(ActivityBase):
    id: UUID
    workspace_id: UUID | None
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
