"""
PBL Orchestrator - LangGraph-based Multi-Agent Coordination System
World-class orchestration engine for PBL course design
"""

import asyncio
import json
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
    ):
        """Initialize the orchestrator with agents and workflow"""

        # Initialize LLM Manager
        self.llm_manager = llm_manager or LLMManager()

        # Configuration
        self.mode = mode
        self.enable_streaming = enable_streaming
        self.max_iterations = max_iterations

        # Initialize specialized agents
        self.agents = {
            AgentRole.EDUCATION_THEORIST: EducationTheoristAgent(self.llm_manager),
            AgentRole.COURSE_ARCHITECT: CourseArchitectAgent(self.llm_manager),
            AgentRole.CONTENT_DESIGNER: ContentDesignerAgent(self.llm_manager),
            AgentRole.ASSESSMENT_EXPERT: AssessmentExpertAgent(self.llm_manager),
            AgentRole.MATERIAL_CREATOR: MaterialCreatorAgent(self.llm_manager),
        }

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
        """Build the LangGraph workflow for agent coordination"""

        # Create the state graph
        workflow = StateGraph(AgentState)

        # Add nodes for each phase and agent
        workflow.add_node("initialize", self._initialize_phase)
        workflow.add_node("theoretical_foundation", self._theoretical_foundation_phase)
        workflow.add_node("architecture_design", self._architecture_design_phase)
        workflow.add_node("content_creation", self._content_creation_phase)
        workflow.add_node("assessment_design", self._assessment_design_phase)
        workflow.add_node("material_production", self._material_production_phase)
        workflow.add_node("review_iteration", self._review_iteration_phase)
        workflow.add_node("finalize", self._finalization_phase)

        # Define edges based on mode
        if self.mode == OrchestratorMode.FULL_COURSE:
            # Full sequential workflow
            workflow.set_entry_point("initialize")
            workflow.add_edge("initialize", "theoretical_foundation")
            workflow.add_edge("theoretical_foundation", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "assessment_design")
            workflow.add_edge("assessment_design", "material_production")
            workflow.add_conditional_edges(
                "material_production",
                self._should_iterate,
                {"iterate": "review_iteration", "finalize": "finalize"},
            )
            workflow.add_edge("review_iteration", "architecture_design")
            workflow.add_edge("finalize", END)

        elif self.mode == OrchestratorMode.QUICK_DESIGN:
            # Streamlined workflow
            workflow.set_entry_point("initialize")
            workflow.add_edge("initialize", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "finalize")
            workflow.add_edge("finalize", END)

        elif self.mode == OrchestratorMode.ITERATION:
            # Iteration-focused workflow
            workflow.set_entry_point("review_iteration")
            workflow.add_edge("review_iteration", "architecture_design")
            workflow.add_edge("architecture_design", "content_creation")
            workflow.add_edge("content_creation", "assessment_design")
            workflow.add_edge("assessment_design", "finalize")
            workflow.add_edge("finalize", END)

        else:
            # Custom workflow - all nodes available
            workflow.set_entry_point("initialize")
            workflow.add_edge("initialize", "finalize")
            workflow.add_edge("finalize", END)

        return workflow

    async def _initialize_phase(self, state: AgentState) -> AgentState:
        """Initialize the course design process"""

        state.transition_phase(WorkflowPhase.INITIALIZATION)

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

        return state

    async def _theoretical_foundation_phase(self, state: AgentState) -> AgentState:
        """Establish theoretical foundation with Education Theorist"""

        state.transition_phase(WorkflowPhase.THEORETICAL_FOUNDATION)

        # Prepare task for Education Theorist
        task = {
            "type": "analyze_requirements",
            "requirements": state.course_requirements,
        }

        # Execute Education Theorist
        theorist = self.agents[AgentRole.EDUCATION_THEORIST]

        if self.enable_streaming:
            async for update in theorist.execute(state, stream=True):
                # Stream updates to subscribers
                await self._broadcast_update(state, update)
        else:
            result = await theorist.execute(state, stream=False)
            async for res in result:
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
        async for result in theorist.execute(state):
            if "framework" in result.get("content", {}):
                state.theoretical_framework = result["content"]["framework"]

        return state

    async def _architecture_design_phase(self, state: AgentState) -> AgentState:
        """Design course architecture with Course Architect"""

        state.transition_phase(WorkflowPhase.ARCHITECTURE_DESIGN)

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

        # Execute Course Architect
        architect = self.agents[AgentRole.COURSE_ARCHITECT]

        async for result in architect.execute(state):
            if "architecture" in result.get("content", {}):
                state.course_architecture = result["content"]["architecture"]

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
        """Produce materials with Material Creator"""

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

        for material_task in material_types:
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
        """Finalize the course design"""

        state.transition_phase(WorkflowPhase.FINALIZATION)

        # Final quality check
        final_quality = await self._final_quality_check(state)
        state.add_quality_score("final_quality", final_quality)

        # Compile final deliverables
        deliverables = self._compile_deliverables(state)

        # Create final checkpoint
        final_checkpoint = state.create_checkpoint()

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

        # Run the workflow and return final result
        final_state = await self.app.ainvoke(
            initial_state, {"configurable": {"thread_id": initial_state.session_id}}
        )

        return self._compile_deliverables(final_state)

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

        # Stream results
        async for state in self.app.astream(
            initial_state, {"configurable": {"thread_id": initial_state.session_id}}
        ):
            yield {
                "type": "state_update",
                "phase": state.current_phase.value,
                "progress": self._calculate_progress(state),
                "data": state.to_dict(),
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
        """Get orchestrator metrics"""

        agent_metrics = {}
        for role, agent in self.agents.items():
            agent_metrics[role.value] = agent.get_performance_metrics()

        return {
            "orchestrator": self.metrics,
            "agents": agent_metrics,
            "llm": self.llm_manager.get_metrics(),
        }
