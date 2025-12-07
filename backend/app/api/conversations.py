"""
对话API（简化版，完整版需包含流式响应和WebSocket）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.character import Character
from app.models.conversation import Conversation, Message, UserActivity
from app.models.affection import AffectionScore
from app.schemas.conversation import MessageCreate, MessageResponse, ConversationResponse
from app.api.auth import get_current_user
from app.services.llm_provider import get_llm_provider
from app.services.affection_service import AffectionService
from app.core.security import decrypt_api_key
from datetime import datetime
from typing import List

router = APIRouter()


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息并获取AI回复"""

    # 获取对话和角色
    result = await db.execute(
        select(Conversation, Character)
        .join(Character, Conversation.character_id == Character.id)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conv_char = result.one_or_none()

    if not conv_char:
        raise HTTPException(status_code=404, detail="对话不存在")

    conversation, character = conv_char

    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    await db.commit()

    # 获取对话历史
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    history = list(reversed(history_result.scalars().all()))

    # 构建消息列表
    messages = [{"role": "system", "content": character.system_prompt}]
    messages.extend([{"role": msg.role, "content": msg.content} for msg in history])

    # 调用AI
    provider = get_llm_provider(character.llm_provider)

    # 获取并解密API Key
    api_key_config = current_user.encrypted_api_keys.get(character.llm_provider)
    if not api_key_config:
        raise HTTPException(status_code=400, detail=f"请先配置{character.llm_provider}的API Key")

    api_key = decrypt_api_key(api_key_config["key"])

    # 调用AI
    ai_response = await provider.chat_completion(
        messages=messages,
        api_key=api_key,
        model=character.llm_model,
        temperature=character.config.get("temperature", 0.8)
    )

    # 解析情感分析
    from app.services.affection_service import AffectionService
    sentiment_result = AffectionService.analyze_sentiment_from_ai_response(ai_response)

    # 保存AI回复
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=sentiment_result["content"]
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)

    # 更新好感度
    affection = await AffectionService.get_or_create_affection(
        db, current_user.id, character.id
    )
    await AffectionService.update_affection(
        db,
        affection.id,
        sentiment_result["affection_change"],
        sentiment_result["reason"],
        ai_message.id,
        sentiment_result["sentiment_data"]
    )

    # 更新活跃状态
    activity_result = await db.execute(
        select(UserActivity).where(UserActivity.conversation_id == conversation_id)
    )
    activity = activity_result.scalar_one_or_none()

    if activity:
        activity.last_message_at = datetime.now()
    else:
        activity = UserActivity(
            conversation_id=conversation_id,
            last_message_at=datetime.now()
        )
        db.add(activity)

    await db.commit()

    # 构建响应
    response = MessageResponse.from_orm(ai_message)
    response.affection_change = sentiment_result["affection_change"]

    return response


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations
