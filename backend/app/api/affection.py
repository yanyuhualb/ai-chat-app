"""
好感度API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.affection import AffectionScore, AffectionLog
from app.schemas.affection import AffectionScoreResponse, AffectionDetailResponse, AffectionLogResponse
from app.api.auth import get_current_user
from app.services.affection_service import get_next_level_score
from typing import List

router = APIRouter()


@router.get("/{character_id}", response_model=AffectionDetailResponse)
async def get_affection(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取与某个AI角色的好感度"""

    result = await db.execute(
        select(AffectionScore).where(
            AffectionScore.user_id == current_user.id,
            AffectionScore.character_id == character_id
        )
    )
    affection = result.scalar_one_or_none()

    if not affection:
        raise HTTPException(status_code=404, detail="好感度记录不存在")

    # 获取最近的好感度变化记录
    logs_result = await db.execute(
        select(AffectionLog)
        .where(AffectionLog.affection_score_id == affection.id)
        .order_by(AffectionLog.created_at.desc())
        .limit(10)
    )
    recent_logs = logs_result.scalars().all()

    # 构建响应
    response = AffectionDetailResponse(
        character_id=character_id,
        current_score=affection.current_score,
        level=affection.level,
        next_level_score=get_next_level_score(affection.current_score),
        total_interactions=affection.total_interactions,
        last_interaction=affection.last_interaction,
        recent_changes=[AffectionLogResponse.from_orm(log) for log in recent_logs]
    )

    return response
