import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission
from app.models.membership import Membership
from app.models.project import Project
from app.models.user import User
from app.repositories.activity import activity_repo
from app.repositories.project import project_repo
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post(
    "/{workspace_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    workspace_id: UUID,
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Project:
    # 1. Check slug uniqueness in workspace
    slug = project_in.slug
    if not slug:
        slug = project_in.name.lower().replace(" ", "-").replace("/", "-")
        # sanitize
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

    existing = project_repo.get_by_slug(db, workspace_id=workspace_id, slug=slug)
    if existing:
        # Append unique prefix/suffix to slug
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    db_obj = Project(
        workspace_id=workspace_id,
        name=project_in.name,
        description=project_in.description,
        slug=slug,
        icon=project_in.icon,
        color=project_in.color,
        status=project_in.status,
        priority=project_in.priority,
        owner_id=project_in.owner_id or current_user.id,
        archived=False,
    )
    project_repo.create(db, obj_in=db_obj)

    # 2. Log activity timeline
    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_created",
        entity_type="project",
        entity_id=db_obj.id,
        description=f"Created project '{db_obj.name}' in workspace.",
    )

    return db_obj


@router.get("/{workspace_id}", response_model=list[ProjectResponse])
def list_projects(
    workspace_id: UUID,
    search: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> list[Project]:
    return project_repo.get_multi_by_workspace(
        db,
        workspace_id=workspace_id,
        search=search,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit,
    )


@router.get("/{workspace_id}/{project_id}", response_model=ProjectResponse)
def get_project(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> Project:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )
    return project


@router.put("/{workspace_id}/{project_id}", response_model=ProjectResponse)
def update_project(
    workspace_id: UUID,
    project_id: UUID,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Project:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    # If slug is changing, verify unique slug
    if project_in.slug and project_in.slug != project.slug:
        existing = project_repo.get_by_slug(
            db, workspace_id=workspace_id, slug=project_in.slug
        )
        if existing and existing.id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project slug is already taken in this workspace",
            )

    updated = project_repo.update(db, db_obj=project, obj_in=project_in)

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_updated",
        entity_type="project",
        entity_id=project.id,
        description=f"Updated project '{project.name}' details.",
    )
    return updated


@router.delete("/{workspace_id}/{project_id}", response_model=ProjectResponse)
def delete_project(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_DELETE)
    ),
) -> Project:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    soft_deleted = project_repo.soft_remove(db, id=project_id)
    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_deleted",
        entity_type="project",
        entity_id=project_id,
        description=f"Soft deleted project '{project.name}'.",
    )
    return soft_deleted


@router.post("/{workspace_id}/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Project:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    project.archived = True
    project.status = "Archived"
    db.add(project)
    db.commit()
    db.refresh(project)

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_archived",
        entity_type="project",
        entity_id=project_id,
        description=f"Archived project '{project.name}'.",
    )
    return project


@router.post("/{workspace_id}/{project_id}/restore", response_model=ProjectResponse)
def restore_project(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.workspace_id == workspace_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    project.archived = False
    project.deleted_at = None
    project.status = "Planning"
    db.add(project)
    db.commit()
    db.refresh(project)

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_restored",
        entity_type="project",
        entity_id=project_id,
        description=f"Restored project '{project.name}'.",
    )
    return project


@router.post("/{workspace_id}/{project_id}/duplicate", response_model=ProjectResponse)
def duplicate_project(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Project:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    duplicated = project_repo.duplicate(
        db, project_id=project_id, owner_id=current_user.id
    )
    if not duplicated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not duplicate project",
        )

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="project_duplicated",
        entity_type="project",
        entity_id=duplicated.id,
        description=f"Duplicated project '{project.name}' as '{duplicated.name}'.",
    )
    return duplicated


@router.get("/{workspace_id}/{project_id}/dashboard", status_code=status.HTTP_200_OK)
def get_project_dashboard(
    workspace_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> dict:
    project = project_repo.get(db, project_id)
    if not project or project.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this workspace",
        )

    # 1. Fetch recent activity related to project
    from app.models.activity import Activity

    activities = (
        db.query(Activity)
        .filter(
            Activity.workspace_id == workspace_id,
            Activity.entity_type == "project",
            Activity.entity_id == project_id,
        )
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    # 2. Fetch documents linked to project
    from app.models.document import Document

    documents = (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.deleted_at.is_(None))
        .order_by(Document.updated_at.desc())
        .limit(10)
        .all()
    )

    # 3. Calculate statistics
    total_docs = len(documents)
    total_bytes = sum(doc.file_size for doc in documents)

    return {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "priority": project.priority,
            "color": project.color,
            "icon": project.icon,
            "archived": project.archived,
        },
        "recent_activity": [
            {
                "id": str(act.id),
                "action": act.action,
                "description": act.description,
                "created_at": act.created_at,
            }
            for act in activities
        ],
        "recent_documents": [
            {
                "id": str(doc.id),
                "name": doc.name,
                "category": doc.category,
                "file_size": doc.file_size,
                "updated_at": doc.updated_at,
            }
            for doc in documents
        ],
        "stats": {
            "document_count": total_docs,
            "storage_used_bytes": total_bytes,
        },
    }
