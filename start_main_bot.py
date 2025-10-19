#!/usr/bin/env python3
"""
Запуск основного бота с полной функциональностью
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

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🚀 Запуск основного Telegram бота...")
        logger.info("📋 Конфигурация:")
        logger.info(f"   - Токен бота: {os.environ['BOT_TOKEN'][:20]}...")
        logger.info(f"   - База данных: {os.environ['DATABASE_URL']}")
        logger.info(f"   - Окружение: {os.environ['ENVIRONMENT']}")
        
        # Импорт основного модуля
        from src.main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()
        
        # Попытка запустить простой бот как fallback
        logger.info("🔄 Попытка запуска простого бота...")
        try:
            from simple_bot import main as simple_main
            await simple_main()
        except Exception as fallback_error:
            logger.error(f"❌ Ошибка запуска простого бота: {fallback_error}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
