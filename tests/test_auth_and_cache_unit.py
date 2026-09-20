"""Unit tests for JWT, authorization, and Redis serialization."""

import json
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from jose import jwt

from src.conf.config import config
from src.database.models import User, UserRole
from src.services import cache
from src.services.auth import (
    create_token, decode_token, get_current_admin_user, get_current_user,
    hash_password, verify_password,
)


def test_password_hash_and_typed_tokens():
    hashed = hash_password("secret-password")
    assert verify_password("secret-password", hashed)
    assert not verify_password("wrong", hashed)
    token = create_token("alice", "access", 60)
    assert decode_token(token, "access") == "alice"
    with pytest.raises(HTTPException):
        decode_token(token, "email")
    malformed = jwt.encode({"type": "access"}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    with pytest.raises(HTTPException):
        decode_token(malformed, "access")


@pytest.mark.asyncio
async def test_cache_roundtrip(mock_redis):
    user = User(id=7, username="alice", email="a@example.com", hashed_password="hash",
                confirmed=True, role=UserRole.ADMIN)
    await cache.cache_user(user)
    payload = mock_redis["set"].await_args.args[1]
    mock_redis["get"].return_value = payload
    cached = await cache.get_cached_user("alice")
    assert cached.id == 7
    assert cached.role == UserRole.ADMIN
    await cache.delete_cached_user("alice")
    mock_redis["delete"].assert_awaited()


@pytest.mark.asyncio
async def test_invalid_cache_is_deleted(mock_redis):
    mock_redis["get"].return_value = json.dumps({"invalid": True})
    assert await cache.get_cached_user("alice") is None
    mock_redis["delete"].assert_awaited_once()


@pytest.mark.asyncio
async def test_current_user_cache_hit_and_roles(monkeypatch):
    admin = User(id=1, username="admin", email="a@example.com", hashed_password="h",
                 confirmed=True, role=UserRole.ADMIN)
    monkeypatch.setattr("src.services.auth.get_cached_user", AsyncMock(return_value=admin))
    db = AsyncMock()
    token = create_token("admin", "access", 60)
    assert await get_current_user(token, db) is admin
    assert await get_current_admin_user(admin) is admin
    admin.role = UserRole.USER
    with pytest.raises(HTTPException) as error:
        await get_current_admin_user(admin)
    assert error.value.status_code == 403
