from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

@pytest.mark.parametrize("counter_data, expected_status, expected_detail", [
    # Valid case
    ({"counter_number": 2, "service_name": "Medical_Store"}, 200, None),
    # Service does not exist
    ({"counter_number": 1, "service_name": "NonExistentService"}, 400, "Service not found"),
    # Counter already exists
    ({"counter_number": 1, "service_name": "Health_Checkup"}, 400, "Counter already exists"),
])
def test_post_counter(counter_data, expected_status, expected_detail):
    response = client.post("/counter", json=counter_data)
    assert response.status_code == expected_status

    if expected_status == 400:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        response_data = response.json()
        assert "id" in response_data
        assert response_data["counter_number"] == counter_data["counter_number"]

# 2. Parametrized test for GET /counter/{counter_id}
@pytest.mark.parametrize("counter_id, expected_status, expected_detail", [
    (1, 200, None),  # Valid counter ID
    (999, 404, "Counter not found")  # Non-existent counter ID
])
@patch('app.crud.counter_management.get_counter_by_id')
def test_get_counter_by_id(mock_get_counter, counter_id, expected_status, expected_detail):
    mock_get_counter.return_value = {"id": counter_id, "counter_number": 1, "service_id": 1} if expected_status == 200 else None
    response = client.get(f"/counter/{counter_id}")
    assert response.status_code == expected_status

    if expected_status == 404:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        response_data = response.json()
        assert response_data["id"] == counter_id


