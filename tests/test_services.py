import pytest


@pytest.fixture()
def admin_headers():
    return {"Authorization": "Bearer test_admin_token"}


@pytest.mark.asyncio
async def test_create_service(async_client, admin_headers):
    service_data = {
        "name": "Oil Change",
        "description": "Full synthetic oil change",
        "price": 49.99,
        "duration": 60,
    }

    response = await async_client.post(
        "api/v1/services/", json=service_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Oil Change"
    assert data["description"] == "Full synthetic oil change"
    assert data["price"] == "49.99"
    assert data["duration"] == 60


@pytest.mark.asyncio
async def test_read_services(async_client):
    response = await async_client.get("/api/v1/services/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_read_service(async_client, admin_headers):
    service_data = {
        "name": "Brake Inspection",
        "description": "Detailed brake system inspection",
        "price": 30.00,
        "duration": 45,
    }
    create_response = await async_client.post(
        "/api/v1/services/", json=service_data, headers=admin_headers
    )
    assert create_response.status_code == 200
    service_id = create_response.json()["service_id"]

    response = await async_client.get(f"/api/v1/services/{service_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["service_id"] == service_id
    assert data["name"] == "Brake Inspection"


@pytest.mark.asyncio
async def test_update_service(async_client, admin_headers):
    service_data = {
        "name": "Tire Rotation",
        "description": "Rotate all four tires",
        "price": 20.00,
        "duration": 30,
    }
    create_response = await async_client.post(
        "/api/v1/services/", json=service_data, headers=admin_headers
    )
    assert create_response.status_code == 200
    service_id = create_response.json()["service_id"]

    update_data = {"name": "Premium Tire Rotation", "price": 25.00}
    response = await async_client.put(
        f"/api/v1/services/{service_id}", json=update_data, headers=admin_headers
    )
    assert response.status_code == 200
    updated_service = response.json()
    assert updated_service["name"] == "Premium Tire Rotation"
    assert updated_service["price"] == "25.00"


@pytest.mark.asyncio
async def test_delete_service(async_client, admin_headers):
    service_data = {
        "name": "Car Wash",
        "description": "Exterior and interior car wash",
        "price": 15.00,
        "duration": 20,
    }
    create_response = await async_client.post(
        "/api/v1/services/", json=service_data, headers=admin_headers
    )
    assert create_response.status_code == 200
    service_id = create_response.json()["service_id"]

    response = await async_client.delete(
        f"/api/v1/services/{service_id}", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Service deleted successfully"}

    response = await async_client.get(f"/services/{service_id}")
    assert response.status_code == 404
