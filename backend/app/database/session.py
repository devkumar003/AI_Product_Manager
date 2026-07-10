from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.settings import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_size=10, max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Yields database session and guarantees closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
