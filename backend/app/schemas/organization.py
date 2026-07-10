from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    logo: str | None = Field(None, max_length=1024)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    logo: str | None = Field(None, max_length=1024)
    status: str | None = Field(None, max_length=50)


class OrganizationResponse(OrganizationBase):
    id: UUID
    owner_id: UUID
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
