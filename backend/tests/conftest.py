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


@pytest.fixture(autouse=True)
def mock_llm_generate_globally():
    from unittest.mock import AsyncMock, patch
    from app.ai.schemas import AIResponse, TokenUsage

    # Patch LLMManager's async generate method to return a valid structured response
    with patch("app.ai.core.llm_manager.LLMManager.generate", new_callable=AsyncMock) as mock_gen:
        # Custom mock response matching standard pipeline structures
        mock_gen.return_value = AIResponse(
            content="""{
                "success": true,
                "plan_id": "88888888-8888-8888-8888-888888888888",
                "steps": ["Step 1: Setup Stripe webhook listener", "Step 2: Wire events to subscription database updater"],
                "file_path": "backend/app/controllers/billing.py",
                "score": 85,
                "complexity_score": 12,
                "comments": [{"text": "Ensure connection parameters are properly sanitized.", "line": 10, "severity": "Medium"}],
                "title": "Bug scan completed",
                "risk_analysis": "Medium risk - Database credentials exposure potential",
                "testing_plan": "Unit tests for webhook callbacks",
                "deployment_guide": "Deploy using Docker ECS container"
            }""",
            model="gpt-4o",
            provider="openai",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
            latency_ms=10.0,
            success=True,
        )
        yield mock_gen
