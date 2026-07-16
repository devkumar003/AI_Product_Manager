import io
import json
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import (
    get_current_active_user,
    get_db,
    require_workspace_permission,
)
from app.core.permissions import Permission
from app.models.document import Document
from app.models.membership import Membership
from app.models.user import User
from app.repositories.activity import activity_repo
from app.repositories.document import document_repo
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.storage import storage_service

router = APIRouter()


@router.post(
    "/{workspace_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    workspace_id: UUID,
    file: UploadFile = File(...),
    name: str = Form(...),
    project_id: str | None = Form(None),
    category: str = Form("General"),
    tags_json: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Document:
    # 1. Parse tags and project_id UUID
    try:
        tags = json.loads(tags_json)
        if not isinstance(tags, list):
            tags = []
    except Exception:
        tags = [t.strip() for t in tags_json.split(",") if t.strip()]

    proj_uuid = None
    if project_id and project_id != "null" and project_id.strip():
        try:
            proj_uuid = UUID(project_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid project_id UUID format",
            )

    # 2. Read bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file",
        )

    # 3. Create document record and save file
    db_doc = document_repo.create_with_file(
        db,
        workspace_id=workspace_id,
        project_id=proj_uuid,
        name=name,
        file_bytes=file_bytes,
        mime_type=file.content_type or "application/octet-stream",
        category=category,
        tags=tags,
        created_by_id=current_user.id,
    )

    # 4. Log activity timeline
    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="document_uploaded",
        entity_type="document",
        entity_id=db_doc.id,
        description=f"Uploaded specification document '{db_doc.name}'.",
    )

    return db_doc


@router.get("/{workspace_id}", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: UUID,
    project_id: UUID | None = None,
    category: str | None = None,
    status: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> list[Document]:
    return document_repo.get_multi_by_workspace(
        db,
        workspace_id=workspace_id,
        project_id=project_id,
        category=category,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/{workspace_id}/{document_id}", response_model=DocumentResponse)
def get_document(
    workspace_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this workspace",
        )
    return doc


@router.get("/{workspace_id}/{document_id}/download")
def download_document(
    workspace_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        file_bytes = storage_service.read(doc.filename)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on disk",
        )

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=doc.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.name}"'},
    )


@router.put("/{workspace_id}/{document_id}", response_model=DocumentResponse)
def update_document(
    workspace_id: UUID,
    document_id: UUID,
    doc_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this workspace",
        )

    updated = document_repo.update(db, db_obj=doc, obj_in=doc_in)

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="document_updated",
        entity_type="document",
        entity_id=doc.id,
        description=f"Updated document metadata for '{doc.name}'.",
    )
    return updated


@router.post("/{workspace_id}/{document_id}/version", response_model=DocumentResponse)
async def upload_new_version(
    workspace_id: UUID,
    document_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in this workspace",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file version",
        )

    updated = document_repo.add_version(
        db, db_obj=doc, file_bytes=file_bytes, created_by_id=current_user.id
    )

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="document_version_added",
        entity_type="document",
        entity_id=doc.id,
        description=f"Uploaded version {updated.current_version_number} of '{doc.name}'.",
    )
    return updated


@router.post(
    "/{workspace_id}/{document_id}/version/{version_number}/restore",
    response_model=DocumentResponse,
)
def restore_document_version(
    workspace_id: UUID,
    document_id: UUID,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    restored = document_repo.restore_version(
        db, db_obj=doc, version_number=version_number, created_by_id=current_user.id
    )
    if not restored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for this document",
        )

    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="document_version_restored",
        entity_type="document",
        entity_id=doc.id,
        description=f"Restored document '{doc.name}' to version {version_number} (new active version: {restored.current_version_number}).",
    )
    return restored


@router.delete("/{workspace_id}/{document_id}", response_model=DocumentResponse)
def delete_document(
    workspace_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_DELETE)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Soft remove
    soft_deleted = document_repo.soft_remove(db, id=document_id)
    activity_repo.log(
        db,
        user_id=current_user.id,
        workspace_id=workspace_id,
        action="document_deleted",
        entity_type="document",
        entity_id=document_id,
        description=f"Soft deleted document '{doc.name}'.",
    )
    return soft_deleted


@router.get("/{workspace_id}/{document_id}/content")
def get_document_content(
    workspace_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    try:
        file_bytes = storage_service.read(doc.filename)
        return {"content": file_bytes.decode("utf-8", errors="ignore")}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read document content: {str(e)}",
        )


from pydantic import BaseModel
class DocumentContentUpdate(BaseModel):
    content: str
    is_draft: bool = False


@router.put("/{workspace_id}/{document_id}/content", response_model=DocumentResponse)
def update_document_content(
    workspace_id: UUID,
    document_id: UUID,
    content_in: DocumentContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_WRITE)
    ),
) -> Document:
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    content_bytes = content_in.content.encode("utf-8")
    
    if content_in.is_draft:
        # Overwrite current active file content to save version noise
        try:
            # Save using the exact same filename
            storage_service.save(content_bytes, doc.filename)
            # Update file_size and checksum
            import hashlib
            doc.file_size = len(content_bytes)
            doc.checksum = hashlib.md5(content_bytes).hexdigest()
            doc.updated_by = current_user.id
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            # Log activity timeline
            activity_repo.log(
                db,
                user_id=current_user.id,
                workspace_id=workspace_id,
                action="document_draft_saved",
                entity_type="document",
                entity_id=doc.id,
                description=f"Auto-saved draft of '{doc.name}'.",
            )
            return doc
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save draft: {str(e)}",
            )
    else:
        # Create a new official version
        try:
            updated = document_repo.add_version(
                db, db_obj=doc, file_bytes=content_bytes, created_by_id=current_user.id
            )
            
            activity_repo.log(
                db,
                user_id=current_user.id,
                workspace_id=workspace_id,
                action="document_version_added",
                entity_type="document",
                entity_id=doc.id,
                description=f"Published version {updated.current_version_number} of '{doc.name}'.",
            )
            return updated
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create new version: {str(e)}",
            )


from app.schemas.document import DocumentVersionResponse
@router.get("/{workspace_id}/{document_id}/versions", response_model=list[DocumentVersionResponse])
def get_document_versions(
    workspace_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return doc.versions_list


@router.get("/{workspace_id}/{document_id}/version/{version_number}/content")
def get_document_version_content(
    workspace_id: UUID,
    document_id: UUID,
    version_number: int,
    db: Session = Depends(get_db),
    membership: Membership = Depends(
        require_workspace_permission(Permission.WORKSPACE_READ)
    ),
):
    doc = document_repo.get(db, document_id, workspace_id=workspace_id)
    if not doc or doc.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    # Find the version
    ver = next((v for v in doc.versions_list if v.version_number == version_number), None)
    if not ver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found",
        )
    try:
        file_bytes = storage_service.read(ver.filename)
        return {"content": file_bytes.decode("utf-8", errors="ignore")}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read version content: {str(e)}",
        )
