import pytest


@pytest.fixture()
def admin_headers():
    return {"Authorization": "Bearer test_admin_token"}


@pytest.mark.asyncio
async def test_create_car(async_client):
    car_data = {
        "user_id": 1,
        "brand": "Toyota",
        "model": "Camry",
        "year": 2022,
        "plate_number": "ABf123",
        "vin": "1HGBH41JfMN109186",
    }

    response = await async_client.post("/api/v1/cars/", json=car_data)
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == "Toyota"
    assert data["vin"] == "1HGBH41JfMN109186"


@pytest.mark.asyncio
async def test_read_cars(async_client, admin_headers):

    response = await async_client.get("/api/v1/cars/", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_read_car(async_client, admin_headers):

    car_data = {
        "user_id": 1,
        "brand": "Toyota",
        "model": "Camry",
        "year": 2022,
        "plate_number": "ABC1f3",
        "vin": "1HGBH41JXMN10f186",
    }
    response = await async_client.post(
        "/api/v1/cars/", json=car_data, headers=admin_headers
    )
    assert response.status_code == 200
    created_car = response.json()
    car_id = created_car["car_id"]

    response = await async_client.get(f"/api/v1/cars/{car_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["car_id"] == car_id
    assert data["brand"] == "Toyota"


@pytest.mark.asyncio
async def test_update_car(async_client, admin_headers):

    car_data = {
        "user_id": 1,
        "brand": "Toyota",
        "model": "Camry",
        "year": 2022,
        "plate_number": "ABC123",
        "vin": "1HGBH41JXMN109186",
    }
    response = await async_client.post(
        "/api/v1/cars/", json=car_data, headers=admin_headers
    )
    assert response.status_code == 200
    created_car = response.json()
    car_id = created_car["car_id"]

    update_data = {"brand": "Honda", "plate_number": "XYZ789"}
    response = await async_client.put(
        f"/api/v1/cars/{car_id}", json=update_data, headers=admin_headers
    )
    assert response.status_code == 200
    updated_car = response.json()
    assert updated_car["brand"] == "Honda"
    assert updated_car["plate_number"] == "XYZ789"


@pytest.mark.asyncio
async def test_delete_car(async_client, admin_headers):

    car_data = {
        "user_id": 1,
        "brand": "Toyota",
        "model": "Camry",
        "year": 2022,
        "plate_number": "AaC123",
        "vin": "1HGBH41JXMN1091a6",
    }
    response = await async_client.post(
        "/api/v1/cars/", json=car_data, headers=admin_headers
    )
    assert response.status_code == 200
    created_car = response.json()
    car_id = created_car["car_id"]

    response = await async_client.delete(
        f"/api/v1/cars/{car_id}", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Car deleted successfully"}

    response = await async_client.get(f"/cars/{car_id}", headers=admin_headers)
    assert response.status_code == 404
