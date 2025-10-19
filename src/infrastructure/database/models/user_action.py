"""
User Action SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base


class UserActionModel(Base):
    """Модель действия пользователя для аналитики"""
    
    __tablename__ = "user_actions"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False, index=True)  # start, view_kit, click_payment, etc.
    action_data = Column(JSON, nullable=True)  # Дополнительные данные
    created_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="user_actions")
