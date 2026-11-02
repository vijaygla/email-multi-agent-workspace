"""
Pytest configuration and shared test fixtures.
Provides TestClient and mock environments.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal

@pytest.fixture(scope="session")
def client():
    """Provides FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_case1_email():
    return {
        "subject": "Sync on tomorrow's demo",
        "sender": "sarah.connor@nexus.ai",
        "recipient": "user@nexus.ai",
        "body": "Hi there, let's meet tomorrow afternoon to review the client presentation."
    }

@pytest.fixture
def sample_case2_email():
    return {
        "subject": "Action required: Budget report",
        "sender": "alex.turner@nexus.ai",
        "recipient": "user@nexus.ai",
        "body": "Please send the revised budget deck by Friday 5 PM. High urgency."
    }

@pytest.fixture
def sample_case3_email():
    return {
        "subject": "Urgent Budget and Meeting Sync",
        "sender": "elena.rostova@nexus.ai",
        "recipient": "user@nexus.ai",
        "body": "Please finish the budget deck by Friday 5 PM EST. Also let's meet tomorrow afternoon at 2 PM EST to sync."
    }

@pytest.fixture
def sample_case5_email():
    return {
        "subject": "Quick chat sometime",
        "sender": "marcus.vance@nexus.ai",
        "recipient": "user@nexus.ai",
        "body": "Hey, let's connect sometime whenever you have a minute to discuss that thing."
    }
