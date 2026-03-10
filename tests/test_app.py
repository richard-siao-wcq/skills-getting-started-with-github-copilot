import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # backup initial state so that each test runs with fresh data
    backup = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(backup))


def test_root_redirect():
    # Arrange (nothing special to set up)
    # Act: disable redirects so we can inspect the raw response
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all():
    # Arrange
    expected = copy.deepcopy(app_module.activities)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_successful():
    # Arrange
    activity = "Chess Club"
    email = "test@mergington.edu"
    assert email not in app_module.activities[activity]["participants"]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert response.json() == {"message": f"Signed up {email} for {activity}"}


def test_signup_nonexistent_activity():
    # Arrange
    activity = "NonExistent"
    email = "foo@bar.com"
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404


def test_signup_already_registered():
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_unregister_successful():
    # Arrange
    activity = "Basketball Team"
    email = app_module.activities[activity]["participants"][0]
    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity]["participants"]
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}


def test_unregister_nonexistent_activity():
    # Arrange
    activity = "Ghost Club"
    email = "nobody@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 404


def test_unregister_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "ghost@mergington.edu"
    assert email not in app_module.activities[activity]["participants"]
    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert response.status_code == 404
