"""
用户相关Schema
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict
from datetime import datetime


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """用户创建Schema"""
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("密码长度至少6位")
        return v


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    avatar_url: Optional[str] = None
    timezone: str
    preferred_language: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """令牌响应Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class APIKeyCreate(BaseModel):
    """API Key创建Schema"""
    provider: str  # openai | claude | qwen | ernie
    api_key: str
    model: Optional[str] = None


class APIKeyResponse(BaseModel):
    """API Key响应Schema"""
    provider: str
    model: Optional[str]
    status: str = "active"
