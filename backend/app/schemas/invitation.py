from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field("Viewer", max_length=50)
    workspace_id: UUID | None = None


class InvitationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    workspace_id: UUID | None
    email: EmailStr
    role: str
    token: str
    status: str
    expires_at: datetime
    invited_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
