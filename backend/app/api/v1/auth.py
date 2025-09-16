"""
认证API接口 - 模拟实现
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/health")
async def auth_health():
    """认证模块健康检查"""
    return {"status": "ok", "module": "auth"}