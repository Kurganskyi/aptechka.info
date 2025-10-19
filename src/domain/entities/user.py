"""
User entity - пользователь
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """Пользователь бота"""
    
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_blocked: bool = False
    is_admin: bool = False
    referrer_id: Optional[int] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        parts = [self.first_name, self.last_name]
        return " ".join(filter(None, parts)) or "Неизвестно"
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя"""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    def is_active(self) -> bool:
        """Проверка активности пользователя"""
        return not self.is_blocked
    
    def update_activity(self):
        """Обновление времени последней активности"""
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
