"""
WebSocket API接口 - 模拟实现
"""

from fastapi import APIRouter

router = APIRouter(prefix="/websocket", tags=["实时通信"])


@router.get("/health")
async def websocket_health():
    """WebSocket模块健康检查"""
    return {"status": "ok", "module": "websocket"}