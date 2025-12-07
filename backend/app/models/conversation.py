"""
对话模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Conversation(Base):
    """对话会话表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(200))  # 对话标题
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 唯一约束：每个用户与角色只有一个对话
    __table_args__ = (
        Index("idx_user_character", "user_id", "character_id", unique=True),
    )

    # 关系
    user = relationship("User", back_populates="conversations")
    character = relationship("Character", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user_activity = relationship("UserActivity", back_populates="conversation", uselist=False, cascade="all, delete-orphan")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)

    # 统计信息
    tokens_used = Column(Integer, default=0)
    is_proactive = Column(Boolean, default=False)  # 是否为AI主动发送

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")


class UserActivity(Base):
    """用户活跃状态表（用于主动消息检测）"""
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, nullable=False)

    last_message_at = Column(DateTime(timezone=True), nullable=False)
    last_check_at = Column(DateTime(timezone=True))  # 上次检查主动消息的时间
    next_proactive_at = Column(DateTime(timezone=True), index=True)  # 计划的下次主动消息时间

    # 关系
    conversation = relationship("Conversation", back_populates="user_activity")
