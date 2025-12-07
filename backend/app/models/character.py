"""
AI角色模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Character(Base):
    """AI角色表"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 基础信息
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500))
    personality = Column(Text)  # 性格描述
    background_story = Column(Text)  # 背景故事
    system_prompt = Column(Text, nullable=False)  # 生成的系统提示词

    # AI配置
    llm_provider = Column(String(50), default="openai")  # openai | claude | qwen | ernie
    llm_model = Column(String(100), default="gpt-3.5-turbo")
    config = Column(JSON, default={})  # temperature, max_tokens等

    # 语言
    language = Column(String(10), default="en")

    # 状态
    is_active = Column(Boolean, default=True)
    is_preset = Column(Boolean, default=False)  # 是否为预设角色
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="characters")
    conversations = relationship("Conversation", back_populates="character", cascade="all, delete-orphan")
    affection_scores = relationship("AffectionScore", back_populates="character", cascade="all, delete-orphan")
