"""
Payment repository interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from src.domain.entities.payment import Order, Product, UserProduct, PaymentStatus


class PaymentRepository(ABC):
    """Интерфейс репозитория платежей"""
    
    # Products
    @abstractmethod
    async def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Получить продукт по slug"""
        pass
    
    @abstractmethod
    async def get_all_products(self) -> List[Product]:
        """Получить все продукты"""
        pass
    
    @abstractmethod
    async def get_active_products(self) -> List[Product]:
        """Получить активные продукты"""
        pass
    
    # Orders
    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        """Создать заказ"""
        pass
    
    @abstractmethod
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        pass
    
    @abstractmethod
    async def get_order_by_bepaid_id(self, bepaid_transaction_id: str) -> Optional[Order]:
        """Получить заказ по bePaid transaction ID"""
        pass
    
    @abstractmethod
    async def update_order(self, order: Order) -> Order:
        """Обновить заказ"""
        pass
    
    @abstractmethod
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить заказы пользователя"""
        pass
    
    @abstractmethod
    async def get_orders_by_status(self, status: PaymentStatus) -> List[Order]:
        """Получить заказы по статусу"""
        pass
    
    # User Products
    @abstractmethod
    async def create_user_product(self, user_product: UserProduct) -> UserProduct:
        """Создать покупку пользователя"""
        pass
    
    @abstractmethod
    async def get_user_products(self, user_id: int) -> List[UserProduct]:
        """Получить покупки пользователя"""
        pass
    
    @abstractmethod
    async def has_user_product(self, user_id: int, product_slug: str) -> bool:
        """Проверить, есть ли у пользователя продукт"""
        pass
    
    @abstractmethod
    async def get_undelivered_products(self) -> List[UserProduct]:
        """Получить не доставленные продукты"""
        pass
    
    @abstractmethod
    async def mark_as_delivered(self, user_product_id: int) -> bool:
        """Отметить как доставленный"""
        pass
