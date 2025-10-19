"""
Order SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class OrderModel(Base):
    """Модель заказа/платежа"""
    
    __tablename__ = "orders"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    amount_kopecks = Column(Integer, nullable=False)
    currency = Column(String(3), default="BYN", nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)
    bepaid_transaction_id = Column(String(255), unique=True, nullable=True, index=True)
    bepaid_checkout_url = Column(String(500), nullable=True)
    payment_method = Column(String(50), nullable=True)  # card, erip
    expires_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="orders")
    product = relationship("ProductModel", back_populates="orders")
    user_products = relationship("UserProductModel", back_populates="order")


class UserProductModel(Base):
    """Модель покупки пользователя"""
    
    __tablename__ = "user_products"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    purchased_at = Column(DateTime, nullable=False)
    file_delivered = Column(Boolean, default=False, nullable=False)
    delivery_attempts = Column(Integer, default=0, nullable=False)
    last_delivery_attempt = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="user_products")
    product = relationship("ProductModel", back_populates="user_products")
    order = relationship("OrderModel", back_populates="user_products")
