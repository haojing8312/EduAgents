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

            # 调用实际的智能体工作
            try:
                result = await simulate_agent_work(agent_id, course_requirement)
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

        # 所有智能体完成
        await manager.send_personal_message({
            "type": "design_completed",
            "message": "🎉 课程设计完成！",
            "course_data": course_data
        }, session_id)

    except Exception as e:
        logger.error(f"课程设计协作失败: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"设计过程中发生错误: {str(e)}"
        }, session_id)

async def simulate_agent_work(agent_id: str, course_requirement: str):
    """模拟智能体工作"""

    simulation_results = {
        "education_theorist": {
            "theory_framework": "AI时代教育理论框架",
            "learning_principles": [
                "人机协作学习原理",
                "元认知发展理论",
                "创造性思维培养",
                "数字素养基础"
            ],
            "pedagogical_approach": "项目式学习 + AI辅助探究",
            "course_requirement_analysis": f"基于需求分析：{course_requirement[:100]}..."
        },

        "course_architect": {
            "course_structure": {
                "phases": [
                    {"name": "认知唤醒期", "duration": "2周", "focus": "AI时代意识培养"},
                    {"name": "技能建构期", "duration": "4周", "focus": "核心能力发展"},
                    {"name": "应用实践期", "duration": "2周", "focus": "综合项目实践"}
                ],
                "learning_path": "螺旋式递进，理论与实践并重"
            },
            "interdisciplinary_design": "科学+技术+人文+艺术整合"
        },

        "content_designer": {
            "learning_scenarios": [
                {
                    "title": "AI伦理辩论赛",
                    "description": "通过角色扮演探讨AI发展的社会影响",
                    "ai_tools": ["ChatGPT", "Claude", "论证分析工具"]
                },
                {
                    "title": "智慧城市设计挑战",
                    "description": "运用设计思维和AI工具设计未来城市",
                    "ai_tools": ["Midjourney", "数据分析平台", "建模软件"]
                }
            ],
            "content_types": ["视频", "交互式模拟", "VR体验", "AI对话"]
        },

        "assessment_expert": {
            "assessment_framework": {
                "formative_assessment": "过程性评价，关注学习过程",
                "summative_assessment": "成果性评价，关注能力表现",
                "peer_assessment": "同伴评价，培养批判性思维",
                "self_reflection": "自我反思，发展元认知能力"
            },
            "core_competencies_rubric": {
                "human_ai_collaboration": "人机协作能力评价标准",
                "creative_problem_solving": "创造性问题解决评价标准",
                "digital_literacy": "数字素养评价标准"
            }
        },

        "material_creator": {
            "digital_resources": [
                {
                    "type": "交互式课件",
                    "description": "支持AI辅助学习的多媒体课件",
                    "tools": ["H5P", "Articulate", "AI对话集成"]
                },
                {
                    "type": "项目工具包",
                    "description": "学生项目实践所需的数字工具集",
                    "tools": ["协作平台", "AI写作助手", "数据可视化工具"]
                }
            ],
            "ai_integration_guide": "学生和教师AI工具使用指南"
        }
    }

    # 模拟处理时间
    await asyncio.sleep(1.5)

    return simulation_results.get(agent_id, {"result": f"{agent_id} 模拟结果"})

@router.get("/health")
async def websocket_health():
    """WebSocket模块健康检查"""
    return {"status": "ok", "module": "websocket", "active_connections": len(manager.active_connections)}