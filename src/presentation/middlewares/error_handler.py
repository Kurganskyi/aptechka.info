"""
Error handler middleware
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from loguru import logger

from src.domain.exceptions import DomainException


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с обработкой ошибок"""
        
        try:
            return await handler(event, data)
            
        except DomainException as e:
            # Обработка доменных исключений
            logger.warning(f"Domain exception: {e}")
            await self._send_error_message(event, "❌ " + str(e))
            
        except TelegramBadRequest as e:
            # Обработка ошибок Telegram API
            logger.error(f"Telegram API error: {e}")
            await self._send_error_message(event, "❌ Произошла ошибка при обработке запроса.")
            
        except TelegramNetworkError as e:
            # Обработка сетевых ошибок
            logger.error(f"Network error: {e}")
            await self._send_error_message(event, "❌ Проблемы с сетью. Попробуйте позже.")
            
        except Exception as e:
            # Обработка всех остальных ошибок
            logger.error(f"Unexpected error: {e}", exc_info=True)
            await self._send_error_message(event, "❌ Произошла неожиданная ошибка. Попробуйте позже.")
    
    async def _send_error_message(self, event: TelegramObject, message: str):
        """Отправка сообщения об ошибке"""
        try:
            if isinstance(event, Message):
                await event.answer(message)
            elif isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
