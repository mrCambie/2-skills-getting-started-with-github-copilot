"""
Test cases for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check if we have all expected activities
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
        "Basketball Club", "Art Club", "Drama Club", "Debate Team", "Math Club"
    ]
    assert all(activity in activities for activity in expected_activities)
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert all(key in chess_club for key in ["description", "schedule", "max_participants", "participants"])
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the student was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/signup", params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_duplicate_signup():
    """Test signing up for an activity when already registered"""
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # This email is already registered in the test data
    
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is in the initial test data
    
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Successfully unregistered {email} from {activity_name}"
    
    # Verify the student was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]