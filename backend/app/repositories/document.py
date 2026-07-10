import hashlib
import uuid
from sqlalchemy import or_, JSON, cast
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.repositories.base import BaseRepository
from app.services.storage import storage_service


class DocumentRepository(BaseRepository[Document]):
    def create_with_file(
        self,
        db: Session,
        *,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID | None,
        name: str,
        file_bytes: bytes,
        mime_type: str,
        category: str,
        tags: list[str],
        status: str = "Draft",
        created_by_id: uuid.UUID | None = None,
    ) -> Document:
        # 1. Compute MD5 checksum
        checksum = hashlib.md5(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # 2. Save file bytes to storage layer
        unique_suffix = uuid.uuid4().hex[:8]
        filename = f"{unique_suffix}_{name}"
        saved_filename = storage_service.save(file_bytes, filename)

        # 3. Create Document entry
        db_doc = Document(
            workspace_id=workspace_id,
            project_id=project_id,
            name=name,
            filename=saved_filename,
            mime_type=mime_type,
            file_size=file_size,
            checksum=checksum,
            category=category,
            tags=tags,
            status=status,
            current_version_number=1,
            archived=False,
            created_by=created_by_id,
        )
        db.add(db_doc)
        db.flush()  # populate ID

        # 4. Create DocumentVersion entry
        db_version = DocumentVersion(
            document_id=db_doc.id,
            version_number=1,
            filename=saved_filename,
            file_size=file_size,
            checksum=checksum,
            created_by=created_by_id,
        )
        db.add(db_version)
        db.commit()
        db.refresh(db_doc)
        return db_doc

    def add_version(
        self,
        db: Session,
        *,
        db_obj: Document,
        file_bytes: bytes,
        created_by_id: uuid.UUID | None = None,
    ) -> Document:
        checksum = hashlib.md5(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # Save to storage
        next_ver = db_obj.current_version_number + 1
        filename = f"v{next_ver}_{uuid.uuid4().hex[:8]}_{db_obj.name}"
        saved_filename = storage_service.save(file_bytes, filename)

        # Create new version record
        db_version = DocumentVersion(
            document_id=db_obj.id,
            version_number=next_ver,
            filename=saved_filename,
            file_size=file_size,
            checksum=checksum,
            created_by=created_by_id,
        )
        db.add(db_version)

        # Update document main record
        db_obj.current_version_number = next_ver
        db_obj.filename = saved_filename
        db_obj.file_size = file_size
        db_obj.checksum = checksum
        db_obj.updated_by = created_by_id

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def restore_version(
        self,
        db: Session,
        *,
        db_obj: Document,
        version_number: int,
        created_by_id: uuid.UUID | None = None,
    ) -> Document | None:
        target_version = (
            db.query(DocumentVersion)
            .filter(
                DocumentVersion.document_id == db_obj.id,
                DocumentVersion.version_number == version_number,
            )
            .first()
        )
        if not target_version:
            return None

        # Fetch version contents from storage
        file_bytes = storage_service.read(target_version.filename)

        # Save as a brand new version to keep the version timeline forward-moving
        return self.add_version(
            db, db_obj=db_obj, file_bytes=file_bytes, created_by_id=created_by_id
        )

    def get_multi_by_workspace(
        self,
        db: Session,
        *,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID | None = None,
        search: str | None = None,
        category: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        query = db.query(self.model).filter(
            self.model.workspace_id == workspace_id,
            self.model.deleted_at.is_(None),
        )

        if project_id:
            query = query.filter(self.model.project_id == project_id)
        if category:
            query = query.filter(self.model.category == category)
        if status:
            query = query.filter(self.model.status == status)
        if search:
            search_filt = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.name.ilike(search_filt),
                    self.model.filename.ilike(search_filt),
                )
            )

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()


document_repo = DocumentRepository(Document)
