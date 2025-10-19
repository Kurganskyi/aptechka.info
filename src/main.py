"""
Main entry point для Telegram бота
"""

import asyncio
import signal
import sys
from typing import NoReturn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from src.config.settings import settings
from src.config.logging import setup_logging
from src.infrastructure.database.connection import db_connection
from src.infrastructure.database.models import Base
from src.infrastructure.telegram.bot import create_bot, create_dispatcher
from src.infrastructure.webhook.server import webhook_server
from src.utils.di import setup_dependencies


class BotApplication:
    """Основной класс приложения бота"""
    
    def __init__(self):
        self.bot: Bot = None
        self.dp: Dispatcher = None
        self.webhook_runner = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Инициализация приложения"""
        try:
            # Настройка логирования
            setup_logging()
            logger.info("Starting Telegram bot application...")
            
            # Инициализация БД
            await db_connection.initialize()
            logger.info("Database connection established")
            
            # Создание таблиц (только для разработки)
            if settings.is_development:
                await self._create_tables()
            
            # Настройка зависимостей
            setup_dependencies()
            
            # Создание бота и диспетчера
            self.bot = create_bot()
            self.dp = create_dispatcher()
            
            # Запуск webhook сервера
            if settings.webhook_host:
                self.webhook_runner = await webhook_server.start(
                    port=settings.webhook_port
                )
                logger.info("Webhook server started")
            
            # Настройка обработчиков сигналов
            self._setup_signal_handlers()
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    async def _create_tables(self):
        """Создание таблиц БД (только для разработки)"""
        try:
            async with db_connection.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов для graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Запуск бота"""
        try:
            logger.info("Starting bot polling...")
            
            # Запуск polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
            )
            
        except Exception as e:
            logger.error(f"Error during bot polling: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down application...")
        
        try:
            # Остановка polling
            if self.dp:
                await self.dp.stop_polling()
                logger.info("Bot polling stopped")
            
            # Остановка webhook сервера
            if self.webhook_runner:
                await self.webhook_runner.cleanup()
                logger.info("Webhook server stopped")
            
            # Закрытие сессий бота
            if self.bot:
                session = await self.bot.session()
                await session.close()
                logger.info("Bot session closed")
            
            # Закрытие подключения к БД
            await db_connection.close()
            logger.info("Database connection closed")
            
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


async def main():
    """Главная функция"""
    app = BotApplication()
    
    try:
        await app.initialize()
        
        # Ожидание сигнала завершения
        shutdown_task = asyncio.create_task(app._shutdown_event.wait())
        run_task = asyncio.create_task(app.run())
        
        # Ожидание завершения одной из задач
        done, pending = await asyncio.wait(
            [shutdown_task, run_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отмена оставшихся задач
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(1)
    finally:
        await app.shutdown()


def run_bot() -> NoReturn:
    """Запуск бота (точка входа)"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
