"""
智能体API接口模块
提供多智能体交互的RESTful API和实时通信接口
"""

from typing import List, Dict, Any, Optional, Union
from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    BackgroundTasks, 
    Query,
    Body
)
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

from app.core.dependencies import get_current_user, get_agent_orchestrator
from app.core.exceptions import AgentException, ValidationException
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    AgentStatus,
    ConversationCreate,
    ConversationResponse,
    ConversationHistory,
    AgentCollaborationRequest,
    AgentMetrics
)
from app.schemas.user import User
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.websocket_manager import WebSocketManager
from app.utils.cache import cache_result
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """
    获取所有可用智能体信息
    
    返回智能体列表，包括名称、描述、状态和能力信息
    """
    agents_info = {
        "education_director": {
            "name": "教育总监",
            "description": "教育愿景指导、战略决策制定、跨学科整合专家",
            "model": "opus",
            "capabilities": [
                "教育愿景与战略规划",
                "跨学科课程整合", 
                "学习者中心设计",
                "创新教育实践推广",
                "教育质量保证"
            ],
            "status": "active",
            "expertise_level": "expert",
            "response_time_avg": "2-5秒"
        },
        "pbl_curriculum_designer": {
            "name": "PBL课程设计师",
            "description": "项目式学习课程设计、驱动性问题创建专家",
            "model": "opus",
            "capabilities": [
                "驱动性问题设计",
                "项目框架构建",
                "学习目标对齐",
                "评估体系设计",
                "差异化教学方案"
            ],
            "status": "active",
            "expertise_level": "expert",
            "response_time_avg": "3-6秒"
        },
        "learning_experience_designer": {
            "name": "学习体验设计师",
            "description": "学习旅程优化、互动体验设计专家",
            "model": "sonnet",
            "capabilities": [
                "学习路径设计",
                "互动体验优化",
                "学习分析应用",
                "个性化学习支持",
                "用户体验改进"
            ],
            "status": "active",
            "expertise_level": "advanced",
            "response_time_avg": "1-3秒"
        },
        "creative_technologist": {
            "name": "创意技术专家", 
            "description": "技术教育应用、AI工具指导专家",
            "model": "sonnet",
            "capabilities": [
                "AI工具集成指导",
                "数字创作支持",
                "技术教学应用",
                "创新工具推荐",
                "数字素养培养"
            ],
            "status": "active",
            "expertise_level": "advanced",
            "response_time_avg": "1-3秒"
        },
        "makerspace_manager": {
            "name": "创客空间管理员",
            "description": "物理空间运营、工具管理、制作指导专家",
            "model": "sonnet", 
            "capabilities": [
                "空间布局设计",
                "工具设备管理",
                "安全规范制定",
                "制作流程指导",
                "项目展示规划"
            ],
            "status": "active",
            "expertise_level": "advanced",
            "response_time_avg": "1-3秒"
        }
    }
    
    return {
        "agents": agents_info,
        "total_count": len(agents_info),
        "active_count": sum(1 for agent in agents_info.values() if agent["status"] == "active"),
        "collaboration_modes": ["sequential", "parallel", "hierarchical"],
        "supported_languages": ["中文", "English"],
        "last_updated": datetime.utcnow().isoformat()
    }


@router.post("/agents/{agent_name}/chat", response_model=AgentResponse)
async def chat_with_agent(
    agent_name: str,
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    与指定智能体进行单轮对话
    
    Args:
        agent_name: 智能体名称
        request: 对话请求内容
        current_user: 当前用户
        orchestrator: 智能体编排器
    
    Returns:
        智能体响应结果
    """
    try:
        logger.info(f"用户 {current_user.id} 开始与智能体 {agent_name} 对话")
        
        # 验证智能体是否存在
        if not await orchestrator.is_agent_available(agent_name):
            raise HTTPException(
                status_code=404,
                detail=f"智能体 '{agent_name}' 不存在或不可用"
            )
        
        # 执行对话
        response = await orchestrator.chat_with_agent(
            agent_name=agent_name,
            message=request.message,
            context=request.context,
            user_id=current_user.id,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"智能体 {agent_name} 对话完成，响应长度: {len(response.content)}")
        
        return AgentResponse(
            agent_name=agent_name,
            content=response.content,
            conversation_id=response.conversation_id,
            message_id=response.message_id,
            metadata=response.metadata,
            timestamp=datetime.utcnow(),
            status="success"
        )
        
    except AgentException as e:
        logger.error(f"智能体 {agent_name} 处理失败: {e}")
        raise
    except Exception as e:
        logger.exception(f"与智能体 {agent_name} 对话时发生未知错误")
        raise HTTPException(status_code=500, detail="智能体服务暂时不可用")


@router.post("/agents/collaborate", response_model=AgentResponse) 
async def multi_agent_collaboration(
    request: AgentCollaborationRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    多智能体协作处理复杂任务
    
    根据任务类型和需求，自动选择合适的智能体组合进行协作
    
    Args:
        request: 协作请求，包含任务描述和协作模式
        current_user: 当前用户
        orchestrator: 智能体编排器
    
    Returns:
        协作结果，包含各智能体的贡献
    """
    try:
        logger.info(f"用户 {current_user.id} 发起多智能体协作任务")
        
        # 根据任务自动选择智能体
        selected_agents = await orchestrator.select_agents_for_task(
            task_description=request.task_description,
            task_type=request.task_type,
            required_expertise=request.required_expertise
        )
        
        logger.info(f"为任务选择智能体: {selected_agents}")
        
        # 执行协作流程
        collaboration_result = await orchestrator.execute_collaboration(
            agents=selected_agents,
            task=request.task_description,
            mode=request.collaboration_mode,
            context=request.context,
            user_id=current_user.id
        )
        
        return AgentResponse(
            agent_name="collaboration_team",
            content=collaboration_result.final_output,
            conversation_id=collaboration_result.session_id,
            message_id=collaboration_result.task_id,
            metadata={
                "participating_agents": collaboration_result.agents_involved,
                "collaboration_mode": request.collaboration_mode,
                "task_type": request.task_type,
                "execution_time": collaboration_result.execution_time,
                "quality_score": collaboration_result.quality_score
            },
            timestamp=datetime.utcnow(),
            status="success"
        )
        
    except Exception as e:
        logger.exception("多智能体协作失败")
        raise HTTPException(status_code=500, detail="协作任务执行失败")


@router.get("/agents/{agent_name}/stream")
async def stream_agent_response(
    agent_name: str,
    message: str = Query(..., description="发送给智能体的消息"),
    conversation_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    流式获取智能体响应
    
    适用于需要实时显示智能体思考过程的场景
    """
    async def generate_stream():
        try:
            async for chunk in orchestrator.stream_agent_response(
                agent_name=agent_name,
                message=message,
                user_id=current_user.id,
                conversation_id=conversation_id
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_data = {
                "error": "stream_error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    创建新的对话会话
    
    支持指定主题、参与智能体和初始上下文
    """
    try:
        session = await orchestrator.create_conversation(
            title=conversation.title,
            description=conversation.description,
            participants=conversation.agents,
            initial_context=conversation.initial_context,
            user_id=current_user.id
        )
        
        return ConversationResponse(
            conversation_id=session.id,
            title=session.title,
            description=session.description,
            participants=session.agents,
            created_at=session.created_at,
            status="active"
        )
    except Exception as e:
        logger.exception("创建对话会话失败")
        raise HTTPException(status_code=500, detail="无法创建对话会话")


@router.get("/conversations/{conversation_id}/history", response_model=ConversationHistory)
@cache_result(ttl=300)  # 缓存5分钟
async def get_conversation_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    获取对话历史记录
    
    支持分页和过滤
    """
    try:
        history = await orchestrator.get_conversation_history(
            conversation_id=conversation_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=history.messages,
            total_count=history.total_count,
            has_more=history.has_more
        )
    except Exception as e:
        logger.exception("获取对话历史失败")
        raise HTTPException(status_code=500, detail="无法获取对话历史")


@router.get("/agents/metrics", response_model=AgentMetrics)
async def get_agent_metrics(
    agent_name: Optional[str] = Query(None),
    time_range: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$"),
    current_user: User = Depends(get_current_user)
):
    """
    获取智能体性能指标
    
    包括响应时间、成功率、用户满意度等指标
    """
    try:
        # 这里应该从监控系统获取实际指标
        # 暂时返回模拟数据
        metrics = {
            "time_range": time_range,
            "agent_name": agent_name,
            "total_requests": 1250,
            "successful_requests": 1198,
            "success_rate": 0.958,
            "average_response_time": 2.3,
            "p95_response_time": 4.1,
            "user_satisfaction": 4.6,
            "error_rate": 0.042,
            "most_common_tasks": [
                {"task": "PBL课程设计", "count": 456},
                {"task": "学习体验优化", "count": 342}, 
                {"task": "技术工具指导", "count": 287}
            ],
            "timestamp": datetime.utcnow()
        }
        
        return AgentMetrics(**metrics)
        
    except Exception as e:
        logger.exception("获取智能体指标失败")
        raise HTTPException(status_code=500, detail="无法获取指标数据")


@router.post("/agents/{agent_name}/feedback")
async def submit_agent_feedback(
    agent_name: str,
    message_id: str = Body(..., embed=True),
    rating: int = Body(..., ge=1, le=5, embed=True),
    feedback: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user)
):
    """
    提交智能体反馈
    
    用于改进智能体性能和用户体验
    """
    try:
        # 记录用户反馈
        await orchestrator.record_feedback(
            agent_name=agent_name,
            message_id=message_id,
            user_id=current_user.id,
            rating=rating,
            feedback=feedback,
            timestamp=datetime.utcnow()
        )
        
        return {
            "message": "反馈提交成功",
            "agent_name": agent_name,
            "rating": rating,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.exception("提交智能体反馈失败") 
        raise HTTPException(status_code=500, detail="反馈提交失败")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    删除对话会话
    
    仅允许用户删除自己的对话
    """
    try:
        await orchestrator.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        return {"message": "对话删除成功", "conversation_id": conversation_id}
        
    except Exception as e:
        logger.exception("删除对话失败")
        raise HTTPException(status_code=500, detail="删除对话失败")


# 批量操作接口
@router.post("/agents/batch-process")
async def batch_process_requests(
    requests: List[AgentRequest],
    max_concurrency: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    批量处理智能体请求
    
    适用于需要处理大量类似任务的场景
    """
    try:
        # 创建批量处理任务
        batch_id = await orchestrator.create_batch_task(
            requests=requests,
            user_id=current_user.id,
            max_concurrency=max_concurrency
        )
        
        # 在后台执行批量处理
        background_tasks.add_task(
            orchestrator.execute_batch_task,
            batch_id=batch_id
        )
        
        return {
            "batch_id": batch_id,
            "total_requests": len(requests),
            "status": "processing",
            "estimated_completion": "根据队列情况而定"
        }
        
    except Exception as e:
        logger.exception("批量处理请求失败")
        raise HTTPException(status_code=500, detail="批量处理请求失败")