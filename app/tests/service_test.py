import pytest
from app.core.config import settings
from unittest.mock import patch

# 1. Parametrized test for POST /service with different edge cases
@pytest.mark.parametrize("service_data, expected_status, expected_detail", [
    ({"service_name": "Benefits", "service_entry_time": "09:00:00", "service_end_time": "18:00:00", "number_of_counters": 2}, 200, None),
    ({"service_name": "Admin", "service_entry_time": "09:00:00", "service_end_time": "18:00:00", "number_of_counters": 2}, 400, "Service already exists"),
    ({"service_name": "Accounts", "service_entry_time": "09:00:00", "service_end_time": "18:00:00", "number_of_counters": 0}, 400, "The number of counter not to be in negative or 0-")
])
def test_post_service(service_data,expected_status,expected_detail):
    response = settings.client.post("/service",json=service_data)
    assert response.status_code == expected_status

    if expected_status == 400:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        response_data = response.json()
        assert "id" in response_data
        assert response_data["service_name"] ==service_data["service_name"]

# 2. Parametrized test for GET /service/{service_name}
@pytest.mark.parametrize("service_name, expected_status, expected_detail", [
    ("Health Checkup", 200, None),  
    ("NonExistentService", 400, "Service not found or exist") 
])
@patch('app.crud.services_management.get_service_by_name')
def test_get_service_by_name(mock_get_service,service_name, expected_status, expected_detail):

    mock_get_service.return_value = None
    response = settings.client.get(f"service/{service_name}")
    assert response.status_code == expected_status

    if expected_status ==400:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        response_data = response.json()
        assert response_data["service_name"] == service_name

# 3. Test for GET /service to retrieve all services
def test_get_all_services():
    response = settings.client.get("/service")
    assert response.status_code == 200
    response_data=response.json()

    assert isinstance(response_data, list)
    assert len(response_data) >0

    for service in response_data:
        assert "id" in service
        assert "service_name" in service
