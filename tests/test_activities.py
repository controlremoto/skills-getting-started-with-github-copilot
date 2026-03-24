"""
Unit tests for activities business logic functions.
Tests signup_for_activity and unregister_from_activity functions in isolation.
"""

import pytest
from fastapi import HTTPException
from src.app import signup_for_activity, unregister_from_activity


class TestSignupForActivity:
    """Test cases for signup_for_activity function."""

    def test_valid_signup(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test successful signup for an existing activity."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # Act
        result = signup_for_activity(sample_activity, sample_email)

        # Assert
        assert result["message"] == f"Signed up {sample_email} for {sample_activity}"
        assert sample_email in fresh_activities[sample_activity]["participants"]

    def test_signup_activity_not_found(self, fresh_activities, sample_email, monkeypatch):
        """Test signup for non-existent activity raises 404."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("NonExistent Activity", sample_email)

        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail

    def test_duplicate_signup(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test signing up for an activity twice raises 400."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # First signup should succeed
        signup_for_activity(sample_activity, sample_email)

        # Second signup should fail
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(sample_activity, sample_email)

        assert exc_info.value.status_code == 400
        assert "Student already signed up" in exc_info.value.detail

    def test_signup_participants_list_updated(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test that participants list is correctly updated after signup."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        initial_count = len(fresh_activities[sample_activity]["participants"])

        signup_for_activity(sample_activity, sample_email)

        assert len(fresh_activities[sample_activity]["participants"]) == initial_count + 1
        assert sample_email in fresh_activities[sample_activity]["participants"]


class TestUnregisterFromActivity:
    """Test cases for unregister_from_activity function."""

    def test_valid_unregistration(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test successful unregistration from an activity."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # First signup
        signup_for_activity(sample_activity, sample_email)

        # Then unregister
        result = unregister_from_activity(sample_activity, sample_email)

        # Assert
        assert result["message"] == f"Unregistered {sample_email} from {sample_activity}"
        assert sample_email not in fresh_activities[sample_activity]["participants"]

    def test_unregister_activity_not_found(self, fresh_activities, sample_email, monkeypatch):
        """Test unregistration from non-existent activity raises 404."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("NonExistent Activity", sample_email)

        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail

    def test_unregister_not_enrolled(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test unregistration when student is not enrolled raises 400."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(sample_activity, sample_email)

        assert exc_info.value.status_code == 400
        assert "Student is not registered" in exc_info.value.detail

    def test_unregister_participants_list_updated(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test that participants list is correctly updated after unregistration."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # Signup first
        signup_for_activity(sample_activity, sample_email)
        initial_count = len(fresh_activities[sample_activity]["participants"])

        # Unregister
        unregister_from_activity(sample_activity, sample_email)

        assert len(fresh_activities[sample_activity]["participants"]) == initial_count - 1
        assert sample_email not in fresh_activities[sample_activity]["participants"]


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_signup_with_whitespace_email(self, fresh_activities, sample_activity, monkeypatch):
        """Test signup with email containing whitespace."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        email_with_whitespace = " test@mergington.edu "

        result = signup_for_activity(sample_activity, email_with_whitespace)

        assert result["message"] == f"Signed up {email_with_whitespace} for {sample_activity}"
        assert email_with_whitespace in fresh_activities[sample_activity]["participants"]

    def test_signup_with_special_chars_activity(self, fresh_activities, sample_email, monkeypatch):
        """Test signup with activity name containing special characters."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # Use an activity that exists in fresh_activities
        special_activity = "Programming Class"

        result = signup_for_activity(special_activity, sample_email)

        assert result["message"] == f"Signed up {sample_email} for {special_activity}"
        assert sample_email in fresh_activities[special_activity]["participants"]

    def test_re_signup_after_unregistration(self, fresh_activities, sample_email, sample_activity, monkeypatch):
        """Test that a student can sign up again after unregistration."""
        # Mock the global activities dictionary
        monkeypatch.setattr("src.app.activities", fresh_activities)

        # Signup, unregister, then signup again
        signup_for_activity(sample_activity, sample_email)
        unregister_from_activity(sample_activity, sample_email)
        result = signup_for_activity(sample_activity, sample_email)

        assert result["message"] == f"Signed up {sample_email} for {sample_activity}"
        assert sample_email in fresh_activities[sample_activity]["participants"]