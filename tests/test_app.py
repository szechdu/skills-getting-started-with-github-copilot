from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

TEST_ACTIVITY = "Test Activity AAA"


def test_get_activities():
    # Arrange
    # (Use the existing seeded activity data.)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_creates_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activities[TEST_ACTIVITY] = {
        "description": "Temporary test activity",
        "schedule": "Now",
        "max_participants": 5,
        "participants": [],
    }

    try:
        # Act
        response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {TEST_ACTIVITY}"
        assert email in activities[TEST_ACTIVITY]["participants"]
    finally:
        activities.pop(TEST_ACTIVITY, None)


def test_delete_removes_participant():
    # Arrange
    email = "remove@student.edu"
    activities[TEST_ACTIVITY] = {
        "description": "Temporary test activity",
        "schedule": "Later",
        "max_participants": 3,
        "participants": [email],
    }

    try:
        # Act
        response = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {TEST_ACTIVITY}"
        assert email not in activities[TEST_ACTIVITY]["participants"]
    finally:
        activities.pop(TEST_ACTIVITY, None)


def test_delete_nonexistent_participant_returns_404():
    # Arrange
    activities[TEST_ACTIVITY] = {
        "description": "Temp test activity",
        "schedule": "Later",
        "max_participants": 3,
        "participants": [],
    }

    try:
        # Act
        response = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email=missing@student.edu")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    finally:
        activities.pop(TEST_ACTIVITY, None)


def test_activity_not_found_returns_404_for_delete():
    # Arrange

    # Act
    response = client.delete("/activities/UnknownActivity/participants?email=test@school.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
