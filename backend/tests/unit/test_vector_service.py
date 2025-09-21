"""
测试向量数据库服务
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import uuid

from app.services.vector_service import (
    EmbeddingManager,
    AdvancedVectorService,
    vector_service,
    add_course_to_vectors,
    search_similar_courses,
    enhance_agent_with_knowledge,
    get_vector_store_health
)


class TestEmbeddingManager:
    """嵌入管理器测试"""

    def test_embedding_manager_initialization(self):
        """测试嵌入管理器初始化"""
        # 模拟没有API密钥的情况
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = None

            manager = EmbeddingManager()
            assert isinstance(manager.embedding_functions, dict)

    def test_get_embedding_function_auto(self):
        """测试自动选择嵌入函数"""
        manager = EmbeddingManager()

        # 模拟有可用的嵌入函数
        manager.embedding_functions = {
            "openai": MagicMock(),
            "sentence_transformers": MagicMock()
        }

        # 测试自动选择（优先OpenAI）
        func = manager.get_embedding_function("auto")
        assert func == manager.embedding_functions["openai"]

        # 测试只有SentenceTransformers时
        manager.embedding_functions = {"sentence_transformers": MagicMock()}
        func = manager.get_embedding_function("auto")
        assert func == manager.embedding_functions["sentence_transformers"]

    def test_get_embedding_function_specific(self):
        """测试获取特定嵌入函数"""
        manager = EmbeddingManager()
        mock_func = MagicMock()
        manager.embedding_functions = {"openai": mock_func}

        func = manager.get_embedding_function("openai")
        assert func == mock_func

        # 测试不存在的函数
        func = manager.get_embedding_function("nonexistent")
        assert func is None


class TestAdvancedVectorService:
    """高级向量服务测试"""

    @pytest_asyncio.fixture
    async def mock_vector_service(self):
        """模拟向量服务"""
        service = AdvancedVectorService()

        # 模拟ChromaDB客户端
        mock_client = MagicMock()
        mock_collection = MagicMock()

        service.client = mock_client
        service.collections = {
            "course_designs": mock_collection,
            "educational_knowledge": mock_collection,
            "agent_memories": mock_collection
        }
        service.initialized = True

        yield service

    @pytest.mark.asyncio
    async def test_vector_service_initialization(self):
        """测试向量服务初始化"""
        service = AdvancedVectorService()

        # 模拟ChromaDB不可用
        with patch('app.services.vector_service.CHROMADB_AVAILABLE', False):
            result = await service.initialize()
            assert result is False

        # 模拟ChromaDB可用
        with patch('app.services.vector_service.CHROMADB_AVAILABLE', True), \
             patch('chromadb.PersistentClient') as mock_client:

            mock_client.return_value = MagicMock()

            # 模拟初始化集合成功
            with patch.object(service, '_initialize_collections') as mock_init:
                mock_init.return_value = None
                result = await service.initialize()
                assert result is True
                assert service.initialized is True

    @pytest.mark.asyncio
    async def test_add_course_design(self, mock_vector_service):
        """测试添加课程设计"""
        service = mock_vector_service
        course_id = str(uuid.uuid4())
        course_data = {
            "course_requirement": "AI基础课程设计",
            "agents_data": {
                "education_theorist": {
                    "content": "基于建构主义理论的课程设计框架"
                },
                "course_architect": {
                    "result": "8周课程结构，包含理论学习和实践项目"
                }
            },
            "session_id": "test-session-123"
        }

        # 模拟集合操作
        mock_collection = service.collections["course_designs"]
        mock_collection.add.return_value = None

        # 模拟缓存
        with patch('app.services.vector_service.smart_cache_manager') as mock_cache:
            mock_cache.initialized = True
            mock_cache.set.return_value = True

            result = await service.add_course_design(course_id, course_data)
            assert result is True
            mock_collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_similar_courses(self, mock_vector_service):
        """测试搜索相似课程"""
        service = mock_vector_service
        query = "Python编程入门课程"

        # 模拟搜索结果
        mock_results = {
            "documents": [["课程1内容", "课程2内容"]],
            "distances": [[0.1, 0.3]],
            "ids": [["course1", "course2"]],
            "metadatas": [[
                {"course_id": "course1", "subject": "编程"},
                {"course_id": "course2", "subject": "计算机科学"}
            ]]
        }

        mock_collection = service.collections["course_designs"]
        mock_collection.query.return_value = mock_results

        # 模拟缓存
        with patch('app.services.vector_service.smart_cache_manager') as mock_cache:
            mock_cache.initialized = True
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True

            results = await service.search_similar_courses(query, limit=2)
            assert len(results) == 2
            assert results[0]["course_id"] == "course1"
            assert results[0]["similarity_score"] > results[1]["similarity_score"]

    @pytest.mark.asyncio
    async def test_add_educational_knowledge(self, mock_vector_service):
        """测试添加教育知识"""
        service = mock_vector_service
        knowledge_id = "bloom_taxonomy"
        content = "布鲁姆教育目标分类法是一个经典的教育理论框架..."
        knowledge_type = "theory"

        mock_collection = service.collections["educational_knowledge"]
        mock_collection.add.return_value = None

        result = await service.add_educational_knowledge(
            knowledge_id, content, knowledge_type, source="academic", tags=["pedagogy", "assessment"]
        )
        assert result is True
        mock_collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, mock_vector_service):
        """测试搜索知识库"""
        service = mock_vector_service
        query = "项目式学习评估方法"
        knowledge_types = ["methodology", "assessment"]

        # 模拟搜索结果
        mock_results = {
            "documents": [["PBL评估框架内容"]],
            "distances": [[0.2]],
            "ids": [["pbl_assessment"]],
            "metadatas": [[{"knowledge_type": "methodology", "source": "research"}]]
        }

        mock_collection = service.collections["educational_knowledge"]
        mock_collection.query.return_value = mock_results

        results = await service.search_knowledge_base(query, knowledge_types, limit=5)
        assert len(results) == 1
        assert results[0]["knowledge_id"] == "pbl_assessment"
        assert "relevance_score" in results[0]

    @pytest.mark.asyncio
    async def test_store_agent_memory(self, mock_vector_service):
        """测试存储智能体记忆"""
        service = mock_vector_service
        agent_id = "education_theorist"
        experience_type = "success"
        content = "成功设计了一个基于STEAM理念的PBL课程"
        success_score = 0.9
        context = {"subject": "STEAM", "grade": "high_school"}

        mock_collection = service.collections["agent_memories"]
        mock_collection.add.return_value = None

        result = await service.store_agent_memory(
            agent_id, experience_type, content, success_score, context
        )
        assert result is True
        mock_collection.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_agent_patterns(self, mock_vector_service):
        """测试检索智能体模式"""
        service = mock_vector_service
        agent_id = "education_theorist"
        context_query = "STEAM课程设计"
        min_success_score = 0.8

        # 模拟搜索结果
        mock_results = {
            "documents": [["成功的STEAM课程设计经验"]],
            "distances": [[0.15]],
            "metadatas": [[{
                "success_score": 0.9,
                "context": {"subject": "STEAM", "grade": "high_school"}
            }]]
        }

        mock_collection = service.collections["agent_memories"]
        mock_collection.query.return_value = mock_results

        results = await service.retrieve_agent_patterns(
            agent_id, context_query, min_success_score, limit=3
        )
        assert len(results) == 1
        assert results[0]["success_score"] == 0.9
        assert "pattern" in results[0]
        assert "relevance" in results[0]

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, mock_vector_service):
        """测试获取集合统计"""
        service = mock_vector_service

        # 模拟集合统计
        for collection_name, collection in service.collections.items():
            collection.count.return_value = 100
            collection.metadata = {"description": f"测试集合{collection_name}"}

        stats = await service.get_collection_stats()
        assert stats["initialized"] is True
        assert stats["total_documents"] == 300  # 3个集合，每个100个文档
        assert "course_designs" in stats["collections"]
        assert stats["collections"]["course_designs"]["document_count"] == 100

    @pytest.mark.asyncio
    async def test_vector_service_uninitialized(self):
        """测试未初始化的向量服务"""
        service = AdvancedVectorService()
        assert service.initialized is False

        # 测试未初始化时的操作应该返回False或空
        result = await service.add_course_design("test", {})
        assert result is False

        results = await service.search_similar_courses("test")
        assert results == []

        stats = await service.get_collection_stats()
        assert stats["initialized"] is False


class TestVectorServiceIntegration:
    """向量服务集成测试"""

    @pytest.mark.asyncio
    async def test_global_vector_service(self):
        """测试全局向量服务实例"""
        assert vector_service is not None
        assert isinstance(vector_service, AdvancedVectorService)

    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """测试便利函数"""
        course_id = "test-course"
        course_data = {"course_requirement": "测试课程"}

        # 模拟向量服务
        with patch.object(vector_service, 'add_course_design') as mock_add:
            mock_add.return_value = True
            result = await add_course_to_vectors(course_id, course_data)
            assert result is True
            mock_add.assert_called_once_with(course_id, course_data, None)

        # 测试搜索函数
        with patch.object(vector_service, 'search_similar_courses') as mock_search:
            mock_search.return_value = [{"course_id": "test"}]
            results = await search_similar_courses("测试查询", limit=5)
            assert len(results) == 1
            mock_search.assert_called_once_with("测试查询", 5, None)

    @pytest.mark.asyncio
    async def test_enhance_agent_with_knowledge(self):
        """测试智能体知识增强"""
        agent_id = "test_agent"
        context_query = "测试查询"

        with patch.object(vector_service, 'search_knowledge_base') as mock_knowledge, \
             patch.object(vector_service, 'retrieve_agent_patterns') as mock_patterns:

            mock_knowledge.return_value = [{"knowledge_id": "test_knowledge"}]
            mock_patterns.return_value = [{"pattern": "test_pattern"}]

            results = await enhance_agent_with_knowledge(agent_id, context_query)
            assert "knowledge" in results
            assert "patterns" in results
            assert len(results["knowledge"]) == 1
            assert len(results["patterns"]) == 1

    @pytest.mark.asyncio
    async def test_get_vector_store_health(self):
        """测试向量存储健康检查"""
        with patch.object(vector_service, 'get_collection_stats') as mock_stats:
            mock_stats.return_value = {
                "initialized": True,
                "total_documents": 500,
                "collections": {
                    "course_designs": {"document_count": 200},
                    "educational_knowledge": {"document_count": 150},
                    "agent_memories": {"document_count": 150}
                }
            }

            health = await get_vector_store_health()
            assert health["initialized"] is True
            assert health["total_documents"] == 500

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_vector_service):
        """测试错误处理"""
        service = mock_vector_service

        # 模拟集合操作异常
        mock_collection = service.collections["course_designs"]
        mock_collection.add.side_effect = Exception("模拟错误")

        result = await service.add_course_design("test", {"requirement": "test"})
        assert result is False

        # 模拟搜索异常
        mock_collection.query.side_effect = Exception("搜索错误")
        results = await service.search_similar_courses("test")
        assert results == []


@pytest.mark.asyncio
async def test_embedding_fallback_strategy():
    """测试嵌入策略降级"""
    manager = EmbeddingManager()

    # 测试没有任何嵌入函数时
    manager.embedding_functions = {}
    func = manager.get_embedding_function("auto")
    assert func is None

    # 测试只有部分嵌入函数可用时
    manager.embedding_functions = {"sentence_transformers": MagicMock()}
    func = manager.get_embedding_function("auto")
    assert func == manager.embedding_functions["sentence_transformers"]


@pytest.mark.asyncio
async def test_content_extraction_and_processing():
    """测试内容提取和处理"""
    service = AdvancedVectorService()

    # 测试复杂课程数据的内容提取
    complex_course_data = {
        "course_requirement": "高中AI课程设计",
        "agents_data": {
            "education_theorist": {
                "content": "基于建构主义的课程理论框架",
                "result": {"theory": "constructivism", "approach": "PBL"}
            },
            "course_architect": {
                "result": "8周课程结构，包含4个主要项目模块"
            }
        },
        "session_id": "test-123",
        "ai_generated": True
    }

    # 由于这是私有方法测试，我们可以通过add_course_design来间接测试
    service.initialized = True
    service.collections = {"course_designs": MagicMock()}

    result = await service.add_course_design("test-course", complex_course_data)
    # 验证内容被正确处理和存储