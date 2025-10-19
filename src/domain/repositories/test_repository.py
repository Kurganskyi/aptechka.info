"""
Test repository interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.test_result import TestResult


class TestRepository(ABC):
    """Интерфейс репозитория тестов"""
    
    @abstractmethod
    async def create_test_result(self, test_result: TestResult) -> TestResult:
        """Создать результат теста"""
        pass
    
    @abstractmethod
    async def get_user_test_results(self, user_id: int) -> List[TestResult]:
        """Получить результаты тестов пользователя"""
        pass
    
    @abstractmethod
    async def get_latest_test_result(self, user_id: int) -> Optional[TestResult]:
        """Получить последний результат теста пользователя"""
        pass
    
    @abstractmethod
    async def get_test_result_by_id(self, test_result_id: int) -> Optional[TestResult]:
        """Получить результат теста по ID"""
        pass
    
    @abstractmethod
    async def update_test_result(self, test_result: TestResult) -> TestResult:
        """Обновить результат теста"""
        pass
    
    @abstractmethod
    async def get_test_statistics(self) -> dict:
        """Получить статистику тестов"""
        pass
