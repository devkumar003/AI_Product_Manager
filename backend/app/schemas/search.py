from pydantic import BaseModel

from app.schemas.document import DocumentResponse
from app.schemas.organization import OrganizationResponse
from app.schemas.project import ProjectResponse
from app.schemas.workspace import WorkspaceResponse


class SearchResultsResponse(BaseModel):
    projects: list[ProjectResponse] = []
    documents: list[DocumentResponse] = []
    workspaces: list[WorkspaceResponse] = []
    organizations: list[OrganizationResponse] = []

    class Config:
        from_attributes = True
