"""
AI角色相关Schema
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict
from datetime import datetime


class CharacterBase(BaseModel):
    """角色基础Schema"""
    name: str
    personality: Optional[str] = None
    background_story: Optional[str] = None
    avatar_url: Optional[str] = None
    language: str = "en"


class CharacterCreate(CharacterBase):
    """角色创建Schema"""
    llm_provider: str = "openai"
    llm_model: str = "gpt-3.5-turbo"
    config: Optional[Dict] = {}

    @validator("llm_provider")
    def validate_provider(cls, v):
        allowed = ["openai", "claude", "qwen", "ernie"]
        if v not in allowed:
            raise ValueError(f"不支持的AI平台: {v}")
        return v


class CharacterUpdate(BaseModel):
    """角色更新Schema"""
    name: Optional[str] = None
    personality: Optional[str] = None
    background_story: Optional[str] = None
    avatar_url: Optional[str] = None
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    config: Optional[Dict] = None


class CharacterResponse(CharacterBase):
    """角色响应Schema"""
    id: int
    user_id: int
    llm_provider: str
    llm_model: str
    system_prompt: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
