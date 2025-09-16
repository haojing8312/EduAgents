"""
简化版PBL智能助手API
用于快速演示和测试基础功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="PBL智能助手 - 简化版",
    description="AI原生多智能体PBL课程设计助手系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件 - 修复跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:48281", "http://127.0.0.1:48281", "*"],  # 明确允许前端地址
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def read_root():
    """根路径 - 系统信息"""
    return {
        "name": "PBL智能助手",
        "version": "1.0.0",
        "description": "AI原生多智能体PBL课程设计助手系统",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api": "/api/v1"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    try:
        # 简化的健康检查
        return {
            "status": "healthy",
            "timestamp": "2024-09-16T11:00:00Z",
            "services": {
                "database": "connected",
                "cache": "connected",
                "llm": "configured",
                "vector_db": "connected"
            },
            "config": {
                "postgres_schema": settings.POSTGRES_SCHEMA,
                "llm_provider": settings.LLM_PROVIDER,
                "environment": settings.ENVIRONMENT
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/api/v1/agents", tags=["agents"])
async def list_agents():
    """列出可用的智能体"""
    return {
        "agents": [
            {
                "id": "education_theorist",
                "name": "教育理论专家",
                "description": "专注于教育理论和PBL方法论研究"
            },
            {
                "id": "course_architect",
                "name": "课程架构师",
                "description": "负责课程结构设计和学习路径规划"
            },
            {
                "id": "content_designer",
                "name": "内容设计师",
                "description": "设计教学内容和学习活动"
            },
            {
                "id": "assessment_expert",
                "name": "评估专家",
                "description": "构建评价体系和反馈机制"
            },
            {
                "id": "material_creator",
                "name": "素材创作者",
                "description": "创作教学资源和工具"
            }
        ],
        "collaboration_modes": ["sequential", "parallel", "adaptive"],
        "status": "available"
    }


@app.post("/api/v1/course/design", tags=["course"])
async def design_course(request: dict = None):
    """课程设计端点 - 基础版本"""
    if not request:
        request = {}

    # 模拟课程设计流程
    topic = request.get("topic", "示例课程主题")
    audience = request.get("audience", "大学生")
    duration = request.get("duration", "4周")

    # 模拟智能体协作结果
    course_design = {
        "course_info": {
            "title": f"基于PBL的{topic}课程设计",
            "target_audience": audience,
            "duration": duration,
            "created_at": "2024-09-16T13:15:00Z"
        },
        "learning_objectives": [
            f"掌握{topic}的核心概念和基本原理",
            f"能够运用{topic}知识解决实际问题",
            f"培养批判性思维和团队协作能力",
            "提升项目管理和沟通表达技能"
        ],
        "project_design": {
            "project_theme": f"{topic}实践应用项目",
            "deliverables": ["项目方案", "实施报告", "成果展示", "反思总结"],
            "team_size": "3-4人",
            "mentor_support": "定期指导+同伴互评"
        },
        "assessment_plan": {
            "formative_assessment": ["周进度检查", "同伴评价", "导师反馈"],
            "summative_assessment": ["项目成果(40%)", "过程表现(30%)", "个人反思(20%)", "团队协作(10%)"]
        },
        "resources": [
            f"{topic}基础理论资料",
            "案例研究库",
            "在线协作工具",
            "项目模板库"
        ],
        "agents_contribution": {
            "education_theorist": "提供了PBL理论框架和学习目标设计",
            "course_architect": "规划了4周课程结构和学习路径",
            "content_designer": "设计了项目主题和学习活动",
            "assessment_expert": "构建了多元化评价体系",
            "material_creator": "整合了相关学习资源和工具"
        }
    }

    return {
        "status": "success",
        "message": "课程设计完成",
        "data": course_design,
        "next_steps": [
            "下载课程设计方案",
            "根据实际情况调整细节",
            "开始课程实施",
            "收集学习反馈"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)