"""
协作过程追踪API
提供查询和可视化多智能体协作过程的接口
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.agent_service import AgentService
from ...models.collaboration_record import (
    CollaborationQueryParams,
    CollaborationSummarySchema,
    CollaborationDetailSchema,
    CollaborationAnalyticsSchema
)

# Initialize router
router = APIRouter(prefix="/collaboration", tags=["Collaboration Tracking"])

# Initialize agent service
agent_service = AgentService()


class CollaborationSessionResponse(BaseModel):
    """协作会话响应模型"""
    session_id: str
    status: str
    total_duration_seconds: Optional[float] = None
    agents_involved: List[str] = Field(default_factory=list)
    phases_completed: int = 0
    total_ai_calls: int = 0
    total_tokens: Dict[str, int] = Field(default_factory=dict)
    success_rate: float = 0.0
    created_at: datetime


class CollaborationFlowResponse(BaseModel):
    """协作流程响应模型"""
    session_id: str
    workflow_phases: List[Dict[str, Any]]
    agent_interactions: List[Dict[str, Any]]
    state_transitions: List[Dict[str, Any]]
    deliverable_traces: Dict[str, Any]


class AICallAnalyticsResponse(BaseModel):
    """AI调用分析响应模型"""
    session_id: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    average_duration_ms: float
    total_tokens: Dict[str, int]
    estimated_cost_usd: float
    model_usage: Dict[str, Dict[str, Any]]
    call_timeline: List[Dict[str, Any]]


@router.get("/sessions", response_model=List[CollaborationSessionResponse])
async def get_collaboration_sessions(
    status: Optional[str] = Query(None, description="过滤会话状态"),
    limit: int = Query(50, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取协作会话列表

    返回系统中的多智能体协作会话记录
    """

    # 从agent service获取会话信息
    sessions_data = []

    # 遍历活跃的orchestrators获取会话信息
    for session_id, orchestrator in agent_service.orchestrators.items():
        collaboration_record = orchestrator.get_collaboration_record()

        if collaboration_record:
            session_metadata = collaboration_record.get("session_metadata", {})
            collaboration_stats = collaboration_record.get("collaboration_statistics", {})
            workflow_phases = collaboration_record.get("workflow_execution", {}).get("phases", [])

            # 提取涉及的智能体
            agent_interactions = collaboration_record.get("agent_interactions", [])
            agents_involved = list(set([
                interaction.get("agent_role")
                for interaction in agent_interactions
                if interaction.get("agent_role")
            ]))

            session_response = CollaborationSessionResponse(
                session_id=session_id,
                status=session_metadata.get("status", "unknown"),
                total_duration_seconds=session_metadata.get("total_duration_seconds"),
                agents_involved=agents_involved,
                phases_completed=len([p for p in workflow_phases if p.get("status") == "completed"]),
                total_ai_calls=collaboration_stats.get("total_ai_api_calls", 0),
                total_tokens=collaboration_stats.get("total_tokens_used", {}),
                success_rate=collaboration_stats.get("success_rate", 0.0),
                created_at=datetime.fromisoformat(session_metadata.get("started_at", datetime.utcnow().isoformat()))
            )

            # 应用状态过滤
            if status is None or session_response.status == status:
                sessions_data.append(session_response)

    # 按创建时间倒序排列
    sessions_data.sort(key=lambda x: x.created_at, reverse=True)

    # 应用分页
    return sessions_data[offset:offset + limit]


@router.get("/sessions/{session_id}/flow", response_model=CollaborationFlowResponse)
async def get_collaboration_flow(session_id: str):
    """
    获取指定会话的协作流程详情

    返回完整的智能体协作流程，包括工作流阶段、智能体交互和状态转换
    """

    # 首先检查活跃的orchestrator
    collaboration_record = None
    if session_id in agent_service.orchestrators:
        orchestrator = agent_service.orchestrators[session_id]
        collaboration_record = orchestrator.get_collaboration_record()

    # 如果没有找到协作记录，检查会话记录
    if not collaboration_record and session_id in agent_service.sessions:
        session = agent_service.sessions[session_id]
        # 从会话结果中获取部分协作数据
        result = session.get("result", {})
        if "collaboration_record" in result:
            collaboration_record = result["collaboration_record"]

    if not collaboration_record:
        raise HTTPException(status_code=404, detail=f"No collaboration record found for session {session_id}")

    # 构建协作流程响应
    workflow_phases = collaboration_record.get("workflow_execution", {}).get("phases", [])
    agent_interactions = collaboration_record.get("agent_interactions", [])
    state_evolution = collaboration_record.get("state_evolution", [])
    deliverable_traces = collaboration_record.get("deliverable_traceability", {})

    return CollaborationFlowResponse(
        session_id=session_id,
        workflow_phases=workflow_phases,
        agent_interactions=agent_interactions,
        state_transitions=state_evolution,
        deliverable_traces=deliverable_traces
    )


@router.get("/sessions/{session_id}/ai-calls", response_model=AICallAnalyticsResponse)
async def get_ai_call_analytics(session_id: str):
    """
    获取指定会话的AI调用分析

    返回详细的AI API调用统计和分析数据
    """

    # 首先检查活跃的orchestrator
    orchestrator = None
    if session_id in agent_service.orchestrators:
        orchestrator = agent_service.orchestrators[session_id]

    # 如果没有活跃orchestrator但会话存在，返回默认响应
    if not orchestrator:
        if session_id in agent_service.sessions:
            return AICallAnalyticsResponse(
                session_id=session_id,
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                average_duration_ms=0.0,
                total_tokens={"input": 0, "output": 0},
                estimated_cost_usd=0.0,
                model_usage={},
                call_timeline=[]
            )
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # 获取AI调用统计
    ai_call_stats = orchestrator.ai_call_logger.get_call_statistics()
    performance_metrics = orchestrator.ai_call_logger.get_performance_metrics()
    all_calls = orchestrator.ai_call_logger.get_all_calls()

    # 构建调用时间线
    call_timeline = []
    for call in all_calls:
        call_timeline.append({
            "timestamp": call.get("called_at"),
            "model": call.get("model"),
            "duration_ms": call.get("duration_ms"),
            "tokens_used": call.get("tokens_used"),
            "success": call.get("success")
        })

    # 按时间排序
    call_timeline.sort(key=lambda x: x["timestamp"])

    return AICallAnalyticsResponse(
        session_id=session_id,
        total_calls=ai_call_stats["total_calls"],
        successful_calls=ai_call_stats["successful_calls"],
        failed_calls=ai_call_stats["failed_calls"],
        average_duration_ms=performance_metrics["average_call_ms"],
        total_tokens=ai_call_stats["total_tokens"],
        estimated_cost_usd=ai_call_stats["total_cost_usd"],
        model_usage=ai_call_stats["model_usage"],
        call_timeline=call_timeline
    )


@router.get("/sessions/{session_id}/deliverables")
async def get_deliverable_traceability(session_id: str):
    """
    获取交付物追踪信息

    返回每个交付物的数据来源和生成过程追踪
    """

    # 首先检查活跃的orchestrator
    collaboration_record = None
    if session_id in agent_service.orchestrators:
        orchestrator = agent_service.orchestrators[session_id]
        collaboration_record = orchestrator.get_collaboration_record()

    # 如果没有找到协作记录，检查会话记录
    if not collaboration_record and session_id in agent_service.sessions:
        session = agent_service.sessions[session_id]
        result = session.get("result", {})
        if "collaboration_record" in result:
            collaboration_record = result["collaboration_record"]

    # 如果仍然没有找到，但会话存在，返回空响应
    if not collaboration_record:
        if session_id in agent_service.sessions:
            return {
                "session_id": session_id,
                "deliverable_traces": {},
                "summary": {
                    "total_deliverables": 0,
                    "agents_involved": 0,
                    "total_processing_time": 0
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    deliverable_traces = collaboration_record.get("deliverable_traceability", {})
    agent_interactions = collaboration_record.get("agent_interactions", [])

    # 为每个交付物构建详细的追踪信息
    detailed_traces = {}

    for component_name, trace in deliverable_traces.items():
        source_execution_ids = trace.get("source_execution_ids", [])

        # 查找相关的智能体执行记录
        related_executions = []
        for execution_id in source_execution_ids:
            execution = next(
                (ex for ex in agent_interactions if ex.get("execution_id") == execution_id),
                None
            )
            if execution:
                related_executions.append({
                    "execution_id": execution_id,
                    "agent_role": execution.get("agent_role"),
                    "agent_name": execution.get("agent_name"),
                    "task_type": execution.get("task_type"),
                    "started_at": execution.get("started_at"),
                    "duration_seconds": execution.get("duration_seconds"),
                    "quality_score": execution.get("quality_score"),
                    "ai_calls_count": len(execution.get("ai_api_calls", []))
                })

        detailed_traces[component_name] = {
            "component_info": {
                "name": component_name,
                "generated_at": trace.get("generated_at"),
                "content_hash": trace.get("content_hash"),
                "content_size": len(str(trace.get("data_content", "")))
            },
            "contributing_agents": trace.get("contributing_agents", []),
            "source_executions": related_executions,
            "data_lineage": {
                "total_executions": len(related_executions),
                "total_ai_calls": sum(ex.get("ai_calls_count", 0) for ex in related_executions),
                "average_quality_score": (
                    sum(ex.get("quality_score", 0) for ex in related_executions) / len(related_executions)
                    if related_executions else 0
                ),
                "total_processing_time": sum(ex.get("duration_seconds", 0) for ex in related_executions)
            }
        }

    return {
        "session_id": session_id,
        "deliverable_traces": detailed_traces,
        "summary": {
            "total_deliverables": len(detailed_traces),
            "agents_involved": len(set([
                agent for trace in detailed_traces.values()
                for agent in trace.get("contributing_agents", [])
            ])),
            "total_processing_time": sum([
                trace.get("data_lineage", {}).get("total_processing_time", 0)
                for trace in detailed_traces.values()
            ])
        }
    }


@router.get("/sessions/{session_id}/export")
async def export_collaboration_record(
    session_id: str,
    format_type: str = Query("json", regex="^(json|csv)$", description="导出格式")
):
    """
    导出协作记录

    将完整的协作过程记录导出为指定格式
    """

    # 首先检查活跃的orchestrator
    orchestrator = None
    if session_id in agent_service.orchestrators:
        orchestrator = agent_service.orchestrators[session_id]

    # 如果没有活跃orchestrator但会话存在，提供基本导出
    if not orchestrator:
        if session_id in agent_service.sessions:
            session = agent_service.sessions[session_id]
            if format_type == "json":
                return {
                    "session_id": session_id,
                    "format": "json",
                    "content": {
                        "session_id": session_id,
                        "status": session.get("status", "unknown"),
                        "error": session.get("error"),
                        "note": "This session failed or is incomplete. Limited data available."
                    },
                    "exported_at": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(status_code=501, detail="CSV export not yet implemented for failed sessions")
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    try:
        if format_type == "json":
            report = orchestrator.export_collaboration_report("json")
            return {
                "session_id": session_id,
                "format": "json",
                "content": report,
                "exported_at": datetime.utcnow().isoformat()
            }
        elif format_type == "csv":
            # 实现CSV导出逻辑
            raise HTTPException(status_code=501, detail="CSV export not yet implemented")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format_type}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/analytics/overview")
async def get_collaboration_analytics():
    """
    获取协作分析概览

    返回系统级别的协作统计和分析数据
    """

    total_sessions = len(agent_service.orchestrators)
    active_sessions = 0
    completed_sessions = 0
    failed_sessions = 0

    total_ai_calls = 0
    total_cost = 0.0
    agent_usage_stats = {}
    model_usage_stats = {}

    # 聚合所有会话的统计数据
    for session_id, orchestrator in agent_service.orchestrators.items():
        collaboration_record = orchestrator.get_collaboration_record()

        if collaboration_record:
            session_metadata = collaboration_record.get("session_metadata", {})
            collaboration_stats = collaboration_record.get("collaboration_statistics", {})

            # 会话状态统计
            status = session_metadata.get("status", "unknown")
            if status == "running":
                active_sessions += 1
            elif status == "completed":
                completed_sessions += 1
            elif status == "failed":
                failed_sessions += 1

            # AI调用统计
            total_ai_calls += collaboration_stats.get("total_ai_api_calls", 0)
            total_cost += collaboration_stats.get("estimated_cost_usd", 0.0)

            # 智能体使用统计
            agent_interactions = collaboration_record.get("agent_interactions", [])
            for interaction in agent_interactions:
                agent_role = interaction.get("agent_role")
                if agent_role:
                    if agent_role not in agent_usage_stats:
                        agent_usage_stats[agent_role] = {
                            "total_executions": 0,
                            "total_duration": 0,
                            "average_quality": 0,
                            "success_rate": 0
                        }

                    agent_usage_stats[agent_role]["total_executions"] += 1
                    agent_usage_stats[agent_role]["total_duration"] += interaction.get("duration_seconds", 0)

                    # AI调用统计
                    ai_calls = interaction.get("ai_api_calls", [])
                    for ai_call in ai_calls:
                        model = ai_call.get("model")
                        if model:
                            if model not in model_usage_stats:
                                model_usage_stats[model] = {
                                    "total_calls": 0,
                                    "total_tokens": {"input": 0, "output": 0},
                                    "total_cost": 0,
                                    "average_duration": 0
                                }

                            model_usage_stats[model]["total_calls"] += 1
                            tokens_used = ai_call.get("tokens_used", {})
                            model_usage_stats[model]["total_tokens"]["input"] += tokens_used.get("input", 0)
                            model_usage_stats[model]["total_tokens"]["output"] += tokens_used.get("output", 0)

    # 计算平均值
    for agent_role, stats in agent_usage_stats.items():
        if stats["total_executions"] > 0:
            stats["average_duration"] = stats["total_duration"] / stats["total_executions"]

    for model, stats in model_usage_stats.items():
        if stats["total_calls"] > 0:
            stats["average_duration"] = stats.get("total_duration", 0) / stats["total_calls"]

    return CollaborationAnalyticsSchema(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        completed_sessions=completed_sessions,
        failed_sessions=failed_sessions,
        total_ai_calls=total_ai_calls,
        total_cost_usd=total_cost,
        agent_usage_stats=agent_usage_stats,
        model_usage_stats=model_usage_stats
    )


@router.delete("/sessions/{session_id}")
async def cleanup_collaboration_session(session_id: str):
    """
    清理协作会话

    删除指定会话的协作记录和相关数据
    """

    if session_id not in agent_service.orchestrators:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    try:
        # 清理orchestrator
        del agent_service.orchestrators[session_id]

        # 清理session记录
        if session_id in agent_service.sessions:
            del agent_service.sessions[session_id]

        # 清理后台任务
        if session_id in agent_service.background_tasks:
            task = agent_service.background_tasks[session_id]
            if not task.done():
                task.cancel()
            del agent_service.background_tasks[session_id]

        return {
            "session_id": session_id,
            "status": "cleaned_up",
            "message": f"Session {session_id} and related data have been cleaned up"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")