"""
API endpoints for multi-agent PBL course design system
World-class API design with streaming support and comprehensive error handling
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...core.deps import get_current_user
from ...services.agent_service import AgentService

# Initialize router
router = APIRouter(prefix="/agents", tags=["Multi-Agent System"])

# Initialize agent service
agent_service = AgentService()


@router.get("/status", response_model=Dict[str, Any])
async def get_agents_status():
    """
    获取多智能体系统状态

    返回5个专业智能体的状态信息
    """
    agents_info = [
        {
            "type": "education_theorist",
            "name": "教育理论专家",
            "description": "AI时代教育理论和PBL方法论",
            "status": "ready",
            "capabilities": ["教育理论分析", "能力导向设计", "AI教育哲学"]
        },
        {
            "type": "course_architect",
            "name": "课程架构师",
            "description": "面向AI时代能力的课程结构设计",
            "status": "ready",
            "capabilities": ["跨学科整合", "计算思维培养", "项目式学习架构"]
        },
        {
            "type": "content_designer",
            "name": "内容设计师",
            "description": "AI时代场景化学习内容创作",
            "status": "ready",
            "capabilities": ["真实问题情境", "人机协作活动", "数字素养实践"]
        },
        {
            "type": "assessment_expert",
            "name": "评估专家",
            "description": "AI时代核心能力评价体系设计",
            "status": "ready",
            "capabilities": ["过程性评价", "创造力评估", "元认知测评"]
        },
        {
            "type": "material_creator",
            "name": "素材创作者",
            "description": "AI时代数字化资源生成",
            "status": "ready",
            "capabilities": ["多媒体内容", "交互式工具", "AI工具指南"]
        }
    ]

    return {
        "success": True,
        "agents": agents_info,
        "total_agents": len(agents_info),
        "all_ready": True,
        "system_status": "operational",
        "ai_native": True,
        "collaboration_enabled": True
    }


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


@router.post("/test-real-agent", response_model=Dict[str, Any])
async def test_real_agent_execution(
    agent_id: str = Query(..., description="Agent to test (education_theorist, course_architect, etc.)"),
    course_requirement: str = Query(default="AI伦理教育", description="Course requirement for testing")
) -> Dict[str, Any]:
    """
    Test real agent execution (for development and validation)

    This endpoint tests the real agent service integration by executing
    a single agent with a test course requirement.
    """
    try:
        from app.services.real_agent_service import execute_real_agent_work

        result = await execute_real_agent_work(agent_id, course_requirement)

        return {
            "success": True,
            "data": result,
            "message": f"Real agent {agent_id} executed successfully",
            "agent_id": agent_id,
            "course_requirement": course_requirement
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Real agent {agent_id} execution failed",
            "agent_id": agent_id,
            "course_requirement": course_requirement
        }


@router.get("/courses", response_model=Dict[str, Any])
async def get_ai_generated_courses(
    limit: int = Query(default=10, description="Number of courses to return"),
    offset: int = Query(default=0, description="Offset for pagination")
) -> Dict[str, Any]:
    """
    Get AI-generated courses from database

    Returns a list of courses generated by AI agents with their metadata.
    """
    try:
        from app.services.course_persistence_service import get_persistence_service
        from app.core.database import get_session
        from app.models.course import Course
        from sqlalchemy import select, desc

        async with await get_session() as session:
            # Query AI-generated courses
            stmt = (
                select(Course)
                .where(Course.extra_data["ai_generated"].astext == "true")
                .order_by(desc(Course.created_at))
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)
            courses = result.scalars().all()

            # Convert to dictionary format
            courses_data = []
            for course in courses:
                course_dict = course.to_dict()
                courses_data.append(course_dict)

            # Get statistics
            async with await get_persistence_service() as persistence:
                persistence.session = session
                stats = await persistence.get_course_statistics()

            return {
                "success": True,
                "data": {
                    "courses": courses_data,
                    "total_returned": len(courses_data),
                    "limit": limit,
                    "offset": offset,
                    "statistics": stats
                },
                "message": f"Found {len(courses_data)} AI-generated courses"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "courses": [],
                "total_returned": 0,
                "statistics": {}
            },
            "message": f"Failed to retrieve courses: {str(e)}"
        }


@router.get("/courses/{course_id}", response_model=Dict[str, Any])
async def get_course_by_id(course_id: str) -> Dict[str, Any]:
    """
    Get a specific course by ID

    Returns detailed course information including lessons, assessments, and resources.
    """
    try:
        from app.core.database import get_session
        from app.models.course import Course, Lesson, Assessment, Resource
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        import uuid

        course_uuid = uuid.UUID(course_id)

        async with await get_session() as session:
            # Query course with related data
            stmt = (
                select(Course)
                .options(
                    selectinload(Course.lessons),
                    selectinload(Course.assessments),
                    selectinload(Course.resources)
                )
                .where(Course.id == course_uuid)
            )

            result = await session.execute(stmt)
            course = result.scalar_one_or_none()

            if not course:
                return {
                    "success": False,
                    "error": "Course not found",
                    "data": None,
                    "message": f"No course found with ID: {course_id}"
                }

            # Convert to dictionary with relationships
            course_dict = course.to_dict()
            course_dict["lessons"] = [lesson.to_dict() for lesson in course.lessons]
            course_dict["assessments"] = [assessment.to_dict() for assessment in course.assessments]
            course_dict["resources"] = [resource.to_dict() for resource in course.resources]

            return {
                "success": True,
                "data": course_dict,
                "message": "Course retrieved successfully"
            }

    except ValueError:
        return {
            "success": False,
            "error": "Invalid course ID format",
            "data": None,
            "message": "Course ID must be a valid UUID"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Failed to retrieve course: {str(e)}"
        }


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


@router.get("/cache/health", response_model=Dict[str, Any])
async def get_cache_health() -> Dict[str, Any]:
    """
    Get cache system health status

    Returns detailed information about Redis cache connections,
    memory usage, and key statistics.
    """
    try:
        from app.core.cache import get_cache_health

        health_data = await get_cache_health()

        return {
            "success": True,
            "data": health_data,
            "message": "Cache health retrieved successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Failed to get cache health: {str(e)}"
        }


@router.delete("/cache/clear/{cache_type}")
async def clear_cache_by_type(cache_type: str) -> Dict[str, Any]:
    """
    Clear cache by type

    Supported cache types: agent, session, llm, template, export
    """
    try:
        from app.core.cache import smart_cache_manager

        valid_types = ["agent", "session", "llm", "template", "export", "cache"]
        if cache_type not in valid_types:
            return {
                "success": False,
                "error": "Invalid cache type",
                "data": None,
                "message": f"Cache type must be one of: {', '.join(valid_types)}"
            }

        # Clear cache by pattern
        pattern = f"{cache_type}:*"
        cleared_count = await smart_cache_manager.delete_pattern(pattern, cache_type)

        return {
            "success": True,
            "data": {
                "cache_type": cache_type,
                "cleared_keys": cleared_count
            },
            "message": f"Cleared {cleared_count} keys from {cache_type} cache"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Failed to clear cache: {str(e)}"
        }


@router.get("/vector/search", response_model=Dict[str, Any])
async def search_similar_courses(
    query: str,
    limit: int = 5,
    education_level: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for similar courses using semantic vector search

    Uses ChromaDB vector similarity search to find courses related to the query.
    """
    try:
        from app.services.vector_service import search_similar_courses as vector_search

        # Build filters
        filters = {}
        if education_level:
            filters["education_level"] = education_level
        if subject:
            filters["subject"] = subject

        # Perform vector search
        results = await vector_search(query, limit, filters)

        return {
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "total_found": len(results),
                "filters_applied": filters
            },
            "message": f"Found {len(results)} similar courses"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Vector search failed: {str(e)}"
        }


@router.get("/vector/health", response_model=Dict[str, Any])
async def get_vector_store_health() -> Dict[str, Any]:
    """
    Get vector store health and statistics

    Returns information about ChromaDB collections and document counts.
    """
    try:
        from app.services.vector_service import get_vector_store_health

        health_data = await get_vector_store_health()

        return {
            "success": True,
            "data": health_data,
            "message": "Vector store health retrieved successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Failed to get vector store health: {str(e)}"
        }


@router.get("/export/formats", response_model=Dict[str, Any])
async def get_export_formats() -> Dict[str, Any]:
    """
    Get supported export formats

    Returns a list of all supported course export formats.
    """
    try:
        from app.services.export_service import get_supported_formats

        formats = await get_supported_formats()

        return {
            "success": True,
            "data": {
                "supported_formats": formats,
                "format_descriptions": {
                    "json": "Complete course data in JSON format",
                    "markdown": "Human-readable Markdown documentation",
                    "docx": "Microsoft Word document",
                    "html": "Styled HTML webpage"
                }
            },
            "message": f"Found {len(formats)} supported export formats"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Failed to get export formats: {str(e)}"
        }


@router.post("/export/{course_id}", response_model=Dict[str, Any])
async def export_course(
    course_id: str,
    export_format: str,
    include_materials: bool = True,
    custom_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Export a course in the specified format

    Exports an AI-generated course with all materials in the requested format.
    Supported formats: json, markdown, docx, html
    """
    try:
        from app.services.export_service import export_course_to_format

        result = await export_course_to_format(
            course_id=course_id,
            export_format=export_format,
            include_materials=include_materials,
            custom_options=custom_options or {}
        )

        if result.get("success"):
            return {
                "success": True,
                "data": {
                    "course_id": course_id,
                    "export_format": export_format,
                    "file_info": {
                        "filename": result.get("filename"),
                        "file_path": result.get("file_path"),
                        "size_bytes": result.get("size_bytes")
                    },
                    "include_materials": include_materials
                },
                "message": f"Course exported successfully as {export_format}"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Export failed"),
                "data": None,
                "message": f"Failed to export course {course_id}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Course export failed: {str(e)}"
        }


@router.post("/export/{course_id}/package", response_model=Dict[str, Any])
async def create_export_package(
    course_id: str,
    formats: List[str],
    include_materials: bool = True
) -> Dict[str, Any]:
    """
    Create a complete course export package

    Creates a ZIP package containing the course exported in multiple formats.
    """
    try:
        from app.services.export_service import create_course_package

        result = await create_course_package(
            course_id=course_id,
            formats=formats,
            include_materials=include_materials
        )

        if result.get("success"):
            return {
                "success": True,
                "data": {
                    "course_id": course_id,
                    "package_info": {
                        "filename": result.get("package_filename"),
                        "size_bytes": result.get("package_size_bytes"),
                        "exported_files": result.get("exported_files", []),
                        "total_files": len(result.get("exported_files", []))
                    },
                    "errors": result.get("errors", []),
                    "formats_requested": formats
                },
                "message": f"Course package created with {len(result.get('exported_files', []))} files"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Package creation failed"),
                "data": None,
                "message": f"Failed to create package for course {course_id}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "message": f"Package creation failed: {str(e)}"
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
