"""
项目管理API接口 - 模拟实现
"""

from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("/health")
async def projects_health():
    """项目模块健康检查"""
    return {"status": "ok", "module": "projects"}