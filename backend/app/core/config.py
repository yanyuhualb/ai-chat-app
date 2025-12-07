"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    APP_NAME: str = "AI角色对话App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    # Redis配置
    REDIS_URL: str

    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 加密配置
    ENCRYPTION_KEY: str

    # Celery配置
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # CORS配置
    CORS_ORIGINS: List[str] = []

    # Firebase配置
    FIREBASE_CREDENTIALS_PATH: str = ""

    # 日志配置
    LOG_LEVEL: str = "INFO"

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """解析CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
