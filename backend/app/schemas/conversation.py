"""
对话和消息相关Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """消息创建Schema"""
    content: str
    stream: bool = False  # 是否使用流式返回


class MessageResponse(BaseModel):
    """消息响应Schema"""
    id: int
    conversation_id: int
    role: str
    content: str
    tokens_used: int
    is_proactive: bool
    created_at: datetime
    affection_change: Optional[int] = None  # 好感度变化

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """对话响应Schema"""
    id: int
    user_id: int
    character_id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    """对话详情Schema"""
    messages: List[MessageResponse] = []
