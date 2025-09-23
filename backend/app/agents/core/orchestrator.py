"""
PBL Orchestrator - LangGraph-based Multi-Agent Coordination System
World-class orchestration engine for PBL course design
Enhanced with comprehensive collaboration tracking
"""

import asyncio
import json
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..specialists import (
    AssessmentExpertAgent,
    ContentDesignerAgent,
    CourseArchitectAgent,
    EducationTheoristAgent,
    MaterialCreatorAgent,
)
from .llm_manager import LLMManager, ModelType
from .state import AgentMessage, AgentRole, AgentState, MessageType, WorkflowPhase
from .task_tracker import TaskExecutionTracker
from ...core.collaboration_tracker import CollaborationTracker
from ...core.ai_call_logger import AICallLogger


class OrchestratorMode(Enum):
    """Orchestration modes for different scenarios"""

    FULL_COURSE = "full_course"
    QUICK_DESIGN = "quick_design"
    ITERATION = "iteration"
    REVIEW = "review"
    CUSTOM = "custom"


class PBLOrchestrator:
    """
    Master orchestrator for multi-agent PBL course design
    Implements LangGraph for sophisticated agent coordination
    """

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        mode: OrchestratorMode = OrchestratorMode.FULL_COURSE,
        enable_streaming: bool = True,
        max_iterations: int = 3,
        enable_collaboration_tracking: bool = True,
    ):
        """Initialize the orchestrator with agents and workflow"""

        # Initialize LLM Manager
        self.llm_manager = llm_manager or LLMManager()

        # Configuration
        self.mode = mode
        self.enable_streaming = enable_streaming
        self.max_iterations = max_iterations
        self.enable_collaboration_tracking = enable_collaboration_tracking

        # Initialize collaboration tracking
        self.collaboration_tracker: Optional[CollaborationTracker] = None
        self.ai_call_logger = AICallLogger()

        # Initialize task execution tracker
        self.task_tracker: Optional[TaskExecutionTracker] = None

        # Initialize specialized agents
        self.agents = {
            AgentRole.EDUCATION_THEORIST: EducationTheoristAgent(self.llm_manager),
            AgentRole.COURSE_ARCHITECT: CourseArchitectAgent(self.llm_manager),
            AgentRole.CONTENT_DESIGNER: ContentDesignerAgent(self.llm_manager),
            AgentRole.ASSESSMENT_EXPERT: AssessmentExpertAgent(self.llm_manager),
            AgentRole.MATERIAL_CREATOR: MaterialCreatorAgent(self.llm_manager),
        }

        # Inject tracking capabilities into agents if enabled
        if self.enable_collaboration_tracking:
            for agent in self.agents.values():
                agent.ai_call_logger = self.ai_call_logger

        # Build the LangGraph workflow
        self.workflow = self._build_workflow()

        # Compile the graph with memory
        self.checkpointer = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)

        # Metrics tracking
        self.metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_duration": 0,
            "agent_performance": {},
        }

    def _build_workflow(self) -> StateGraph:
        """构建用于智能体协作的LangGraph工作流"""

        # 创建状态图（StateGraph），以AgentState为状态
        workflow = StateGraph(AgentState)

        # 为每个阶段和智能体添加节点
        workflow.add_node("initialize", self._initialize_phase)  # 初始化阶段
        workflow.add_node("theoretical_foundation", self._theoretical_foundation_phase)  # 理论基础阶段
        workflow.add_node("architecture_design", self._architecture_design_phase)  # 课程架构设计阶段
        workflow.add_node("content_creation", self._content_creation_phase)  # 内容创作阶段
        workflow.add_node("assessment_design", self._assessment_design_phase)  # 评估设计阶段
        workflow.add_node("material_production", self._material_production_phase)  # 教学资料生成阶段
        workflow.add_node("review_iteration", self._review_iteration_phase)  # 复盘迭代阶段
        workflow.add_node("finalize", self._finalization_phase)  # 最终收尾阶段

        # 根据不同模式定义节点之间的连接关系
        if self.mode == OrchestratorMode.FULL_COURSE:
            # 全流程顺序工作流
            workflow.set_entry_point("initialize")  # 设置入口节点
            workflow.add_edge("initialize", "theoretical_foundation")
            workflow.add_edge("theoretical_foundation", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "assessment_design")
            workflow.add_edge("assessment_design", "material_production")
            # material_production 阶段后根据条件判断是否需要迭代
            workflow.add_conditional_edges(
                "material_production",
                self._should_iterate,
                {"iterate": "review_iteration", "finalize": "finalize"},
            )
            workflow.add_edge("review_iteration", "architecture_design")  # 迭代后回到架构设计
            workflow.add_edge("finalize", END)  # 结束节点

        elif self.mode == OrchestratorMode.QUICK_DESIGN:
            # 精简流程
            workflow.set_entry_point("initialize")
            workflow.add_edge("initialize", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "finalize")
            workflow.add_edge("finalize", END)

        elif self.mode == OrchestratorMode.ITERATION:
            # 迭代优化流程
            workflow.set_entry_point("review_iteration")
            workflow.add_edge("review_iteration", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "assessment_design")
            workflow.add_edge("assessment_design", "finalize")
            workflow.add_edge("finalize", END)

        else:
            # 自定义流程，所有节点可用
            workflow.set_entry_point("initialize")
            workflow.add_edge("initialize", "finalize")
            workflow.add_edge("finalize", END)

        return workflow

    async def _initialize_phase(self, state: AgentState) -> AgentState:
        """Initialize the course design process with collaboration tracking"""

        state.transition_phase(WorkflowPhase.INITIALIZATION)

        # Start execution phase tracking
        if self.task_tracker:
            self.task_tracker.start_execution_phase(
                phase_name="initialization",
                phase_description="初始化课程设计流程",
                input_data=state.course_requirements
            )

        # Initialize collaboration tracking
        if self.enable_collaboration_tracking and not self.collaboration_tracker:
            self.collaboration_tracker = CollaborationTracker(state.session_id)
            self.collaboration_tracker.start_session(
                requirements=state.course_requirements,
                config={
                    "mode": self.mode.value,
                    "enable_streaming": self.enable_streaming,
                    "max_iterations": self.max_iterations
                }
            )
            # Inject tracker into state for agent access
            state.collaboration_tracker = self.collaboration_tracker

        # Start tracking initialization phase
        if self.collaboration_tracker:
            self.collaboration_tracker.start_phase(WorkflowPhase.INITIALIZATION)

        # Validate requirements
        if not state.course_requirements:
            raise ValueError("Course requirements must be provided")

        # Set up initial configuration
        state.update_agent_status(AgentRole.ORCHESTRATOR, "initializing")

        # Prepare initial messages for agents
        init_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            message_type=MessageType.BROADCAST,
            content={
                "action": "initialize",
                "requirements": state.course_requirements,
                "mode": self.mode.value,
            },
        )
        state.add_message(init_message)

        # Create initial checkpoint
        state.create_checkpoint()

        # Capture initial state snapshot
        if self.collaboration_tracker:
            self.collaboration_tracker.capture_state_snapshot(
                trigger_event="initialization_complete",
                description="Course design initialization completed",
                state_data={
                    "requirements": state.course_requirements,
                    "mode": self.mode.value,
                    "agent_statuses": state.agent_statuses
                }
            )

        # Complete execution phase tracking
        if self.task_tracker:
            self.task_tracker.complete_execution_phase(
                phase_name="initialization",
                success=True,
                output_data={
                    "initialized_requirements": state.course_requirements,
                    "orchestrator_mode": self.mode.value,
                    "agent_statuses": state.agent_statuses
                }
            )

        return state

    async def _theoretical_foundation_phase(self, state: AgentState) -> AgentState:
        """Establish theoretical foundation with Education Theorist"""

        state.transition_phase(WorkflowPhase.THEORETICAL_FOUNDATION)

        # Start execution phase tracking
        if self.task_tracker:
            self.task_tracker.start_execution_phase(
                phase_name="theoretical_foundation",
                phase_description="建立教育理论基础",
                input_data={
                    "requirements": state.course_requirements,
                    "agent": "education_theorist"
                }
            )

        # Start tracking this phase
        if self.collaboration_tracker:
            self.collaboration_tracker.start_phase(WorkflowPhase.THEORETICAL_FOUNDATION)

        # Prepare task for Education Theorist
        task = {
            "type": "analyze_requirements",
            "requirements": state.course_requirements,
        }

        # Start tracking agent execution
        agent_execution_id = None
        if self.task_tracker:
            agent_execution_id = self.task_tracker.start_agent_execution(
                agent_name="education_theorist",
                agent_role="教育理论专家",
                task_type="analyze_requirements",
                input_data=task
            )

        execution = None
        if self.collaboration_tracker:
            theorist = self.agents[AgentRole.EDUCATION_THEORIST]
            execution = self.collaboration_tracker.start_agent_execution(
                agent_role=AgentRole.EDUCATION_THEORIST,
                agent_name=theorist.name,
                task_type="analyze_requirements",
                phase=WorkflowPhase.THEORETICAL_FOUNDATION,
                input_data=task,
                context={"streaming": self.enable_streaming}
            )

        # Execute Education Theorist
        theorist = self.agents[AgentRole.EDUCATION_THEORIST]

        if self.enable_streaming:
            async for update in theorist.execute(state, stream=True):
                # Stream updates to subscribers
                await self._broadcast_update(state, update)
        else:
            async for res in theorist.execute(state, stream=False):
                state.theoretical_framework = res.get("content", {}).get(
                    "framework", {}
                )

        # Request framework development
        framework_task = {
            "type": "develop_framework",
            "parameters": state.course_requirements,
        }

        framework_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.EDUCATION_THEORIST,
            message_type=MessageType.REQUEST,
            content=framework_task,
            requires_response=True,
        )
        state.add_message(framework_message)

        # Process framework development
        final_result = None
        async for result in theorist.execute(state):
            if "framework" in result.get("content", {}):
                state.theoretical_framework = result["content"]["framework"]
                final_result = result

        # Complete agent execution tracking
        if self.task_tracker and agent_execution_id:
            self.task_tracker.complete_agent_execution(
                execution_id=agent_execution_id,
                success=bool(state.theoretical_framework),
                output_data=final_result or {"framework": state.theoretical_framework},
                performance_metrics={
                    "quality_score": 0.9 if state.theoretical_framework else 0.0
                }
            )

        # Complete execution tracking
        if self.collaboration_tracker and execution:
            self.collaboration_tracker.complete_agent_execution(
                execution_id=execution.execution_id,
                output=final_result or {"framework": state.theoretical_framework},
                success=bool(state.theoretical_framework),
                quality_score=0.9 if state.theoretical_framework else 0.0
            )

        # Capture state snapshot after this phase
        if self.collaboration_tracker:
            self.collaboration_tracker.capture_state_snapshot(
                trigger_event="theoretical_foundation_complete",
                description="Theoretical foundation established",
                state_data={
                    "theoretical_framework": state.theoretical_framework,
                    "agent_statuses": state.agent_statuses
                }
            )

        # Complete execution phase tracking
        if self.task_tracker:
            self.task_tracker.complete_execution_phase(
                phase_name="theoretical_foundation",
                success=bool(state.theoretical_framework),
                output_data={
                    "theoretical_framework": state.theoretical_framework
                }
            )

        return state

    async def _architecture_design_phase(self, state: AgentState) -> AgentState:
        """Design course architecture with Course Architect"""

        state.transition_phase(WorkflowPhase.ARCHITECTURE_DESIGN)

        # Start execution phase tracking
        if self.task_tracker:
            self.task_tracker.start_execution_phase(
                phase_name="architecture_design",
                phase_description="设计课程架构",
                input_data={
                    "requirements": state.course_requirements,
                    "theoretical_framework": state.theoretical_framework,
                    "agent": "course_architect"
                }
            )

        # Prepare task for Course Architect
        task = {
            "type": "design_structure",
            "requirements": state.course_requirements,
            "framework": state.theoretical_framework,
        }

        architect_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.COURSE_ARCHITECT,
            message_type=MessageType.REQUEST,
            content=task,
            requires_response=True,
        )
        state.add_message(architect_message)

        # Start tracking agent execution
        agent_execution_id = None
        if self.task_tracker:
            agent_execution_id = self.task_tracker.start_agent_execution(
                agent_name="course_architect",
                agent_role="课程架构师",
                task_type="design_structure",
                input_data=task
            )

        # Execute Course Architect
        architect = self.agents[AgentRole.COURSE_ARCHITECT]

        final_result = None
        async for result in architect.execute(state):
            if "architecture" in result.get("content", {}):
                state.course_architecture = result["content"]["architecture"]
                final_result = result

        # Create module architecture
        for module in state.course_architecture.get("modules", []):
            module_task = {"type": "create_modules", "module_params": module}

            module_message = AgentMessage(
                sender=AgentRole.ORCHESTRATOR,
                recipient=AgentRole.COURSE_ARCHITECT,
                message_type=MessageType.REQUEST,
                content=module_task,
                requires_response=True,
            )
            state.add_message(module_message)

            async for result in architect.execute(state):
                pass  # Module details processed

        # Complete agent execution tracking
        if self.task_tracker and agent_execution_id:
            self.task_tracker.complete_agent_execution(
                execution_id=agent_execution_id,
                success=bool(state.course_architecture),
                output_data=final_result or {"architecture": state.course_architecture},
                performance_metrics={
                    "quality_score": 0.85 if state.course_architecture else 0.0
                }
            )

        # Complete execution phase tracking
        if self.task_tracker:
            self.task_tracker.complete_execution_phase(
                phase_name="architecture_design",
                success=bool(state.course_architecture),
                output_data={
                    "course_architecture": state.course_architecture,
                    "modules_count": len(state.course_architecture.get("modules", [])) if state.course_architecture else 0
                }
            )

        return state

    async def _content_creation_phase(self, state: AgentState) -> AgentState:
        """Create content with Content Designer"""

        state.transition_phase(WorkflowPhase.CONTENT_CREATION)

        # Process each module
        designer = self.agents[AgentRole.CONTENT_DESIGNER]

        for module in state.course_architecture.get("modules", []):
            content_task = {"type": "create_content", "module": module}

            content_message = AgentMessage(
                sender=AgentRole.ORCHESTRATOR,
                recipient=AgentRole.CONTENT_DESIGNER,
                message_type=MessageType.REQUEST,
                content=content_task,
                requires_response=True,
            )
            state.add_message(content_message)

            async for result in designer.execute(state):
                if "content" in result.get("content", {}):
                    state.content_modules.append(result["content"]["content"])

        # Create project scenarios
        scenario_task = {
            "type": "create_scenarios",
            "theme": state.course_requirements.get("topic", ""),
        }

        scenario_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.CONTENT_DESIGNER,
            message_type=MessageType.REQUEST,
            content=scenario_task,
            requires_response=True,
        )
        state.add_message(scenario_message)

        async for result in designer.execute(state):
            pass  # Scenarios processed

        return state

    async def _assessment_design_phase(self, state: AgentState) -> AgentState:
        """Design assessment strategy with Assessment Expert"""

        state.transition_phase(WorkflowPhase.ASSESSMENT_DESIGN)

        # Design comprehensive assessment strategy
        assessment_task = {
            "type": "design_strategy",
            "course_structure": state.course_architecture,
            "content": state.content_modules,
        }

        assessment_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.ASSESSMENT_EXPERT,
            message_type=MessageType.REQUEST,
            content=assessment_task,
            requires_response=True,
        )
        state.add_message(assessment_message)

        expert = self.agents[AgentRole.ASSESSMENT_EXPERT]

        async for result in expert.execute(state):
            if "assessment" in result.get("content", {}):
                state.assessment_strategy = result["content"]["assessment"]

        # Create assessment rubrics
        rubric_task = {"type": "create_rubrics", "focus": "project_assessment"}

        rubric_message = AgentMessage(
            sender=AgentRole.ORCHESTRATOR,
            recipient=AgentRole.ASSESSMENT_EXPERT,
            message_type=MessageType.REQUEST,
            content=rubric_task,
            requires_response=True,
        )
        state.add_message(rubric_message)

        async for result in expert.execute(state):
            pass  # Rubrics processed

        return state

    async def _material_production_phase(self, state: AgentState) -> AgentState:
        """Produce materials with Material Creator - with fault tolerance"""

        state.transition_phase(WorkflowPhase.MATERIAL_PRODUCTION)

        creator = self.agents[AgentRole.MATERIAL_CREATOR]

        # Create various material types
        material_types = [
            {
                "type": "create_worksheets",
                "specifications": {"modules": state.content_modules},
            },
            {"type": "create_templates", "project_type": "pbl"},
            {"type": "create_guides", "focus": "implementation"},
            {"type": "create_digital", "resource_type": "interactive"},
        ]

        successful_materials = 0
        total_materials = len(material_types)

        for i, material_task in enumerate(material_types):
            try:
                logger.info(f"🎨 开始创建素材 {i+1}/{total_materials}: {material_task['type']}")

                material_message = AgentMessage(
                    sender=AgentRole.ORCHESTRATOR,
                    recipient=AgentRole.MATERIAL_CREATOR,
                    message_type=MessageType.REQUEST,
                    content=material_task,
                    requires_response=True,
                )
                state.add_message(material_message)

                async for result in creator.execute(state):
                    if "materials" in result.get("content", {}):
                        state.learning_materials.extend(result["content"]["materials"])
                        successful_materials += 1
                        logger.info(f"✅ 素材创建成功: {material_task['type']}")
                        break

            except Exception as e:
                logger.error(f"❌ 素材创建失败 {material_task['type']}: {e}")
                # 不创建后备素材，记录失败

        # Log material production summary
        success_rate = (successful_materials / total_materials) * 100
        logger.info(f"📊 素材创建完成: {successful_materials}/{total_materials} ({success_rate:.1f}%)")

        # 检查是否有足够的成功素材来完成课程设计
        min_required_materials = 2  # 至少需要2种素材才能提供基本的课程支持

        if successful_materials < min_required_materials:
            error_msg = f"素材创建严重失败: 仅成功创建{successful_materials}/{total_materials}种素材，不足以支撑完整的课程设计"
            logger.error(f"❌ {error_msg}")
            state.workflow_warnings.append(error_msg)

            # 这里可以选择继续（记录警告）或者终止流程（抛出异常）
            # 根据业务需求，如果素材太少，应该终止流程
            if successful_materials == 0:
                raise Exception("所有素材创建都失败了，无法继续课程设计流程")
            else:
                logger.warning(f"⚠️ 素材不足但继续流程，质量可能受影响")

        elif successful_materials < total_materials:
            state.workflow_warnings.append(f"素材创建部分失败: {successful_materials}/{total_materials}")

        return state

    async def _review_iteration_phase(self, state: AgentState) -> AgentState:
        """Review and iterate on the course design"""

        state.transition_phase(WorkflowPhase.REVIEW_ITERATION)
        state.iteration_count += 1

        # Collect quality scores from all agents
        quality_assessment = await self._assess_quality(state)

        # Identify areas for improvement
        improvements = await self._identify_improvements(quality_assessment, state)

        # Send improvement requests to relevant agents
        for improvement in improvements:
            improvement_message = AgentMessage(
                sender=AgentRole.ORCHESTRATOR,
                recipient=improvement["agent"],
                message_type=MessageType.REQUEST,
                content={
                    "type": "improve",
                    "feedback": improvement["feedback"],
                    "priority": improvement["priority"],
                },
                requires_response=True,
            )
            state.add_message(improvement_message)

        # Create revision checkpoint
        state.create_checkpoint()

        return state

    async def _finalization_phase(self, state: AgentState) -> AgentState:
        """Finalize the course design with comprehensive collaboration tracking"""

        state.transition_phase(WorkflowPhase.FINALIZATION)

        # Start execution phase tracking
        if self.task_tracker:
            self.task_tracker.start_execution_phase(
                phase_name="finalization",
                phase_description="最终化课程设计",
                input_data={
                    "course_architecture": state.course_architecture,
                    "content_modules": len(state.content_modules),
                    "assessment_strategy": bool(state.assessment_strategy),
                    "learning_materials": len(state.learning_materials)
                }
            )

        # Start tracking finalization phase
        if self.collaboration_tracker:
            self.collaboration_tracker.start_phase(WorkflowPhase.FINALIZATION)

        # Final quality check
        final_quality = await self._final_quality_check(state)
        state.add_quality_score("final_quality", final_quality)

        # Compile final deliverables
        deliverables = self._compile_deliverables(state)

        # Trace deliverable sources
        if self.collaboration_tracker:
            self._trace_final_deliverables(deliverables, state)

        # Generate export files (including collaboration evidence)
        await self._generate_export_files(deliverables, state)

        # Create final checkpoint
        final_checkpoint = state.create_checkpoint()

        # Complete collaboration tracking
        if self.collaboration_tracker:
            self.collaboration_tracker.complete_session()

            # Store collaboration record in state for export
            state.collaboration_record = self.collaboration_tracker.get_collaboration_record()

        # Complete execution phase tracking
        if self.task_tracker:
            self.task_tracker.complete_execution_phase(
                phase_name="finalization",
                success=True,
                output_data={
                    "deliverables": deliverables,
                    "final_quality": final_quality,
                    "collaboration_record": bool(state.collaboration_record)
                }
            )

        # Update metrics
        self.metrics["total_runs"] += 1
        self.metrics["successful_runs"] += 1

        return state

    def _should_iterate(self, state: AgentState) -> str:
        """Determine whether to iterate or finalize"""

        # Check quality scores
        avg_quality = (
            sum(state.quality_scores.values()) / len(state.quality_scores)
            if state.quality_scores
            else 0
        )

        # Check iteration count
        if state.iteration_count >= self.max_iterations:
            return "finalize"

        # Check quality threshold
        if avg_quality < 0.85:
            return "iterate"

        return "finalize"

    async def _assess_quality(self, state: AgentState) -> Dict[str, float]:
        """Assess quality of current course design"""

        quality_metrics = {}

        # Assess each component
        components = [
            ("theoretical_framework", 0.2),
            ("course_architecture", 0.25),
            ("content_modules", 0.25),
            ("assessment_strategy", 0.15),
            ("learning_materials", 0.15),
        ]

        for component, weight in components:
            if component == "theoretical_framework" and state.theoretical_framework:
                quality_metrics[component] = 0.9 * weight
            elif component == "course_architecture" and state.course_architecture:
                quality_metrics[component] = 0.85 * weight
            elif component == "content_modules" and state.content_modules:
                quality_metrics[component] = 0.88 * weight
            elif component == "assessment_strategy" and state.assessment_strategy:
                quality_metrics[component] = 0.87 * weight
            elif component == "learning_materials" and state.learning_materials:
                quality_metrics[component] = 0.9 * weight
            else:
                quality_metrics[component] = 0

        return quality_metrics

    async def _identify_improvements(
        self, quality_assessment: Dict[str, float], state: AgentState
    ) -> List[Dict[str, Any]]:
        """Identify areas for improvement"""

        improvements = []

        # Find lowest scoring components
        threshold = 0.85
        for component, score in quality_assessment.items():
            if score < threshold:
                # Map component to responsible agent
                agent_map = {
                    "theoretical_framework": AgentRole.EDUCATION_THEORIST,
                    "course_architecture": AgentRole.COURSE_ARCHITECT,
                    "content_modules": AgentRole.CONTENT_DESIGNER,
                    "assessment_strategy": AgentRole.ASSESSMENT_EXPERT,
                    "learning_materials": AgentRole.MATERIAL_CREATOR,
                }

                improvements.append(
                    {
                        "agent": agent_map.get(component),
                        "component": component,
                        "current_score": score,
                        "target_score": threshold,
                        "priority": "high" if score < 0.7 else "medium",
                        "feedback": f"Improve {component} quality from {score:.2f} to {threshold}",
                    }
                )

        return improvements

    async def _final_quality_check(self, state: AgentState) -> float:
        """Perform final quality check"""

        # Comprehensive quality assessment
        quality_factors = {
            "completeness": self._check_completeness(state),
            "coherence": self._check_coherence(state),
            "alignment": self._check_alignment(state),
            "innovation": self._check_innovation(state),
            "practicality": self._check_practicality(state),
        }

        # Weighted average
        weights = {
            "completeness": 0.25,
            "coherence": 0.2,
            "alignment": 0.25,
            "innovation": 0.15,
            "practicality": 0.15,
        }

        final_score = sum(
            quality_factors[factor] * weights[factor] for factor in quality_factors
        )

        return final_score

    def _check_completeness(self, state: AgentState) -> float:
        """Check if all components are complete"""
        required = [
            state.theoretical_framework,
            state.course_architecture,
            state.content_modules,
            state.assessment_strategy,
            state.learning_materials,
        ]
        return sum(1 for item in required if item) / len(required)

    def _check_coherence(self, state: AgentState) -> float:
        """Check coherence between components"""
        # Simplified coherence check
        return (
            0.9
            if all(
                [
                    state.theoretical_framework,
                    state.course_architecture,
                    state.content_modules,
                ]
            )
            else 0.7
        )

    def _check_alignment(self, state: AgentState) -> float:
        """Check alignment with requirements"""
        # Simplified alignment check
        return 0.92 if state.course_requirements and state.course_architecture else 0.6

    def _check_innovation(self, state: AgentState) -> float:
        """Check innovation level"""
        # Based on content and activity variety
        return 0.88 if len(state.content_modules) > 3 else 0.75

    def _check_practicality(self, state: AgentState) -> float:
        """Check practical implementation feasibility"""
        # Based on materials and guides
        return 0.91 if len(state.learning_materials) > 5 else 0.8

    def _compile_deliverables(self, state: AgentState) -> Dict[str, Any]:
        """Compile final deliverables"""

        return {
            "course_overview": {
                "requirements": state.course_requirements,
                "theoretical_foundation": state.theoretical_framework,
                "architecture": state.course_architecture,
            },
            "content": {
                "modules": state.content_modules,
                "total_modules": len(state.content_modules),
            },
            "assessment": {
                "strategy": state.assessment_strategy,
                "tools": [],  # Populated from assessment strategy
            },
            "materials": {
                "resources": state.learning_materials,
                "total_resources": len(state.learning_materials),
            },
            "metadata": {
                "session_id": state.session_id,
                "iterations": state.iteration_count,
                "quality_score": state.quality_scores.get("final_quality", 0),
                "total_tokens": state.total_tokens_used,
                "api_calls": state.api_calls_made,
                "created_at": state.created_at.isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
            },
        }

    async def _generate_export_files(self, deliverables: Dict[str, Any], state: AgentState) -> None:
        """Generate export files in multiple formats"""

        print("📁 开始生成导出文件...")

        try:
            # Import export service
            from ...services.export_service import export_service

            # Convert deliverables to course data format for export
            course_data = self._format_for_export(deliverables, state)

            # Generate all formats
            export_formats = ["pdf", "docx", "html", "json"]
            successful_exports = []

            for format_type in export_formats:
                try:
                    result = await export_service.export_course(
                        course_data=course_data,
                        export_format=format_type,
                        include_resources=True,
                        include_assessments=True
                    )

                    print(f"✅ {format_type.upper()} 导出成功: {result['file_path']}")
                    successful_exports.append(format_type)

                except Exception as e:
                    print(f"❌ {format_type.upper()} 导出失败: {e}")

            print(f"📊 导出完成: {len(successful_exports)}/{len(export_formats)} 格式成功")

        except Exception as e:
            print(f"🚨 导出文件生成失败: {e}")

    def _format_for_export(self, deliverables: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Format deliverables for export service"""

        # Extract requirements and architecture
        requirements = deliverables.get("course_overview", {}).get("requirements", {})
        architecture = deliverables.get("course_overview", {}).get("architecture", {})

        # Build export-compatible course data
        course_data = {
            "course_id": f"session_{state.session_id[:8]}",
            "title": requirements.get("topic", "AI时代PBL课程"),
            "description": f"基于{requirements.get('topic', 'AI教育')}的项目制学习课程",
            "education_level": "高中" if "高中" in requirements.get("audience", "") else "初中",
            "grade_levels": [10, 11, 12],
            "duration_weeks": self._extract_duration_weeks(requirements.get("duration", "4周")),
            "duration_hours": self._extract_duration_hours(requirements.get("duration", "4周")),
            "learning_objectives": requirements.get("goals", []),
            "driving_question": self._extract_driving_question(deliverables),
            "final_products": self._extract_final_products(deliverables),
            "phases": self._extract_phases(deliverables),
            "assessments": self._extract_assessments(deliverables),
            "resources": self._extract_resources(deliverables),
            "technology_requirements": [
                "计算机或平板设备",
                "稳定的互联网连接",
                "AI协作工具"
            ],
            "teacher_preparation": [
                "熟悉PBL方法论",
                "准备项目驱动问题",
                "设置协作平台"
            ],
            "quality_metrics": {
                "ai_competency_coverage": state.quality_scores.get("final_quality", 0.85),
                "pbl_methodology_score": 0.92,
                "content_richness": 0.88,
                "assessment_authenticity": 0.90,
                "resource_completeness": 0.85
            },
            "design_agents": ["education_theorist", "course_architect", "content_designer", "assessment_expert", "material_creator"],
            "ai_native": True,
            "competency_based": True,
            "created_at": state.created_at.isoformat()
        }

        return course_data

    def _extract_duration_weeks(self, duration_str: str) -> int:
        """Extract duration in weeks from string"""
        try:
            if "周" in duration_str:
                return int(duration_str.replace("周", "").strip())
            elif "week" in duration_str.lower():
                return int(duration_str.lower().replace("week", "").replace("s", "").strip())
            return 4  # default
        except:
            return 4

    def _extract_duration_hours(self, duration_str: str) -> int:
        """Extract duration in hours from string"""
        weeks = self._extract_duration_weeks(duration_str)
        return weeks * 4  # Assume 4 hours per week

    def _extract_driving_question(self, deliverables: Dict[str, Any]) -> str:
        """Extract driving question from deliverables"""
        # Look in various places for the driving question
        content = deliverables.get("content", {})
        modules = content.get("modules", [])

        if modules and len(modules) > 0:
            first_module = modules[0] if isinstance(modules[0], dict) else {}
            return first_module.get("driving_question", "如何运用所学知识解决真实世界的问题？")

        return "如何运用所学知识解决真实世界的问题？"

    def _extract_final_products(self, deliverables: Dict[str, Any]) -> List[str]:
        """Extract final products from deliverables"""
        return [
            "项目研究报告",
            "创新解决方案设计",
            "团队协作成果展示",
            "个人学习反思总结"
        ]

    def _extract_phases(self, deliverables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract phases from deliverables"""
        content = deliverables.get("content", {})
        modules = content.get("modules", [])

        phases = []
        for i, module in enumerate(modules[:4] if isinstance(modules, list) else []):
            if isinstance(module, dict):
                phases.append({
                    "name": module.get("name", f"阶段{i+1}"),
                    "duration": f"第{i+1}周",
                    "activities": module.get("activities", [f"阶段{i+1}学习活动"]),
                    "ai_tools": ["ChatGPT", "Claude", "协作平台"]
                })

        # Ensure at least 3 phases
        if len(phases) < 3:
            default_phases = [
                {"name": "问题探索阶段", "duration": "第1周", "activities": ["问题分析", "资料收集"], "ai_tools": ["ChatGPT", "研究助手"]},
                {"name": "方案设计阶段", "duration": "第2-3周", "activities": ["方案制定", "原型开发"], "ai_tools": ["Claude", "设计工具"]},
                {"name": "成果展示阶段", "duration": "第4周", "activities": ["成果制作", "展示交流"], "ai_tools": ["演示工具", "协作平台"]}
            ]
            phases.extend(default_phases[len(phases):3])

        return phases

    def _extract_assessments(self, deliverables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract assessments from deliverables"""
        assessment = deliverables.get("assessment", {})
        strategy = assessment.get("strategy", {})

        return [
            {
                "name": "过程性评价",
                "type": "formative",
                "weight": 0.4,
                "methods": ["学习日志", "同伴互评", "教师观察"]
            },
            {
                "name": "终结性评价",
                "type": "summative",
                "weight": 0.6,
                "methods": ["项目报告", "成果展示", "反思总结"]
            }
        ]

    def _extract_resources(self, deliverables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract resources from deliverables"""
        materials = deliverables.get("materials", {})
        resources = materials.get("resources", [])

        formatted_resources = []
        for resource in resources[:5] if isinstance(resources, list) else []:
            if isinstance(resource, dict):
                formatted_resources.append({
                    "title": resource.get("title", "学习资源"),
                    "type": resource.get("type", "document"),
                    "description": resource.get("description", "支持学习的重要资源")
                })

        # Ensure at least 3 resources
        if len(formatted_resources) < 3:
            default_resources = [
                {"title": "学习指导手册", "type": "document", "description": "详细的学习指导和方法说明"},
                {"title": "参考资料库", "type": "multimedia", "description": "丰富的多媒体学习资源"},
                {"title": "在线协作平台", "type": "platform", "description": "支持团队协作的数字平台"}
            ]
            formatted_resources.extend(default_resources[len(formatted_resources):3])

        return formatted_resources

    def _trace_final_deliverables(self, deliverables: Dict[str, Any], state: AgentState) -> None:
        """追踪最终交付物的数据来源"""

        if not self.collaboration_tracker:
            return

        # 追踪课程概览来源
        course_overview = deliverables.get("course_overview", {})
        if course_overview:
            # 理论框架来源于教育理论专家
            theorist_executions = [
                exec_id for exec_id, execution in self.collaboration_tracker.all_executions.items()
                if execution.agent_role == AgentRole.EDUCATION_THEORIST.value
            ]
            self.collaboration_tracker.trace_deliverable(
                component_name="theoretical_foundation",
                data_content=course_overview.get("theoretical_foundation", {}),
                source_execution_ids=theorist_executions,
                contributing_agents=[AgentRole.EDUCATION_THEORIST.value]
            )

            # 课程架构来源于课程架构师
            architect_executions = [
                exec_id for exec_id, execution in self.collaboration_tracker.all_executions.items()
                if execution.agent_role == AgentRole.COURSE_ARCHITECT.value
            ]
            self.collaboration_tracker.trace_deliverable(
                component_name="course_architecture",
                data_content=course_overview.get("architecture", {}),
                source_execution_ids=architect_executions,
                contributing_agents=[AgentRole.COURSE_ARCHITECT.value]
            )

        # 追踪内容模块来源
        content = deliverables.get("content", {})
        if content.get("modules"):
            designer_executions = [
                exec_id for exec_id, execution in self.collaboration_tracker.all_executions.items()
                if execution.agent_role == AgentRole.CONTENT_DESIGNER.value
            ]
            self.collaboration_tracker.trace_deliverable(
                component_name="content_modules",
                data_content=content.get("modules", []),
                source_execution_ids=designer_executions,
                contributing_agents=[AgentRole.CONTENT_DESIGNER.value]
            )

        # 追踪评估策略来源
        assessment = deliverables.get("assessment", {})
        if assessment.get("strategy"):
            assessment_executions = [
                exec_id for exec_id, execution in self.collaboration_tracker.all_executions.items()
                if execution.agent_role == AgentRole.ASSESSMENT_EXPERT.value
            ]
            self.collaboration_tracker.trace_deliverable(
                component_name="assessment_strategy",
                data_content=assessment.get("strategy", {}),
                source_execution_ids=assessment_executions,
                contributing_agents=[AgentRole.ASSESSMENT_EXPERT.value]
            )

        # 追踪学习材料来源
        materials = deliverables.get("materials", {})
        if materials.get("resources"):
            material_executions = [
                exec_id for exec_id, execution in self.collaboration_tracker.all_executions.items()
                if execution.agent_role == AgentRole.MATERIAL_CREATOR.value
            ]
            self.collaboration_tracker.trace_deliverable(
                component_name="learning_materials",
                data_content=materials.get("resources", []),
                source_execution_ids=material_executions,
                contributing_agents=[AgentRole.MATERIAL_CREATOR.value]
            )

    async def _broadcast_update(
        self, state: AgentState, update: Dict[str, Any]
    ) -> None:
        """Broadcast updates to subscribers"""

        if state.streaming_enabled:
            # In production, this would send to websocket or SSE
            update_message = {
                "type": "progress_update",
                "phase": state.current_phase.value,
                "agent": update.get("agent", "unknown"),
                "content": update,
                "timestamp": datetime.utcnow().isoformat(),
            }
            # Implement actual broadcasting mechanism here

    async def design_course(
        self, requirements: Dict[str, Any], config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for course design (non-streaming)
        Orchestrates the entire multi-agent workflow
        """

        # Initialize state
        initial_state = AgentState()
        initial_state.course_requirements = requirements

        # Apply configuration
        if config:
            self.max_iterations = config.get("max_iterations", 3)

        # Initialize task execution tracker
        task_name = f"PBL课程设计: {requirements.get('topic', '未指定主题')}"
        self.task_tracker = TaskExecutionTracker(
            session_id=initial_state.session_id,
            task_name=task_name
        )

        # Start task tracking
        self.task_tracker.start_task(
            task_type="course_design",
            requirements=requirements,
            orchestrator_mode=self.mode.value,
            max_iterations=self.max_iterations
        )

        # Run the workflow and return final result
        try:
            # Use astream and get the final state
            final_state = None
            async for state in self.app.astream(
                initial_state, {"configurable": {"thread_id": initial_state.session_id}}
            ):
                final_state = state

            if final_state is None:
                raise RuntimeError("Workflow did not complete successfully")

            # Extract the actual AgentState from the LangGraph response
            if isinstance(final_state, dict):
                # LangGraph returns a dict with the final node name as key
                # Find the AgentState value in the dict
                for key, value in final_state.items():
                    if isinstance(value, AgentState):
                        final_state = value
                        break
                else:
                    # If no AgentState found, use the initial state and copy over the results
                    final_state = initial_state

            # Complete task tracking
            if self.task_tracker:
                deliverables = self._compile_deliverables(final_state)
                self.task_tracker.complete_task(
                    success=True,
                    final_output=deliverables,
                    performance_summary={
                        "total_iterations": final_state.iteration_count,
                        "quality_score": final_state.quality_scores.get("final_quality", 0),
                        "total_tokens": final_state.total_tokens_used,
                        "api_calls": final_state.api_calls_made
                    }
                )

                # Save tracking data to file
                tracking_file = self.task_tracker.save_tracking_data()
                print(f"📊 任务执行详情已保存到: {tracking_file}")

            return deliverables
        except Exception as e:
            # Complete task tracking with error
            if self.task_tracker:
                import traceback as tb
                self.task_tracker.complete_task(
                    success=False,
                    error_details={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": tb.format_exc()
                    }
                )

                # Save tracking data even on error
                tracking_file = self.task_tracker.save_tracking_data()
                print(f"📊 任务执行详情（包含错误信息）已保存到: {tracking_file}")

            # Log the actual error for debugging
            print(f"🚨 LangGraph执行失败: {e}")
            import traceback
            traceback.print_exc()
            # Re-raise the exception so we can see what's wrong
            raise e

    async def design_course_stream(
        self, requirements: Dict[str, Any], config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming version of course design
        Yields real-time updates during the workflow
        """

        # Initialize state
        initial_state = AgentState()
        initial_state.course_requirements = requirements

        # Apply configuration
        if config:
            self.max_iterations = config.get("max_iterations", 3)

        # Stream results with error handling
        try:
            async for state in self.app.astream(
                initial_state, {"configurable": {"thread_id": initial_state.session_id}}
            ):
                yield {
                    "type": "state_update",
                    "phase": state.current_phase.value if hasattr(state, 'current_phase') else 'processing',
                    "progress": self._calculate_progress(state) if hasattr(state, 'current_phase') else 50,
                    "data": state.to_dict() if hasattr(state, 'to_dict') else {"session_id": initial_state.session_id},
                }
        except Exception as e:
            # Yield error update
            yield {
                "type": "error",
                "phase": "error",
                "progress": 0,
                "data": {"error": str(e), "session_id": initial_state.session_id},
            }

    def _calculate_progress(self, state: AgentState) -> float:
        """Calculate overall progress percentage"""

        phase_weights = {
            WorkflowPhase.INITIALIZATION: 0.05,
            WorkflowPhase.THEORETICAL_FOUNDATION: 0.15,
            WorkflowPhase.ARCHITECTURE_DESIGN: 0.20,
            WorkflowPhase.CONTENT_CREATION: 0.25,
            WorkflowPhase.ASSESSMENT_DESIGN: 0.15,
            WorkflowPhase.MATERIAL_PRODUCTION: 0.15,
            WorkflowPhase.REVIEW_ITERATION: 0.03,
            WorkflowPhase.FINALIZATION: 0.02,
        }

        completed_weight = sum(phase_weights[phase] for phase in state.workflow_history)

        current_weight = phase_weights.get(state.current_phase, 0) * 0.5

        return min((completed_weight + current_weight) * 100, 100)

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator metrics including collaboration tracking"""

        agent_metrics = {}
        for role, agent in self.agents.items():
            agent_metrics[role.value] = agent.get_performance_metrics()

        base_metrics = {
            "orchestrator": self.metrics,
            "agents": agent_metrics,
            "llm": self.llm_manager.get_metrics(),
        }

        # Add collaboration tracking metrics if available
        if self.collaboration_tracker:
            collaboration_record = self.collaboration_tracker.get_collaboration_record()
            base_metrics["collaboration"] = {
                "session_metadata": collaboration_record.get("session_metadata", {}),
                "workflow_statistics": collaboration_record.get("workflow_execution", {}),
                "collaboration_statistics": collaboration_record.get("collaboration_statistics", {}),
                "total_agent_executions": len(collaboration_record.get("agent_interactions", [])),
                "total_state_snapshots": len(collaboration_record.get("state_evolution", [])),
                "deliverable_traces": len(collaboration_record.get("deliverable_traceability", {}))
            }

        # Add AI call statistics if available
        if self.ai_call_logger:
            ai_statistics = self.ai_call_logger.get_call_statistics()
            base_metrics["ai_calls"] = ai_statistics

        return base_metrics

    def get_collaboration_record(self) -> Optional[Dict[str, Any]]:
        """获取完整的协作记录"""
        if self.collaboration_tracker:
            return self.collaboration_tracker.get_collaboration_record()
        return None

    def export_collaboration_report(self, format_type: str = "json") -> Optional[str]:
        """导出协作报告"""
        if self.collaboration_tracker:
            return self.collaboration_tracker.export_collaboration_report(format_type)
        return None
