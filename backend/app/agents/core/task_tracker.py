"""
任务执行追踪器
提供完整的多智能体任务执行追踪和记录功能
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


class TaskExecutionTracker:
    """
    任务执行追踪器 - 记录任务执行的完整详细信息
    """

    def __init__(self, session_id: str, task_name: str = "未知任务"):
        """
        初始化任务追踪器

        Args:
            session_id: 会话ID
            task_name: 任务名称
        """
        self.session_id = session_id
        self.task_name = task_name
        self.tracking_id = str(uuid4())
        self.start_time = time.time()
        self.start_datetime = datetime.now(timezone.utc)

        # 追踪数据结构
        self.tracking_data = {
            "tracking_metadata": {
                "tracking_id": self.tracking_id,
                "session_id": session_id,
                "task_name": task_name,
                "created_at": self.start_datetime.isoformat(),
                "tracking_version": "1.0"
            },
            "task_overview": {
                "status": "initialized",
                "total_duration_seconds": 0,
                "start_time": self.start_datetime.isoformat(),
                "end_time": None,
                "success": None,
                "error_message": None,
                "final_result": None
            },
            "execution_phases": [],
            "agent_executions": [],
            "llm_interactions": [],
            "state_changes": [],
            "performance_metrics": {
                "total_agents_involved": 0,
                "total_llm_calls": 0,
                "total_tokens_used": {"input": 0, "output": 0},
                "average_response_time_seconds": 0,
                "longest_operation_seconds": 0,
                "memory_usage_mb": 0
            },
            "error_tracking": {
                "errors_encountered": [],
                "warnings_issued": [],
                "recovery_actions": []
            }
        }

        # 导出目录
        self.export_dir = Path("exports/task_tracking")
        self.export_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎯 任务执行追踪器已初始化: {self.tracking_id}")

    def start_task(self, task_type: str, requirements: Dict = None,
                   orchestrator_mode: str = None, max_iterations: int = None):
        """
        开始任务执行

        Args:
            task_type: 任务类型
            requirements: 任务需求
            orchestrator_mode: 编排器模式
            max_iterations: 最大迭代次数
        """
        self.tracking_data["task_overview"]["status"] = "running"
        self.tracking_data["task_overview"]["task_type"] = task_type
        self.tracking_data["task_overview"]["orchestrator_mode"] = orchestrator_mode
        self.tracking_data["task_overview"]["max_iterations"] = max_iterations
        self.tracking_data["task_overview"]["requirements"] = requirements

        logger.info(f"🚀 任务开始执行: {task_type}")

    def start_execution_phase(self, phase_name: str, phase_description: str = "", input_data: Dict = None):
        """
        开始执行阶段 (兼容旧方法名)
        """
        return self.start_phase(phase_name, phase_description)

    def complete_execution_phase(self, phase_name: str, success: bool = True, output_data: Dict = None):
        """
        完成执行阶段
        """
        # 找到最近的该阶段
        for phase in reversed(self.tracking_data["execution_phases"]):
            if phase["phase_name"] == phase_name and phase["status"] == "running":
                phase["end_time"] = datetime.now(timezone.utc).isoformat()
                phase["status"] = "completed" if success else "failed"
                phase["output_data"] = output_data or {}
                phase["success"] = success
                start_time = datetime.fromisoformat(phase["start_time"].replace('Z', '+00:00'))
                end_time = datetime.now(timezone.utc)
                phase["duration_seconds"] = (end_time - start_time).total_seconds()
                break

    def start_agent_execution(self, agent_name: str, agent_role: str, task_type: str, input_data: Dict = None) -> str:
        """
        开始智能体执行 (重写以匹配新的调用方式)
        """
        execution_id = str(uuid4())
        execution_data = {
            "execution_id": execution_id,
            "agent_name": agent_name,
            "agent_role": agent_role,
            "task_type": task_type,
            "input_data": input_data or {},
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "status": "running",
            "success": None,
            "output_data": None,
            "performance_metrics": {}
        }

        self.tracking_data["agent_executions"].append(execution_data)
        self.tracking_data["performance_metrics"]["total_agents_involved"] += 1

        logger.info(f"🤖 智能体开始执行: {agent_name} ({agent_role})")
        return execution_id

    def complete_agent_execution(self, execution_id: str, success: bool = True,
                                output_data: Dict = None, performance_metrics: Dict = None):
        """
        完成智能体执行
        """
        for execution in self.tracking_data["agent_executions"]:
            if execution["execution_id"] == execution_id:
                execution["end_time"] = datetime.now(timezone.utc).isoformat()
                execution["status"] = "completed" if success else "failed"
                execution["success"] = success
                execution["output_data"] = output_data or {}
                execution["performance_metrics"] = performance_metrics or {}

                # 计算执行时间
                start_time = datetime.fromisoformat(execution["start_time"].replace('Z', '+00:00'))
                end_time = datetime.now(timezone.utc)
                execution["duration_seconds"] = (end_time - start_time).total_seconds()

                logger.info(f"✅ 智能体执行完成: {execution['agent_name']}")
                break

    def complete_task(self, success: bool = True, final_output: Any = None,
                     error_details: Dict = None, performance_summary: Dict = None):
        """
        完成任务执行
        """
        end_time = datetime.now(timezone.utc)
        self.tracking_data["task_overview"]["end_time"] = end_time.isoformat()
        self.tracking_data["task_overview"]["status"] = "completed" if success else "failed"
        self.tracking_data["task_overview"]["success"] = success
        self.tracking_data["task_overview"]["total_duration_seconds"] = end_time.timestamp() - self.start_time

        if success:
            self.tracking_data["task_overview"]["final_result"] = final_output
            if performance_summary:
                self.tracking_data["performance_metrics"].update(performance_summary)
        else:
            self.tracking_data["task_overview"]["error_message"] = error_details.get("error_message", "Unknown error") if error_details else "Unknown error"
            self.tracking_data["error_tracking"]["errors_encountered"].append({
                "timestamp": end_time.isoformat(),
                "error_details": error_details or {}
            })

        logger.info(f"🎯 任务执行完成: {'成功' if success else '失败'}")

    def save_tracking_data(self, filename: str = None) -> str:
        """
        保存追踪数据到文件
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_execution_{self.session_id[:8]}_{timestamp}.json"

        filepath = self.export_dir / filename

        # 自定义JSON编码器以处理枚举和其他复杂类型
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                from ..core.state import AgentRole, WorkflowPhase
                if isinstance(obj, (AgentRole, WorkflowPhase)):
                    return obj.value
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                return super().default(obj)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)

        logger.info(f"💾 任务追踪数据已保存: {filepath}")
        return str(filepath)

    def start_phase(self, phase_name: str, description: str = "") -> str:
        """
        开始一个执行阶段

        Args:
            phase_name: 阶段名称
            description: 阶段描述

        Returns:
            phase_id: 阶段ID
        """
        phase_id = str(uuid4())
        phase_data = {
            "phase_id": phase_id,
            "phase_name": phase_name,
            "description": description,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "status": "running",
            "agents_involved": [],
            "sub_tasks": [],
            "outputs": {}
        }

        self.tracking_data["execution_phases"].append(phase_data)
        logger.info(f"📋 开始执行阶段: {phase_name} (ID: {phase_id})")
        return phase_id

    def end_phase(self, phase_id: str, status: str = "completed", outputs: Dict = None):
        """
        结束一个执行阶段

        Args:
            phase_id: 阶段ID
            status: 阶段状态 (completed, failed, skipped)
            outputs: 阶段输出
        """
        for phase in self.tracking_data["execution_phases"]:
            if phase["phase_id"] == phase_id:
                end_time = datetime.now(timezone.utc)
                phase["end_time"] = end_time.isoformat()
                phase["status"] = status
                phase["outputs"] = outputs or {}

                # 计算耗时
                start_time = datetime.fromisoformat(phase["start_time"].replace('Z', '+00:00'))
                phase["duration_seconds"] = (end_time - start_time).total_seconds()

                logger.info(f"✅ 阶段完成: {phase['phase_name']} - {status} (耗时: {phase['duration_seconds']:.2f}秒)")
                break


    def end_agent_execution(self, execution_id: str, status: str = "completed",
                          output_data: Any = None, error_message: str = None):
        """
        结束智能体执行

        Args:
            execution_id: 执行ID
            status: 执行状态
            output_data: 输出数据
            error_message: 错误信息
        """
        for execution in self.tracking_data["agent_executions"]:
            if execution["execution_id"] == execution_id:
                end_time = datetime.now(timezone.utc)
                execution["end_time"] = end_time.isoformat()
                execution["status"] = status
                execution["output_data"] = output_data

                if error_message:
                    execution["error_message"] = error_message

                # 计算耗时
                start_time = datetime.fromisoformat(execution["start_time"].replace('Z', '+00:00'))
                execution["duration_seconds"] = (end_time - start_time).total_seconds()

                # 更新性能指标
                metrics = self.tracking_data["performance_metrics"]
                if execution["duration_seconds"] > metrics["longest_operation_seconds"]:
                    metrics["longest_operation_seconds"] = execution["duration_seconds"]

                logger.info(f"🎉 智能体执行完成: {execution['agent_name']} - {status}")
                break

    def record_llm_interaction(self, execution_id: str, model: str, prompt: str,
                             response: str, tokens_used: Dict, duration_seconds: float,
                             success: bool = True, error_message: str = None):
        """
        记录LLM交互

        Args:
            execution_id: 关联的智能体执行ID
            model: 模型名称
            prompt: 输入提示
            response: 响应内容
            tokens_used: 使用的token数量 {"input": x, "output": y}
            duration_seconds: 耗时
            success: 是否成功
            error_message: 错误信息
        """
        interaction_id = str(uuid4())
        interaction_data = {
            "interaction_id": interaction_id,
            "execution_id": execution_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
            "prompt_length": len(prompt),
            "response_preview": response[:500] + "..." if len(response) > 500 else response,
            "response_length": len(response),
            "tokens_used": tokens_used,
            "duration_seconds": duration_seconds,
            "success": success,
            "error_message": error_message
        }

        self.tracking_data["llm_interactions"].append(interaction_data)

        # 更新性能指标
        metrics = self.tracking_data["performance_metrics"]
        metrics["total_llm_calls"] += 1
        metrics["total_tokens_used"]["input"] += tokens_used.get("input", 0)
        metrics["total_tokens_used"]["output"] += tokens_used.get("output", 0)

        # 更新对应智能体执行的指标
        for execution in self.tracking_data["agent_executions"]:
            if execution["execution_id"] == execution_id:
                execution["llm_calls"].append(interaction_id)
                execution["performance_metrics"]["api_calls_count"] += 1
                execution["performance_metrics"]["tokens_used"]["input"] += tokens_used.get("input", 0)
                execution["performance_metrics"]["tokens_used"]["output"] += tokens_used.get("output", 0)
                if not success:
                    execution["performance_metrics"]["error_count"] += 1
                break

        logger.debug(f"💬 LLM交互已记录: {model} (ID: {interaction_id})")

    def record_state_change(self, change_type: str, description: str,
                          before_state: Dict = None, after_state: Dict = None):
        """
        记录状态变化

        Args:
            change_type: 变化类型
            description: 变化描述
            before_state: 变化前状态
            after_state: 变化后状态
        """
        state_change = {
            "change_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "change_type": change_type,
            "description": description,
            "before_state": before_state,
            "after_state": after_state
        }

        self.tracking_data["state_changes"].append(state_change)
        logger.debug(f"🔄 状态变化已记录: {change_type}")

    def record_error(self, error_type: str, error_message: str,
                    context: Dict = None, stack_trace: str = None):
        """
        记录错误

        Args:
            error_type: 错误类型
            error_message: 错误信息
            context: 错误上下文
            stack_trace: 堆栈跟踪
        """
        error_record = {
            "error_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {},
            "stack_trace": stack_trace
        }

        self.tracking_data["error_tracking"]["errors_encountered"].append(error_record)
        logger.error(f"❌ 错误已记录: {error_type} - {error_message}")

    def record_warning(self, warning_type: str, warning_message: str, context: Dict = None):
        """
        记录警告

        Args:
            warning_type: 警告类型
            warning_message: 警告信息
            context: 警告上下文
        """
        warning_record = {
            "warning_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "warning_type": warning_type,
            "warning_message": warning_message,
            "context": context or {}
        }

        self.tracking_data["error_tracking"]["warnings_issued"].append(warning_record)
        logger.warning(f"⚠️ 警告已记录: {warning_type} - {warning_message}")

    def record_recovery_action(self, action_type: str, description: str,
                             original_error_id: str = None):
        """
        记录恢复操作

        Args:
            action_type: 操作类型
            description: 操作描述
            original_error_id: 原始错误ID
        """
        recovery_record = {
            "recovery_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "description": description,
            "original_error_id": original_error_id
        }

        self.tracking_data["error_tracking"]["recovery_actions"].append(recovery_record)
        logger.info(f"🔧 恢复操作已记录: {action_type}")

    def finalize_tracking(self, success: bool = True, final_result: Any = None,
                         error_message: str = None):
        """
        完成追踪

        Args:
            success: 是否成功
            final_result: 最终结果
            error_message: 错误信息
        """
        end_time = datetime.now(timezone.utc)
        total_duration = time.time() - self.start_time

        # 更新任务概览
        overview = self.tracking_data["task_overview"]
        overview["status"] = "completed" if success else "failed"
        overview["end_time"] = end_time.isoformat()
        overview["total_duration_seconds"] = total_duration
        overview["success"] = success
        overview["final_result"] = final_result
        overview["error_message"] = error_message

        # 计算平均响应时间
        if self.tracking_data["llm_interactions"]:
            total_llm_time = sum(
                interaction["duration_seconds"]
                for interaction in self.tracking_data["llm_interactions"]
            )
            self.tracking_data["performance_metrics"]["average_response_time_seconds"] = (
                total_llm_time / len(self.tracking_data["llm_interactions"])
            )

        # 保存到文件
        self.save_to_file()

        logger.info(f"🎯 任务追踪完成: {self.task_name} - {'成功' if success else '失败'} (总耗时: {total_duration:.2f}秒)")

    def save_to_file(self, filename: str = None) -> str:
        """
        保存追踪数据到文件

        Args:
            filename: 文件名 (可选)

        Returns:
            file_path: 保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_tracking_{self.session_id}_{timestamp}.json"

        file_path = self.export_dir / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 任务追踪数据已保存: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"❌ 保存任务追踪数据失败: {e}")
            return None

    def get_tracking_summary(self) -> Dict:
        """
        获取追踪摘要

        Returns:
            summary: 追踪摘要
        """
        overview = self.tracking_data["task_overview"]
        metrics = self.tracking_data["performance_metrics"]
        errors = self.tracking_data["error_tracking"]

        return {
            "tracking_id": self.tracking_id,
            "task_name": self.task_name,
            "status": overview["status"],
            "duration_seconds": overview["total_duration_seconds"],
            "success": overview["success"],
            "agents_count": metrics["total_agents_involved"],
            "llm_calls_count": metrics["total_llm_calls"],
            "total_tokens": metrics["total_tokens_used"],
            "errors_count": len(errors["errors_encountered"]),
            "warnings_count": len(errors["warnings_issued"])
        }

    def export_detailed_report(self) -> str:
        """
        导出详细报告

        Returns:
            report_path: 报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"detailed_report_{self.session_id}_{timestamp}.json"

        # 创建详细报告
        detailed_report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "tracking_id": self.tracking_id,
                "session_id": self.session_id,
                "report_version": "1.0"
            },
            "executive_summary": self.get_tracking_summary(),
            "full_tracking_data": self.tracking_data,
            "analysis": self._generate_analysis()
        }

        report_path = self.export_dir / report_filename

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(detailed_report, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 详细报告已导出: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"❌ 导出详细报告失败: {e}")
            return None

    def _generate_analysis(self) -> Dict:
        """
        生成分析数据

        Returns:
            analysis: 分析结果
        """
        phases = self.tracking_data["execution_phases"]
        agents = self.tracking_data["agent_executions"]
        llm_calls = self.tracking_data["llm_interactions"]

        analysis = {
            "phase_analysis": {
                "total_phases": len(phases),
                "completed_phases": len([p for p in phases if p["status"] == "completed"]),
                "failed_phases": len([p for p in phases if p["status"] == "failed"]),
                "average_phase_duration": (
                    sum(p["duration_seconds"] for p in phases) / len(phases)
                    if phases else 0
                ),
                "longest_phase": (
                    max(phases, key=lambda p: p["duration_seconds"])["phase_name"]
                    if phases else None
                )
            },
            "agent_analysis": {
                "total_agents": len(agents),
                "successful_agents": len([a for a in agents if a["status"] == "completed"]),
                "failed_agents": len([a for a in agents if a["status"] == "failed"]),
                "average_agent_duration": (
                    sum(a["duration_seconds"] for a in agents) / len(agents)
                    if agents else 0
                ),
                "most_active_agent": (
                    max(agents, key=lambda a: len(a["llm_calls"]))["agent_name"]
                    if agents else None
                )
            },
            "llm_analysis": {
                "total_calls": len(llm_calls),
                "successful_calls": len([c for c in llm_calls if c["success"]]),
                "failed_calls": len([c for c in llm_calls if not c["success"]]),
                "average_call_duration": (
                    sum(c["duration_seconds"] for c in llm_calls) / len(llm_calls)
                    if llm_calls else 0
                ),
                "total_tokens": self.tracking_data["performance_metrics"]["total_tokens_used"]
            },
            "performance_insights": {
                "bottlenecks": [],
                "optimization_suggestions": [],
                "error_patterns": []
            }
        }

        # 添加性能洞察
        if analysis["llm_analysis"]["average_call_duration"] > 10:
            analysis["performance_insights"]["bottlenecks"].append("LLM调用响应时间较长")
            analysis["performance_insights"]["optimization_suggestions"].append("考虑优化提示词或使用更快的模型")

        if analysis["agent_analysis"]["failed_agents"] > 0:
            analysis["performance_insights"]["error_patterns"].append("存在智能体执行失败")
            analysis["performance_insights"]["optimization_suggestions"].append("检查智能体错误处理逻辑")

        return analysis