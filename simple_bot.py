#!/usr/bin/env python3
"""
Простой тестовый бот для проверки работы
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8220071391:AAF3z2o1RC3m6yn6XiCUWX1fNcx9WH0EILA"

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я тестовый бот для проверки работы.\n\n"
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/help - помощь\n"
        "/test - тест"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "📚 Помощь по боту:\n\n"
        "Это тестовый бот для проверки работы системы.\n"
        "Если вы видите это сообщение, значит бот работает правильно!"
    )

@dp.message(Command("test"))
async def test_command(message: types.Message):
    """Обработчик команды /test"""
    await message.answer("✅ Тест прошел успешно! Бот работает.")

@dp.message()
async def echo_message(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(f"Вы написали: {message.text}")

async def main():
    """Главная функция"""
    try:
        logger.info("Запуск тестового бота...")
        
        # Удаление webhook (если был установлен)
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запуск polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
