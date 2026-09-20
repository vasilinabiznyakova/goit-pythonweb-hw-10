"""Shared isolated database and API client fixtures."""

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from main import app
from src.database.db import get_db
from src.database.models import Base, User, UserRole
from src.services.auth import create_token, hash_password


engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    """Recreate all tables and seed regular and administrator accounts."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with TestingSession() as session:
        session.add_all(
            [
                User(
                    username="regular",
                    email="regular@example.com",
                    hashed_password=hash_password("password1"),
                    confirmed=True,
                    role=UserRole.USER,
                ),
                User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=hash_password("password1"),
                    confirmed=True,
                    role=UserRole.ADMIN,
                ),
            ]
        )
        await session.commit()
    yield


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Keep tests independent of a running Redis service."""
    get = AsyncMock(return_value=None)
    set_ = AsyncMock(return_value=True)
    delete = AsyncMock(return_value=1)
    monkeypatch.setattr("src.services.cache.redis_client.get", get)
    monkeypatch.setattr("src.services.cache.redis_client.set", set_)
    monkeypatch.setattr("src.services.cache.redis_client.delete", delete)
    return {"get": get, "set": set_, "delete": delete}


@pytest.fixture
def client():
    """Return a TestClient wired to the in-memory test database."""
    async def override_get_db():
        async with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user_headers():
    token = create_token("regular", "access", 3600)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    token = create_token("admin", "access", 3600)
    return {"Authorization": f"Bearer {token}"}
