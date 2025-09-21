"""
向量数据库工具模块
提供ChromaDB连接和向量操作
"""

import logging
from typing import Any, Dict, List, Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from ..core.config import settings


logger = logging.getLogger(__name__)


class VectorStoreManager:
    """向量存储管理器"""

    def __init__(self):
        self.client: Optional[Any] = None
        self.collection: Optional[Any] = None

    async def init_chroma(self):
        """初始化ChromaDB"""
        if not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ChromaDB未安装，向量功能将被禁用")
            return

        try:
            # 创建ChromaDB客户端
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(settings.DATA_DIR / "chroma")
            ))

            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="pbl_courses",
                metadata={"description": "PBL课程向量存储"}
            )

            logger.info("✅ ChromaDB初始化成功")

        except Exception as e:
            logger.warning(f"⚠️ ChromaDB初始化失败: {e}")
            self.client = None
            self.collection = None

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """添加文档到向量库"""
        if not self.collection:
            return False

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            logger.error(f"向量文档添加失败: {e}")
            return False

    async def search_similar(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            # 格式化结果
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else str(i)
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []

    async def delete_documents(self, ids: List[str]) -> bool:
        """删除文档"""
        if not self.collection:
            return False

        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            logger.error(f"向量文档删除失败: {e}")
            return False


# 全局向量存储管理器实例
vector_store_manager = VectorStoreManager()


async def init_chroma():
    """初始化ChromaDB"""
    await vector_store_manager.init_chroma()


async def add_course_to_vector_store(
    course_id: str,
    course_content: str,
    metadata: Dict[str, Any]
) -> bool:
    """添加课程到向量库"""
    return await vector_store_manager.add_documents(
        documents=[course_content],
        metadatas=[metadata],
        ids=[course_id]
    )


async def search_similar_courses(
    query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """搜索相似课程"""
    return await vector_store_manager.search_similar(
        query=query,
        n_results=limit
    )