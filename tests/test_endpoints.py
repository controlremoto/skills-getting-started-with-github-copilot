"""
Integration tests for FastAPI endpoints.
Tests complete API workflows using TestClient.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")

        assert response.status_code == 200
        data = response.json()

        # Should return a dictionary with activity names as keys
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities

        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity

        # Participants should be a list
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that activities include current participant lists."""
        response = client.get("/activities")
        data = response.json()

        # Find an activity with known participants
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert len(chess_club["participants"]) >= 2  # Should have initial participants
        assert "michael@mergington.edu" in chess_club["participants"]


class TestRootEndpoint:
    """Test cases for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_valid_signup(self, client, sample_email, sample_activity):
        """Test successful signup via API."""
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity in data["message"]

    def test_signup_missing_email_parameter(self, client, sample_activity):
        """Test signup without email parameter."""
        response = client.post(f"/activities/{sample_activity}/signup")

        # Should return 422 Unprocessable Entity for missing required param
        assert response.status_code == 422

    def test_signup_invalid_activity(self, client, sample_email):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": sample_email}
        )

        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup_via_api(self, client, sample_email, sample_activity):
        """Test signing up twice via API."""
        # First signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Second signup should fail
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_valid_unregistration(self, client, sample_email, sample_activity):
        """Test successful unregistration via API."""
        # First signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Then unregister
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity in data["message"]

    def test_unregister_missing_email_parameter(self, client, sample_activity):
        """Test unregistration without email parameter."""
        response = client.delete(f"/activities/{sample_activity}/unregister")

        # Should return 422 Unprocessable Entity for missing required param
        assert response.status_code == 422

    def test_unregister_invalid_activity(self, client, sample_email):
        """Test unregistration from non-existent activity."""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": sample_email}
        )

        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_enrolled(self, client, sample_email, sample_activity):
        """Test unregistration when not enrolled."""
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )

        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()


class TestStateTransitions:
    """Test complex state transition workflows."""

    def test_signup_unregister_resignup_workflow(self, client, sample_email, sample_activity):
        """Test complete workflow: signup -> unregister -> signup again."""
        # Initial signup
        response1 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200

        # Unregister
        response2 = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        assert response2.status_code == 200

        # Signup again (should succeed)
        response3 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200

    def test_multiple_participants_same_activity(self, client, sample_activity):
        """Test multiple different participants can join the same activity."""
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        # All signups should succeed
        for email in emails:
            response = client.post(
                f"/activities/{sample_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Verify all are enrolled by checking activities endpoint
        response = client.get("/activities")
        data = response.json()
        participants = data[sample_activity]["participants"]

        for email in emails:
            assert email in participants

    def test_participant_isolation_between_activities(self, client, sample_email):
        """Test that signup in one activity doesn't affect others."""
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Signup for activity1
        client.post(
            f"/activities/{activity1}/signup",
            params={"email": sample_email}
        )

        # Check activity2 still doesn't have this participant
        response = client.get("/activities")
        data = response.json()

        assert sample_email in data[activity1]["participants"]
        assert sample_email not in data[activity2]["participants"]