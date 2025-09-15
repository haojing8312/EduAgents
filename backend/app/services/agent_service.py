"""
Agent Service - API integration for multi-agent system
Provides high-level interface for PBL course design
"""

import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import uuid4

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
        self.llm_manager = LLMManager()

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
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """
        Start the course design process

        Args:
            session_id: Session identifier
            stream: Whether to stream results

        Returns:
            Course design results (streamed or complete)
        """

        # Validate session
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        orchestrator = self.orchestrators[session_id]

        # Update session status
        session["status"] = "running"
        session["started_at"] = datetime.utcnow()

        try:
            if stream:
                # Stream results
                async for update in orchestrator.design_course(
                    session["requirements"], session["config"]
                ):
                    # Update session progress
                    session["progress"] = update.get("progress", 0)
                    session["current_phase"] = update.get("phase")

                    # Yield update to client
                    yield {
                        "session_id": session_id,
                        "type": update.get("type"),
                        "phase": update.get("phase"),
                        "progress": update.get("progress"),
                        "data": update.get("data"),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                # Mark as completed
                session["status"] = "completed"
                session["completed_at"] = datetime.utcnow()
                session["progress"] = 100

            else:
                # Get complete result
                result = await orchestrator.design_course(
                    session["requirements"], session["config"]
                )

                # Update session
                session["status"] = "completed"
                session["completed_at"] = datetime.utcnow()
                session["progress"] = 100
                session["result"] = result

                return {
                    "session_id": session_id,
                    "status": "completed",
                    "result": result,
                    "metrics": orchestrator.get_metrics(),
                }

        except Exception as e:
            # Handle errors
            session["status"] = "failed"
            session["error"] = str(e)
            session["failed_at"] = datetime.utcnow()

            if stream:
                yield {
                    "session_id": session_id,
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                raise e

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the status of a course design session

        Args:
            session_id: Session identifier

        Returns:
            Session status information
        """

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        return {
            "session_id": session_id,
            "status": session["status"],
            "progress": session["progress"],
            "current_phase": session["current_phase"],
            "created_at": session["created_at"].isoformat(),
            "started_at": (
                session.get("started_at", "").isoformat()
                if session.get("started_at")
                else None
            ),
            "completed_at": (
                session.get("completed_at", "").isoformat()
                if session.get("completed_at")
                else None
            ),
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

        if session["status"] != "completed":
            raise ValueError(f"Session {session_id} is not completed")

        result = session.get("result", {})

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
