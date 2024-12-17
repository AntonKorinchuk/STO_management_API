import pytest


@pytest.fixture()
def admin_headers():
    return {"Authorization": "Bearer test_admin_token"}


@pytest.mark.asyncio
async def test_register_user(async_client):
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "securepassword",
        "role": "CUSTOMER",
    }

    response = await async_client.post("api/v1/users/register", json=user_data)
    assert response.status_code == 200

    data = response.json()

    assert "user_id" in data
    assert "name" in data
    assert "email" in data
    assert "role" in data
    assert "created_at" in data

    assert data["name"] == "Test User"
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "CUSTOMER"

    assert isinstance(data["user_id"], int)
    assert isinstance(data["created_at"], str)


@pytest.mark.asyncio
async def test_login_user(async_client):
    user_data = {"email": "testuser@example.com", "password": "securepassword"}

    response = await async_client.post("/api/v1/users/login", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_read_users(async_client, admin_headers):
    response = await async_client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Очікуємо, що є хоча б один користувач


@pytest.mark.asyncio
async def test_update_user(async_client, admin_headers):
    user_data = {
        "name": "Updated User",
        "email": "updateduser@example.com",
        "role": "ADMIN",
    }

    response = await async_client.put(
        "/api/v1/users/1", json=user_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["email"] == "updateduser@example.com"
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_delete_user(async_client, admin_headers):
    # Створюємо користувача для видалення
    user_data = {
        "name": "User to Delete",
        "email": "deletethisuser@example.com",
        "password": "password",
        "role": "CUSTOMER",
    }
    create_response = await async_client.post("/api/v1/users/register", json=user_data)
    assert create_response.status_code == 200
    user_id = create_response.json()["user_id"]

    delete_response = await async_client.delete(
        f"/api/v1/users/{user_id}", headers=admin_headers
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "User deleted successfully"}
