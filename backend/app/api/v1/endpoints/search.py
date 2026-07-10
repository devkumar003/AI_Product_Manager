from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.document import Document
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.search import SearchResultsResponse

router = APIRouter()


@router.get("/", response_model=SearchResultsResponse)
def search_workspace(
    q: str,
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Search workspace projects, documents, workspaces, and organizations based on string query 'q'.
    """
    if not q or len(q.strip()) < 2:
        return {"projects": [], "documents": [], "workspaces": [], "organizations": []}

    # Verify workspace membership
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == current_user.id,
            Membership.workspace_id == workspace_id,
            Membership.deleted_at.is_(None),
        )
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace",
        )

    # 1. Fetch current workspace details to check organization_id
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    org_id = workspace.organization_id

    # 2. Search projects in workspace
    search_filt = f"%{q}%"
    projects = (
        db.query(Project)
        .filter(
            Project.workspace_id == workspace_id,
            Project.deleted_at.is_(None),
            or_(
                Project.name.ilike(search_filt),
                Project.description.ilike(search_filt),
            ),
        )
        .limit(20)
        .all()
    )

    # 3. Search documents in workspace
    documents = (
        db.query(Document)
        .filter(
            Document.workspace_id == workspace_id,
            Document.deleted_at.is_(None),
            or_(
                Document.name.ilike(search_filt),
                Document.category.ilike(search_filt),
            ),
        )
        .limit(20)
        .all()
    )

    # 4. Search workspaces in organization
    workspaces = (
        db.query(Workspace)
        .join(Membership)
        .filter(
            Workspace.organization_id == org_id,
            Membership.user_id == current_user.id,
            Workspace.deleted_at.is_(None),
            Membership.deleted_at.is_(None),
            Workspace.name.ilike(search_filt),
        )
        .limit(20)
        .all()
    )

    # 5. Search organizations user belongs to
    organizations = (
        db.query(Organization)
        .filter(
            Organization.deleted_at.is_(None),
            Organization.owner_id == current_user.id,
            Organization.name.ilike(search_filt),
        )
        .limit(20)
        .all()
    )

    return {
        "projects": projects,
        "documents": documents,
        "workspaces": workspaces,
        "organizations": organizations,
    }
