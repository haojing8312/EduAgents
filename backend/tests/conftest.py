"""
测试配置和共享fixtures
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.base import Base

# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)
TestSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """数据库会话fixture"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """测试客户端fixture"""

    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    """同步测试客户端"""
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Redis测试客户端"""
    client = redis.from_url("redis://localhost:6379/15")  # 使用测试数据库
    await client.flushdb()  # 清空测试数据库
    yield client
    await client.flushdb()
    await client.close()


@pytest.fixture
def mock_ai_service():
    """模拟AI服务"""
    mock = MagicMock()
    mock.generate_response = AsyncMock(return_value="Mock AI response")
    mock.analyze_content = AsyncMock(
        return_value={"sentiment": "positive", "score": 0.8}
    )
    return mock


@pytest.fixture
def mock_websocket():
    """模拟WebSocket连接"""
    mock = MagicMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock()
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
    }


@pytest.fixture
def sample_course_data():
    """示例课程数据"""
    return {
        "title": "测试PBL课程",
        "description": "这是一个测试用的PBL课程",
        "subject": "计算机科学",
        "grade_level": "高中",
        "duration_weeks": 12,
        "learning_objectives": [
            "掌握Python编程基础",
            "学会项目管理方法",
            "培养团队协作能力",
        ],
    }


@pytest.fixture
def sample_project_data():
    """示例项目数据"""
    return {
        "title": "智能家居系统设计",
        "description": "设计并实现一个智能家居控制系统",
        "type": "technology",
        "complexity_level": "intermediate",
        "estimated_hours": 40,
        "required_skills": ["Python", "IoT", "UI设计"],
    }


# 性能测试相关fixtures
@pytest.fixture
def performance_thresholds():
    """性能基准阈值"""
    return {
        "api_response_time": 200,  # ms
        "database_query_time": 50,  # ms
        "ai_response_time": 5000,  # ms
        "websocket_latency": 100,  # ms
    }


# 并发测试fixtures
@pytest.fixture
def concurrent_users():
    """并发用户数量"""
    return 10


# 安全测试fixtures
@pytest.fixture
def malicious_inputs():
    """恶意输入数据"""
    return [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "{{7*7}}",
        "../../../etc/passwd",
        "javascript:alert(1)",
    ]


# 测试标记
def pytest_configure(config):
    """配置测试标记"""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")


# 测试钩子
def pytest_runtest_setup(item):
    """测试运行前的设置"""
    # 设置测试环境变量
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "ERROR"


def pytest_runtest_teardown(item):
    """测试运行后的清理"""
    # 清理环境变量
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
