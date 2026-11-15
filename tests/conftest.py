"""Isolated SQLite database and FastAPI test client fixtures."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_stockflow.db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-with-more-than-32-characters"
from fastapi.testclient import TestClient
import pytest
from app.core.database import Base, engine
from app.main import app

@pytest.fixture
def client():
    """Create a clean schema for each test to prevent cross-test state leakage."""
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    with TestClient(app) as test_client: yield test_client
    Base.metadata.drop_all(engine)
