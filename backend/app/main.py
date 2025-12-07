"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core import redis
from app.api import auth, characters, conversations, affection
from loguru import logger

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(characters.router, prefix="/api/characters", tags=["AI角色"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["对话"])
app.include_router(affection.router, prefix="/api/affection", tags=["好感度"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"{settings.APP_NAME} 启动中...")
    # 可以在这里初始化Redis连接等


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭应用...")
    await redis.close_redis()


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
