import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to the static index page."""
    # Arrange
    expected_location = "/static/index.html"
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location

def test_get_activities():
    """Test retrieving all activities."""
    # Arrange
    expected_activity = "Chess Club"
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity in data
    assert "description" in data[expected_activity]
    assert "participants" in data[expected_activity]

def test_signup_success():
    """Test successful signup for an existing activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newsignup@example.com"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity_name]["participants"]

def test_signup_duplicate():
    """Test signup failure due to duplicate registration."""
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@example.com"
    
    # Act - First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act - Duplicate signup attempt
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}

def test_signup_nonexistent_activity():
    """Test signup failure for a nonexistent activity."""
    # Arrange
    nonexistent_activity = "Nonexistent Activity"
    email = "test@example.com"
    
    # Act
    response = client.post(f"/activities/{nonexistent_activity}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange
    activity_name = "Gym Class"
    email = "unregister@example.com"
    
    # Act - First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act - Unregister
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify participant was removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistration failure when the student is not registered."""
    # Arrange
    activity_name = "Basketball Team"
    email = "notregistered@example.com"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not registered for this activity"}

def test_unregister_nonexistent_activity():
    """Test unregistration failure for a nonexistent activity."""
    # Arrange
    nonexistent_activity = "Nonexistent Activity"
    email = "test@example.com"
    
    # Act
    response = client.delete(f"/activities/{nonexistent_activity}/unregister", params={"email": email})
    
    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
