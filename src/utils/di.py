"""
Dependency Injection container
"""

from typing import Dict, Any, Type, TypeVar, Callable
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.repositories.test_repository import TestRepository
from src.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.database.repositories.payment_repository import SQLAlchemyPaymentRepository
from src.infrastructure.database.repositories.test_repository import SQLAlchemyTestRepository

T = TypeVar('T')


class DIContainer:
    """Контейнер для dependency injection"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register(self, service_type: Type[T], implementation: Type[T]):
        """Регистрация сервиса"""
        self._services[service_type] = implementation
    
    def register_singleton(self, service_type: Type[T], instance: T):
        """Регистрация singleton сервиса"""
        self._instances[service_type] = instance
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]):
        """Регистрация фабрики для создания экземпляров"""
        self._factories[service_type] = factory
    
    def get(self, service_type: Type[T]) -> T:
        """Получение сервиса"""
        # Проверяем singleton
        if service_type in self._instances:
            return self._instances[service_type]
        
        # Используем фабрику
        if service_type in self._factories:
            factory = self._factories[service_type]
            return factory()
        
        # Создаем новый экземпляр
        if service_type in self._services:
            implementation = self._services[service_type]
            instance = implementation()
            return instance
        
        raise ValueError(f"Service {service_type} not registered")
    
    def is_registered(self, service_type: Type[T]) -> bool:
        """Проверка регистрации сервиса"""
        return (service_type in self._services or 
                service_type in self._instances or 
                service_type in self._factories)


# Глобальный контейнер
container = DIContainer()


def setup_dependencies():
    """Настройка зависимостей"""
    # Регистрация фабрик для репозиториев
    # Они будут создаваться с сессией БД при каждом запросе
    
    def user_repository_factory():
        from src.infrastructure.database.session import get_db_session_dependency
        # В реальном использовании сессия будет передаваться через dependency injection
        return SQLAlchemyUserRepository
    
    def payment_repository_factory():
        from src.infrastructure.database.session import get_db_session_dependency
        return SQLAlchemyPaymentRepository
    
    def test_repository_factory():
        from src.infrastructure.database.session import get_db_session_dependency
        return SQLAlchemyTestRepository
    
    # Регистрация фабрик
    container.register_factory(UserRepository, user_repository_factory)
    container.register_factory(PaymentRepository, payment_repository_factory)
    container.register_factory(TestRepository, test_repository_factory)
