"""
Create or update user use case
"""

from datetime import datetime
from loguru import logger

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.exceptions import UserNotFoundException


class CreateOrUpdateUserUseCase:
    """Use case для создания или обновления пользователя"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, telegram_user) -> User:
        """
        Создать или обновить пользователя
        
        Args:
            telegram_user: Объект пользователя от Telegram
        
        Returns:
            Пользователь из БД
        """
        try:
            # Ищем существующего пользователя
            existing_user = await self.user_repository.get_by_telegram_id(telegram_user.id)
            
            if existing_user:
                # Обновляем данные существующего пользователя
                existing_user.username = telegram_user.username
                existing_user.first_name = telegram_user.first_name
                existing_user.last_name = telegram_user.last_name
                existing_user.language_code = telegram_user.language_code
                existing_user.update_activity()
                
                updated_user = await self.user_repository.update(existing_user)
                logger.info(f"User updated: {updated_user.telegram_id}")
                return updated_user
            else:
                # Создаем нового пользователя
                new_user = User(
                    id=0,  # Будет установлен после сохранения
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    language_code=telegram_user.language_code,
                    is_blocked=False,
                    is_admin=False,
                    referrer_id=None,
                    created_at=datetime.utcnow(),
                    last_activity_at=datetime.utcnow(),
                )
                
                created_user = await self.user_repository.create(new_user)
                logger.info(f"User created: {created_user.telegram_id}")
                return created_user
                
        except Exception as e:
            logger.error(f"Error creating or updating user {telegram_user.id}: {e}")
            raise
