from datetime import date

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from crud.mechanic import get_current_mechanic
from main import app
from database import get_async_db, Base
from models.mechanic import MechanicRole, Mechanic
from models.user import User, UserRole
from crud.user import get_current_user


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True, scope="module")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
def override_get_async_db():
    async def get_db_override():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_async_db] = get_db_override


@pytest.fixture()
def override_get_current_user():
    def mock_get_current_user():
        return User(user_id=1, name="test_user", role=UserRole.ADMIN)

    app.dependency_overrides[get_current_user] = mock_get_current_user


@pytest.fixture()
def override_get_current_mechanic():
    def mock_get_current_mechanic():
        return Mechanic(
            mechanic_id=1,
            name="Test Mechanic",
            birth_date=date(1991, 1, 1),
            login="test_mechanic",
            role=MechanicRole.ADMIN,
            position="Test Position",
        )

    app.dependency_overrides[get_current_mechanic] = mock_get_current_mechanic


@pytest.fixture()
async def async_client(override_get_async_db, override_get_current_user):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
