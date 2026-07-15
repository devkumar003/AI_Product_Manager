import abc
import os
from pathlib import Path


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save(self, file_data: bytes, filename: str) -> str:
        """
        Saves file bytes and returns the stored filename/relative path or URL.
        """
        pass

    @abc.abstractmethod
    def read(self, filename: str) -> bytes:
        """
        Reads file bytes from storage.
        """
        pass

    @abc.abstractmethod
    def delete(self, filename: str) -> None:
        """
        Removes file from storage.
        """
        pass


class LocalStorage(BaseStorage):
    def __init__(self, upload_dir: str | None = None):
        if upload_dir is None:
            # Create uploads directory in workspace root
            self.upload_dir = Path("uploads")
        else:
            self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_data: bytes, filename: str) -> str:
        # Prevent path traversal attacks
        safe_name = Path(filename).name
        target_path = self.upload_dir / safe_name

        # Write binary
        with open(target_path, "wb") as f:
            f.write(file_data)

        return safe_name

    def read(self, filename: str) -> bytes:
        safe_name = Path(filename).name
        target_path = self.upload_dir / safe_name
        if not target_path.exists():
            raise FileNotFoundError(f"File {filename} not found in local storage.")
        with open(target_path, "rb") as f:
            return f.read()

    def delete(self, filename: str) -> None:
        safe_name = Path(filename).name
        target_path = self.upload_dir / safe_name
        if target_path.exists():
            target_path.unlink()


class S3Storage(BaseStorage):
    """
    Placeholder/Future S3 driver that complies with the BaseStorage interface.
    """

    def __init__(self):
        self.bucket = os.getenv("AWS_S3_BUCKET", "ai-product-os")

    def save(self, file_data: bytes, filename: str) -> str:
        # In the future, this will use boto3 client to upload.
        # For now, we raise NotImplementedError or fall back to local/simulate if configured.
        raise NotImplementedError("S3 storage driver is registered but not configured.")

    def read(self, filename: str) -> bytes:
        raise NotImplementedError("S3 storage driver is registered but not configured.")

    def delete(self, filename: str) -> None:
        raise NotImplementedError("S3 storage driver is registered but not configured.")


# Driver factory registry
def get_storage_driver() -> BaseStorage:
    driver_type = os.getenv("STORAGE_DRIVER", "local").lower()
    if driver_type == "s3":
        return S3Storage()
    # Default is LocalStorage
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    return LocalStorage(upload_dir=upload_dir)


storage_service = get_storage_driver()
