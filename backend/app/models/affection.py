"""
好感度模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AffectionScore(Base):
    """好感度表"""
    __tablename__ = "affection_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)

    # 好感度数值（-100 ~ 100）
    current_score = Column(Integer, default=0, nullable=False)
    level = Column(String(50), default="普通")  # 厌恶 | 陌生 | 普通 | 熟人 | 朋友 | 挚友 | 恋人

    # 统计信息
    last_interaction = Column(DateTime(timezone=True))
    total_interactions = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 约束
    __table_args__ = (
        Index("idx_user_character_affection", "user_id", "character_id", unique=True),
        CheckConstraint("current_score >= -100 AND current_score <= 100", name="score_range"),
    )

    # 关系
    character = relationship("Character", back_populates="affection_scores")
    logs = relationship("AffectionLog", back_populates="affection_score", cascade="all, delete-orphan")


class AffectionLog(Base):
    """好感度变化历史表"""
    __tablename__ = "affection_logs"

    id = Column(Integer, primary_key=True, index=True)
    affection_score_id = Column(Integer, ForeignKey("affection_scores.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))

    score_change = Column(Integer, nullable=False)  # 积分变化（可为负）
    reason = Column(Text)  # 变化原因
    sentiment_analysis = Column(JSON)  # 情感分析详情

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    affection_score = relationship("AffectionScore", back_populates="logs")
