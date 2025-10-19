"""
Authentication middleware
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.use_cases.user.create_or_update_user import CreateOrUpdateUserUseCase
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.config.settings import settings


class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентификации пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с аутентификацией"""
        
        # Получаем пользователя из события
        telegram_user = None
        if isinstance(event, Message):
            telegram_user = event.from_user
        elif isinstance(event, CallbackQuery):
            telegram_user = event.from_user
        
        if not telegram_user:
            # Если нет пользователя, пропускаем middleware
            return await handler(event, data)
        
        # Проверяем, заблокирован ли пользователь
        if telegram_user.id in settings.admin_telegram_ids:
            # Админ - пропускаем все проверки
            data["is_admin"] = True
            data["user"] = None  # TODO: Получить пользователя из БД
            return await handler(event, data)
        
        try:
            # Получаем или создаем пользователя в БД
            async with get_db_session() as session:
                user_repository = SQLAlchemyUserRepository(session)
                create_or_update_user_uc = CreateOrUpdateUserUseCase(user_repository)
                
                db_user = await create_or_update_user_uc.execute(telegram_user)
                
                # Проверяем, заблокирован ли пользователь
                if db_user.is_blocked:
                    logger.warning(f"Blocked user {db_user.telegram_id} tried to use bot")
                    
                    if isinstance(event, Message):
                        await event.answer(
                            "❌ Ваш аккаунт заблокирован. Обратитесь в поддержку для получения помощи."
                        )
                    elif isinstance(event, CallbackQuery):
                        await event.answer(
                            "❌ Ваш аккаунт заблокирован. Обратитесь в поддержку для получения помощи.",
                            show_alert=True
                        )
                    
                    return  # Не выполняем обработчик
                
                # Добавляем пользователя в данные
                data["user"] = db_user
                data["is_admin"] = db_user.is_admin
                
        except Exception as e:
            logger.error(f"Error in auth middleware for user {telegram_user.id}: {e}")
            # В случае ошибки продолжаем выполнение без пользователя
            data["user"] = None
            data["is_admin"] = False
        
        return await handler(event, data)
