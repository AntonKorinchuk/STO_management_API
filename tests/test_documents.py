import os
from datetime import date, datetime, timedelta
import pytest
from pathlib import Path

from dotenv import load_dotenv
from jose import jwt
from models.mechanic import Mechanic, MechanicRole
from crud.mechanic import get_current_mechanic


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

UPLOAD_DIRECTORY = "uploads/documents"
TEST_FILE_PATH = "tests/test_files"
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)
Path(TEST_FILE_PATH).mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="module", autouse=True)
def create_test_files():
    with open(f"{TEST_FILE_PATH}/test.pdf", "wb") as f:
        f.write(b"PDF file content")
    with open(f"{TEST_FILE_PATH}/test_invalid.txt", "wb") as f:
        f.write(b"Invalid file content")


def override_get_current_mechanic():
    mechanic_data = {
        "sub": "test_mechanic",
        "role": MechanicRole.ADMIN.value,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    token = jwt.encode(mechanic_data, SECRET_KEY, algorithm=ALGORITHM)

    def mock_get_current_mechanic():
        return Mechanic(
            mechanic_id=1,
            name="Test Mechanic",
            birth_date=date(1991, 1, 1),
            login="test_mechanic",
            role=MechanicRole.ADMIN,
            position="Test Position",
        )

    from main import app

    app.dependency_overrides[get_current_mechanic] = mock_get_current_mechanic

    return token


@pytest.fixture()
def mechanic_headers():
    token = override_get_current_mechanic()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers():
    token = override_get_current_mechanic()
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_document(async_client, mechanic_headers):
    with open(f"{TEST_FILE_PATH}/test.pdf", "rb") as file:
        response = await async_client.post(
            "api/v1/documents/upload",
            headers=mechanic_headers,
            files={"file": ("test.pdf", file, "application/pdf")},
            data={"document_type": "PASSPORT"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"].endswith("test.pdf")
    assert data["type"] == "PASSPORT"


@pytest.mark.asyncio
async def test_upload_invalid_document(async_client, mechanic_headers):
    with open(f"{TEST_FILE_PATH}/test_invalid.txt", "rb") as file:
        response = await async_client.post(
            "api/v1/documents/upload",
            headers=mechanic_headers,
            files={"file": ("test_invalid.txt", file, "text/plain")},
            data={"document_type": "PASSPORT"},
        )
    assert response.status_code == 400
    assert (
        response.json()["detail"] == "Invalid file type. Allowed types: PDF, JPG, PNG"
    )


@pytest.mark.asyncio
async def test_get_mechanic_documents(async_client, mechanic_headers):
    response = await async_client.get("api/v1/documents/", headers=mechanic_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_all_documents(async_client, admin_headers):
    response = await async_client.get("api/v1/documents/all", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
