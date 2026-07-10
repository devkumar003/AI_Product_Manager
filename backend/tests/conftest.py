import os

os.environ["ENVIRONMENT"] = "testing"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.api.v1.deps import get_db
from app.database.session import Base
from app.main import app

# In-memory SQLite for extremely fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables in the testing database
    Base.metadata.create_all(bind=engine)

    from app.services.integration.plugin_manager import plugin_manager
    db = TestingSessionLocal()
    plugin_manager.seed_default_plugins(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def client_fixture(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
