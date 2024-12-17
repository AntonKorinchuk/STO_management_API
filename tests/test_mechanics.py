import pytest
from datetime import date, timedelta


@pytest.fixture()
def mechanic_admin_headers():
    return {"Authorization": "Bearer test_mechanic_admin_token"}


@pytest.mark.asyncio
async def test_register_mechanic(async_client, override_get_current_mechanic):

    birth_date = date.today() - timedelta(days=365 * 25)

    mechanic_data = {
        "name": "John Mechanic",
        "birth_date": birth_date.isoformat(),
        "login": "john_mech",
        "password": "mechanicpass123",
        "role": "ADMIN",
        "position": "Senior Mechanic",
    }

    response = await async_client.post("/api/v1/mechanics/register", json=mechanic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Mechanic"
    assert data["login"] == "john_mech"
    assert data["position"] == "Senior Mechanic"
    assert data["role"] == "ADMIN"
    assert "mechanic_id" in data


@pytest.mark.asyncio
async def test_get_current_mechanic(async_client, override_get_current_mechanic):
    response = await async_client.get("/api/v1/mechanics/me")
    assert response.status_code == 200
    data = response.json()
    assert "mechanic_id" in data
    assert "name" in data
    assert "login" in data
    assert "role" in data


@pytest.mark.asyncio
async def test_read_mechanics(async_client, override_get_current_mechanic):
    response = await async_client.get("/api/v1/mechanics/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_update_mechanic(async_client, override_get_current_mechanic):
    birth_date = date.today() - timedelta(days=365 * 25)

    register_data = {
        "name": "Update Mechanic",
        "birth_date": birth_date.isoformat(),
        "login": "update_mech",
        "password": "updatepassword123",
        "role": "MECHANIC",
        "position": "Mechanic",
    }
    register_response = await async_client.post(
        "/api/v1/mechanics/register", json=register_data
    )
    mechanic_id = register_response.json()["mechanic_id"]

    update_data = {
        "name": "Mechanic",
        "birth_date": birth_date.isoformat(),
        "login": "update_mech",
        "role": "MECHANIC",
        "position": "Senior",
    }
    response = await async_client.put(
        f"/api/v1/mechanics/{mechanic_id}", json=update_data
    )
    assert response.status_code == 200
    updated_mechanic = response.json()
    assert updated_mechanic["name"] == "Mechanic"
    assert updated_mechanic["position"] == "Senior"
    assert updated_mechanic["login"] == "update_mech"


@pytest.mark.asyncio
async def test_delete_mechanic(async_client, override_get_current_mechanic):
    birth_date = date.today() - timedelta(days=365 * 25)

    register_data = {
        "name": "Delete Mechanic",
        "birth_date": birth_date.isoformat(),
        "login": "delete_mech",
        "password": "deletepassword123",
        "role": "MECHANIC",
        "position": "Junior Mechanic",
    }
    register_response = await async_client.post(
        "/api/v1/mechanics/register", json=register_data
    )
    mechanic_id = register_response.json()["mechanic_id"]

    response = await async_client.delete(f"/api/v1/mechanics/{mechanic_id}")
    assert response.status_code == 200
    assert response.json() == {"detail": "Mechanic deleted successfully"}


@pytest.mark.asyncio
async def test_get_mechanic_appointments(async_client, override_get_current_mechanic):
    response = await async_client.get("/api/v1/mechanics/appointments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
