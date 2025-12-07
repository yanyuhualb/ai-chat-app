"""
Redis连接管理
"""
import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.core.config import settings
from typing import Optional

# Redis连接池
redis_pool: Optional[Redis] = None


async def get_redis() -> Redis:
    """
    获取Redis连接
    """
    global redis_pool
    if redis_pool is None:
        redis_pool = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return redis_pool


async def close_redis():
    """
    关闭Redis连接
    """
    global redis_pool
    if redis_pool:
        await redis_pool.close()
