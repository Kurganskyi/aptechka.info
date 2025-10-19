"""
Product SQLAlchemy model
"""

from sqlalchemy import Column, String, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class ProductModel(Base):
    """Модель продукта"""
    
    __tablename__ = "products"
    
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_kopecks = Column(Integer, nullable=False)  # Цена в копейках
    file_id = Column(String(255), nullable=True)  # Telegram file_id
    file_type = Column(String(50), nullable=True)  # video, document, photo
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    orders = relationship("OrderModel", back_populates="product")
    user_products = relationship("UserProductModel", back_populates="product")
