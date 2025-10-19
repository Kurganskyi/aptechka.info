"""
User SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class UserModel(Base):
    """Модель пользователя"""
    
    __tablename__ = "users"
    
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    is_blocked = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    referrer_id = Column(BigInteger, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("OrderModel", back_populates="user", cascade="all, delete-orphan")
    user_products = relationship("UserProductModel", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("TestResultModel", back_populates="user", cascade="all, delete-orphan")
    user_questions = relationship("UserQuestionModel", back_populates="user", cascade="all, delete-orphan")
    timers = relationship("TimerModel", back_populates="user", cascade="all, delete-orphan")
    user_actions = relationship("UserActionModel", back_populates="user", cascade="all, delete-orphan")
