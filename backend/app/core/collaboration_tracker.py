"""
多智能体协作过程追踪器
记录详细的Agent交互、AI调用和状态变化过程
确保协作过程的完全透明度和可追溯性
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..agents.core.state import AgentRole, WorkflowPhase


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AIAPICall:
    """AI API调用记录"""
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model: str = ""
    prompt: str = ""
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    called_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    response_content: str = ""
    tokens_used: Dict[str, int] = field(default_factory=dict)
    duration_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class AgentExecution:
    """Agent执行记录"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_role: str = ""
    agent_name: str = ""
    phase: str = ""
    task_type: str = ""
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    status: ExecutionStatus = ExecutionStatus.PENDING

    # 输入数据
    input_data: Dict[str, Any] = field(default_factory=dict)
    task_content: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    # AI调用记录
    ai_api_calls: List[AIAPICall] = field(default_factory=list)

    # 输出数据
    output_content: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

    # 协作消息
    collaboration_messages: List[Dict[str, Any]] = field(default_factory=list)

    def complete(self, output: Dict[str, Any], success: bool = True, error: Optional[str] = None):
        """标记执行完成"""
        self.completed_at = datetime.utcnow().isoformat()
        self.output_content = output
        self.success = success
        self.status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
        if error:
            self.error_message = error

        # 计算执行时长
        if self.started_at and self.completed_at:
            start_dt = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
            self.duration_seconds = (end_dt - start_dt).total_seconds()

    def add_ai_call(self, ai_call: AIAPICall):
        """添加AI调用记录"""
        self.ai_api_calls.append(ai_call)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass
class WorkflowPhaseExecution:
    """工作流阶段执行记录"""
    phase_name: str = ""
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    status: ExecutionStatus = ExecutionStatus.PENDING
    agent_executions: List[AgentExecution] = field(default_factory=list)

    def complete(self):
        """标记阶段完成"""
        self.completed_at = datetime.utcnow().isoformat()
        self.status = ExecutionStatus.COMPLETED

        # 计算阶段时长
        if self.started_at and self.completed_at:
            start_dt = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
            self.duration_seconds = (end_dt - start_dt).total_seconds()

    def add_agent_execution(self, execution: AgentExecution):
        """添加Agent执行记录"""
        self.agent_executions.append(execution)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass
class StateSnapshot:
    """状态快照"""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    phase: str = ""
    trigger_event: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


@dataclass
class DeliverableTrace:
    """交付物追踪记录"""
    component_name: str = ""
    data_content: Any = None
    source_executions: List[str] = field(default_factory=list)  # execution_ids
    contributing_agents: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    content_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)


class CollaborationTracker:
    """
    多智能体协作过程追踪器
    记录完整的协作过程，确保透明度和可追溯性
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.started_at = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None
        self.total_duration_seconds: float = 0.0

        # 会话元数据
        self.course_requirements: Dict[str, Any] = {}
        self.session_config: Dict[str, Any] = {}

        # 工作流执行记录
        self.workflow_phases: List[WorkflowPhaseExecution] = []
        self.current_phase: Optional[WorkflowPhaseExecution] = None

        # 所有Agent执行记录（扁平化存储便于查询）
        self.all_executions: Dict[str, AgentExecution] = {}

        # 状态演进记录
        self.state_snapshots: List[StateSnapshot] = []

        # 交付物追踪
        self.deliverable_traces: Dict[str, DeliverableTrace] = {}

        # 统计数据
        self.total_ai_calls: int = 0
        self.total_tokens_used: Dict[str, int] = {"input": 0, "output": 0}
        self.total_cost_usd: float = 0.0

    def start_session(self, requirements: Dict[str, Any], config: Dict[str, Any] = None):
        """开始会话追踪"""
        self.course_requirements = requirements
        self.session_config = config or {}
        self.started_at = datetime.utcnow().isoformat()

        # 记录初始状态快照
        self.capture_state_snapshot("session_start", "Session initialized", {
            "requirements": requirements,
            "config": config
        })

    def start_phase(self, phase: WorkflowPhase) -> WorkflowPhaseExecution:
        """开始新的工作流阶段"""
        # 完成当前阶段（如果有）
        if self.current_phase and self.current_phase.status == ExecutionStatus.PENDING:
            self.current_phase.complete()

        # 创建新阶段
        phase_execution = WorkflowPhaseExecution(
            phase_name=phase.value,
            status=ExecutionStatus.RUNNING
        )

        self.workflow_phases.append(phase_execution)
        self.current_phase = phase_execution

        return phase_execution

    def start_agent_execution(
        self,
        agent_role: AgentRole,
        agent_name: str,
        task_type: str,
        phase: WorkflowPhase,
        input_data: Dict[str, Any],
        task_content: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> AgentExecution:
        """开始Agent执行追踪"""

        execution = AgentExecution(
            agent_role=agent_role.value,
            agent_name=agent_name,
            phase=phase.value,
            task_type=task_type,
            input_data=input_data,
            task_content=task_content or {},
            context=context or {},
            status=ExecutionStatus.RUNNING
        )

        # 存储到全局执行记录
        self.all_executions[execution.execution_id] = execution

        # 添加到当前阶段
        if self.current_phase:
            self.current_phase.add_agent_execution(execution)

        return execution

    def log_ai_call(
        self,
        execution_id: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AIAPICall:
        """记录AI API调用开始"""

        ai_call = AIAPICall(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # 添加到对应的Agent执行记录
        if execution_id in self.all_executions:
            self.all_executions[execution_id].add_ai_call(ai_call)

        return ai_call

    def complete_ai_call(
        self,
        ai_call: AIAPICall,
        response_content: str,
        tokens_used: Dict[str, int] = None,
        duration_ms: int = 0,
        success: bool = True,
        error: Optional[str] = None
    ):
        """完成AI API调用记录"""

        ai_call.response_content = response_content
        ai_call.tokens_used = tokens_used or {"input": 0, "output": 0}
        ai_call.duration_ms = duration_ms
        ai_call.success = success
        ai_call.error_message = error

        # 更新统计数据
        self.total_ai_calls += 1
        if tokens_used:
            self.total_tokens_used["input"] += tokens_used.get("input", 0)
            self.total_tokens_used["output"] += tokens_used.get("output", 0)

    def complete_agent_execution(
        self,
        execution_id: str,
        output: Dict[str, Any],
        quality_score: float = 0.0,
        success: bool = True,
        error: Optional[str] = None
    ):
        """完成Agent执行"""

        if execution_id in self.all_executions:
            execution = self.all_executions[execution_id]
            execution.complete(output, success, error)
            execution.quality_score = quality_score

    def capture_state_snapshot(
        self,
        trigger_event: str,
        description: str,
        state_data: Dict[str, Any]
    ):
        """捕获状态快照"""

        snapshot = StateSnapshot(
            phase=self.current_phase.phase_name if self.current_phase else "unknown",
            trigger_event=trigger_event,
            state_data=state_data
        )

        self.state_snapshots.append(snapshot)

    def trace_deliverable(
        self,
        component_name: str,
        data_content: Any,
        source_execution_ids: List[str],
        contributing_agents: List[str] = None
    ):
        """追踪交付物来源"""

        trace = DeliverableTrace(
            component_name=component_name,
            data_content=data_content,
            source_executions=source_execution_ids,
            contributing_agents=contributing_agents or []
        )

        # 计算内容哈希（用于验证完整性）
        content_str = json.dumps(data_content, sort_keys=True, ensure_ascii=False)
        import hashlib
        trace.content_hash = hashlib.md5(content_str.encode()).hexdigest()

        self.deliverable_traces[component_name] = trace

    def complete_session(self):
        """完成会话追踪"""
        self.completed_at = datetime.utcnow().isoformat()

        # 完成当前阶段
        if self.current_phase and self.current_phase.status != ExecutionStatus.COMPLETED:
            self.current_phase.complete()

        # 计算总时长
        if self.started_at and self.completed_at:
            start_dt = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
            self.total_duration_seconds = (end_dt - start_dt).total_seconds()

        # 捕获最终状态快照
        self.capture_state_snapshot("session_complete", "Session completed", {
            "total_executions": len(self.all_executions),
            "total_phases": len(self.workflow_phases),
            "total_ai_calls": self.total_ai_calls,
            "total_tokens": self.total_tokens_used
        })

    def get_collaboration_record(self) -> Dict[str, Any]:
        """获取完整的协作记录"""

        return {
            "session_metadata": {
                "session_id": self.session_id,
                "started_at": self.started_at,
                "completed_at": self.completed_at,
                "total_duration_seconds": self.total_duration_seconds,
                "course_requirements": self.course_requirements,
                "session_config": self.session_config
            },
            "workflow_execution": {
                "total_phases": len(self.workflow_phases),
                "phases": [phase.to_dict() for phase in self.workflow_phases]
            },
            "agent_interactions": [
                execution.to_dict() for execution in self.all_executions.values()
            ],
            "state_evolution": [
                snapshot.to_dict() for snapshot in self.state_snapshots
            ],
            "deliverable_traceability": {
                name: trace.to_dict() for name, trace in self.deliverable_traces.items()
            },
            "collaboration_statistics": {
                "total_agent_executions": len(self.all_executions),
                "total_ai_api_calls": self.total_ai_calls,
                "total_tokens_used": self.total_tokens_used,
                "estimated_cost_usd": self.total_cost_usd,
                "average_execution_duration": self._calculate_avg_execution_duration(),
                "success_rate": self._calculate_success_rate()
            }
        }

    def _calculate_avg_execution_duration(self) -> float:
        """计算平均执行时长"""
        completed_executions = [
            ex for ex in self.all_executions.values()
            if ex.status == ExecutionStatus.COMPLETED
        ]

        if not completed_executions:
            return 0.0

        total_duration = sum(ex.duration_seconds for ex in completed_executions)
        return total_duration / len(completed_executions)

    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.all_executions:
            return 0.0

        successful = sum(1 for ex in self.all_executions.values() if ex.success)
        return successful / len(self.all_executions)

    def export_collaboration_report(self, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """导出协作报告"""

        record = self.get_collaboration_record()

        if format_type == "json":
            return json.dumps(record, indent=2, ensure_ascii=False)
        elif format_type == "dict":
            return record
        else:
            raise ValueError(f"Unsupported format: {format_type}")