"""
AI角色管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterResponse, CharacterUpdate
from app.api.auth import get_current_user
from typing import List

router = APIRouter()


def generate_system_prompt(character_data: CharacterCreate) -> str:
    """根据角色信息生成系统提示词"""
    prompt = f"""你是{character_data.name}。

性格特点：{character_data.personality or '友好、乐于助人'}

背景故事：{character_data.background_story or '无特殊背景'}

重要指示：
1. 始终保持角色一致性，用第一人称"我"来回答
2. 根据对话内容在回复末尾附带情感分析（JSON格式）
3. 使用{character_data.language}语言回复
4. 回复自然、真实，避免机械感

情感分析格式（必须包含在每次回复中）：
<sentiment>{{"affection_change": -5到5的整数, "reason": "简短说明"}}</sentiment>

示例：
用户：今天心情不太好
你：怎么了？发生什么事了吗？愿意和我聊聊吗？<sentiment>{{"affection_change": 2, "reason": "用户主动分享情绪，表示信任"}}</sentiment>
"""
    return prompt


@router.post("", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建AI角色"""
    # 生成系统提示词
    system_prompt = generate_system_prompt(character_data)

    character = Character(
        user_id=current_user.id,
        name=character_data.name,
        personality=character_data.personality,
        background_story=character_data.background_story,
        avatar_url=character_data.avatar_url,
        language=character_data.language,
        llm_provider=character_data.llm_provider,
        llm_model=character_data.llm_model,
        system_prompt=system_prompt,
        config=character_data.config
    )

    db.add(character)
    await db.commit()
    await db.refresh(character)

    return character


@router.get("", response_model=List[CharacterResponse])
async def list_characters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有AI角色"""
    result = await db.execute(
        select(Character)
        .where(Character.user_id == current_user.id, Character.is_active == True)
        .order_by(Character.created_at.desc())
    )
    characters = result.scalars().all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取AI角色详情"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")

    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新AI角色"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 更新字段
    update_data = character_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)

    # 如果更新了基础信息，重新生成系统提示词
    if any(k in update_data for k in ['name', 'personality', 'background_story', 'language']):
        character.system_prompt = generate_system_prompt(CharacterCreate(**character.__dict__))

    await db.commit()
    await db.refresh(character)

    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除AI角色"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")

    await db.delete(character)
    await db.commit()

    return {"message": "角色已删除"}
