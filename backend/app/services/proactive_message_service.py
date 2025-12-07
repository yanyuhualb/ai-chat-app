"""
主动消息生成和发送服务
"""
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Message, Conversation, UserActivity
from app.models.character import Character
from app.models.affection import AffectionScore
from app.services.llm_provider import get_llm_provider
from app.core.security import decrypt_api_key
import random


class ProactiveMessageService:
    """主动消息服务"""

    @staticmethod
    async def generate_proactive_message(
        db: AsyncSession,
        conversation_id: int,
        affection_score: int,
        user_api_keys: Dict[str, str]
    ) -> str:
        """生成主动消息内容"""

        # 获取对话和角色信息
        result = await db.execute(
            select(Conversation, Character)
            .join(Character, Conversation.character_id == Character.id)
            .where(Conversation.id == conversation_id)
        )
        conv, character = result.one()

        # 获取最近对话历史
        recent_messages = await ProactiveMessageService._get_recent_messages(db, conversation_id, limit=5)

        # 构建提示词
        prompt = ProactiveMessageService._build_proactive_prompt(
            character, affection_score, recent_messages
        )

        # 调用AI生成消息
        provider = get_llm_provider(character.llm_provider)

        # 解密API Key
        encrypted_key = user_api_keys.get(character.llm_provider)
        if not encrypted_key:
            raise ValueError(f"用户未配置{character.llm_provider}平台的API Key")

        api_key = decrypt_api_key(encrypted_key)

        messages = [
            {"role": "system", "content": character.system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = await provider.chat_completion(
            messages=messages,
            api_key=api_key,
            model=character.llm_model,
            temperature=character.config.get("temperature", 0.9),
            max_tokens=150  # 主动消息简短一些
        )

        return response.strip()

    @staticmethod
    async def _get_recent_messages(
        db: AsyncSession,
        conversation_id: int,
        limit: int = 5
    ) -> List[Message]:
        """获取最近的消息"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # 反转为时间正序

    @staticmethod
    def _build_proactive_prompt(
        character: Character,
        affection_score: int,
        recent_messages: List[Message]
    ) -> str:
        """构建主动消息生成提示"""

        # 格式化最近对话
        context = "\n".join([
            f"{'用户' if msg.role == 'user' else '我'}: {msg.content}"
            for msg in recent_messages[-3:]  # 只用最近3条
        ])

        # 根据好感度选择消息类型
        if affection_score >= 95:
            message_type = "恋人之间的甜蜜问候或想念"
        elif affection_score >= 80:
            message_type = "挚友之间的关心或分享"
        elif affection_score >= 60:
            message_type = "朋友之间的友好问候"
        else:
            message_type = "熟人之间的礼貌问候"

        prompt = f"""
你是{character.name}，当前与用户的好感度等级对应的亲密程度需要表现为：{message_type}。

最近对话内容：
{context if context else "（还没有对话记录）"}

现在你想主动给用户发一条消息。要求：
1. 自然、不突兀，像真实的{character.name}一样
2. 可以提及之前的对话内容（如果有的话）
3. 根据好感度调整语气和内容的亲密程度
4. 30-50字以内
5. 不要重复说过的话

请直接生成消息内容：
"""
        return prompt
