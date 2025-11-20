"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src import app as app_module
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and varsity play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and match play",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Drawing, painting, and visual arts exploration",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu"]
        },
        "Theater Club": {
            "description": "Perform in school plays and musical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    }
    app_module.activities.clear()
    app_module.activities.update(original_activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


class TestRoot:
    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_participants_are_strings(self, reset_activities):
        """Test that participants are email strings"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity in data.items():
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignup:
    def test_signup_for_activity_success(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newemail@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, reset_activities):
        """Test that signup actually adds the participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_email_fails(self, reset_activities):
        """Test that duplicate signup is rejected"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_url_encoding_handled(self, reset_activities):
        """Test that URL encoding is handled correctly"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]


class TestUnregister:
    def test_unregister_success(self, reset_activities):
        """Test successful unregistration from an activity"""
        # michael@mergington.edu is already in Chess Club
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister actually removes the participant"""
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregister from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_nonexistent_participant_fails(self, reset_activities):
        """Test that unregister of non-existent participant fails"""
        response = client.delete(
            "/activities/Chess Club/signup?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_url_encoding_handled(self, reset_activities):
        """Test that URL encoding is handled correctly for unregister"""
        response = client.delete(
            "/activities/Programming%20Class/signup?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        assert "emma@mergington.edu" in response.json()["message"]


class TestIntegrationFlow:
    def test_complete_signup_and_unregister_flow(self, reset_activities):
        """Test a complete flow: signup, verify, unregister, verify"""
        activity = "Chess Club"
        email = "integration@mergington.edu"

        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200

        # Verify signup
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert unregister_response.status_code == 200

        # Verify unregister
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_multiple_signups_different_activities(self, reset_activities):
        """Test signing up for multiple different activities"""
        email = "multiactivity@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]

        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200

        # Verify all signups
        activities_response = client.get("/activities")
        activities = activities_response.json()
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]
