"""
智能体编排服务
核心的多智能体协作引擎，基于LangGraph实现复杂的工作流编排
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.agent_factory import AgentFactory
from app.agents.base_agent import BaseAgent
from app.core.config import settings
from app.core.exceptions import AgentException, ValidationException
from app.models.agent import AgentInteraction, ConversationSession
from app.schemas.agent import CollaborationMode, TaskType
from app.utils.cache import CacheManager, cache_result
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentState:
    """智能体状态类"""

    messages: List[Dict[str, Any]] = field(default_factory=list)
    current_agent: Optional[str] = None
    task_context: Dict[str, Any] = field(default_factory=dict)
    collaboration_mode: str = "sequential"
    completed_agents: List[str] = field(default_factory=list)
    final_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class AgentOrchestrator:
    """智能体编排器 - 多智能体协作的核心引擎"""

    def __init__(self):
        self.agent_factory = AgentFactory()
        self.cache_manager = CacheManager()
        self.active_sessions: Dict[str, Any] = {}
        self.collaboration_graph = self._build_collaboration_graph()

        # 智能体能力映射
        self.agent_capabilities = {
            "education_director": {
                "expertise": ["战略规划", "教育愿景", "跨学科整合", "文化建设"],
                "task_types": ["curriculum_review", "learning_optimization"],
                "priority": 1,
                "model": "opus",
            },
            "pbl_curriculum_designer": {
                "expertise": ["项目设计", "驱动性问题", "评估体系", "UBD设计"],
                "task_types": [
                    "course_design",
                    "project_planning",
                    "assessment_design",
                ],
                "priority": 2,
                "model": "opus",
            },
            "learning_experience_designer": {
                "expertise": ["用户体验", "学习路径", "互动设计", "个性化"],
                "task_types": ["learning_optimization", "course_design"],
                "priority": 3,
                "model": "sonnet",
            },
            "creative_technologist": {
                "expertise": ["技术应用", "AI工具", "数字创作", "创新工具"],
                "task_types": ["technology_integration", "project_planning"],
                "priority": 4,
                "model": "sonnet",
            },
            "makerspace_manager": {
                "expertise": ["空间设计", "工具管理", "制作指导", "安全规范"],
                "task_types": ["space_planning", "project_planning"],
                "priority": 5,
                "model": "sonnet",
            },
        }

    def _build_collaboration_graph(self) -> StateGraph:
        """构建智能体协作图"""
        graph = StateGraph(AgentState)

        # 定义协作节点
        graph.add_node("route_task", self._route_task)
        graph.add_node("education_director", self._execute_education_director)
        graph.add_node("pbl_curriculum_designer", self._execute_pbl_designer)
        graph.add_node(
            "learning_experience_designer", self._execute_experience_designer
        )
        graph.add_node("creative_technologist", self._execute_technologist)
        graph.add_node("makerspace_manager", self._execute_manager)
        graph.add_node("synthesize_results", self._synthesize_results)

        # 设置入口点
        graph.set_entry_point("route_task")

        # 定义条件边
        graph.add_conditional_edges(
            "route_task",
            self._determine_next_agent,
            {
                "education_director": "education_director",
                "pbl_curriculum_designer": "pbl_curriculum_designer",
                "learning_experience_designer": "learning_experience_designer",
                "creative_technologist": "creative_technologist",
                "makerspace_manager": "makerspace_manager",
                "synthesize": "synthesize_results",
            },
        )

        # 各智能体完成后的路由
        for agent_name in self.agent_capabilities.keys():
            graph.add_conditional_edges(
                agent_name,
                self._check_collaboration_complete,
                {
                    "continue": "route_task",
                    "synthesize": "synthesize_results",
                    "end": END,
                },
            )

        graph.add_edge("synthesize_results", END)

        return graph.compile(checkpointer=MemorySaver())

    async def is_agent_available(self, agent_name: str) -> bool:
        """检查智能体是否可用"""
        return agent_name in self.agent_capabilities

    async def chat_with_agent(
        self,
        agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = None,
        conversation_id: Optional[str] = None,
    ) -> Any:
        """与单个智能体对话"""
        try:
            # 获取智能体实例
            agent = await self.agent_factory.get_agent(agent_name)
            if not agent:
                raise AgentException(
                    f"智能体 {agent_name} 不可用",
                    agent_type=agent_name,
                    error_code="AGENT_NOT_AVAILABLE",
                )

            # 准备上下文
            full_context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                **(context or {}),
            }

            # 执行对话
            response = await agent.process_message(
                message=message, context=full_context
            )

            # 记录交互
            await self._record_interaction(
                agent_name=agent_name,
                user_id=user_id,
                conversation_id=conversation_id,
                message=message,
                response=response.content,
                metadata=response.metadata,
            )

            return response

        except Exception as e:
            logger.error(f"与智能体 {agent_name} 对话失败: {e}")
            raise AgentException(
                f"智能体对话失败: {str(e)}",
                agent_type=agent_name,
                error_code="CHAT_FAILED",
            )

    async def execute_collaboration(
        self,
        agents: List[str],
        task: str,
        mode: CollaborationMode = CollaborationMode.SEQUENTIAL,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = None,
    ) -> Any:
        """执行多智能体协作"""
        try:
            session_id = str(uuid.uuid4())

            # 初始化状态
            initial_state = AgentState(
                messages=[{"role": "user", "content": task}],
                task_context={
                    "user_id": user_id,
                    "session_id": session_id,
                    "selected_agents": agents,
                    "original_task": task,
                    **(context or {}),
                },
                collaboration_mode=mode.value,
            )

            # 执行协作图
            config = RunnableConfig(configurable={"thread_id": session_id})

            logger.info(f"开始多智能体协作，会话ID: {session_id}")
            start_time = datetime.utcnow()

            final_state = await self.collaboration_graph.ainvoke(
                initial_state, config=config
            )

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            # 构建协作结果
            from app.schemas.agent import CollaborationResult

            result = CollaborationResult(
                session_id=session_id,
                task_id=str(uuid.uuid4()),
                final_output=final_state.final_output,
                agents_involved=final_state.completed_agents,
                execution_time=execution_time,
                quality_score=self._calculate_quality_score(final_state),
                individual_contributions=self._extract_contributions(final_state),
                collaboration_summary=self._generate_collaboration_summary(final_state),
            )

            logger.info(f"多智能体协作完成，耗时: {execution_time:.2f}秒")
            return result

        except Exception as e:
            logger.exception("多智能体协作执行失败")
            raise AgentException(
                f"协作执行失败: {str(e)}",
                agent_type="collaboration",
                error_code="COLLABORATION_FAILED",
            )

    async def select_agents_for_task(
        self,
        task_description: str,
        task_type: Optional[TaskType] = None,
        required_expertise: Optional[List[str]] = None,
    ) -> List[str]:
        """根据任务自动选择合适的智能体"""
        selected_agents = []

        # 基于任务类型选择
        if task_type:
            for agent_name, capabilities in self.agent_capabilities.items():
                if task_type.value in capabilities["task_types"]:
                    selected_agents.append(agent_name)

        # 基于专业技能选择
        if required_expertise:
            for agent_name, capabilities in self.agent_capabilities.items():
                if any(
                    skill in capabilities["expertise"] for skill in required_expertise
                ):
                    if agent_name not in selected_agents:
                        selected_agents.append(agent_name)

        # 基于任务内容的关键词匹配
        task_lower = task_description.lower()
        keyword_mapping = {
            "education_director": ["战略", "愿景", "整合", "跨学科", "文化"],
            "pbl_curriculum_designer": ["项目", "PBL", "课程", "驱动", "评估"],
            "learning_experience_designer": ["体验", "学习", "互动", "个性化", "路径"],
            "creative_technologist": ["技术", "AI", "工具", "数字", "创新"],
            "makerspace_manager": ["空间", "制作", "工具", "安全", "设备"],
        }

        for agent_name, keywords in keyword_mapping.items():
            if any(keyword in task_lower for keyword in keywords):
                if agent_name not in selected_agents:
                    selected_agents.append(agent_name)

        # 如果没有匹配到，使用默认组合
        if not selected_agents:
            selected_agents = ["education_director", "pbl_curriculum_designer"]

        # 按优先级排序
        selected_agents.sort(key=lambda x: self.agent_capabilities[x]["priority"])

        logger.info(f"为任务选择智能体: {selected_agents}")
        return selected_agents

    async def stream_agent_response(
        self,
        agent_name: str,
        message: str,
        user_id: str = None,
        conversation_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式获取智能体响应"""
        try:
            agent = await self.agent_factory.get_agent(agent_name)
            if not agent:
                yield {"error": f"智能体 {agent_name} 不可用"}
                return

            context = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "streaming": True,
            }

            async for chunk in agent.stream_response(message, context):
                yield {
                    "agent_name": agent_name,
                    "content": chunk.get("content", ""),
                    "type": chunk.get("type", "content"),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.exception(f"流式响应失败: {e}")
            yield {"error": f"流式响应失败: {str(e)}", "agent_name": agent_name}

    # 协作图节点实现
    async def _route_task(self, state: AgentState) -> AgentState:
        """任务路由节点"""
        # 确定下一个要执行的智能体
        if not state.task_context.get("selected_agents"):
            # 自动选择智能体
            task = state.messages[-1]["content"]
            selected = await self.select_agents_for_task(task)
            state.task_context["selected_agents"] = selected

        return state

    def _determine_next_agent(self, state: AgentState) -> str:
        """确定下一个智能体"""
        selected_agents = state.task_context.get("selected_agents", [])
        completed = state.completed_agents

        # 找到下一个未执行的智能体
        for agent_name in selected_agents:
            if agent_name not in completed:
                return agent_name

        # 所有智能体都执行完毕，进行结果合成
        return "synthesize"

    async def _execute_education_director(self, state: AgentState) -> AgentState:
        """执行教育总监智能体"""
        return await self._execute_agent("education_director", state)

    async def _execute_pbl_designer(self, state: AgentState) -> AgentState:
        """执行PBL设计师智能体"""
        return await self._execute_agent("pbl_curriculum_designer", state)

    async def _execute_experience_designer(self, state: AgentState) -> AgentState:
        """执行学习体验设计师智能体"""
        return await self._execute_agent("learning_experience_designer", state)

    async def _execute_technologist(self, state: AgentState) -> AgentState:
        """执行创意技术专家智能体"""
        return await self._execute_agent("creative_technologist", state)

    async def _execute_manager(self, state: AgentState) -> AgentState:
        """执行创客空间管理员智能体"""
        return await self._execute_agent("makerspace_manager", state)

    async def _execute_agent(self, agent_name: str, state: AgentState) -> AgentState:
        """执行指定智能体"""
        try:
            agent = await self.agent_factory.get_agent(agent_name)

            # 准备上下文，包含前面智能体的输出
            context = state.task_context.copy()
            context["previous_outputs"] = [
                msg for msg in state.messages if msg.get("role") == "assistant"
            ]

            # 获取用户的原始任务
            user_message = next(
                (msg["content"] for msg in state.messages if msg["role"] == "user"), ""
            )

            # 执行智能体
            response = await agent.process_message(
                message=user_message, context=context
            )

            # 更新状态
            state.messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                    "agent": agent_name,
                    "metadata": response.metadata,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            state.current_agent = agent_name
            state.completed_agents.append(agent_name)

            logger.info(f"智能体 {agent_name} 执行完成")
            return state

        except Exception as e:
            logger.error(f"执行智能体 {agent_name} 失败: {e}")
            state.error = f"智能体 {agent_name} 执行失败: {str(e)}"
            return state

    def _check_collaboration_complete(self, state: AgentState) -> str:
        """检查协作是否完成"""
        if state.error:
            return "end"

        selected_agents = state.task_context.get("selected_agents", [])
        completed = state.completed_agents

        # 检查是否所有选定的智能体都已完成
        if len(completed) >= len(selected_agents):
            return "synthesize"

        # 继续执行下一个智能体
        return "continue"

    async def _synthesize_results(self, state: AgentState) -> AgentState:
        """合成协作结果"""
        try:
            # 收集所有智能体的输出
            agent_outputs = [
                msg for msg in state.messages if msg.get("role") == "assistant"
            ]

            # 基于协作模式合成最终结果
            mode = state.collaboration_mode

            if mode == "sequential":
                # 顺序模式：以最后一个智能体的输出为主，整合前面的见解
                final_output = self._synthesize_sequential(agent_outputs, state)
            elif mode == "parallel":
                # 并行模式：平衡整合所有智能体的贡献
                final_output = self._synthesize_parallel(agent_outputs, state)
            elif mode == "hierarchical":
                # 分层模式：按优先级整合
                final_output = self._synthesize_hierarchical(agent_outputs, state)
            else:
                # 默认合成
                final_output = self._synthesize_default(agent_outputs, state)

            state.final_output = final_output
            state.metadata["synthesis_mode"] = mode
            state.metadata["agents_count"] = len(agent_outputs)

            logger.info(f"协作结果合成完成，模式: {mode}")
            return state

        except Exception as e:
            logger.error(f"结果合成失败: {e}")
            state.error = f"结果合成失败: {str(e)}"
            return state

    def _synthesize_sequential(self, outputs: List[Dict], state: AgentState) -> str:
        """顺序模式结果合成"""
        if not outputs:
            return "未生成有效输出"

        # 以最后一个输出为主体
        main_output = outputs[-1]["content"]

        # 整合前面智能体的关键见解
        insights = []
        for i, output in enumerate(outputs[:-1]):
            agent_name = output.get("agent", f"智能体{i+1}")
            content = (
                output["content"][:200] + "..."
                if len(output["content"]) > 200
                else output["content"]
            )
            insights.append(
                f"**{self._get_agent_display_name(agent_name)}的见解:**\n{content}"
            )

        if insights:
            return (
                f"{main_output}\n\n---\n\n**协作过程中的关键见解:**\n\n"
                + "\n\n".join(insights)
            )

        return main_output

    def _synthesize_parallel(self, outputs: List[Dict], state: AgentState) -> str:
        """并行模式结果合成"""
        if not outputs:
            return "未生成有效输出"

        # 平衡整合所有智能体的贡献
        sections = []
        for output in outputs:
            agent_name = output.get("agent", "未知智能体")
            display_name = self._get_agent_display_name(agent_name)
            content = output["content"]
            sections.append(f"## {display_name}的专业建议\n\n{content}")

        # 生成整合性总结
        summary = self._generate_integration_summary(outputs, state)

        return f"# 多专家协作方案\n\n{summary}\n\n---\n\n" + "\n\n".join(sections)

    def _synthesize_hierarchical(self, outputs: List[Dict], state: AgentState) -> str:
        """分层模式结果合成"""
        # 按智能体优先级排序输出
        sorted_outputs = sorted(
            outputs,
            key=lambda x: self.agent_capabilities.get(x.get("agent", ""), {}).get(
                "priority", 99
            ),
        )

        return self._synthesize_sequential(sorted_outputs, state)

    def _synthesize_default(self, outputs: List[Dict], state: AgentState) -> str:
        """默认合成模式"""
        return self._synthesize_parallel(outputs, state)

    def _get_agent_display_name(self, agent_name: str) -> str:
        """获取智能体显示名称"""
        name_mapping = {
            "education_director": "教育总监",
            "pbl_curriculum_designer": "PBL课程设计师",
            "learning_experience_designer": "学习体验设计师",
            "creative_technologist": "创意技术专家",
            "makerspace_manager": "创客空间管理员",
        }
        return name_mapping.get(agent_name, agent_name)

    def _generate_integration_summary(
        self, outputs: List[Dict], state: AgentState
    ) -> str:
        """生成整合性总结"""
        # 这里可以使用LLM来生成更智能的总结
        # 暂时使用模板化方法
        task = state.task_context.get("original_task", "")
        agent_count = len(outputs)

        return f"""
基于您的需求"{task}"，我们的{agent_count}位专业智能体从不同角度提供了综合性解决方案。

每位专家都从自己的专业领域出发，为您提供了详细的分析和建议。请查看下方各专家的具体建议，并根据您的实际情况进行选择和整合。
        """.strip()

    def _calculate_quality_score(self, state: AgentState) -> Optional[float]:
        """计算协作质量评分"""
        try:
            # 基于多个维度计算质量分数
            score_factors = []

            # 1. 完成度评分
            selected_agents = len(state.task_context.get("selected_agents", []))
            completed_agents = len(state.completed_agents)
            completion_score = (
                completed_agents / selected_agents if selected_agents > 0 else 0
            )
            score_factors.append(completion_score * 3)  # 权重3

            # 2. 响应质量评分（基于输出长度和结构）
            agent_outputs = [
                msg for msg in state.messages if msg.get("role") == "assistant"
            ]
            if agent_outputs:
                avg_length = sum(len(msg["content"]) for msg in agent_outputs) / len(
                    agent_outputs
                )
                length_score = min(avg_length / 1000, 1.0)  # 标准化到0-1
                score_factors.append(length_score * 2)  # 权重2

            # 3. 无错误执行评分
            error_penalty = 1.0 if not state.error else 0.5
            score_factors.append(error_penalty * 1)  # 权重1

            # 计算加权平均分
            total_score = sum(score_factors) / 6 * 10  # 转换到10分制
            return round(min(max(total_score, 0), 10), 2)

        except Exception as e:
            logger.error(f"计算质量评分失败: {e}")
            return None

    def _extract_contributions(self, state: AgentState) -> Dict[str, str]:
        """提取各智能体的贡献"""
        contributions = {}

        for msg in state.messages:
            if msg.get("role") == "assistant" and msg.get("agent"):
                agent_name = msg["agent"]
                content = msg["content"]
                # 截取前500个字符作为贡献摘要
                summary = content[:500] + "..." if len(content) > 500 else content
                contributions[agent_name] = summary

        return contributions

    def _generate_collaboration_summary(self, state: AgentState) -> str:
        """生成协作过程总结"""
        completed = state.completed_agents
        mode = state.collaboration_mode

        return f"本次协作采用{mode}模式，共有{len(completed)}个智能体参与：{', '.join([self._get_agent_display_name(agent) for agent in completed])}。协作过程顺利完成。"

    async def _record_interaction(
        self,
        agent_name: str,
        user_id: str,
        conversation_id: Optional[str],
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """记录智能体交互"""
        try:
            # 这里应该保存到数据库
            # 暂时记录到日志
            logger.info(f"记录交互 - 智能体: {agent_name}, 用户: {user_id}")
        except Exception as e:
            logger.error(f"记录交互失败: {e}")

    # 其他辅助方法
    async def create_conversation(
        self,
        title: str,
        description: Optional[str] = None,
        participants: Optional[List[str]] = None,
        initial_context: Optional[Dict[str, Any]] = None,
        user_id: str = None,
    ):
        """创建对话会话"""
        # 实现对话会话创建逻辑
        pass

    async def get_conversation_history(
        self, conversation_id: str, user_id: str, limit: int = 50, offset: int = 0
    ):
        """获取对话历史"""
        # 实现对话历史获取逻辑
        pass

    async def delete_conversation(self, conversation_id: str, user_id: str):
        """删除对话"""
        # 实现对话删除逻辑
        pass

    async def record_feedback(
        self,
        agent_name: str,
        message_id: str,
        user_id: str,
        rating: int,
        feedback: Optional[str] = None,
        timestamp: datetime = None,
    ):
        """记录用户反馈"""
        # 实现反馈记录逻辑
        pass

    async def create_batch_task(
        self, requests: List[Any], user_id: str, max_concurrency: int = 5
    ) -> str:
        """创建批量任务"""
        # 实现批量任务创建逻辑
        return str(uuid.uuid4())

    async def execute_batch_task(self, batch_id: str):
        """执行批量任务"""
        # 实现批量任务执行逻辑
        pass
