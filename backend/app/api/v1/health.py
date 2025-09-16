"""
健康检查API接口
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "service": "PBL智能助手 API",
        "version": "1.0.0"
    }