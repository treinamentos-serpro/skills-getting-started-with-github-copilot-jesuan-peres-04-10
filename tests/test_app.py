"""Tests for the Mergington High School API, structured with Arrange-Act-Assert."""

from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == set(activities.keys())

    def test_activity_has_expected_shape(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        chess = response.json()["Chess Club"]
        assert chess["description"] == "Learn strategies and compete in chess tournaments"
        assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess["max_participants"] == 12
        assert chess["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


class TestSignup:
    def test_signup_succeeds_for_new_student(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        assert email not in activities[activity]["participants"]

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity}"}
        assert email in activities[activity]["participants"]

    def test_signup_fails_when_already_signed_up(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity]["participants"]

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity]["participants"].count(email) == 1

    def test_signup_fails_for_unknown_activity(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregister:
    def test_unregister_succeeds_for_signed_up_student(self, client):
        # Arrange
        activity = "Programming Class"
        email = "emma@mergington.edu"
        assert email in activities[activity]["participants"]

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity}"}
        assert email not in activities[activity]["participants"]

    def test_unregister_fails_when_not_signed_up(self, client):
        # Arrange
        activity = "Art Club"
        email = "ghost@mergington.edu"
        assert email not in activities[activity]["participants"]

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_fails_for_unknown_activity(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
