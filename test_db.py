#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к базе данных
"""

import asyncio
import asyncpg
from loguru import logger

async def test_database_connection():
    """Тест подключения к базе данных"""
    try:
        # Параметры подключения
        connection_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'aptechka',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        logger.info("Попытка подключения к базе данных...")
        
        # Подключение к базе данных
        conn = await asyncpg.connect(**connection_params)
        
        # Тестовый запрос
        result = await conn.fetchval('SELECT version()')
        logger.success(f"Подключение успешно! Версия PostgreSQL: {result}")
        
        # Закрытие соединения
        await conn.close()
        logger.info("Соединение закрыто")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
