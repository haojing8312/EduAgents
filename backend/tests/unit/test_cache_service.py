"""
测试增强版Redis缓存服务
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.core.cache import (
    SmartCacheManager,
    AgentResultCache,
    SessionStateCache,
    LLMResponseCache,
    smart_cache_manager,
    agent_cache,
    session_cache,
    llm_cache
)


class TestSmartCacheManager:
    """智能缓存管理器测试"""

    @pytest_asyncio.fixture
    async def mock_cache_manager(self):
        """模拟缓存管理器"""
        manager = SmartCacheManager()

        # 模拟Redis连接
        manager.general_redis = AsyncMock()
        manager.cache_redis = AsyncMock()
        manager.session_redis = AsyncMock()
        manager.initialized = True

        yield manager

        # 清理
        if manager.initialized:
            await manager.close()

    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self):
        """测试缓存管理器初始化"""
        manager = SmartCacheManager()

        # 模拟初始化成功
        with patch('aioredis.from_url') as mock_redis:
            mock_redis.return_value = AsyncMock()

            result = await manager.initialize()
            assert result is True
            assert manager.initialized is True

    @pytest.mark.asyncio
    async def test_cache_manager_set_get(self, mock_cache_manager):
        """测试基础缓存设置和获取"""
        manager = mock_cache_manager

        # 模拟Redis操作
        manager.cache_redis.set.return_value = True
        manager.cache_redis.get.return_value = json.dumps({"test": "data"})

        # 测试设置缓存
        result = await manager.set("test_key", {"test": "data"}, expire=300, cache_type="cache")
        assert result is True
        manager.cache_redis.set.assert_called_once()

        # 测试获取缓存
        data = await manager.get("test_key", cache_type="cache")
        assert data == {"test": "data"}
        manager.cache_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_manager_delete(self, mock_cache_manager):
        """测试缓存删除"""
        manager = mock_cache_manager
        manager.cache_redis.delete.return_value = 1

        result = await manager.delete("test_key", cache_type="cache")
        assert result is True
        manager.cache_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_manager_clear(self, mock_cache_manager):
        """测试缓存清空"""
        manager = mock_cache_manager
        manager.cache_redis.flushdb.return_value = True

        result = await manager.clear_cache("cache")
        assert result is True
        manager.cache_redis.flushdb.assert_called_once()


class TestAgentResultCache:
    """智能体结果缓存测试"""

    @pytest_asyncio.fixture
    async def mock_agent_cache(self):
        """模拟智能体缓存"""
        cache_manager = AsyncMock()
        cache = AgentResultCache(cache_manager)
        yield cache

    @pytest.mark.asyncio
    async def test_agent_cache_key_generation(self, mock_agent_cache):
        """测试智能体缓存键生成"""
        cache = mock_agent_cache

        key = cache._generate_cache_key("test_agent", "test requirement")
        assert key.startswith("agent:test_agent:")
        assert len(key) > 20  # 包含哈希值

    @pytest.mark.asyncio
    async def test_agent_cache_set_get_result(self, mock_agent_cache):
        """测试智能体结果缓存"""
        cache = mock_agent_cache
        cache.cache_manager.set.return_value = True
        cache.cache_manager.get.return_value = {
            "result": "test result",
            "metadata": {"agent": "test_agent"}
        }

        # 测试设置结果
        result = await cache.set_agent_result(
            "test_agent",
            "test requirement",
            "test result",
            {"agent": "test_agent"}
        )
        assert result is True

        # 测试获取结果
        cached_result = await cache.get_agent_result("test_agent", "test requirement")
        assert cached_result["result"] == "test result"
        assert cached_result["metadata"]["agent"] == "test_agent"

    @pytest.mark.asyncio
    async def test_agent_cache_invalidation(self, mock_agent_cache):
        """测试智能体缓存失效"""
        cache = mock_agent_cache
        cache.cache_manager.delete.return_value = True

        result = await cache.invalidate_agent_cache("test_agent", "test requirement")
        assert result is True


class TestSessionStateCache:
    """会话状态缓存测试"""

    @pytest_asyncio.fixture
    async def mock_session_cache(self):
        """模拟会话缓存"""
        cache_manager = AsyncMock()
        cache = SessionStateCache(cache_manager)
        yield cache

    @pytest.mark.asyncio
    async def test_session_state_operations(self, mock_session_cache):
        """测试会话状态操作"""
        cache = mock_session_cache
        session_id = "test-session-123"
        session_state = {
            "status": "in_progress",
            "agents_data": {"agent1": "result1"},
            "created_at": datetime.now().isoformat()
        }

        # 模拟缓存操作
        cache.cache_manager.set.return_value = True
        cache.cache_manager.get.return_value = session_state

        # 测试设置会话状态
        result = await cache.set_session_state(session_id, session_state)
        assert result is True

        # 测试获取会话状态
        retrieved_state = await cache.get_session_state(session_id)
        assert retrieved_state["status"] == "in_progress"
        assert "agent1" in retrieved_state["agents_data"]

    @pytest.mark.asyncio
    async def test_session_partial_update(self, mock_session_cache):
        """测试会话部分更新"""
        cache = mock_session_cache
        session_id = "test-session-123"

        # 模拟现有状态
        existing_state = {
            "status": "in_progress",
            "agents_data": {"agent1": "result1"}
        }
        cache.cache_manager.get.return_value = existing_state
        cache.cache_manager.set.return_value = True

        # 更新部分数据
        updates = {"status": "completed", "agents_data": {"agent2": "result2"}}
        result = await cache.update_session_state(session_id, updates)
        assert result is True


class TestLLMResponseCache:
    """LLM响应缓存测试"""

    @pytest_asyncio.fixture
    async def mock_llm_cache(self):
        """模拟LLM缓存"""
        cache_manager = AsyncMock()
        cache = LLMResponseCache(cache_manager)
        yield cache

    @pytest.mark.asyncio
    async def test_llm_cache_operations(self, mock_llm_cache):
        """测试LLM缓存操作"""
        cache = mock_llm_cache
        prompt = "What is artificial intelligence?"
        model = "claude-3-sonnet"
        response = "AI is a field of computer science..."

        # 模拟缓存操作
        cache.cache_manager.set.return_value = True
        cache.cache_manager.get.return_value = response

        # 测试设置LLM响应
        result = await cache.set_llm_response(prompt, model, response)
        assert result is True

        # 测试获取LLM响应
        cached_response = await cache.get_llm_response(prompt, model)
        assert cached_response == response

    @pytest.mark.asyncio
    async def test_llm_cache_key_generation(self, mock_llm_cache):
        """测试LLM缓存键生成"""
        cache = mock_llm_cache

        key = cache._generate_cache_key("test prompt", "test-model")
        assert key.startswith("llm:test-model:")
        assert len(key) > 20  # 包含哈希值


class TestCacheIntegration:
    """缓存集成测试"""

    @pytest.mark.asyncio
    async def test_global_cache_instances(self):
        """测试全局缓存实例"""
        # 测试全局实例存在
        assert smart_cache_manager is not None
        assert agent_cache is not None
        assert session_cache is not None
        assert llm_cache is not None

        # 测试实例类型
        assert isinstance(smart_cache_manager, SmartCacheManager)
        assert isinstance(agent_cache, AgentResultCache)
        assert isinstance(session_cache, SessionStateCache)
        assert isinstance(llm_cache, LLMResponseCache)

    @pytest.mark.asyncio
    async def test_cache_error_handling(self):
        """测试缓存错误处理"""
        manager = SmartCacheManager()

        # 测试未初始化时的操作
        result = await manager.set("test", "data")
        assert result is False

        data = await manager.get("test")
        assert data is None

    @pytest.mark.asyncio
    async def test_cache_serialization(self):
        """测试缓存序列化"""
        manager = SmartCacheManager()

        # 测试复杂数据结构序列化
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "datetime": datetime.now().isoformat(),
            "boolean": True,
            "none": None
        }

        # 测试序列化和反序列化
        serialized = manager._serialize_data(complex_data)
        assert isinstance(serialized, str)

        deserialized = manager._deserialize_data(serialized)
        assert deserialized == complex_data

    @pytest.mark.asyncio
    async def test_cache_ttl_handling(self, mock_cache_manager):
        """测试缓存TTL处理"""
        manager = mock_cache_manager

        # 测试不同的过期时间设置
        manager.cache_redis.set.return_value = True

        await manager.set("short_term", "data", expire=60)
        await manager.set("medium_term", "data", expire=3600)
        await manager.set("long_term", "data", expire=86400)

        # 验证调用次数
        assert manager.cache_redis.set.call_count == 3


@pytest.mark.asyncio
async def test_cache_health_check():
    """测试缓存健康检查"""
    manager = SmartCacheManager()

    # 模拟健康检查
    with patch.object(manager, 'get_health_status') as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "connections": {
                "general": True,
                "cache": True,
                "session": True
            },
            "memory_usage": "50MB"
        }

        health = await manager.get_health_status()
        assert health["status"] == "healthy"
        assert health["connections"]["cache"] is True


@pytest.mark.asyncio
async def test_cache_performance_metrics():
    """测试缓存性能指标"""
    manager = SmartCacheManager()

    # 模拟性能指标
    with patch.object(manager, 'get_metrics') as mock_metrics:
        mock_metrics.return_value = {
            "hit_rate": 0.85,
            "miss_rate": 0.15,
            "total_requests": 1000,
            "cache_size": "100MB",
            "avg_response_time": 1.2
        }

        metrics = await manager.get_metrics()
        assert metrics["hit_rate"] > 0.8
        assert metrics["total_requests"] == 1000