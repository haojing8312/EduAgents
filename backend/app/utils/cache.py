"""
Redis缓存工具模块
提供异步Redis连接和缓存操作
"""

import logging
from typing import Any, Optional
import redis.asyncio as aioredis

from ..core.config import settings


logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            # 测试连接
            await self.redis.ping()
            logger.info("✅ Redis连接初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ Redis连接失败: {e}")
            self.redis = None

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存值"""
        if not self.redis:
            return False
        try:
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False

    async def close(self):
        """关闭连接"""
        if self.redis:
            await self.redis.close()


# 全局缓存管理器实例
cache_manager = CacheManager()


async def init_redis():
    """初始化Redis"""
    await cache_manager.init_redis()


async def get_cache(key: str) -> Optional[Any]:
    """获取缓存"""
    return await cache_manager.get(key)


async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """设置缓存"""
    return await cache_manager.set(key, value, expire)


async def delete_cache(key: str) -> bool:
    """删除缓存"""
    return await cache_manager.delete(key)