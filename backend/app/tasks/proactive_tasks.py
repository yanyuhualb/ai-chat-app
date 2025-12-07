"""
主动消息定时任务
"""
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.conversation import UserActivity, Conversation
from app.models.user import User
from app.models.affection import AffectionScore
from app.services.affection_service import should_send_proactive, calculate_proactive_interval
from app.services.proactive_message_service import ProactiveMessageService
from sqlalchemy import select
from datetime import datetime, timedelta
from loguru import logger


@celery_app.task
def check_proactive_messages_task():
    """
    定时任务：检查并发送主动消息
    每分钟执行一次
    """
    logger.info("开始检查主动消息...")

    db = SessionLocal()
    try:
        # 查询需要检查的对话
        now = datetime.now()

        result = db.execute(
            select(
                UserActivity,
                Conversation,
                AffectionScore,
                User
            )
            .join(Conversation, UserActivity.conversation_id == Conversation.id)
            .join(
                AffectionScore,
                (AffectionScore.user_id == Conversation.user_id) &
                (AffectionScore.character_id == Conversation.character_id)
            )
            .join(User, Conversation.user_id == User.id)
            .where(
                AffectionScore.current_score >= 40,  # 只检查好感度 >= 40 的
                UserActivity.last_message_at < now - timedelta(minutes=3),  # 超过3分钟未互动
                (UserActivity.next_proactive_at == None) |
                (UserActivity.next_proactive_at <= now)
            )
        )

        count = 0
        for activity, conv, affection, user in result:
            try:
                # 计算空闲时间
                minutes_idle = (now - activity.last_message_at).total_seconds() / 60

                # 判断是否应该发送
                if should_send_proactive(affection.current_score, minutes_idle):
                    # 生成并发送消息（这里需要异步转同步）
                    # 实际生产环境建议使用异步任务队列
                    logger.info(
                        f"准备为用户 {user.id} 和角色 {conv.character_id} 发送主动消息"
                    )

                    # 这里简化处理，实际应该调用异步函数
                    # 可以发送到另一个队列或直接保存到待发送表

                    # 计算下次发送时间
                    interval = calculate_proactive_interval(affection.current_score)
                    if interval:
                        next_time = now + timedelta(minutes=interval)
                        activity.next_proactive_at = next_time
                        db.commit()

                    count += 1

            except Exception as e:
                logger.error(f"处理对话 {conv.id} 时出错: {e}")
                continue

        logger.info(f"主动消息检查完成，触发 {count} 条消息")

    except Exception as e:
        logger.error(f"检查主动消息任务失败: {e}")
    finally:
        db.close()


@celery_app.task
def send_proactive_message_task(conversation_id: int):
    """
    异步任务：生成并发送主动消息
    """
    # 这里需要实现实际的发送逻辑
    # 包括调用AI生成、保存到数据库、发送推送通知等
    pass
