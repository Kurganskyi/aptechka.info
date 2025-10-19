"""
Timer SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class TimerModel(Base):
    """Модель таймера для офферов"""
    
    __tablename__ = "timers"
    
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timer_type = Column(String(50), nullable=False)  # tripwire_99byn
    started_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_triggered = Column(Boolean, default=False, nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="timers")
