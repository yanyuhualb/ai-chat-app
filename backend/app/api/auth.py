"""
认证相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_api_key
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse, APIKeyCreate, APIKeyResponse
from typing import List

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )

    user_id = payload.get("user_id")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用"
        )

    return user


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 查找用户
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成令牌
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse)
async def save_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """保存用户的API Key"""
    # 加密API Key
    encrypted_key = encrypt_api_key(api_key_data.api_key)

    # 更新用户的加密API Keys
    if not current_user.encrypted_api_keys:
        current_user.encrypted_api_keys = {}

    current_user.encrypted_api_keys[api_key_data.provider] = {
        "key": encrypted_key,
        "model": api_key_data.model
    }

    await db.commit()

    return {
        "provider": api_key_data.provider,
        "model": api_key_data.model,
        "status": "active"
    }


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(current_user: User = Depends(get_current_user)):
    """获取用户配置的API Key列表（不返回实际key）"""
    if not current_user.encrypted_api_keys:
        return []

    return [
        {
            "provider": provider,
            "model": config.get("model"),
            "status": "active"
        }
        for provider, config in current_user.encrypted_api_keys.items()
    ]
