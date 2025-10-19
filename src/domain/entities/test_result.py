"""
Test Result entity - результат теста
"""

from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestResult:
    """Результат теста"""
    
    id: int
    user_id: int
    score: int
    total_questions: int = 6
    attempts: int = 1
    passed: bool = False
    answers_json: Optional[Dict[str, Any]] = None
    completed_at: datetime = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def percentage(self) -> float:
        """Процент правильных ответов"""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100
    
    @property
    def is_excellent(self) -> bool:
        """Отличный результат (100%)"""
        return self.score == self.total_questions
    
    @property
    def is_good(self) -> bool:
        """Хороший результат (>=80%)"""
        return self.percentage >= 80.0
    
    @property
    def is_poor(self) -> bool:
        """Плохой результат (<50%)"""
        return self.percentage < 50.0
    
    def get_result_message(self) -> str:
        """Получить сообщение результата"""
        if self.is_excellent:
            if self.attempts == 1:
                return "Кто это? Просто Киборг! Помешанный на аптечках!"
            else:
                return "Мы поняли, что ты можешь запомнить три слова!"
        else:
            return "Не все ответы правильны, так что аптечку лучше [купить]"
