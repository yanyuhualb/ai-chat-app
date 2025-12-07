"""
好感度相关Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AffectionScoreResponse(BaseModel):
    """好感度响应Schema"""
    character_id: int
    current_score: int
    level: str
    next_level_score: Optional[int]
    total_interactions: int
    last_interaction: Optional[datetime]

    class Config:
        from_attributes = True


class AffectionLogResponse(BaseModel):
    """好感度变化记录Schema"""
    id: int
    score_change: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AffectionDetailResponse(AffectionScoreResponse):
    """好感度详情Schema"""
    recent_changes: List[AffectionLogResponse] = []
