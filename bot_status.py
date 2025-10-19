#!/usr/bin/env python3
"""
Скрипт для проверки статуса бота и базы данных
"""

import asyncio
import asyncpg
import requests
from loguru import logger

async def check_database():
    """Проверка подключения к базе данных"""
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='aptechka',
            user='postgres',
            password='postgres'
        )
        
        version = await conn.fetchval('SELECT version()')
        await conn.close()
        
        logger.success(f"✅ База данных: {version}")
        return True
        
    except Exception as e:
        logger.error(f"❌ База данных: {e}")
        return False

def check_bot_token():
    """Проверка токена бота"""
    try:
        token = "8220071391:AAF3z2o1RC3m6yn6XiCUWX1fNcx9WH0EILA"
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                logger.success(f"✅ Бот: @{bot_info['username']} - {bot_info['first_name']}")
                return True
        
        logger.error(f"❌ Бот: Ошибка API - {response.status_code}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Бот: {e}")
        return False

async def main():
    """Главная функция проверки"""
    logger.info("🔍 Проверка статуса системы...")
    
    # Проверка базы данных
    db_ok = await check_database()
    
    # Проверка бота
    bot_ok = check_bot_token()
    
    if db_ok and bot_ok:
        logger.success("🎉 Система готова к работе!")
        return True
    else:
        logger.warning("⚠️ Есть проблемы с системой")
        return False

if __name__ == "__main__":
    asyncio.run(main())
