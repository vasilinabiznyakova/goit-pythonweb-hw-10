import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import config


class DatabaseSessionManager:
    """Own the async SQLAlchemy engine and produce transactional sessions."""

    def __init__(self, url: str):
        """Create an engine and session factory for ``url``."""
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Yield a session and roll it back when SQLAlchemy raises an error."""
        if self._session_maker is None:
            raise RuntimeError("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_all(self):
        """Create all application tables that do not already exist."""
        if self._engine is None:
            raise RuntimeError("Database engine is not initialized")
        from src.database.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """FastAPI dependency yielding one asynchronous database session."""
    async with sessionmanager.session() as session:
        yield session
