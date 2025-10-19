"""
Test Result SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base


class TestResultModel(Base):
    """Модель результата теста"""
    
    __tablename__ = "test_results"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, default=6, nullable=False)
    attempts = Column(Integer, default=1, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    answers_json = Column(JSON, nullable=True)  # Детали ответов для аналитики
    completed_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="test_results")
