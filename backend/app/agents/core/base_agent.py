"""
Base Agent Class - Foundation for all specialized agents
Implements core agent behaviors and communication protocols
Enhanced with comprehensive collaboration tracking
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from .llm_manager import LLMManager, ModelCapability, ModelType
from .state import AgentMessage, AgentRole, AgentState, MessageType

# 配置智能体专用日志
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent operational status"""

    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_FOR_INPUT = "waiting_for_input"
    COLLABORATING = "collaborating"
    ERROR = "error"
    COMPLETED = "completed"


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents
    Provides core functionality for LLM interaction, state management, and communication
    """

    def __init__(
        self,
        role: AgentRole,
        llm_manager: LLMManager,
        name: str,
        description: str,
        capabilities: List[ModelCapability],
        preferred_model: Optional[ModelType] = None,
    ):
        """Initialize base agent"""
        self.role = role
        self.llm_manager = llm_manager
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.preferred_model = preferred_model

        # Agent state
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Dict[str, Any]] = None
        self.task_history: List[Dict[str, Any]] = []
        self.collaboration_requests: List[AgentMessage] = []

        # Performance tracking
        self.tasks_completed = 0
        self.total_processing_time = 0
        self.quality_scores: List[float] = []

        # Collaboration tracking (injected by orchestrator)
        self.ai_call_logger = None
        self.current_execution_id: Optional[str] = None

        # System prompts cache
        self._system_prompts: Dict[str, str] = {}
        self._initialize_system_prompts()

    @abstractmethod
    def _initialize_system_prompts(self) -> None:
        """Initialize agent-specific system prompts"""
        pass

    @abstractmethod
    async def process_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process a specific task - must be implemented by each agent"""
        pass

    @abstractmethod
    async def collaborate(
        self, message: AgentMessage, state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""
        pass

    async def execute(
        self, state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """
        Main execution method for the agent
        Processes messages, executes tasks, and updates state
        """
        start_time = datetime.utcnow()
        logger.info(f"🤖 [{self.name}] 开始执行任务")

        self.status = AgentStatus.PROCESSING
        state.update_agent_status(self.role, self.status.value)

        try:
            # Process incoming messages
            messages = state.get_messages_for_agent(self.role)
            logger.info(f"📬 [{self.name}] 处理 {len(messages)} 条消息")

            for i, message in enumerate(messages):
                logger.info(f"📝 [{self.name}] 处理消息 {i+1}/{len(messages)}: {message.message_type.value}")

                if message.message_type == MessageType.REQUEST:
                    # Log task details
                    task_content = message.content
                    task_preview = str(task_content)[:200] + "..." if len(str(task_content)) > 200 else str(task_content)
                    logger.info(f"🎯 [{self.name}] 任务内容: {task_preview}")

                    # Process task request - handle both async generator and dict returns
                    logger.info(f"⚡ [{self.name}] 调用任务处理方法...")
                    task_start = datetime.utcnow()

                    task_result = self.process_task(message.content, state, stream)

                    # Check if it's an async generator or coroutine
                    import inspect
                    if inspect.isasyncgen(task_result):
                        logger.info(f"🔄 [{self.name}] 处理异步生成器结果...")
                        # It's an async generator
                        if stream:
                            chunk_count = 0
                            async for chunk in task_result:
                                chunk_count += 1
                                logger.debug(f"📦 [{self.name}] 生成块 {chunk_count}")
                                yield chunk
                        else:
                            # Collect all results from async generator
                            result = None
                            chunk_count = 0
                            async for chunk in task_result:
                                chunk_count += 1
                                result = chunk  # Take the last result

                            task_duration = (datetime.utcnow() - task_start).total_seconds()
                            logger.info(f"✅ [{self.name}] 任务完成，耗时 {task_duration:.2f}秒，生成 {chunk_count} 个块")

                            # Send response
                            response = AgentMessage(
                                sender=self.role,
                                recipient=message.sender,
                                message_type=MessageType.RESPONSE,
                                content=result,
                                parent_message_id=message.id,
                            )
                            state.add_message(response)
                            yield result
                    else:
                        logger.info(f"⏳ [{self.name}] 等待协程完成...")
                        # It's a coroutine, await it
                        result = await task_result

                        task_duration = (datetime.utcnow() - task_start).total_seconds()
                        result_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                        logger.info(f"✅ [{self.name}] 任务完成，耗时 {task_duration:.2f}秒")
                        logger.info(f"📋 [{self.name}] 结果预览: {result_preview}")

                        # Send response
                        response = AgentMessage(
                            sender=self.role,
                            recipient=message.sender,
                            message_type=MessageType.RESPONSE,
                            content=result,
                            parent_message_id=message.id,
                        )
                        state.add_message(response)
                        yield result

                elif message.message_type == MessageType.COLLABORATION:
                    logger.info(f"🤝 [{self.name}] 处理协作请求...")
                    # Handle collaboration request
                    response = await self.collaborate(message, state)
                    state.add_message(response)
                    logger.info(f"✅ [{self.name}] 协作响应已发送")

            # Clear processed messages
            state.clear_message_queue(self.role)

            self.status = AgentStatus.COMPLETED
            state.update_agent_status(self.role, self.status.value)

            total_duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"🎉 [{self.name}] 执行完成，总耗时 {total_duration:.2f}秒")

        except Exception as e:
            self.status = AgentStatus.ERROR
            state.update_agent_status(self.role, self.status.value)
            state.log_error(e, self.role, {"task": self.current_task})

            error_duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ [{self.name}] 执行失败，耗时 {error_duration:.2f}秒: {str(e)}", exc_info=True)

            # Send error message
            error_message = AgentMessage(
                sender=self.role,
                message_type=MessageType.ERROR,
                content={
                    "error": str(e),
                    "agent": self.role.value,
                    "task": self.current_task,
                },
            )
            state.add_message(error_message)

            if not stream:
                raise e

    async def _generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None] | str:
        """Generate response using LLM with detailed logging and tracking"""

        # Log prompt details
        prompt_preview = prompt[:300] + "..." if len(prompt) > 300 else prompt
        system_preview = (system_prompt or self._system_prompts.get("default", ""))[:200] + "..." if system_prompt and len(system_prompt) > 200 else system_prompt

        logger.info(f"🧠 [{self.name}] 准备调用AI模型")
        logger.info(f"📝 [{self.name}] Prompt预览: {prompt_preview}")
        logger.info(f"⚙️ [{self.name}] 系统提示: {system_preview}")
        logger.info(f"🌡️ [{self.name}] 温度参数: {temperature}")
        logger.info(f"🎯 [{self.name}] 模型: {self.preferred_model}")

        # Start AI call tracking
        ai_call = None
        if self.ai_call_logger:
            ai_call = self.ai_call_logger.start_call(
                model=str(self.preferred_model) if self.preferred_model else "unknown",
                prompt=prompt,
                system_prompt=system_prompt or self._system_prompts.get("default", ""),
                temperature=temperature
            )

        start_time = datetime.utcnow()

        try:
            response = await self.llm_manager.generate(
                prompt=prompt,
                system_prompt=system_prompt or self._system_prompts.get("default"),
                model=self.preferred_model,
                temperature=temperature,
                required_capabilities=self.capabilities,
                stream=stream,
            )

            if stream:
                logger.info(f"🔄 [{self.name}] 开始流式响应")
                # For streaming, we'll need to collect response and complete tracking later
                return response
            else:
                api_duration = (datetime.utcnow() - start_time).total_seconds()
                response_preview = response.content[:300] + "..." if len(response.content) > 300 else response.content

                logger.info(f"✅ [{self.name}] AI响应完成，耗时 {api_duration:.2f}秒")
                logger.info(f"📖 [{self.name}] 响应内容预览: {response_preview}")
                logger.info(f"📊 [{self.name}] 响应长度: {len(response.content)} 字符")

                # Complete AI call tracking
                if ai_call and self.ai_call_logger:
                    tokens_used = getattr(response, 'usage', {}) or {"input": 0, "output": 0}
                    self.ai_call_logger.complete_call(
                        call_id=ai_call.call_id,
                        response_content=response.content,
                        tokens_used=tokens_used,
                        model_info={"model": str(self.preferred_model)},
                        success=True
                    )

                return response.content

        except Exception as e:
            api_duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"❌ [{self.name}] AI调用失败，耗时 {api_duration:.2f}秒: {str(e)}", exc_info=True)

            # Complete failed AI call tracking
            if ai_call and self.ai_call_logger:
                self.ai_call_logger.complete_call(
                    call_id=ai_call.call_id,
                    response_content="",
                    tokens_used={"input": 0, "output": 0},
                    success=False,
                    error_message=str(e)
                )

            raise

    async def _generate_structured_response(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate structured response using LLM"""
        return await self.llm_manager.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_prompt=system_prompt or self._system_prompts.get("structured"),
            model=self.preferred_model,
        )

    async def request_collaboration(
        self, target_agent: AgentRole, request: Dict[str, Any], state: AgentState
    ) -> None:
        """Request collaboration from another agent"""
        message = AgentMessage(
            sender=self.role,
            recipient=target_agent,
            message_type=MessageType.COLLABORATION,
            content=request,
            requires_response=True,
        )
        state.add_message(message)
        self.collaboration_requests.append(message)

    async def broadcast_update(self, update: Dict[str, Any], state: AgentState) -> None:
        """Broadcast an update to all agents"""
        message = AgentMessage(
            sender=self.role, message_type=MessageType.BROADCAST, content=update
        )
        state.add_message(message)

    def evaluate_quality(self, result: Dict[str, Any]) -> float:
        """Evaluate the quality of a result (0-1 scale)"""
        # Base implementation - can be overridden by specific agents
        criteria = {
            "completeness": 0.3,
            "accuracy": 0.3,
            "relevance": 0.2,
            "innovation": 0.2,
        }

        score = 0.0
        for criterion, weight in criteria.items():
            if criterion in result.get("quality_metrics", {}):
                score += result["quality_metrics"][criterion] * weight
            else:
                # Default moderate score if not evaluated
                score += 0.7 * weight

        self.quality_scores.append(score)
        return score

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_quality = (
            sum(self.quality_scores) / len(self.quality_scores)
            if self.quality_scores
            else 0
        )

        return {
            "agent": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "average_quality_score": avg_quality,
            "total_processing_time": self.total_processing_time,
            "current_task": self.current_task,
        }

    async def validate_input(self, task: Dict[str, Any]) -> bool:
        """Validate task input before processing"""
        required_fields = self._get_required_fields()

        for field in required_fields:
            if field not in task:
                raise ValueError(f"Missing required field: {field}")

        return True

    @abstractmethod
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for task input"""
        pass

    def _create_response(
        self, content: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized response format"""
        return {
            "agent": self.name,
            "role": self.role.value,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": metadata or {},
            "quality_score": self.evaluate_quality({"content": content}),
        }
