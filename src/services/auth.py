from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.database.models import User, UserRole
from src.repository.users import UserRepository
from src.services.cache import cache_user, get_cached_user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Hash a plain-text password using the configured password context."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str, token_type: str, expires_in: int) -> str:
    """Create a signed JWT for a subject and a narrowly scoped token type."""
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(UTC) + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str) -> str:
    """Decode a JWT and return its subject if its type matches."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        if payload.get("type") != expected_type or not payload.get("sub"):
            raise JWTError()
        return payload["sub"]
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from error


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Resolve the authenticated user from Redis, falling back to the database."""
    username = decode_token(token, "access")
    user = await get_cached_user(username)
    if user is None:
        user = await UserRepository(db).get_by_username(username)
        if user is not None:
            await cache_user(user)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


async def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    """Require the authenticated user to have the administrator role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required"
        )
    return user
