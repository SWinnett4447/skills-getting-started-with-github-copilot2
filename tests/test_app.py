from src import app as app_module


def test_root_redirects_to_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seeded_data(client):
    # Arrange
    expected_keys = set(app_module.activities.keys())

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert set(data.keys()) == expected_keys
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    starting_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == starting_count + 1


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    starting_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"].count(email) == 1
    assert len(app_module.activities[activity_name]["participants"]) == starting_count


def test_signup_returns_404_for_missing_activity(client):
    # Arrange
    activity_name = "Robotics Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"


def test_remove_participant_removes_existing_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_participant_returns_404_when_student_is_missing(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Student is not signed up for this activity"
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_activity(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Activity not found"


def test_signup_can_exceed_max_participants(client):
    # Arrange
    activity_name = "Chess Club"
    starting_participants = len(app_module.activities[activity_name]["participants"])
    max_participants = app_module.activities[activity_name]["max_participants"]

    # Act
    for index in range(max_participants + 1):
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": f"extra-{index}@mergington.edu"},
        )

        assert response.status_code == 200

    # Assert
    assert len(app_module.activities[activity_name]["participants"]) == starting_participants + max_participants + 1
    assert len(app_module.activities[activity_name]["participants"]) > max_participants
