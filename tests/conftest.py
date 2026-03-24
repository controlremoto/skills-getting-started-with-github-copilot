"""
Shared fixtures for FastAPI tests.
Provides TestClient and fresh activities state for each test.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Returns a TestClient instance for making HTTP requests to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Returns a fresh copy of the activities dictionary for test isolation."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture
def sample_email():
    """Returns a sample email for testing."""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity():
    """Returns a sample activity name for testing."""
    return "Chess Club"


@pytest.fixture(autouse=True)
def reset_activities(fresh_activities, monkeypatch):
    """Automatically reset the global activities dictionary before each test."""
    monkeypatch.setattr("src.app.activities", fresh_activities)