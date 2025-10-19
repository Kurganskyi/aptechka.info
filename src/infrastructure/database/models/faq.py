"""
FAQ SQLAlchemy model
"""

from sqlalchemy import Column, String, Text, Integer, Boolean
from .base import Base


class FAQItemModel(Base):
    """Модель FAQ элемента"""
    
    __tablename__ = "faq_items"
    
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
