"""
课程管理API接口 - 模拟实现
"""

from fastapi import APIRouter

router = APIRouter(prefix="/courses", tags=["课程管理"])


@router.get("/health")
async def courses_health():
    """课程模块健康检查"""
    return {"status": "ok", "module": "courses"}