"""
Payment entity - платеж/заказ
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class PaymentStatus(Enum):
    """Статус платежа"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class PaymentMethod(Enum):
    """Способ оплаты"""
    CARD = "card"
    ERIP = "erip"


@dataclass
class Product:
    """Продукт"""
    
    id: int
    slug: str
    name: str
    description: str
    price_kopecks: int  # Цена в копейках
    file_id: Optional[str] = None
    file_type: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @property
    def price_byn(self) -> float:
        """Цена в BYN"""
        return self.price_kopecks / 100
    
    def is_available(self) -> bool:
        """Проверка доступности продукта"""
        return self.is_active


@dataclass
class Order:
    """Заказ/платеж"""
    
    id: int
    user_id: int
    product_id: int
    amount_kopecks: int
    currency: str = "BYN"
    status: PaymentStatus = PaymentStatus.PENDING
    bepaid_transaction_id: Optional[str] = None
    bepaid_checkout_url: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @property
    def amount_byn(self) -> float:
        """Сумма в BYN"""
        return self.amount_kopecks / 100
    
    def is_paid(self) -> bool:
        """Проверка оплаты"""
        return self.status == PaymentStatus.PAID
    
    def is_expired(self) -> bool:
        """Проверка истечения срока"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def mark_as_paid(self, payment_method: PaymentMethod = None):
        """Отметить как оплаченный"""
        self.status = PaymentStatus.PAID
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if payment_method:
            self.payment_method = payment_method


@dataclass
class UserProduct:
    """Покупка пользователя"""
    
    id: int
    user_id: int
    product_id: int
    order_id: int
    purchased_at: datetime = None
    file_delivered: bool = False
    delivery_attempts: int = 0
    last_delivery_attempt: Optional[datetime] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.purchased_at is None:
            self.purchased_at = datetime.utcnow()
    
    def mark_as_delivered(self):
        """Отметить как доставленный"""
        self.file_delivered = True
    
    def increment_delivery_attempts(self):
        """Увеличить счетчик попыток доставки"""
        self.delivery_attempts += 1
        self.last_delivery_attempt = datetime.utcnow()
