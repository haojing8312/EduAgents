"""
PBL智能助手 - 简化版FastAPI应用
用于测试和基础功能验证
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# 只导入基础路由
from app.api.v1.health import router as health_router
from app.api.v1.agents import router as agents_router
from app.api.v1.websocket import router as websocket_router

from app.core.config import settings
from app.core.exceptions import (
    AgentException,
    AuthenticationException,
    ValidationException,
)
from app.utils.cache import init_redis
from app.utils.logger import setup_logging
from app.utils.vector_store import init_chroma


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger = logging.getLogger(__name__)
    logger.info("🚀 启动PBL智能助手后端服务...")

    try:
        # 初始化Redis缓存
        await init_redis()
        logger.info("✅ Redis缓存初始化完成")

        # 初始化ChromaDB向量数据库
        await init_chroma()
        logger.info("✅ ChromaDB向量数据库初始化完成")

        logger.info("🎉 所有服务初始化完成，系统准备就绪")

    except Exception as e:
        logger.error(f"❌ 服务初始化失败: {e}")
        raise

    yield

    # 关闭时清理
    logger.info("🛑 正在关闭PBL智能助手后端服务...")


# 创建FastAPI应用实例
app = FastAPI(
    title="PBL智能助手 API",
    description="""
    ## AI时代PBL课程设计智能助手后端API

    基于FastAPI构建的高性能后端服务，集成多智能体协作框架，
    为PBL（项目式学习）课程设计提供智能化支持。

    ### 核心特性
    - 🤖 **5个专业智能体协同工作**
    - ⚡ **高性能异步API**
    - 🔄 **实时WebSocket通信**
    - 🧠 **LangGraph智能体编排**
    - 📊 **多层数据存储方案**
    - 🔒 **企业级安全认证**

    ### AI时代智能体团队
    - **教育理论专家**: AI时代教育理论基础和框架设计
    - **课程架构师**: 面向AI时代能力的课程结构设计
    - **内容设计师**: AI时代场景化学习内容创作
    - **评估专家**: AI时代核心能力评价体系设计
    - **素材创作者**: AI时代数字化资源生成
    """,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 简化版本允许所有来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)

# 压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)


# 全局异常处理器
@app.exception_handler(AgentException)
async def agent_exception_handler(request: Request, exc: AgentException):
    """智能体异常处理"""
    logger.error(
        f"智能体异常: {exc.detail}",
        extra={
            "agent_type": exc.agent_type,
            "error_code": exc.error_code,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "agent_error",
            "message": exc.detail,
            "agent_type": exc.agent_type,
            "error_code": exc.error_code,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """数据验证异常处理"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": exc.detail,
            "field": exc.field,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(AuthenticationException)
async def auth_exception_handler(request: Request, exc: AuthenticationException):
    """认证异常处理"""
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_error",
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.exception(
        "未处理的异常",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "服务器内部错误",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# 注册API路由
app.include_router(health_router, prefix="/api", tags=["健康检查"])
app.include_router(agents_router, prefix="/api/v1", tags=["智能体"])
app.include_router(websocket_router, prefix="/api/v1/ws", tags=["实时通信"])


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """API根路径信息"""
    return {
        "service": "PBL智能助手 API",
        "version": "1.0.0",
        "status": "running",
        "documentation": (
            "/docs" if settings.ENVIRONMENT != "production" else "disabled"
        ),
        "agents": {
            "education_theorist": "AI时代教育理论专家",
            "course_architect": "AI时代课程架构师",
            "content_designer": "AI时代内容设计师",
            "assessment_expert": "AI时代评估专家",
            "material_creator": "AI时代素材创作者",
        },
        "features": [
            "多智能体协作",
            "实时WebSocket通信",
            "高性能缓存",
            "向量语义搜索",
            "企业级安全",
        ],
    }


# 开发服务器启动
if __name__ == "__main__":
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info",
        access_log=True,
        workers=1 if settings.ENVIRONMENT == "development" else 4,
    )