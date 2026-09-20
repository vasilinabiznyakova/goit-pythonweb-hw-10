from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """Persist and retrieve user accounts."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an asynchronous database session."""
        self.db = session

    async def get_by_username(self, username: str) -> User | None:
        """Return a user by username, or ``None`` when absent."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email address, or ``None`` when absent."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, body: UserCreate, hashed_password: str) -> User:
        """Create a regular user with the supplied password hash."""
        user = User(
            username=body.username,
            email=str(body.email),
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirm_email(self, user: User) -> None:
        """Mark a user's email as confirmed."""
        user.confirmed = True
        await self.db.commit()

    async def update_avatar(self, user: User, url: str) -> User:
        """Store a new avatar URL for a user."""
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> None:
        """Replace a user's password hash."""
        user.hashed_password = hashed_password
        await self.db.commit()
