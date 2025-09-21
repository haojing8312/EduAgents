"""
Redis缓存工具模块 - 增强版
提供异步Redis连接和智能缓存策略，优化AI智能体协作性能
"""

import json
import logging
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import pickle
import redis.asyncio as aioredis
from contextlib import asynccontextmanager

from .config import settings


logger = logging.getLogger(__name__)


class CacheKeyManager:
    """缓存键管理器 - 统一管理缓存键的命名规则"""

    # 缓存键前缀
    PREFIX_AGENT_RESULT = "agent:result"
    PREFIX_COURSE_DESIGN = "course:design"
    PREFIX_SESSION_STATE = "session:state"
    PREFIX_LLM_RESPONSE = "llm:response"
    PREFIX_USER_CONTEXT = "user:context"
    PREFIX_TEMPLATE = "template"
    PREFIX_EXPORT = "export"

    @staticmethod
    def agent_result_key(agent_id: str, requirement_hash: str) -> str:
        """智能体结果缓存键"""
        return f"{CacheKeyManager.PREFIX_AGENT_RESULT}:{agent_id}:{requirement_hash}"

    @staticmethod
    def course_design_key(session_id: str) -> str:
        """课程设计缓存键"""
        return f"{CacheKeyManager.PREFIX_COURSE_DESIGN}:{session_id}"

    @staticmethod
    def session_state_key(session_id: str) -> str:
        """会话状态缓存键"""
        return f"{CacheKeyManager.PREFIX_SESSION_STATE}:{session_id}"

    @staticmethod
    def llm_response_key(prompt_hash: str, model: str) -> str:
        """LLM响应缓存键"""
        return f"{CacheKeyManager.PREFIX_LLM_RESPONSE}:{model}:{prompt_hash}"

    @staticmethod
    def user_context_key(user_id: str) -> str:
        """用户上下文缓存键"""
        return f"{CacheKeyManager.PREFIX_USER_CONTEXT}:{user_id}"

    @staticmethod
    def template_key(template_type: str, template_id: str) -> str:
        """模板缓存键"""
        return f"{CacheKeyManager.PREFIX_TEMPLATE}:{template_type}:{template_id}"

    @staticmethod
    def export_key(course_id: str, format_type: str) -> str:
        """导出文件缓存键"""
        return f"{CacheKeyManager.PREFIX_EXPORT}:{course_id}:{format_type}"

    @staticmethod
    def hash_content(content: Union[str, Dict, List]) -> str:
        """生成内容的哈希值"""
        if isinstance(content, (dict, list)):
            content = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode('utf-8')).hexdigest()


class SmartCacheManager:
    """智能缓存管理器 - 针对AI协作场景优化"""

    def __init__(self):
        self.general_redis: Optional[aioredis.Redis] = None
        self.cache_redis: Optional[aioredis.Redis] = None
        self.session_redis: Optional[aioredis.Redis] = None
        self.initialized = False

    async def init_redis_connections(self):
        """初始化多个Redis连接"""
        try:
            # 通用Redis连接 (DB 0)
            self.general_redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )

            # 缓存专用Redis连接 (DB 1)
            self.cache_redis = aioredis.from_url(
                settings.REDIS_CACHE_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=30
            )

            # 会话专用Redis连接 (DB 2)
            self.session_redis = aioredis.from_url(
                settings.REDIS_SESSION_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )

            # 测试所有连接
            await self.general_redis.ping()
            await self.cache_redis.ping()
            await self.session_redis.ping()

            self.initialized = True
            logger.info("✅ Redis多数据库连接初始化成功")

        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败: {e}")
            self.initialized = False

    def _get_redis_by_type(self, cache_type: str) -> Optional[aioredis.Redis]:
        """根据缓存类型获取对应的Redis连接"""
        if not self.initialized:
            return None

        if cache_type in ["session", "websocket"]:
            return self.session_redis
        elif cache_type in ["cache", "agent", "llm", "template", "export"]:
            return self.cache_redis
        else:
            return self.general_redis

    async def get(self, key: str, cache_type: str = "cache") -> Optional[Any]:
        """获取缓存值"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return None

        try:
            value = await redis_conn.get(key)
            if value is None:
                return None

            # 尝试解析JSON，失败则返回原始字符串
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value

        except Exception as e:
            logger.error(f"缓存获取失败 [{key}]: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = None,
        cache_type: str = "cache"
    ) -> bool:
        """设置缓存值"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return False

        try:
            # 自动选择序列化方式
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            else:
                serialized_value = str(value)

            # 使用配置的默认过期时间
            if expire is None:
                expire = self._get_default_ttl(cache_type)

            await redis_conn.set(key, serialized_value, ex=expire)
            logger.debug(f"缓存设置成功 [{key}] TTL: {expire}s")
            return True

        except Exception as e:
            logger.error(f"缓存设置失败 [{key}]: {e}")
            return False

    def _get_default_ttl(self, cache_type: str) -> int:
        """根据缓存类型获取默认TTL"""
        ttl_mapping = {
            "session": settings.CACHE_TTL_SHORT,      # 5分钟
            "agent": settings.CACHE_TTL_MEDIUM,       # 30分钟
            "llm": settings.CACHE_TTL_LONG,           # 1小时
            "template": settings.CACHE_TTL_LONG * 24, # 24小时
            "export": settings.CACHE_TTL_MEDIUM,      # 30分钟
            "cache": settings.CACHE_TTL_MEDIUM        # 默认30分钟
        }
        return ttl_mapping.get(cache_type, settings.CACHE_TTL_MEDIUM)

    async def delete(self, key: str, cache_type: str = "cache") -> bool:
        """删除缓存"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return False

        try:
            await redis_conn.delete(key)
            logger.debug(f"缓存删除成功 [{key}]")
            return True
        except Exception as e:
            logger.error(f"缓存删除失败 [{key}]: {e}")
            return False

    async def delete_pattern(self, pattern: str, cache_type: str = "cache") -> int:
        """批量删除匹配模式的缓存键"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return 0

        try:
            keys = await redis_conn.keys(pattern)
            if keys:
                deleted_count = await redis_conn.delete(*keys)
                logger.info(f"批量删除缓存 [{pattern}]: {deleted_count}个键")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"批量删除缓存失败 [{pattern}]: {e}")
            return 0

    async def exists(self, key: str, cache_type: str = "cache") -> bool:
        """检查缓存是否存在"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return False

        try:
            return bool(await redis_conn.exists(key))
        except Exception as e:
            logger.error(f"缓存存在性检查失败 [{key}]: {e}")
            return False

    async def get_ttl(self, key: str, cache_type: str = "cache") -> Optional[int]:
        """获取缓存剩余过期时间"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return None

        try:
            ttl = await redis_conn.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"获取TTL失败 [{key}]: {e}")
            return None

    async def extend_ttl(self, key: str, seconds: int, cache_type: str = "cache") -> bool:
        """延长缓存过期时间"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            return False

        try:
            return bool(await redis_conn.expire(key, seconds))
        except Exception as e:
            logger.error(f"延长TTL失败 [{key}]: {e}")
            return False

    @asynccontextmanager
    async def pipeline(self, cache_type: str = "cache"):
        """Redis管道上下文管理器"""
        redis_conn = self._get_redis_by_type(cache_type)
        if not redis_conn:
            yield None
            return

        pipe = redis_conn.pipeline()
        try:
            yield pipe
            await pipe.execute()
        except Exception as e:
            logger.error(f"管道执行失败: {e}")
            await pipe.reset()

    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "initialized": self.initialized,
            "connections": {},
            "memory_usage": {},
            "key_counts": {}
        }

        if not self.initialized:
            return stats

        try:
            # 检查各连接状态
            for name, redis_conn in [
                ("general", self.general_redis),
                ("cache", self.cache_redis),
                ("session", self.session_redis)
            ]:
                if redis_conn:
                    try:
                        await redis_conn.ping()
                        info = await redis_conn.info("memory")
                        stats["connections"][name] = "connected"
                        stats["memory_usage"][name] = info.get("used_memory_human", "unknown")

                        # 获取键数量
                        db_size = await redis_conn.dbsize()
                        stats["key_counts"][name] = db_size

                    except Exception as e:
                        stats["connections"][name] = f"error: {e}"

        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")

        return stats

    async def close_all_connections(self):
        """关闭所有Redis连接"""
        for redis_conn in [self.general_redis, self.cache_redis, self.session_redis]:
            if redis_conn:
                try:
                    await redis_conn.close()
                except Exception as e:
                    logger.error(f"关闭Redis连接失败: {e}")

        self.initialized = False
        logger.info("所有Redis连接已关闭")


class AgentResultCache:
    """智能体结果专用缓存类"""

    def __init__(self, cache_manager: SmartCacheManager):
        self.cache_manager = cache_manager

    async def get_agent_result(self, agent_id: str, course_requirement: str) -> Optional[Dict[str, Any]]:
        """获取智能体执行结果"""
        requirement_hash = CacheKeyManager.hash_content(course_requirement)
        key = CacheKeyManager.agent_result_key(agent_id, requirement_hash)

        result = await self.cache_manager.get(key, cache_type="agent")
        if result:
            logger.info(f"🎯 智能体结果缓存命中: {agent_id}")
        return result

    async def cache_agent_result(
        self,
        agent_id: str,
        course_requirement: str,
        result: Dict[str, Any]
    ) -> bool:
        """缓存智能体执行结果"""
        requirement_hash = CacheKeyManager.hash_content(course_requirement)
        key = CacheKeyManager.agent_result_key(agent_id, requirement_hash)

        # 为结果添加缓存元数据
        cached_result = {
            "agent_id": agent_id,
            "requirement_hash": requirement_hash,
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "cache_version": "1.0"
        }

        success = await self.cache_manager.set(
            key,
            cached_result,
            cache_type="agent"
        )

        if success:
            logger.info(f"💾 智能体结果已缓存: {agent_id}")

        return success

    async def invalidate_agent_cache(self, agent_id: str) -> int:
        """清除特定智能体的所有缓存"""
        pattern = f"{CacheKeyManager.PREFIX_AGENT_RESULT}:{agent_id}:*"
        return await self.cache_manager.delete_pattern(pattern, cache_type="agent")


class SessionStateCache:
    """会话状态专用缓存类"""

    def __init__(self, cache_manager: SmartCacheManager):
        self.cache_manager = cache_manager

    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        key = CacheKeyManager.session_state_key(session_id)
        return await self.cache_manager.get(key, cache_type="session")

    async def update_session_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """更新会话状态"""
        key = CacheKeyManager.session_state_key(session_id)

        # 为状态添加时间戳
        state_with_timestamp = {
            **state,
            "updated_at": datetime.now().isoformat(),
            "session_id": session_id
        }

        return await self.cache_manager.set(
            key,
            state_with_timestamp,
            cache_type="session"
        )

    async def extend_session(self, session_id: str, seconds: int = None) -> bool:
        """延长会话有效期"""
        key = CacheKeyManager.session_state_key(session_id)
        if seconds is None:
            seconds = settings.CACHE_TTL_SHORT * 2  # 默认延长10分钟

        return await self.cache_manager.extend_ttl(key, seconds, cache_type="session")

    async def end_session(self, session_id: str) -> bool:
        """结束会话"""
        key = CacheKeyManager.session_state_key(session_id)
        return await self.cache_manager.delete(key, cache_type="session")


class LLMResponseCache:
    """LLM响应专用缓存类"""

    def __init__(self, cache_manager: SmartCacheManager):
        self.cache_manager = cache_manager

    async def get_llm_response(self, prompt: str, model: str) -> Optional[str]:
        """获取LLM响应缓存"""
        prompt_hash = CacheKeyManager.hash_content(prompt)
        key = CacheKeyManager.llm_response_key(prompt_hash, model)

        cached_response = await self.cache_manager.get(key, cache_type="llm")
        if cached_response:
            logger.info(f"🤖 LLM响应缓存命中: {model}")
            return cached_response.get("response") if isinstance(cached_response, dict) else cached_response

        return None

    async def cache_llm_response(self, prompt: str, model: str, response: str) -> bool:
        """缓存LLM响应"""
        prompt_hash = CacheKeyManager.hash_content(prompt)
        key = CacheKeyManager.llm_response_key(prompt_hash, model)

        cached_data = {
            "prompt_hash": prompt_hash,
            "model": model,
            "response": response,
            "cached_at": datetime.now().isoformat(),
            "token_count": len(response.split()) if response else 0
        }

        success = await self.cache_manager.set(
            key,
            cached_data,
            cache_type="llm"
        )

        if success:
            logger.info(f"💾 LLM响应已缓存: {model}")

        return success


# 全局缓存管理器实例
smart_cache_manager = SmartCacheManager()

# 专用缓存实例
agent_cache: Optional[AgentResultCache] = None
session_cache: Optional[SessionStateCache] = None
llm_cache: Optional[LLMResponseCache] = None


async def init_enhanced_redis():
    """初始化增强版Redis缓存系统"""
    global agent_cache, session_cache, llm_cache

    await smart_cache_manager.init_redis_connections()

    if smart_cache_manager.initialized:
        agent_cache = AgentResultCache(smart_cache_manager)
        session_cache = SessionStateCache(smart_cache_manager)
        llm_cache = LLMResponseCache(smart_cache_manager)
        logger.info("🚀 增强版Redis缓存系统初始化完成")
    else:
        logger.warning("⚠️ Redis缓存系统初始化失败，将使用内存缓存")


async def close_enhanced_redis():
    """关闭增强版Redis缓存系统"""
    await smart_cache_manager.close_all_connections()


# 兼容性函数 - 保持向后兼容
async def get_cache(key: str) -> Optional[Any]:
    """获取缓存（兼容性函数）"""
    return await smart_cache_manager.get(key)


async def set_cache(key: str, value: Any, expire: int = None) -> bool:
    """设置缓存（兼容性函数）"""
    return await smart_cache_manager.set(key, value, expire)


async def delete_cache(key: str) -> bool:
    """删除缓存（兼容性函数）"""
    return await smart_cache_manager.delete(key)


# 统计和监控函数
async def get_cache_health() -> Dict[str, Any]:
    """获取缓存系统健康状态"""
    stats = await smart_cache_manager.get_cache_stats()

    return {
        "status": "healthy" if stats["initialized"] else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "details": stats
    }