from typing import AsyncGenerator

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

DATABASE_URL = "sqlite+aiosqlite:///./async0.db"
engine: AsyncEngine = create_async_engine(DATABASE_URL, future=True)
Base = declarative_base()


class IdeaBase(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    initial = Column(String, index=True)
    refined = Column(String, index=True)
    steps = Column(String, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), onupdate=func.now()
    )


async def get_sessionmaker():
    return async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    maker_ = await get_sessionmaker()

    async with maker_() as session:
        try:
            yield session
        finally:
            await session.close()
