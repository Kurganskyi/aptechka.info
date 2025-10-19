"""
Broadcast Message SQLAlchemy model
"""

from sqlalchemy import Column, BigInteger, Text, String, Integer, ForeignKey, JSON, DateTime
from .base import Base


class BroadcastMessageModel(Base):
    """Модель рассылки"""
    
    __tablename__ = "broadcast_messages"
    
    created_by_admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    message_text = Column(Text, nullable=False)
    media_file_id = Column(String(255), nullable=True)
    media_type = Column(String(50), nullable=True)
    target_filter = Column(JSON, nullable=True)  # Фильтр аудитории
    status = Column(String(50), default="draft", nullable=False)  # draft, in_progress, completed, cancelled
    total_users = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
