from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, body: UserCreate, hashed_password: str) -> User:
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
        user.confirmed = True
        await self.db.commit()

    async def update_avatar(self, user: User, url: str) -> User:
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
