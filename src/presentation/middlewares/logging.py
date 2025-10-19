"""
Logging middleware
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger
from datetime import datetime


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования действий пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с логированием"""
        start_time = datetime.utcnow()
        
        # Получаем информацию о пользователе
        user_id = None
        username = None
        event_type = type(event).__name__
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            username = event.from_user.username
            content = event.text or f"[{event.content_type}]"
            
            logger.info(
                f"Message from user {user_id} (@{username}): {content[:100]}"
            )
            
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username
            callback_data = event.data
            
            logger.info(
                f"Callback from user {user_id} (@{username}): {callback_data}"
            )
        
        # Выполняем обработчик
        try:
            result = await handler(event, data)
            
            # Логируем успешное выполнение
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.debug(
                f"Handler executed successfully for user {user_id} in {execution_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            # Логируем ошибку
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(
                f"Handler error for user {user_id} after {execution_time:.3f}s: {e}"
            )
            raise
