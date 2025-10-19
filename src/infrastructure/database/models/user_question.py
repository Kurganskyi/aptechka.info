"""
User Question SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class UserQuestionModel(Base):
    """Модель вопроса пользователя"""
    
    __tablename__ = "user_questions"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    is_answered = Column(Boolean, default=False, nullable=False, index=True)
    answer_text = Column(Text, nullable=True)
    answered_by_admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    answered_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="user_questions", foreign_keys=[user_id])
    answered_by_admin = relationship("UserModel", foreign_keys=[answered_by_admin_id])
