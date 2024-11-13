from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

async_engine = create_async_engine(
    settings.mysql_async_url,
    pool_pre_ping=True,
    pool_size=settings.db_async_pool_size,
    pool_recycle=settings.db_async_pool_recycle,
    max_overflow=settings.db_async_max_overflow,
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

sync_engine = create_engine(
    settings.mysql_url,
    pool_size=settings.db_sync_pool_size,
    pool_recycle=settings.db_sync_pool_recycle,
    max_overflow=settings.db_sync_pool_size,
)

SessionLocal = sessionmaker(
    bind=sync_engine, expire_on_commit=False, class_=Session
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
