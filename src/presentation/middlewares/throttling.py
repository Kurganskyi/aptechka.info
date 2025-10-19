"""
Throttling middleware
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger
from datetime import datetime, timedelta

from collections import defaultdict


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, rate_limit: int = 10, time_window: int = 60):
        """
        Args:
            rate_limit: Максимальное количество запросов
            time_window: Временное окно в секундах
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.user_requests = defaultdict(list)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с проверкой лимитов"""
        
        # Получаем ID пользователя
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        # Проверяем лимиты
        now = datetime.utcnow()
        user_requests = self.user_requests[user_id]
        
        # Удаляем старые запросы
        cutoff_time = now - timedelta(seconds=self.time_window)
        user_requests[:] = [req_time for req_time in user_requests if req_time > cutoff_time]
        
        # Проверяем, превышен ли лимит
        if len(user_requests) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            
            if isinstance(event, Message):
                await event.answer(
                    "⏰ Слишком много запросов. Пожалуйста, подождите немного."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⏰ Слишком много запросов. Пожалуйста, подождите немного.",
                    show_alert=True
                )
            
            return  # Не выполняем обработчик
        
        # Добавляем текущий запрос
        user_requests.append(now)
        
        return await handler(event, data)
