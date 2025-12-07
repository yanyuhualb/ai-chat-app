"""
Celery应用配置
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "ai_chat_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每分钟检查一次主动消息
    "check-proactive-messages": {
        "task": "app.tasks.proactive_tasks.check_proactive_messages_task",
        "schedule": 60.0,  # 每60秒执行一次
    },
    # 每天凌晨3点清理旧数据
    "cleanup-old-data": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_messages_task",
        "schedule": crontab(hour=3, minute=0),
    },
}
