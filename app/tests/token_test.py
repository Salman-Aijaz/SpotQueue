from unittest.mock import patch,MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.token_schemas import TokenResponse
from app.crud.token_management import get_token_by_user_id,update_token_distance_duration
from app.utils.get_distance import get_distance

client = TestClient(app)

# 1. Parameterized test for POST /token
@pytest.mark.parametrize("token_data, expected_status, expected_detail", [
    # Valid Case
    # ({"email": "salman333699@gmail.com", "service_name": "Health_Checkup", "latitude": 24.8416198, "longitude": 67.164574}, 200, None),
    # User Not Found
    # ({"email": "unknown@example.com", "service_name": "Health_Checkup", "latitude": 24.8385635, "longitude": 67.0643958}, 400, "User Not Found"),
    # Service Not Found
    # ({"email": "salman333699@gmail.com", "service_name": "NonExistentService", "latitude": 24.8385635, "longitude": 67.0643958}, 400, "Service not found")
    # Invalid Latitude
    # ({"email": "salman333699@gmail.com", "service_name": "Health_Checkup", "latitude": -95.0, "longitude": 67.164574}, 400, "Invalid latitude  values."),
    # Invalid Longitude
    ({"email": "salman333699@gmail.com", "service_name": "Health_Checkup", "latitude": 24.8416198, "longitude": -200.0}, 400, "Invalid longitude values."),
])
@patch('app.crud.user_management.get_user_by_email')
@patch('app.crud.services_management.get_service_by_name')
@patch('app.crud.counter_management.get_counter_by_service_id')
@patch('app.utils.get_distance.get_distance')
def test_generate_token(mock_get_distance, mock_get_counter_by_service_id, mock_get_service_by_name, mock_get_user_by_email, token_data, expected_status, expected_detail):

    # Mock user lookup
    mock_get_user_by_email.return_value = {"id": 1} if expected_status == 200 else None
    
    # Mock service lookup
    mock_get_service_by_name.return_value = {"id": 1} if expected_status == 200 else None
    
    # Mock counter lookup
    mock_get_counter_by_service_id.return_value = 1 if expected_status == 200 else None
    
    # Mock distance and duration response
    mock_get_distance.return_value = (18.5, 36)  # Example distance and duration values

    # Send POST request to /token
    response = client.post("/users/token", json=token_data)

    # Check the response status code
    assert response.status_code == expected_status

    # Check for expected error details
    if expected_status == 400:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        # Validate successful response data structure
        response_data = response.json()
        assert "token_number" in response_data
        assert response_data["user_id"] == 1
        assert response_data["service_id"] == 1
        assert response_data["distance"] == pytest.approx(18.5, rel=1e-2)
        assert response_data["duration"] == 36
        assert response_data["status"] == "Token generated successfully"

@pytest.mark.parametrize("request_data, expected_status, expected_detail", [
    # Valid Case
    # ({"user_id": 1, "latitude": 24.8523464, "longitude": 67.0078039}, 200, None),
    # Token Not Found
    ({"user_id": 999, "latitude": 24.8416198, "longitude": 67.164574}, 400, "Token Not Found"),
    # Invalid Latitude
    # ({"user_id": 1, "latitude": -95.0, "longitude": 67.164574}, 400, "Invalid latitude or longitude values."),
    # Invalid Longitude
    # ({"user_id": 1, "latitude": 24.8416198, "longitude": -200.0}, 400, "Invalid latitude or longitude values."),
    # Distance Matrix API Error
    # ({"user_id": 1, "latitude": 24.8416198, "longitude": 67.164574}, 500, "Error connecting to the distance matrix service:"),
])
@patch('app.crud.token_management.get_token_by_user_id')
@patch('app.utils.get_distance.get_distance')
@patch('app.crud.token_management.update_token_distance_duration')
def test_update_eta(mock_update_token, mock_get_distance, mock_get_token_by_user_id, request_data, expected_status, expected_detail):
    
    # Mock the token lookup
    if request_data['user_id'] == 999:  # Simulate token not found
        mock_get_token_by_user_id.return_value = None
    else:
        mock_get_token_by_user_id.return_value = {"token_number": 1, "user_id": 1, "service_id": 1, "counter_id": 1}

    # Mock distance and duration response
    if expected_status == 200:
        mock_get_distance.return_value = (1.0, 1)  # Example distance and duration values
        mock_update_token.return_value = {"token_number": 3, "user_id": 1, "service_id": 1, "counter_id": 1, "distance": 1.0, "duration": 1, "reach_out": False}
    else:
        mock_get_distance.side_effect = Exception("Distance Matrix API Error")  # Simulate API error

    # Send PUT request to /new-location
    response = client.put("/users/new-location", json=request_data)

    # Check the response status code
    assert response.status_code == expected_status

    # Check for expected error details
    if expected_status in [400, 500]:
        assert "detail" in response.json()
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        # Validate successful response data structure
        response_data = response.json()
        assert response_data["token_number"] == 3
        assert response_data["user_id"] == 1
        assert response_data["service_id"] == 1
        assert response_data["counter_id"] == 1
        assert response_data["distance"] == pytest.approx(1.0, rel=1e-2)
        assert response_data["duration"] == 1
        assert response_data["status"] == "ETA Updated Successfully"
