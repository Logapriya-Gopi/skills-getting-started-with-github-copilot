from urllib.parse import quote


def test_get_activities_returns_all(client):
    # Arrange
    expected_activity = "Chess Club"
    expected_participant = "michael@mergington.edu"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert expected_participant in data[expected_activity]["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    path = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    signup_response = client.post(path, params={"email": email})

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"

    get_response = client.get("/activities")
    participants = get_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    path = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    first_response = client.post(path, params={"email": email})
    second_response = client.post(path, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"

    participants = client.get("/activities").json()[activity_name]["participants"]
    assert participants.count(email) == 1


def test_signup_activity_not_found(client):
    # Arrange
    path = f"/activities/{quote('Nonexistent Activity', safe='')}/signup"
    email = "missing@mergington.edu"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    remove_response = client.delete(path, params={"email": email})

    # Assert
    assert remove_response.status_code == 200
    assert remove_response.json()["message"] == f"Unregistered {email} from {activity_name}"

    get_response = client.get("/activities")
    participants = get_response.json()[activity_name]["participants"]
    assert email not in participants

    # Act
    missing_response = client.delete(path, params={"email": email})

    # Assert
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found"
