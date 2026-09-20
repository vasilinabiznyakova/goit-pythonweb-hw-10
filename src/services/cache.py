"""Redis-backed current-user cache with graceful failure handling."""

import json

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.conf.config import config
from src.database.models import User, UserRole


redis_client = Redis.from_url(config.REDIS_URL, decode_responses=True)


def user_cache_key(username: str) -> str:
    """Return the namespaced Redis key for a username."""
    return f"current_user:{username}"


async def get_cached_user(username: str) -> User | None:
    """Read a user from Redis, returning ``None`` on a miss or Redis failure."""
    try:
        raw = await redis_client.get(user_cache_key(username))
    except RedisError:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            avatar=data.get("avatar"),
            confirmed=data["confirmed"],
            role=UserRole(data["role"]),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        await delete_cached_user(username)
        return None


async def cache_user(user: User) -> None:
    """Cache the authentication-relevant user fields with a finite TTL."""
    payload = json.dumps(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "confirmed": user.confirmed,
            "role": user.role.value,
        }
    )
    try:
        await redis_client.set(
            user_cache_key(user.username), payload, ex=config.USER_CACHE_TTL_SECONDS
        )
    except RedisError:
        pass


async def delete_cached_user(username: str) -> None:
    """Invalidate a cached user after mutable account data changes."""
    try:
        await redis_client.delete(user_cache_key(username))
    except RedisError:
        pass
