"""
主动消息任务模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProactiveMessageTask(Base):
    """主动消息任务表"""
    __tablename__ = "proactive_message_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)

    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)  # pending | sent | failed
    trigger_reason = Column(String(100))  # high_affection | idle_detected

    message_content = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
