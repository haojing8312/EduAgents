"""
WebSocket endpoints for real-time agent collaboration
"""

import asyncio
import json
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter

from app.schemas.course import CourseDesignRequest
from app.core.exceptions import AgentException

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    """管理WebSocket连接"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_data: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.session_data[session_id] = {
            "websocket": websocket,
            "status": "connected",
            "current_agent": None,
            "progress": 0
        }
        logger.info(f"✅ WebSocket连接建立: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if session_id in self.session_data:
            del self.session_data[session_id]
        logger.info(f"❌ WebSocket连接断开: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        """发送个人消息"""
        if session_id in self.session_data:
            websocket = self.session_data[session_id]["websocket"]
            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送消息失败 {session_id}: {e}")

    async def broadcast(self, message: dict):
        """广播消息"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"广播消息失败: {e}")

manager = ConnectionManager()

@router.websocket("/course-design/{session_id}")
async def websocket_course_design(websocket: WebSocket, session_id: str):
    """
    课程设计WebSocket连接
    实时接收课程设计请求并返回智能体协作进度
    """
    await manager.connect(websocket, session_id)

    try:
        while True:
            # 接收课程设计请求
            data = await websocket.receive_text()
            request_data = json.loads(data)

            logger.info(f"收到课程设计请求: {session_id}")

            # 验证请求格式
            if "action" not in request_data:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "缺少action字段"
                }, session_id)
                continue

            action = request_data["action"]

            if action == "start_design":
                # 启动课程设计流程
                course_requirement = request_data.get("course_requirement", "")
                if not course_requirement.strip():
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "课程需求不能为空"
                    }, session_id)
                    continue

                # 开始课程设计协作
                await start_course_design_collaboration(
                    session_id, course_requirement, manager
                )

            elif action == "get_status":
                # 获取当前状态
                await manager.send_personal_message({
                    "type": "status",
                    "data": manager.session_data.get(session_id, {})
                }, session_id)

            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"未知的action: {action}"
                }, session_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket错误 {session_id}: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"系统错误: {str(e)}"
        }, session_id)
        manager.disconnect(websocket, session_id)

async def start_course_design_collaboration(
    session_id: str,
    course_requirement: str,
    manager: ConnectionManager
):
    """启动课程设计智能体协作流程"""

    try:
        # 发送开始消息
        await manager.send_personal_message({
            "type": "design_started",
            "message": "🚀 智能体协作开始！",
            "agents": [
                {"id": "education_theorist", "name": "AI时代教育理论专家", "status": "waiting"},
                {"id": "course_architect", "name": "AI时代课程架构师", "status": "waiting"},
                {"id": "content_designer", "name": "AI时代内容设计师", "status": "waiting"},
                {"id": "assessment_expert", "name": "AI时代评估专家", "status": "waiting"},
                {"id": "material_creator", "name": "AI时代素材创作者", "status": "waiting"}
            ]
        }, session_id)

        # 智能体协作序列
        agent_sequence = [
            ("education_theorist", "AI时代教育理论专家", "🎯 构建AI时代教育理论框架"),
            ("course_architect", "AI时代课程架构师", "🏗️ 设计跨学科课程架构"),
            ("content_designer", "AI时代内容设计师", "🎨 创作场景化学习内容"),
            ("assessment_expert", "AI时代评估专家", "📊 设计核心能力评价体系"),
            ("material_creator", "AI时代素材创作者", "📦 生成数字化学习资源")
        ]

        course_data = {}
        total_steps = len(agent_sequence)

        for i, (agent_id, agent_name, task_description) in enumerate(agent_sequence):
            # 设置当前智能体为工作中
            await manager.send_personal_message({
                "type": "agent_started",
                "agent_id": agent_id,
                "agent_name": agent_name,
                "task": task_description,
                "step": i + 1,
                "total_steps": total_steps
            }, session_id)

            # 模拟智能体工作进度
            for progress in range(0, 101, 20):
                await asyncio.sleep(0.8)  # 模拟工作时间

                await manager.send_personal_message({
                    "type": "agent_progress",
                    "agent_id": agent_id,
                    "progress": progress,
                    "overall_progress": ((i * 100 + progress) / (total_steps * 100)) * 100
                }, session_id)

            # 调用真实的智能体工作
            try:
                from app.services.real_agent_service import execute_real_agent_work
                result = await execute_real_agent_work(agent_id, course_requirement)
                course_data[agent_id] = result

                # 智能体完成
                await manager.send_personal_message({
                    "type": "agent_completed",
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "result": result,
                    "step": i + 1,
                    "total_steps": total_steps
                }, session_id)

            except AgentException as e:
                logger.error(f"智能体 {agent_id} 执行失败: {e}")
                await manager.send_personal_message({
                    "type": "agent_error",
                    "agent_id": agent_id,
                    "error": str(e)
                }, session_id)
                return

        # 执行完整课程设计并保存到数据库
        try:
            from app.services.real_agent_service import get_real_agent_service

            service = await get_real_agent_service()
            complete_result = await service.execute_complete_course_design(
                course_requirement=course_requirement,
                session_id=session_id,
                user_id=None,  # 暂时不需要用户认证
                save_to_db=True
            )

            # 发送完成消息，包含数据库保存信息
            await manager.send_personal_message({
                "type": "design_completed",
                "message": "🎉 课程设计完成并已保存！",
                "course_data": course_data,
                "complete_result": {
                    "course_id": complete_result.get("course_id"),
                    "saved_to_database": complete_result.get("saved_to_database", False),
                    "status": complete_result.get("status", "completed")
                }
            }, session_id)

        except Exception as db_error:
            logger.warning(f"⚠️ 数据库保存失败，但返回设计结果: {db_error}")

            # 即使数据库保存失败也要返回设计结果
            await manager.send_personal_message({
                "type": "design_completed",
                "message": "🎉 课程设计完成！",
                "course_data": course_data,
                "complete_result": {
                    "course_id": None,
                    "saved_to_database": False,
                    "status": "completed_without_persistence",
                    "note": "课程设计完成但未保存到数据库"
                }
            }, session_id)

    except Exception as e:
        logger.error(f"课程设计协作失败: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"设计过程中发生错误: {str(e)}"
        }, session_id)

# DEPRECATED: simulate_agent_work function has been replaced with real agent execution
# This function is kept for reference but is no longer used
async def simulate_agent_work_deprecated(agent_id: str, course_requirement: str):
    """
    DEPRECATED: This function has been replaced with real agent execution
    Use execute_real_agent_work from app.services.real_agent_service instead
    """
    # This function is now deprecated and replaced with real AI agent execution
    # Keeping for reference only
    pass

@router.get("/health")
async def websocket_health():
    """WebSocket模块健康检查"""
    return {"status": "ok", "module": "websocket", "active_connections": len(manager.active_connections)}