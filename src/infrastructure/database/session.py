"""
Database session management
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.connection import db_connection
from loguru import logger


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для работы с сессией БД
    Автоматически закрывает сессию и откатывает транзакцию при ошибке
    """
    session = db_connection.get_session()
    try:
        yield session
        await session.commit()
        logger.debug("Database session committed successfully")
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session rolled back due to error: {e}")
        raise
    finally:
        await session.close()
        logger.debug("Database session closed")


async def get_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI/aiogram для инъекции сессии БД
    """
    async with get_db_session() as session:
        yield session
