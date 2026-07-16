from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    filename: str
    file_size: int
    checksum: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: str = Field("General", max_length=100)
    tags: list[str] = Field(default_factory=list)
    status: str = Field("Draft", max_length=50)
    is_editable: bool = Field(False)


class DocumentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    project_id: UUID | None = None
    category: str = Field("General", max_length=100)
    tags: list[str] = Field(default_factory=list)
    status: str = Field("Draft", max_length=50)
    is_editable: bool = False


class DocumentUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    project_id: UUID | None = None
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    status: str | None = Field(None, max_length=50)
    archived: bool | None = None
    is_editable: bool | None = None


class DocumentResponse(DocumentBase):
    id: UUID
    workspace_id: UUID
    project_id: UUID | None
    filename: str
    mime_type: str
    file_size: int
    checksum: str | None
    current_version_number: int
    archived: bool
    created_at: datetime
    updated_at: datetime
    versions_list: list[DocumentVersionResponse] = []

    class Config:
        from_attributes = True
