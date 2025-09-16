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

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
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
async def design_course():
    """课程设计端点（简化版）"""
    return {
        "message": "课程设计功能正在开发中",
        "status": "coming_soon",
        "features": [
            "多智能体协作设计",
            "实时进度反馈",
            "个性化课程定制",
            "多格式导出支持"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)