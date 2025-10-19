"""
User repository interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import User


class UserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def get_admins(self) -> List[User]:
        """Получить список администраторов"""
        pass
    
    @abstractmethod
    async def get_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить активных пользователей"""
        pass
    
    @abstractmethod
    async def get_users_count(self) -> int:
        """Получить количество пользователей"""
        pass
    
    @abstractmethod
    async def block_user(self, user_id: int) -> bool:
        """Заблокировать пользователя"""
        pass
    
    @abstractmethod
    async def unblock_user(self, user_id: int) -> bool:
        """Разблокировать пользователя"""
        pass
