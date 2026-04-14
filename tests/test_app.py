import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check that activities have the expected structure
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_valid():
    """Test POST /activities/{activity_name}/signup with valid data"""
    activity_name = "Chess Club"
    email = "student@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    # Check that the participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test POST /activities/{activity_name}/signup with duplicate email"""
    activity_name = "Programming Class"
    email = "duplicate@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity():
    """Test POST /activities/{activity_name}/signup with invalid activity"""
    activity_name = "Invalid Activity"
    email = "student@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_remove_participant_valid():
    """Test DELETE /activities/{activity_name}/participants with valid data"""
    activity_name = "Gym Class"
    email = "remove@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Then remove
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Removed {email} from {activity_name}"
    # Check that the participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_signed_up():
    """Test DELETE /activities/{activity_name}/participants when not signed up"""
    activity_name = "Basketball"
    email = "notsigned@example.com"
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Participant not found for this activity"


def test_remove_participant_invalid_activity():
    """Test DELETE /activities/{activity_name}/participants with invalid activity"""
    activity_name = "Invalid Activity"
    email = "student@example.com"
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()