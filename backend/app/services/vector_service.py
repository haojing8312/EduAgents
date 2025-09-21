"""
Enhanced Vector Database Service - ChromaDB Integration
Provides comprehensive vector storage, semantic search, and knowledge management for AI agents
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction, SentenceTransformerEmbeddingFunction
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

from app.core.config import settings
from app.core.cache import smart_cache_manager


logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages different embedding strategies for vector storage"""

    def __init__(self):
        self.embedding_functions = {}
        self._initialize_embedding_functions()

    def _initialize_embedding_functions(self):
        """Initialize available embedding functions"""
        try:
            # Try OpenAI embeddings (primary)
            if settings.OPENAI_API_KEY:
                try:
                    self.embedding_functions["openai"] = OpenAIEmbeddingFunction(
                        api_key=settings.OPENAI_API_KEY,
                        model_name=settings.OPENAI_EMBEDDING_MODEL
                    )
                    logger.info("✅ OpenAI embedding function initialized")
                except Exception as e:
                    logger.warning(f"⚠️ OpenAI embedding function failed: {e}")

            # Try Sentence Transformers (fallback)
            try:
                self.embedding_functions["sentence_transformers"] = SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
                logger.info("✅ SentenceTransformers embedding function initialized")
            except Exception as e:
                logger.warning(f"⚠️ SentenceTransformers embedding function failed: {e}")

            # If no embedding functions are available, use default
            if not self.embedding_functions:
                logger.warning("⚠️ No embedding functions available - using ChromaDB default")

        except Exception as e:
            logger.warning(f"⚠️ Embedding function initialization failed: {e}")

    def get_embedding_function(self, strategy: str = "auto"):
        """Get the best available embedding function"""
        if strategy == "auto":
            # Prefer OpenAI if available, fallback to SentenceTransformers
            return (
                self.embedding_functions.get("openai") or
                self.embedding_functions.get("sentence_transformers")
            )
        return self.embedding_functions.get(strategy)


class AdvancedVectorService:
    """
    Advanced vector database service with comprehensive features
    Supports multiple collections, smart embedding, and semantic search
    """

    def __init__(self):
        self.client: Optional[Any] = None
        self.collections: Dict[str, Any] = {}
        self.embedding_manager = EmbeddingManager()
        self.initialized = False

    async def initialize(self):
        """Initialize ChromaDB with enhanced configuration"""
        if not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ChromaDB not available - vector features disabled")
            return False

        try:
            # Create ChromaDB client with persistent storage (new API)
            import os
            chroma_dir = os.path.join(os.getcwd(), "data", "chroma")
            os.makedirs(chroma_dir, exist_ok=True)

            # Use the new PersistentClient API
            self.client = chromadb.PersistentClient(path=chroma_dir)

            # Initialize specialized collections
            await self._initialize_collections()

            self.initialized = True
            logger.info("🚀 Advanced ChromaDB vector service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            return False

    async def _initialize_collections(self):
        """Initialize specialized collections for different content types"""
        collection_configs = {
            "course_designs": {
                "description": "AI-generated course designs and curricula",
                "embedding_function": "openai"
            },
            "educational_knowledge": {
                "description": "Educational theories, methodologies, and best practices",
                "embedding_function": "openai"
            },
            "agent_memories": {
                "description": "Agent learning experiences and successful patterns",
                "embedding_function": "sentence_transformers"
            },
            "content_templates": {
                "description": "Reusable course content templates and components",
                "embedding_function": "openai"
            },
            "assessment_patterns": {
                "description": "Assessment strategies and evaluation frameworks",
                "embedding_function": "openai"
            }
        }

        for collection_name, config in collection_configs.items():
            try:
                embedding_function = self.embedding_manager.get_embedding_function(
                    config["embedding_function"]
                )

                # Create collection with or without embedding function
                if embedding_function:
                    collection = self.client.get_or_create_collection(
                        name=collection_name,
                        embedding_function=embedding_function,
                        metadata={
                            "description": config["description"],
                            "created_at": datetime.now().isoformat(),
                            "embedding_strategy": config["embedding_function"]
                        }
                    )
                else:
                    # Fallback to default embedding
                    collection = self.client.get_or_create_collection(
                        name=collection_name,
                        metadata={
                            "description": config["description"],
                            "created_at": datetime.now().isoformat(),
                            "embedding_strategy": "default"
                        }
                    )

                self.collections[collection_name] = collection
                logger.info(f"✅ Collection '{collection_name}' initialized")

            except Exception as e:
                logger.error(f"❌ Failed to initialize collection '{collection_name}': {e}")

    async def add_course_design(
        self,
        course_id: str,
        course_data: Dict[str, Any],
        agent_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a complete course design to the vector store"""
        if not self.initialized or "course_designs" not in self.collections:
            return False

        try:
            # Extract and combine text content for embedding
            content_parts = []

            # Core course information
            if "course_requirement" in course_data:
                content_parts.append(f"Course Requirement: {course_data['course_requirement']}")

            # Agent results
            if "agents_data" in course_data:
                for agent_id, agent_result in course_data["agents_data"].items():
                    if isinstance(agent_result, dict):
                        # Extract meaningful text from agent results
                        if "content" in agent_result:
                            content_parts.append(f"{agent_id}: {agent_result['content']}")
                        elif "result" in agent_result:
                            result_text = str(agent_result["result"])
                            if len(result_text) > 50:  # Only include substantial content
                                content_parts.append(f"{agent_id}: {result_text}")

            # Combine all content
            combined_content = "\n\n".join(content_parts)

            # Prepare metadata
            metadata = {
                "course_id": course_id,
                "created_at": datetime.now().isoformat(),
                "ai_generated": course_data.get("ai_generated", True),
                "agents_count": len(course_data.get("agents_data", {})),
                "content_length": len(combined_content),
                "session_id": course_data.get("session_id", "unknown")
            }

            # Add agent context if provided
            if agent_context:
                metadata.update({
                    f"agent_{k}": str(v) for k, v in agent_context.items()
                })

            # Add to collection
            collection = self.collections["course_designs"]
            collection.add(
                documents=[combined_content],
                metadatas=[metadata],
                ids=[course_id]
            )

            # Cache the vector operation result
            if smart_cache_manager.initialized:
                cache_key = f"vector:course_design:{course_id}"
                await smart_cache_manager.set(
                    cache_key,
                    {"indexed": True, "content_length": len(combined_content)},
                    expire=3600,  # 1 hour
                    cache_type="cache"
                )

            logger.info(f"✅ Course design {course_id} added to vector store")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add course design {course_id}: {e}")
            return False

    async def search_similar_courses(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for similar course designs using semantic similarity"""
        if not self.initialized or "course_designs" not in self.collections:
            return []

        try:
            # Check cache first
            query_hash = hashlib.md5(
                f"{query}:{limit}:{filters}".encode()
            ).hexdigest()
            cache_key = f"vector:search:{query_hash}"

            if smart_cache_manager.initialized:
                cached_results = await smart_cache_manager.get(cache_key, cache_type="cache")
                if cached_results:
                    logger.info(f"🎯 Vector search cache hit for query")
                    return cached_results

            # Perform vector search
            collection = self.collections["course_designs"]
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=filters
            )

            # Format results
            formatted_results = []
            if results and results.get("documents"):
                for i in range(len(results["documents"][0])):
                    result = {
                        "content": results["documents"][0][i],
                        "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "course_id": results["ids"][0][i]
                    }

                    if include_metadata and results.get("metadatas"):
                        result["metadata"] = results["metadatas"][0][i]

                    formatted_results.append(result)

            # Cache results
            if smart_cache_manager.initialized:
                await smart_cache_manager.set(
                    cache_key,
                    formatted_results,
                    expire=1800,  # 30 minutes
                    cache_type="cache"
                )

            logger.info(f"🔍 Found {len(formatted_results)} similar courses for query")
            return formatted_results

        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []

    async def add_educational_knowledge(
        self,
        knowledge_id: str,
        content: str,
        knowledge_type: str,
        source: str = "system",
        tags: Optional[List[str]] = None
    ) -> bool:
        """Add educational knowledge to the knowledge base"""
        if not self.initialized or "educational_knowledge" not in self.collections:
            return False

        try:
            metadata = {
                "knowledge_id": knowledge_id,
                "knowledge_type": knowledge_type,  # theory, methodology, practice, etc.
                "source": source,
                "tags": tags or [],
                "content_length": len(content),
                "created_at": datetime.now().isoformat()
            }

            collection = self.collections["educational_knowledge"]
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[knowledge_id]
            )

            logger.info(f"✅ Educational knowledge '{knowledge_id}' added")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add knowledge '{knowledge_id}': {e}")
            return False

    async def search_knowledge_base(
        self,
        query: str,
        knowledge_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search the educational knowledge base"""
        if not self.initialized or "educational_knowledge" not in self.collections:
            return []

        try:
            filters = None
            if knowledge_types:
                filters = {"knowledge_type": {"$in": knowledge_types}}

            collection = self.collections["educational_knowledge"]
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=filters
            )

            formatted_results = []
            if results and results.get("documents"):
                for i in range(len(results["documents"][0])):
                    result = {
                        "content": results["documents"][0][i],
                        "relevance_score": 1 - results["distances"][0][i],
                        "knowledge_id": results["ids"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {}
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Knowledge base search failed: {e}")
            return []

    async def store_agent_memory(
        self,
        agent_id: str,
        experience_type: str,
        content: str,
        success_score: float,
        context: Dict[str, Any]
    ) -> bool:
        """Store agent learning experiences and successful patterns"""
        if not self.initialized or "agent_memories" not in self.collections:
            return False

        try:
            memory_id = f"{agent_id}_{experience_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            metadata = {
                "agent_id": agent_id,
                "experience_type": experience_type,  # success, failure, pattern, etc.
                "success_score": success_score,
                "context": context,
                "created_at": datetime.now().isoformat()
            }

            collection = self.collections["agent_memories"]
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )

            logger.info(f"💾 Agent memory stored: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store agent memory: {e}")
            return False

    async def retrieve_agent_patterns(
        self,
        agent_id: str,
        context_query: str,
        min_success_score: float = 0.7,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve successful patterns for an agent based on context"""
        if not self.initialized or "agent_memories" not in self.collections:
            return []

        try:
            filters = {
                "agent_id": agent_id,
                "success_score": {"$gte": min_success_score}
            }

            collection = self.collections["agent_memories"]
            results = collection.query(
                query_texts=[context_query],
                n_results=limit,
                where=filters
            )

            formatted_results = []
            if results and results.get("documents"):
                for i in range(len(results["documents"][0])):
                    result = {
                        "pattern": results["documents"][0][i],
                        "relevance": 1 - results["distances"][0][i],
                        "success_score": results["metadatas"][0][i]["success_score"],
                        "context": results["metadatas"][0][i]["context"]
                    }
                    formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Failed to retrieve agent patterns: {e}")
            return []

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        if not self.initialized:
            return {"initialized": False}

        stats = {
            "initialized": True,
            "collections": {},
            "total_documents": 0
        }

        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats["collections"][name] = {
                    "document_count": count,
                    "metadata": collection.metadata
                }
                stats["total_documents"] += count
            except Exception as e:
                stats["collections"][name] = {"error": str(e)}

        return stats

    async def cleanup_old_entries(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old entries from collections"""
        if not self.initialized:
            return {}

        cleanup_stats = {}
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)

        for name, collection in self.collections.items():
            try:
                # This would require custom logic based on metadata timestamps
                # For now, just return the count
                cleanup_stats[name] = 0
                logger.info(f"🧹 Cleanup checked for collection '{name}'")
            except Exception as e:
                logger.error(f"❌ Cleanup failed for collection '{name}': {e}")
                cleanup_stats[name] = -1

        return cleanup_stats


# Global vector service instance
vector_service = AdvancedVectorService()


async def init_enhanced_vector_store():
    """Initialize the enhanced vector store service"""
    success = await vector_service.initialize()
    if success:
        logger.info("🚀 Enhanced vector store service ready")
    return success


async def add_course_to_vectors(
    course_id: str,
    course_data: Dict[str, Any],
    agent_context: Optional[Dict[str, Any]] = None
) -> bool:
    """Add course design to vector store"""
    return await vector_service.add_course_design(course_id, course_data, agent_context)


async def search_similar_courses(
    query: str,
    limit: int = 5,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Search for similar courses"""
    return await vector_service.search_similar_courses(query, limit, filters)


async def enhance_agent_with_knowledge(
    agent_id: str,
    context_query: str,
    knowledge_types: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Enhance agent with relevant knowledge and patterns"""
    knowledge_results = await vector_service.search_knowledge_base(
        context_query, knowledge_types, limit=3
    )

    pattern_results = await vector_service.retrieve_agent_patterns(
        agent_id, context_query, limit=2
    )

    return {
        "knowledge": knowledge_results,
        "patterns": pattern_results
    }


async def get_vector_store_health() -> Dict[str, Any]:
    """Get vector store health and statistics"""
    return await vector_service.get_collection_stats()