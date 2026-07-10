from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=50)
    timezone: str | None = Field(None, max_length=100)
    language: str | None = Field(None, max_length=10)
    avatar_url: str | None = Field(None, max_length=1024)


class UserPreferencesUpdate(BaseModel):
    preferences: dict


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: UUID
    avatar_url: str | None = None
    phone: str | None = None
    timezone: str
    language: str
    is_verified: bool
    is_active: bool
    last_login: datetime | None = None
    preferences: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
