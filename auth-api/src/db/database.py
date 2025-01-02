from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from core.config import settings


class Base(DeclarativeBase):
    pass


SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.db.db_user}:{settings.db.db_pass}@{settings.db.db_host}:{settings.db.db_port}/{settings.db.db_name}"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
