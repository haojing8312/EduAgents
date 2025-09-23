"""
AI调用记录器
详细记录每个AI API调用的完整信息，包括prompt、response和性能指标
确保AI调用过程的完全透明度
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .collaboration_tracker import AIAPICall


class AICallLogger:
    """
    AI API调用记录器
    负责详细记录每次AI调用的完整过程
    """

    def __init__(self):
        self.active_calls: Dict[str, AIAPICall] = {}
        self.completed_calls: List[AIAPICall] = []

    def start_call(
        self,
        model: str,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        additional_params: Dict[str, Any] = None
    ) -> AIAPICall:
        """
        开始记录AI调用

        Args:
            model: 使用的AI模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            additional_params: 其他参数

        Returns:
            AIAPICall: AI调用记录对象
        """

        ai_call = AIAPICall(
            model=model,
            prompt=self._sanitize_prompt(prompt),
            system_prompt=self._sanitize_prompt(system_prompt),
            temperature=temperature,
            max_tokens=max_tokens
        )

        # 添加额外参数
        if additional_params:
            ai_call.additional_params = additional_params

        # 记录调用开始时间（精确到毫秒）
        ai_call.called_at = datetime.utcnow().isoformat()
        ai_call.start_timestamp = time.time()

        # 计算prompt哈希（用于去重和验证）
        ai_call.prompt_hash = self._calculate_prompt_hash(prompt, system_prompt)

        # 存储到活跃调用中
        self.active_calls[ai_call.call_id] = ai_call

        return ai_call

    def complete_call(
        self,
        call_id: str,
        response_content: str,
        tokens_used: Dict[str, int] = None,
        model_info: Dict[str, Any] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Optional[AIAPICall]:
        """
        完成AI调用记录

        Args:
            call_id: 调用ID
            response_content: AI响应内容
            tokens_used: 使用的token数量
            model_info: 模型信息
            success: 是否成功
            error_message: 错误信息

        Returns:
            AIAPICall: 完成的AI调用记录
        """

        if call_id not in self.active_calls:
            return None

        ai_call = self.active_calls[call_id]

        # 记录响应信息
        ai_call.response_content = self._sanitize_response(response_content)
        ai_call.tokens_used = tokens_used or {"input": 0, "output": 0}
        ai_call.success = success
        ai_call.error_message = error_message

        # 计算调用时长
        if hasattr(ai_call, 'start_timestamp'):
            end_timestamp = time.time()
            ai_call.duration_ms = int((end_timestamp - ai_call.start_timestamp) * 1000)
            delattr(ai_call, 'start_timestamp')  # 清理临时属性

        # 计算响应哈希
        ai_call.response_hash = self._calculate_response_hash(response_content)

        # 记录模型信息
        if model_info:
            ai_call.model_info = model_info

        # 计算预估成本
        ai_call.estimated_cost_usd = self._estimate_cost(
            ai_call.model,
            ai_call.tokens_used
        )

        # 移动到已完成调用列表
        del self.active_calls[call_id]
        self.completed_calls.append(ai_call)

        return ai_call

    def get_call_statistics(self) -> Dict[str, Any]:
        """获取调用统计信息"""

        total_calls = len(self.completed_calls)
        successful_calls = sum(1 for call in self.completed_calls if call.success)
        failed_calls = total_calls - successful_calls

        if total_calls == 0:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "success_rate": 0.0,
                "average_duration_ms": 0,
                "total_tokens": {"input": 0, "output": 0},
                "total_cost_usd": 0.0,
                "model_usage": {}
            }

        # 计算平均时长
        total_duration = sum(call.duration_ms for call in self.completed_calls if call.duration_ms > 0)
        average_duration = total_duration / total_calls if total_calls > 0 else 0

        # 计算总token使用
        total_tokens = {"input": 0, "output": 0}
        for call in self.completed_calls:
            total_tokens["input"] += call.tokens_used.get("input", 0)
            total_tokens["output"] += call.tokens_used.get("output", 0)

        # 计算总成本
        total_cost = sum(call.estimated_cost_usd for call in self.completed_calls
                        if hasattr(call, 'estimated_cost_usd') and call.estimated_cost_usd)

        # 统计模型使用情况
        model_usage = {}
        for call in self.completed_calls:
            model = call.model
            if model not in model_usage:
                model_usage[model] = {
                    "count": 0,
                    "total_tokens": {"input": 0, "output": 0},
                    "average_duration_ms": 0,
                    "success_rate": 0.0
                }

            model_usage[model]["count"] += 1
            model_usage[model]["total_tokens"]["input"] += call.tokens_used.get("input", 0)
            model_usage[model]["total_tokens"]["output"] += call.tokens_used.get("output", 0)

        # 计算每个模型的平均时长和成功率
        for model, stats in model_usage.items():
            model_calls = [call for call in self.completed_calls if call.model == model]
            if model_calls:
                total_duration = sum(call.duration_ms for call in model_calls if call.duration_ms > 0)
                stats["average_duration_ms"] = total_duration / len(model_calls)
                successful = sum(1 for call in model_calls if call.success)
                stats["success_rate"] = successful / len(model_calls)

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls,
            "average_duration_ms": average_duration,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "model_usage": model_usage
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""

        if not self.completed_calls:
            return {
                "total_calls": 0,
                "fastest_call_ms": 0,
                "slowest_call_ms": 0,
                "average_call_ms": 0,
                "median_call_ms": 0,
                "p95_call_ms": 0,
                "tokens_per_second": 0
            }

        durations = [call.duration_ms for call in self.completed_calls if call.duration_ms > 0]
        durations.sort()

        total_calls = len(durations)
        if total_calls == 0:
            return {
                "total_calls": 0,
                "fastest_call_ms": 0,
                "slowest_call_ms": 0,
                "average_call_ms": 0,
                "median_call_ms": 0,
                "p95_call_ms": 0,
                "tokens_per_second": 0
            }

        # 计算统计指标
        fastest = min(durations)
        slowest = max(durations)
        average = sum(durations) / total_calls
        median = durations[total_calls // 2]
        p95_index = int(total_calls * 0.95)
        p95 = durations[p95_index] if p95_index < total_calls else durations[-1]

        # 计算token处理速度
        total_tokens = sum(
            call.tokens_used.get("input", 0) + call.tokens_used.get("output", 0)
            for call in self.completed_calls
        )
        total_time_seconds = sum(durations) / 1000
        tokens_per_second = total_tokens / total_time_seconds if total_time_seconds > 0 else 0

        return {
            "total_calls": total_calls,
            "fastest_call_ms": fastest,
            "slowest_call_ms": slowest,
            "average_call_ms": average,
            "median_call_ms": median,
            "p95_call_ms": p95,
            "tokens_per_second": tokens_per_second
        }

    def get_all_calls(self) -> List[Dict[str, Any]]:
        """获取所有调用记录"""
        return [call.to_dict() for call in self.completed_calls]

    def get_failed_calls(self) -> List[Dict[str, Any]]:
        """获取失败的调用记录"""
        failed_calls = [call for call in self.completed_calls if not call.success]
        return [call.to_dict() for call in failed_calls]

    def search_calls(
        self,
        model: Optional[str] = None,
        min_duration_ms: Optional[int] = None,
        max_duration_ms: Optional[int] = None,
        success_only: bool = False,
        prompt_contains: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索调用记录"""

        results = self.completed_calls

        # 按模型过滤
        if model:
            results = [call for call in results if call.model == model]

        # 按时长过滤
        if min_duration_ms is not None:
            results = [call for call in results if call.duration_ms >= min_duration_ms]

        if max_duration_ms is not None:
            results = [call for call in results if call.duration_ms <= max_duration_ms]

        # 只要成功的调用
        if success_only:
            results = [call for call in results if call.success]

        # 按prompt内容过滤
        if prompt_contains:
            results = [call for call in results
                      if prompt_contains.lower() in call.prompt.lower()]

        return [call.to_dict() for call in results]

    def export_calls_report(self, format_type: str = "json") -> Union[str, Dict[str, Any]]:
        """导出调用报告"""

        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_calls": len(self.completed_calls),
                "active_calls": len(self.active_calls)
            },
            "statistics": self.get_call_statistics(),
            "performance_metrics": self.get_performance_metrics(),
            "all_calls": self.get_all_calls(),
            "failed_calls": self.get_failed_calls()
        }

        if format_type == "json":
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif format_type == "dict":
            return report
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _sanitize_prompt(self, prompt: str) -> str:
        """清理prompt内容，移除敏感信息"""
        if not prompt:
            return ""

        # 移除可能的API密钥等敏感信息
        sanitized = prompt

        # 这里可以添加更多的清理规则
        sensitive_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\-]{20,}',
            r'token["\']?\s*[:=]\s*["\']?[\w\-]{20,}',
            r'password["\']?\s*[:=]\s*["\']?.{8,}',
        ]

        import re
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)

        return sanitized

    def _sanitize_response(self, response: str) -> str:
        """清理响应内容"""
        if not response:
            return ""

        # 响应内容通常是安全的，但仍然进行基本清理
        return response

    def _calculate_prompt_hash(self, prompt: str, system_prompt: str) -> str:
        """计算prompt哈希值"""
        combined = f"{system_prompt}|||{prompt}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    def _calculate_response_hash(self, response: str) -> str:
        """计算响应哈希值"""
        return hashlib.md5(response.encode('utf-8')).hexdigest()

    def _estimate_cost(self, model: str, tokens_used: Dict[str, int]) -> float:
        """估算调用成本（美元）"""

        # 简化的成本估算模型
        cost_per_1k_tokens = {
            "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }

        # 默认成本（如果模型不在列表中）
        default_cost = {"input": 0.001, "output": 0.002}

        model_cost = cost_per_1k_tokens.get(model.lower(), default_cost)

        input_cost = (tokens_used.get("input", 0) / 1000) * model_cost["input"]
        output_cost = (tokens_used.get("output", 0) / 1000) * model_cost["output"]

        return input_cost + output_cost

    def clear_completed_calls(self):
        """清理已完成的调用记录（释放内存）"""
        self.completed_calls.clear()

    def get_active_calls_count(self) -> int:
        """获取活跃调用数量"""
        return len(self.active_calls)