"""
依赖注入模块
提供FastAPI依赖项，包括数据库连接、认证等
"""

from typing import AsyncGenerator, Optional

import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session

# 设置
settings = get_settings()

# HTTP Bearer Token验证器
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with get_session() as session:
        yield session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    获取当前用户（简化版本）
    在MVP阶段暂时跳过认证
    """
    # TODO: 实现真实的JWT token验证
    # 目前返回模拟用户用于开发
    return {
        "id": "dev-user-001",
        "username": "developer",
        "email": "dev@pbl-assistant.com",
        "is_active": True,
        "is_superuser": False,
    }


async def get_admin_user(
    current_user=Depends(get_current_user)
):
    """获取管理员用户"""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员权限不足"
        )
    return current_user


async def get_asyncpg_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """获取原始asyncpg连接（用于特殊查询）"""
    conn = await asyncpg.connect(settings.ASYNCPG_URL)
    try:
        yield conn
    finally:
        await conn.close()