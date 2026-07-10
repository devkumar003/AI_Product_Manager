from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    icon: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    visibility: str = Field("private", max_length=50)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    icon: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    visibility: str | None = Field(None, max_length=50)
    archived: bool | None = None


class WorkspaceResponse(WorkspaceBase):
    id: UUID
    organization_id: UUID
    archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MembershipResponse(BaseModel):
    id: UUID
    user_id: UUID
    workspace_id: UUID
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True
