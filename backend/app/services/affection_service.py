"""
好感度计算和管理服务
"""
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.affection import AffectionScore, AffectionLog
from app.models.conversation import Message
import random
import json


# 好感度等级定义
AFFECTION_LEVELS = {
    "厌恶": (-100, -60),
    "陌生": (-60, -20),
    "普通": (-20, 20),
    "熟人": (20, 50),
    "朋友": (50, 80),
    "挚友": (80, 95),
    "恋人": (95, 101),  # 101是上限
}


def get_affection_level(score: int) -> str:
    """根据分数获取好感度等级"""
    for level, (min_score, max_score) in AFFECTION_LEVELS.items():
        if min_score <= score < max_score:
            return level
    return "恋人"  # 满分


def get_next_level_score(current_score: int) -> Optional[int]:
    """获取下一等级所需分数"""
    current_level = get_affection_level(current_score)
    level_names = list(AFFECTION_LEVELS.keys())

    if current_level == "恋人":
        return None  # 已达最高等级

    current_index = level_names.index(current_level)
    next_level = level_names[current_index + 1]
    return AFFECTION_LEVELS[next_level][0]


class AffectionService:
    """好感度服务"""

    @staticmethod
    async def get_or_create_affection(
        db: AsyncSession,
        user_id: int,
        character_id: int
    ) -> AffectionScore:
        """获取或创建好感度记录"""
        result = await db.execute(
            select(AffectionScore).where(
                AffectionScore.user_id == user_id,
                AffectionScore.character_id == character_id
            )
        )
        affection = result.scalar_one_or_none()

        if not affection:
            affection = AffectionScore(
                user_id=user_id,
                character_id=character_id,
                current_score=0,
                level="普通"
            )
            db.add(affection)
            await db.commit()
            await db.refresh(affection)

        return affection

    @staticmethod
    async def update_affection(
        db: AsyncSession,
        affection_id: int,
        score_change: int,
        reason: str,
        message_id: Optional[int] = None,
        sentiment_data: Optional[Dict] = None
    ):
        """更新好感度"""
        # 获取当前好感度
        result = await db.execute(
            select(AffectionScore).where(AffectionScore.id == affection_id)
        )
        affection = result.scalar_one()

        # 计算新分数（限制在-100到100之间）
        new_score = max(-100, min(100, affection.current_score + score_change))
        new_level = get_affection_level(new_score)

        # 更新好感度
        await db.execute(
            update(AffectionScore)
            .where(AffectionScore.id == affection_id)
            .values(
                current_score=new_score,
                level=new_level,
                last_interaction=datetime.now(),
                total_interactions=AffectionScore.total_interactions + 1
            )
        )

        # 创建变化记录
        log = AffectionLog(
            affection_score_id=affection_id,
            message_id=message_id,
            score_change=score_change,
            reason=reason,
            sentiment_analysis=sentiment_data
        )
        db.add(log)
        await db.commit()

        return new_score, new_level

    @staticmethod
    def analyze_sentiment_from_ai_response(ai_response: str) -> Dict:
        """
        从AI回复中提取情感分析结果
        AI回复格式应包含：<sentiment>{"affection_change": 3, "reason": "..."}</sentiment>
        """
        try:
            # 查找<sentiment>标签
            start = ai_response.find("<sentiment>")
            end = ai_response.find("</sentiment>")

            if start != -1 and end != -1:
                sentiment_json = ai_response[start + 11:end]
                sentiment_data = json.loads(sentiment_json)

                # 提取纯文本内容（去除sentiment标签）
                clean_content = ai_response[:start] + ai_response[end + 12:]

                return {
                    "content": clean_content.strip(),
                    "affection_change": sentiment_data.get("affection_change", 0),
                    "reason": sentiment_data.get("reason", ""),
                    "sentiment_data": sentiment_data
                }
        except Exception as e:
            # 解析失败，使用默认值
            pass

        # 默认返回
        return {
            "content": ai_response,
            "affection_change": 1,  # 默认+1
            "reason": "正常对话",
            "sentiment_data": {}
        }


def calculate_proactive_interval(affection_score: int) -> Optional[int]:
    """
    根据好感度计算主动消息间隔（分钟）
    返回：随机间隔的分钟数，如果不应发送则返回None
    """
    if affection_score >= 90:
        return random.randint(1, 10)  # 1-10分钟
    elif affection_score >= 80:
        return random.randint(10, 30)  # 10-30分钟
    elif affection_score >= 60:
        return random.randint(30, 120)  # 0.5-2小时
    elif affection_score >= 40:
        return random.randint(120, 360)  # 2-6小时
    else:
        return None  # 不发送


def should_send_proactive(affection_score: int, minutes_idle: int) -> bool:
    """判断是否应该发送主动消息"""
    if affection_score >= 90 and minutes_idle >= 3:
        return True
    elif affection_score >= 80 and minutes_idle >= 10:
        return True
    elif affection_score >= 60 and minutes_idle >= 30:
        return True
    elif affection_score >= 40 and minutes_idle >= 120:
        return True
    return False
