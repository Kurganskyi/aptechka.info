#!/usr/bin/env python3
"""
Запуск основного бота с исправленными настройками
"""

import os
import sys
import asyncio
from loguru import logger

# Настройка переменных окружения
os.environ['BOT_TOKEN'] = '8220071391:AAF3z2o1RC3m6yn6XiCUWX1fNcx9WH0EILA'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/aptechka'
os.environ['BEPAID_SHOP_ID'] = 'test_shop'
os.environ['BEPAID_SECRET_KEY'] = 'test_key'
os.environ['BEPAID_API_URL'] = 'https://api.bepaid.by'
os.environ['BEPAID_WEBHOOK_SECRET'] = 'test_webhook_secret'
os.environ['ADMIN_TELEGRAM_IDS'] = '123456789,987654321'
os.environ['REVIEWS_CHAT_URL'] = 'https://t.me/test_reviews'
os.environ['SUPPORT_CHAT_URL'] = 'https://t.me/test_support'
os.environ['SECRET_KEY'] = 'test_secret_key_12345'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEBUG'] = 'true'
os.environ['WEBHOOK_PATH'] = '/webhook/bepaid'

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🚀 Запуск основного Telegram бота...")
        
        # Импорт основного модуля
        from src.main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
