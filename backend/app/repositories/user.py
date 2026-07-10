from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def get_by_email(self, db: Session, email: str) -> User | None:
        return (
            db.query(self.model)
            .filter(self.model.email == email, self.model.deleted_at.is_(None))
            .first()
        )

    def get_by_username(self, db: Session, username: str) -> User | None:
        return (
            db.query(self.model)
            .filter(self.model.username == username, self.model.deleted_at.is_(None))
            .first()
        )


user_repo = UserRepository(User)
