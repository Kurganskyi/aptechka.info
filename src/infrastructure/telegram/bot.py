"""
Bot instance creation
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.config.settings import settings
from src.presentation.middlewares.logging import LoggingMiddleware
from src.presentation.middlewares.auth import AuthMiddleware
from src.presentation.middlewares.throttling import ThrottlingMiddleware
from src.presentation.middlewares.error_handler import ErrorHandlerMiddleware
from src.presentation.handlers import start, menu, payment, test, faq, admin, post_payment


def create_bot() -> Bot:
    """Создание экземпляра бота"""
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )


def create_dispatcher() -> Dispatcher:
    """Создание диспетчера"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация middleware (порядок важен!)
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(payment.router)
    dp.include_router(test.router)
    dp.include_router(faq.router)
    dp.include_router(admin.router)
    dp.include_router(post_payment.router)
    
    return dp
