import base64
import hashlib
import logging
from uuid import UUID

from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.integration import EncryptedSecret

logger = logging.getLogger("app.services.integration.secret_vault")


class SecretVault:
    def __init__(self):
        # Derive a valid Fernet 32-byte urlsafe key from global app JWT_SECRET
        derived = hashlib.sha256(settings.JWT_SECRET.encode()).digest()
        key = base64.urlsafe_b64encode(derived)
        self.cipher = Fernet(key)

    def store_secret(
        self, db: Session, workspace_id: UUID, key: str, value: str
    ) -> EncryptedSecret:
        """Encrypts and stores a secret in the vault."""
        encrypted = self.cipher.encrypt(value.encode()).decode()

        # Check if secret already exists
        existing = (
            db.query(EncryptedSecret)
            .filter(
                EncryptedSecret.workspace_id == workspace_id,
                EncryptedSecret.secret_key == key,
            )
            .first()
        )

        if existing:
            existing.encrypted_value = encrypted
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated secret {key} for workspace {workspace_id}")
            return existing

        new_secret = EncryptedSecret(
            workspace_id=workspace_id, secret_key=key, encrypted_value=encrypted
        )
        db.add(new_secret)
        db.commit()
        db.refresh(new_secret)
        logger.info(f"Stored new secret {key} for workspace {workspace_id}")
        return new_secret

    def get_secret(self, db: Session, workspace_id: UUID, key: str) -> str | None:
        """Retrieves and decrypts a secret from the vault."""
        secret = (
            db.query(EncryptedSecret)
            .filter(
                EncryptedSecret.workspace_id == workspace_id,
                EncryptedSecret.secret_key == key,
            )
            .first()
        )

        if not secret:
            return None

        try:
            decrypted = self.cipher.decrypt(secret.encrypted_value.encode()).decode()
            return decrypted
        except Exception as e:
            logger.error(
                f"Failed to decrypt secret {key} for workspace {workspace_id}: {e}"
            )
            return None

    def delete_secret(self, db: Session, workspace_id: UUID, key: str) -> bool:
        """Deletes a secret from the vault."""
        secret = (
            db.query(EncryptedSecret)
            .filter(
                EncryptedSecret.workspace_id == workspace_id,
                EncryptedSecret.secret_key == key,
            )
            .first()
        )

        if not secret:
            return False

        db.delete(secret)
        db.commit()
        logger.info(f"Deleted secret {key} for workspace {workspace_id}")
        return True


secret_vault = SecretVault()
