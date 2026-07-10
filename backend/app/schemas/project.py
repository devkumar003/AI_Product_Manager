from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=1024)
    slug: str = Field(..., min_length=2, max_length=255)
    icon: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    status: str = Field("Planning", max_length=50)
    priority: str = Field("Medium", max_length=50)
    owner_id: UUID | None = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(None, max_length=1024)
    slug: str | None = Field(None, min_length=2, max_length=255)
    icon: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    status: str = Field("Planning", max_length=50)
    priority: str = Field("Medium", max_length=50)
    owner_id: UUID | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, max_length=1024)
    slug: str | None = Field(None, min_length=2, max_length=255)
    icon: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)
    priority: str | None = Field(None, max_length=50)
    owner_id: UUID | None = None
    archived: bool | None = None


class ProjectResponse(ProjectBase):
    id: UUID
    workspace_id: UUID
    archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
