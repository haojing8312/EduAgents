"""
API endpoints for multi-agent PBL course design system
World-class API design with streaming support and comprehensive error handling
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...core.deps import get_current_user
from ...services.agent_service import AgentService

# Initialize router
router = APIRouter(prefix="/agents", tags=["Multi-Agent System"])

# Initialize agent service
agent_service = AgentService()


# Request/Response Models
class CourseRequirements(BaseModel):
    """Course design requirements"""

    topic: str = Field(..., description="Course topic or subject area")
    audience: str = Field(..., description="Target audience description")
    age_group: str | Dict[str, int] = Field(..., description="Age group or range")
    duration: str | int | Dict[str, Any] = Field(..., description="Course duration")
    goals: list[str] = Field(default=[], description="Learning goals")
    context: str = Field(default="", description="Educational context")
    constraints: Dict[str, Any] = Field(default={}, description="Design constraints")
    preferences: Dict[str, Any] = Field(default={}, description="Design preferences")


class SessionConfig(BaseModel):
    """Session configuration"""

    streaming: bool = Field(default=True, description="Enable streaming responses")
    max_iterations: int = Field(default=3, description="Maximum design iterations")
    model_preference: str = Field(default="claude", description="Preferred LLM model")
    temperature: float = Field(default=0.7, description="LLM temperature")


class CreateSessionRequest(BaseModel):
    """Create course design session request"""

    requirements: CourseRequirements
    mode: str = Field(default="full_course", description="Design mode")
    config: Optional[SessionConfig] = None


class IterationFeedback(BaseModel):
    """Feedback for design iteration"""

    aspects: Dict[str, str] = Field(..., description="Feedback on specific aspects")
    priorities: list[str] = Field(default=[], description="Priority improvements")
    additional_requirements: Dict[str, Any] = Field(
        default={}, description="New requirements"
    )


# API Endpoints
@router.post("/sessions", response_model=Dict[str, Any])
async def create_design_session(
    request: CreateSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Create a new PBL course design session

    This endpoint initializes a multi-agent collaborative session for designing
    a complete PBL course based on provided requirements.
    """
    try:
        # Convert Pydantic models to dicts
        requirements = request.requirements.dict()
        config = request.config.dict() if request.config else None

        # Add user context
        requirements["user_id"] = current_user.get("id")

        # Create session
        session = await agent_service.create_course_design_session(
            requirements=requirements, mode=request.mode, config=config
        )

        return {
            "success": True,
            "data": session,
            "message": "Course design session created successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@router.post("/sessions/{session_id}/start")
async def start_design_process(
    session_id: str,
    stream: bool = Query(default=False, description="Enable streaming response"),
    current_user: Dict = Depends(get_current_user),
):
    """
    Start the course design process for a session

    This endpoint triggers the multi-agent orchestration to begin designing
    the PBL course. Supports both streaming and non-streaming modes.
    """
    try:
        if stream:
            # Return streaming response
            async def generate():
                async for update in agent_service.start_course_design(
                    session_id, stream=True
                ):
                    yield f"data: {json.dumps(update)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # Return complete result
            result = await agent_service.start_course_design(session_id, stream=False)
            return {
                "success": True,
                "data": result,
                "message": "Course design completed successfully",
            }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design process failed: {str(e)}")


@router.get("/sessions/{session_id}/status", response_model=Dict[str, Any])
async def get_session_status(
    session_id: str, current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the current status of a design session

    Returns detailed status information including progress, current phase,
    and timing information.
    """
    try:
        status = await agent_service.get_session_status(session_id)
        return {"success": True, "data": status}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/sessions/{session_id}/result", response_model=Dict[str, Any])
async def get_design_result(
    session_id: str, current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the complete result of a finished design session

    Returns the full course design including theoretical framework,
    architecture, content modules, assessments, and materials.
    """
    try:
        result = await agent_service.get_session_result(session_id)
        return {
            "success": True,
            "data": result,
            "message": "Course design retrieved successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")


@router.post("/sessions/{session_id}/iterate", response_model=Dict[str, Any])
async def iterate_on_design(
    session_id: str,
    feedback: IterationFeedback,
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Iterate on an existing course design based on feedback

    This endpoint allows refinement of a completed course design
    by providing specific feedback for the agents to address.
    """
    try:
        result = await agent_service.iterate_on_design(
            session_id=session_id, feedback=feedback.dict()
        )

        return {
            "success": True,
            "data": result,
            "message": "Design iteration completed successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Iteration failed: {str(e)}")


@router.get("/sessions/{session_id}/export")
async def export_course_design(
    session_id: str,
    format: str = Query(default="json", description="Export format (json, pdf, zip)"),
    current_user: Dict = Depends(get_current_user),
):
    """
    Export the course design in various formats

    Supports JSON for data integration, PDF for documentation,
    and ZIP for complete course package with all materials.
    """
    try:
        result = await agent_service.export_course_package(
            session_id=session_id, format=format
        )

        if format == "json":
            return {"success": True, "data": result, "format": "json"}
        elif format == "pdf":
            return StreamingResponse(
                content=result,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=course_design_{session_id}.pdf"
                },
            )
        elif format == "zip":
            return StreamingResponse(
                content=result,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=course_package_{session_id}.zip"
                },
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics(
    session_id: Optional[str] = Query(
        None, description="Optional session ID for specific metrics"
    ),
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get performance metrics for the multi-agent system

    Returns detailed metrics including agent performance, LLM usage,
    token consumption, and quality scores.
    """
    try:
        metrics = await agent_service.get_agent_metrics(session_id)
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.delete("/sessions/{session_id}")
async def cleanup_session(
    session_id: str, current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clean up a session and free resources

    This endpoint removes a session from memory and cleans up
    associated resources. Use after exporting results.
    """
    try:
        await agent_service.cleanup_session(session_id)
        return {
            "success": True,
            "message": f"Session {session_id} cleaned up successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/capabilities", response_model=Dict[str, Any])
async def get_system_capabilities() -> Dict[str, Any]:
    """
    Get information about system capabilities

    Returns details about available agents, supported modes,
    and system features.
    """
    return {
        "success": True,
        "data": {
            "agents": [
                {
                    "name": "Education Theorist",
                    "role": "Provides pedagogical foundation and learning theory expertise",
                    "capabilities": [
                        "Framework development",
                        "Theory application",
                        "Learning validation",
                    ],
                },
                {
                    "name": "Course Architect",
                    "role": "Designs course structure and learning pathways",
                    "capabilities": [
                        "Module sequencing",
                        "Pathway design",
                        "Milestone planning",
                    ],
                },
                {
                    "name": "Content Designer",
                    "role": "Creates engaging educational content and activities",
                    "capabilities": [
                        "Content creation",
                        "Activity design",
                        "Scenario development",
                    ],
                },
                {
                    "name": "Assessment Expert",
                    "role": "Develops comprehensive assessment strategies",
                    "capabilities": [
                        "Rubric creation",
                        "Portfolio design",
                        "Feedback systems",
                    ],
                },
                {
                    "name": "Material Creator",
                    "role": "Produces ready-to-use educational materials",
                    "capabilities": [
                        "Worksheet creation",
                        "Template design",
                        "Digital resources",
                    ],
                },
            ],
            "modes": [
                {
                    "id": "full_course",
                    "name": "Full Course Design",
                    "description": "Complete PBL course design with all components",
                },
                {
                    "id": "quick_design",
                    "name": "Quick Design",
                    "description": "Streamlined course design for rapid prototyping",
                },
                {
                    "id": "iteration",
                    "name": "Iteration Mode",
                    "description": "Refine existing course design based on feedback",
                },
                {
                    "id": "review",
                    "name": "Review Mode",
                    "description": "Review and validate existing course design",
                },
                {
                    "id": "custom",
                    "name": "Custom Mode",
                    "description": "Flexible mode for specific requirements",
                },
            ],
            "features": {
                "streaming": "Real-time progress updates",
                "iteration": "Refinement based on feedback",
                "export": "Multiple export formats",
                "metrics": "Performance and quality tracking",
                "collaboration": "Inter-agent collaboration",
                "dual_model": "Claude and GPT-4o integration",
            },
            "version": "1.0.0",
        },
    }


# WebSocket endpoint for real-time updates (optional enhancement)
@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket, session_id: str):
    """
    WebSocket connection for real-time session updates

    Provides live updates on course design progress, agent activities,
    and system status.
    """
    await websocket.accept()
    try:
        # Start design process with streaming
        async for update in agent_service.start_course_design(session_id, stream=True):
            await websocket.send_json(update)

        await websocket.send_json({"type": "complete", "message": "Design completed"})

    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()
