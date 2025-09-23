"""
Agent Service - API integration for multi-agent system
Provides high-level interface for PBL course design
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import uuid4
from dotenv import load_dotenv

# 配置日志
logger = logging.getLogger(__name__)

# 显式加载环境变量
load_dotenv()

from ..agents.core.llm_manager import LLMManager, ModelType
from ..agents.core.orchestrator import OrchestratorMode, PBLOrchestrator
from ..agents.core.state import AgentState, WorkflowPhase


class AgentService:
    """
    Service layer for multi-agent system integration
    Handles API requests and manages agent orchestration
    """

    def __init__(self):
        """Initialize the agent service"""
        self.orchestrators: Dict[str, PBLOrchestrator] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        # 后台任务存储
        self.background_tasks: Dict[str, asyncio.Task] = {}
        # 使用真实API，确保test_mode=False
        self.llm_manager = LLMManager(test_mode=False)

    async def create_course_design_session(
        self,
        requirements: Dict[str, Any],
        mode: str = "full_course",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new course design session

        Args:
            requirements: Course requirements including topic, audience, duration, etc.
            mode: Design mode (full_course, quick_design, iteration, review, custom)
            config: Optional configuration for the session

        Returns:
            Session information including session_id
        """

        # Validate requirements
        self._validate_requirements(requirements)

        # Create session ID
        session_id = str(uuid4())

        # Determine orchestrator mode
        orchestrator_mode = OrchestratorMode[mode.upper()]

        # Create orchestrator
        orchestrator = PBLOrchestrator(
            llm_manager=self.llm_manager,
            mode=orchestrator_mode,
            enable_streaming=config.get("streaming", True) if config else True,
            max_iterations=config.get("max_iterations", 3) if config else 3,
        )

        # Store orchestrator and session
        self.orchestrators[session_id] = orchestrator
        self.sessions[session_id] = {
            "id": session_id,
            "requirements": requirements,
            "mode": mode,
            "config": config or {},
            "status": "created",
            "created_at": datetime.utcnow(),
            "progress": 0,
            "current_phase": None,
        }

        return {
            "session_id": session_id,
            "status": "created",
            "mode": mode,
            "message": "Course design session created successfully",
        }

    async def start_course_design(
        self, session_id: str, stream: bool = False
    ) -> Dict[str, Any]:
        """
        Start the course design process as a background task

        Args:
            session_id: Session identifier
            stream: Whether to stream results (deprecated - always async now)

        Returns:
            Task status information
        """

        # Validate session
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Check if task is already running
        if session_id in self.background_tasks:
            task = self.background_tasks[session_id]
            if not task.done():
                return {
                    "session_id": session_id,
                    "status": "already_running",
                    "message": "课程设计任务已在运行中"
                }

        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow()
        session["progress"] = 0
        session["current_phase"] = "initializing"
        session["current_agent"] = None

        logger.info(f"🚀 启动课程设计后台任务 - 会话ID: {session_id}")

        # Create and start background task
        task = asyncio.create_task(self._execute_course_design_background(session_id))
        self.background_tasks[session_id] = task

        return {
            "session_id": session_id,
            "status": "started",
            "message": "课程设计任务已启动，请使用状态查询接口监控进度"
        }

    async def _execute_course_design_background(self, session_id: str) -> None:
        """
        Execute course design in background task

        Args:
            session_id: Session identifier
        """
        session = self.sessions[session_id]
        orchestrator = self.orchestrators[session_id]

        try:
            logger.info(f"🤖 [{session_id}] 开始多智能体协作课程设计")

            # Update status
            session["current_phase"] = "agent_collaboration"
            session["progress"] = 10

            # Execute course design with detailed logging
            result = await self._execute_with_progress_tracking(
                orchestrator, session, session_id
            )

            # Update session with results
            session["status"] = "completed"
            session["completed_at"] = datetime.utcnow()
            session["progress"] = 100
            session["result"] = result
            session["current_phase"] = "completed"
            session["current_agent"] = None

            logger.info(f"✅ [{session_id}] 课程设计完成")

        except Exception as e:
            # Handle errors
            session["status"] = "failed"
            session["error"] = str(e)
            session["failed_at"] = datetime.utcnow()
            session["current_phase"] = "failed"
            session["current_agent"] = None

            logger.error(f"❌ [{session_id}] 课程设计失败: {str(e)}", exc_info=True)

        finally:
            # Clean up background task reference
            if session_id in self.background_tasks:
                del self.background_tasks[session_id]

    async def _execute_with_progress_tracking(
        self, orchestrator: PBLOrchestrator, session: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """
        Execute orchestrator with progress tracking and detailed logging

        Args:
            orchestrator: PBL orchestrator instance
            session: Session data
            session_id: Session identifier

        Returns:
            Course design results
        """
        try:
            # Check if orchestrator supports streaming
            design_generator = orchestrator.design_course(
                session["requirements"], session["config"]
            )

            # Handle both generator and direct result
            if hasattr(design_generator, '__aiter__'):
                # Stream mode - collect updates
                result = None
                async for update in design_generator:
                    if isinstance(update, dict):
                        # Update session progress from stream
                        if "progress" in update:
                            session["progress"] = update["progress"]
                        if "phase" in update:
                            session["current_phase"] = update["phase"]
                        if "current_agent" in update:
                            session["current_agent"] = update["current_agent"]

                        # Log progress
                        phase = update.get("phase", "unknown")
                        progress = update.get("progress", 0)
                        agent = update.get("current_agent", "unknown")

                        logger.info(f"📊 [{session_id}] 进度更新: {phase} - {progress}% (当前智能体: {agent})")

                        # Keep the latest result
                        if "result" in update:
                            result = update["result"]
                        elif "data" in update:
                            result = update["data"]

                return result if result else {}
            else:
                # Direct result mode
                result = await design_generator
                return result if result else {}

        except Exception as e:
            logger.error(f"❌ [{session_id}] 编排器执行失败: {str(e)}", exc_info=True)
            raise

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the status of a course design session with enhanced details

        Args:
            session_id: Session identifier

        Returns:
            Session status information including current agent and estimated time
        """

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Calculate estimated remaining time
        estimated_remaining = None
        if session["status"] == "running" and session.get("started_at"):
            # Simple estimation based on progress
            progress = session.get("progress", 0)
            if progress > 0:
                elapsed = (datetime.utcnow() - session["started_at"]).total_seconds()
                estimated_total = elapsed * (100 / progress)
                estimated_remaining = max(0, estimated_total - elapsed)

        # Check if background task is still running
        task_running = session_id in self.background_tasks and not self.background_tasks[session_id].done()

        return {
            "session_id": session_id,
            "status": session["status"],
            "progress": session.get("progress", 0),
            "current_phase": session.get("current_phase"),
            "current_agent": session.get("current_agent"),
            "task_running": task_running,
            "estimated_remaining_seconds": estimated_remaining,
            "created_at": session["created_at"].isoformat(),
            "started_at": (
                session.get("started_at").isoformat()
                if session.get("started_at")
                else None
            ),
            "completed_at": (
                session.get("completed_at").isoformat()
                if session.get("completed_at")
                else None
            ),
            "failed_at": (
                session.get("failed_at").isoformat()
                if session.get("failed_at")
                else None
            ),
            "error": session.get("error"),
        }

    async def get_session_result(self, session_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed course design session

        Args:
            session_id: Session identifier

        Returns:
            Course design results
        """

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        if session["status"] != "completed":
            raise ValueError(
                f"Session {session_id} is not completed. Status: {session['status']}"
            )

        return session.get("result", {})

    async def iterate_on_design(
        self, session_id: str, feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Iterate on an existing course design based on feedback

        Args:
            session_id: Session identifier
            feedback: Feedback for iteration

        Returns:
            Updated course design
        """

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        orchestrator = self.orchestrators[session_id]

        # Create iteration session
        iteration_session_id = str(uuid4())

        # Create new orchestrator for iteration
        iteration_orchestrator = PBLOrchestrator(
            llm_manager=self.llm_manager,
            mode=OrchestratorMode.ITERATION,
            enable_streaming=session["config"].get("streaming", True),
            max_iterations=1,
        )

        # Prepare iteration requirements
        iteration_requirements = {
            **session["requirements"],
            "feedback": feedback,
            "previous_result": session.get("result", {}),
        }

        # Store iteration session
        self.orchestrators[iteration_session_id] = iteration_orchestrator
        self.sessions[iteration_session_id] = {
            "id": iteration_session_id,
            "parent_session": session_id,
            "requirements": iteration_requirements,
            "mode": "iteration",
            "config": session["config"],
            "status": "created",
            "created_at": datetime.utcnow(),
            "progress": 0,
        }

        # Run iteration
        result = await iteration_orchestrator.design_course(
            iteration_requirements, session["config"]
        )

        # Update iteration session
        self.sessions[iteration_session_id]["status"] = "completed"
        self.sessions[iteration_session_id]["result"] = result

        return {
            "session_id": iteration_session_id,
            "parent_session": session_id,
            "status": "completed",
            "result": result,
        }

    async def get_agent_metrics(
        self, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for agents

        Args:
            session_id: Optional session ID for specific metrics

        Returns:
            Agent performance metrics
        """

        if session_id:
            if session_id not in self.orchestrators:
                raise ValueError(f"Session {session_id} not found")

            orchestrator = self.orchestrators[session_id]
            return orchestrator.get_metrics()

        # Global metrics
        total_sessions = len(self.sessions)
        completed_sessions = sum(
            1 for s in self.sessions.values() if s["status"] == "completed"
        )

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "success_rate": (
                completed_sessions / total_sessions if total_sessions > 0 else 0
            ),
            "llm_metrics": self.llm_manager.get_metrics(),
        }

    async def export_course_package(
        self, session_id: str, format: str = "json"
    ) -> Dict[str, Any] | bytes:
        """
        Export course design as a package

        Args:
            session_id: Session identifier
            format: Export format (json, pdf, zip)

        Returns:
            Exported course package
        """

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Allow export for failed sessions with partial results
        session_status = session["status"]
        if session_status not in ["completed", "failed"]:
            raise ValueError(f"Session {session_id} cannot be exported (status: {session_status})")

        result = session.get("result", {})

        # For failed sessions, include partial results and error information
        if session_status == "failed":
            result = {
                "status": "partial_failure",
                "warning": "此会话未完全完成，以下为部分结果",
                "partial_result": result,
                "error_info": session.get("error", "未知错误"),
                "completed_phases": session.get("completed_phases", []),
                "export_timestamp": datetime.utcnow().isoformat()
            }

        if format == "json":
            return result

        elif format == "pdf":
            # Generate PDF (implementation would require additional libraries)
            return self._generate_pdf(result)

        elif format == "zip":
            # Create zip package with all materials
            return self._create_zip_package(result)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _validate_requirements(self, requirements: Dict[str, Any]) -> None:
        """Validate course requirements"""

        required_fields = ["topic", "audience", "duration"]

        for field in required_fields:
            if field not in requirements:
                raise ValueError(f"Missing required field: {field}")

        # Validate audience age if provided
        if "age_group" in requirements:
            age = requirements["age_group"]
            if not isinstance(age, (str, dict)):
                raise ValueError("Age group must be a string or dict with min/max")

        # Validate duration
        duration = requirements["duration"]
        if not isinstance(duration, (str, int, dict)):
            raise ValueError(
                "Duration must be a string, number, or dict with value and unit"
            )

    def _generate_pdf(self, result: Dict[str, Any]) -> bytes:
        """Generate PDF from course design (placeholder)"""
        # This would require libraries like reportlab or weasyprint
        # For now, return empty bytes
        return b""

    def _create_zip_package(self, result: Dict[str, Any]) -> bytes:
        """Create zip package of course materials (placeholder)"""
        # This would require zipfile library to package all materials
        # For now, return empty bytes
        return b""

    async def cleanup_session(self, session_id: str) -> None:
        """
        Clean up a session and free resources

        Args:
            session_id: Session identifier
        """

        if session_id in self.orchestrators:
            del self.orchestrators[session_id]

        if session_id in self.sessions:
            del self.sessions[session_id]
