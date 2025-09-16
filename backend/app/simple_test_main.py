"""
简化的FastAPI应用 - 用于测试
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建简化的FastAPI应用
app = FastAPI(
    title="PBL智能助手测试API",
    description="简化版API用于测试业务流程",
    version="1.0.0-test"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# 根路径
@app.get("/")
async def root():
    """API根路径信息"""
    return {
        "service": "PBL智能助手测试API",
        "version": "1.0.0-test",
        "status": "running",
        "agents": {
            "education_director": "教育总监",
            "pbl_curriculum_designer": "PBL课程设计师",
            "learning_experience_designer": "学习体验设计师",
            "creative_technologist": "创意技术专家",
            "makerspace_manager": "创客空间管理员",
        },
    }


# 健康检查
@app.get("/api/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "service": "PBL智能助手测试API",
        "version": "1.0.0-test"
    }


# 智能体能力查询
@app.get("/api/v1/agents/capabilities")
async def get_system_capabilities():
    """获取系统能力信息"""
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
            ],
            "features": {
                "streaming": "Real-time progress updates",
                "iteration": "Refinement based on feedback",
                "export": "Multiple export formats",
                "metrics": "Performance and quality tracking",
            },
            "version": "1.0.0-test",
        },
    }


# 创建课程设计会话
@app.post("/api/v1/agents/sessions")
async def create_design_session(request: dict):
    """创建课程设计会话"""
    import uuid
    session_id = str(uuid.uuid4())

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "status": "created",
            "requirements": request.get("requirements", {}),
            "mode": request.get("mode", "full_course")
        },
        "message": "Course design session created successfully"
    }


# 启动设计流程
@app.post("/api/v1/agents/sessions/{session_id}/start")
async def start_design_process(session_id: str):
    """启动设计流程"""
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "status": "completed",
            "progress": 100
        },
        "message": "Course design completed successfully"
    }


# 获取会话状态
@app.get("/api/v1/agents/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """获取会话状态"""
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "status": "completed",
            "progress": 100,
            "current_phase": "completed",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T00:01:00Z"
        }
    }


# 获取设计结果
@app.get("/api/v1/agents/sessions/{session_id}/result")
async def get_design_result(session_id: str):
    """获取设计结果"""
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "course": {
                "title": "AI基础与应用课程设计",
                "description": "基于PBL方法的人工智能课程",
                "duration": "8周",
                "target_audience": "高中生",
                "learning_objectives": [
                    "理解人工智能基本概念",
                    "掌握机器学习基础原理",
                    "能够实现简单AI项目"
                ]
            }
        },
        "message": "Course design retrieved successfully"
    }


# 课程迭代
@app.post("/api/v1/agents/sessions/{session_id}/iterate")
async def iterate_on_design(session_id: str, feedback: dict):
    """基于反馈迭代设计"""
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "iteration": 2,
            "improvements": [
                "优化了学习目标的可衡量性",
                "增加了同伴评议环节",
                "添加了AI伦理模块"
            ]
        },
        "message": "Design iteration completed successfully"
    }


# 导出课程
@app.get("/api/v1/agents/sessions/{session_id}/export")
async def export_course_design(session_id: str, format: str = "json"):
    """导出课程设计"""
    if format == "json":
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "export_format": "json",
                "course_data": {"title": "测试课程", "content": "模拟数据"}
            },
            "format": "json"
        }
    else:
        return {
            "success": True,
            "message": f"Export in {format} format completed",
            "download_url": f"/downloads/{session_id}.{format}"
        }


# 获取智能体指标
@app.get("/api/v1/agents/metrics")
async def get_agent_metrics():
    """获取智能体性能指标"""
    return {
        "success": True,
        "data": {
            "total_sessions": 10,
            "active_sessions": 1,
            "success_rate": 95.5,
            "avg_completion_time": "2.5 minutes",
            "agent_performance": {
                "education_theorist": {"success_rate": 98, "avg_time": "30s"},
                "course_architect": {"success_rate": 95, "avg_time": "45s"},
                "content_designer": {"success_rate": 97, "avg_time": "40s"},
                "assessment_expert": {"success_rate": 94, "avg_time": "35s"},
                "material_creator": {"success_rate": 96, "avg_time": "50s"}
            }
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }


# 清理会话
@app.delete("/api/v1/agents/sessions/{session_id}")
async def cleanup_session(session_id: str):
    """清理会话"""
    return {
        "success": True,
        "message": f"Session {session_id} cleaned up successfully"
    }


# 模板相关接口
@app.get("/api/v1/templates/categories")
async def get_template_categories():
    """获取模板分类"""
    return {
        "categories": [
            {"value": "STEM", "label": "STEM教育", "description": "科学、技术、工程、数学"},
            {"value": "HUMANITIES", "label": "人文学科", "description": "语言、文学、历史"},
            {"value": "ARTS", "label": "艺术类", "description": "美术、音乐、创作"}
        ]
    }


@app.get("/api/v1/templates/predefined")
async def get_predefined_templates():
    """获取预定义模板"""
    return {
        "templates": [
            {"id": "stem_basic", "name": "STEM基础模板", "category": "STEM"},
            {"id": "humanities_basic", "name": "人文基础模板", "category": "HUMANITIES"}
        ],
        "message": "预定义模板列表"
    }


@app.get("/api/v1/templates")
async def list_templates(limit: int = 20):
    """获取模板列表"""
    return {
        "templates": [
            {"id": "template1", "name": "AI课程模板", "category": "STEM", "usage_count": 50},
            {"id": "template2", "name": "文学创作模板", "category": "HUMANITIES", "usage_count": 30}
        ],
        "total": 2,
        "page": 1,
        "page_size": limit
    }


# 质量检查接口
@app.get("/api/v1/quality/statistics")
async def get_quality_statistics():
    """获取质量统计"""
    return {
        "total_courses": 100,
        "average_score": 85.5,
        "quality_distribution": {
            "excellent": 20,
            "good": 45,
            "acceptable": 25,
            "needs_improvement": 8,
            "poor": 2
        },
        "common_issues": ["缺少明确学习目标", "评估方法单一"],
        "improvement_trends": ["学习目标设计持续提升"]
    }


@app.get("/api/v1/quality/issues/common")
async def get_common_issues():
    """获取常见质量问题"""
    return {
        "issues": [
            {
                "title": "缺少学习目标",
                "category": "学习目标",
                "severity": "critical",
                "frequency": 45,
                "description": "课程未设定明确的学习目标"
            },
            {
                "title": "评估方法单一",
                "category": "评估设计",
                "severity": "warning",
                "frequency": 35,
                "description": "评估方式缺乏多样性"
            }
        ],
        "total": 2
    }


# 协作功能接口
@app.get("/api/v1/collaboration/my-collaborations")
async def get_my_collaborations():
    """获取协作课程"""
    return {
        "collaborations": [
            {
                "course_id": "course1",
                "title": "AI基础课程",
                "my_role": "owner",
                "last_updated": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0
    }


@app.get("/api/v1/collaboration/statistics")
async def get_collaboration_statistics():
    """获取协作统计"""
    return {
        "total_collaborations": 5,
        "role_distribution": {"owner": 2, "editor": 2, "viewer": 1},
        "recent_activity_count": 3,
        "most_active_role": "editor"
    }


@app.get("/api/v1/collaboration/shared-courses")
async def get_shared_courses():
    """获取共享课程"""
    return [
        {
            "course_id": "shared1",
            "title": "共享的AI课程",
            "shared_by": "用户A",
            "share_scope": "public"
        }
    ]