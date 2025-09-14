# PBL智能助手系统 - 性能优化指南

## 概述

本文档提供了针对PBL智能助手系统的全面性能优化策略和实施方案，涵盖后端、前端、数据库、缓存、智能体协作等多个层面的优化建议。

## 1. 后端性能优化

### 1.1 API响应时间优化

#### 数据库查询优化
```python
# 优化前：N+1查询问题
async def get_courses_with_projects():
    courses = await session.execute(select(Course))
    result = []
    for course in courses:
        projects = await session.execute(
            select(Project).where(Project.course_id == course.id)
        )
        result.append({
            'course': course,
            'projects': projects.scalars().all()
        })
    return result

# 优化后：使用预加载
async def get_courses_with_projects_optimized():
    result = await session.execute(
        select(Course)
        .options(selectinload(Course.projects))
    )
    return result.scalars().all()
```

#### 异步处理优化
```python
# 智能体协作异步处理
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "pbl_assistant",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
async def process_agent_collaboration(task_data):
    """异步处理智能体协作任务"""
    orchestrator = AgentOrchestrator()
    result = await orchestrator.execute_workflow(task_data)
    return result

# API端点立即返回任务ID
@router.post("/agents/collaborate")
async def start_collaboration(task_data: CollaborationRequest):
    task = process_agent_collaboration.delay(task_data.dict())
    return {"task_id": task.id, "status": "processing"}
```

#### 连接池优化
```python
# 数据库连接池配置
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    # 连接池设置
    pool_size=20,              # 基础连接池大小
    max_overflow=30,           # 允许超出的最大连接数
    pool_pre_ping=True,        # 连接前ping测试
    pool_recycle=3600,         # 连接回收时间（秒）
    # 异步设置
    echo=False,
    future=True
)

# Redis连接池
import aioredis
from aioredis import ConnectionPool

redis_pool = ConnectionPool.from_url(
    "redis://localhost:6379",
    max_connections=50,
    retry_on_timeout=True,
    health_check_interval=30
)
```

### 1.2 缓存策略

#### 多层缓存架构
```python
from functools import wraps
import pickle
import hashlib

class CacheManager:
    def __init__(self, redis_client, local_cache_size=1000):
        self.redis = redis_client
        self.local_cache = {}  # 本地缓存
        self.local_cache_size = local_cache_size
    
    async def get(self, key: str):
        # 1. 检查本地缓存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # 2. 检查Redis缓存
        value = await self.redis.get(key)
        if value:
            deserialized = pickle.loads(value)
            # 更新本地缓存
            self._update_local_cache(key, deserialized)
            return deserialized
        
        return None
    
    async def set(self, key: str, value, ttl: int = 3600):
        # 存储到Redis
        await self.redis.setex(key, ttl, pickle.dumps(value))
        # 更新本地缓存
        self._update_local_cache(key, value)
    
    def _update_local_cache(self, key: str, value):
        if len(self.local_cache) >= self.local_cache_size:
            # LRU淘汰策略
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]
        self.local_cache[key] = value

# 缓存装饰器
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:" + hashlib.md5(
                str(args).encode() + str(kwargs).encode()
            ).hexdigest()
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(ttl=1800, key_prefix="course")
async def get_course_detail(course_id: int):
    return await course_service.get_by_id(course_id)
```

#### 智能缓存失效
```python
class SmartCacheInvalidator:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.dependency_map = {
            'course': ['course_list', 'course_detail', 'user_courses'],
            'project': ['project_list', 'course_projects'],
            'user': ['user_profile', 'user_courses']
        }
    
    async def invalidate_related_caches(self, entity_type: str, entity_id: str):
        """智能失效相关缓存"""
        patterns = self.dependency_map.get(entity_type, [])
        
        for pattern in patterns:
            # 使用模式匹配删除相关缓存
            keys = await self.cache_manager.redis.keys(f"{pattern}:*{entity_id}*")
            if keys:
                await self.cache_manager.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys for {entity_type}:{entity_id}")

# 在服务层集成
class CourseService:
    async def update_course(self, course_id: int, update_data: dict):
        result = await self.repository.update(course_id, update_data)
        # 智能缓存失效
        await cache_invalidator.invalidate_related_caches('course', str(course_id))
        return result
```

### 1.3 智能体性能优化

#### 并行处理优化
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedAgentOrchestrator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.semaphore = asyncio.Semaphore(5)  # 限制并发数
    
    async def parallel_agent_consultation(self, agents: List[str], query: str):
        """并行咨询多个智能体"""
        async def consult_agent(agent_type: str):
            async with self.semaphore:
                agent = self.get_agent(agent_type)
                return await agent.process_query(query)
        
        tasks = [consult_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果和异常
        successful_results = []
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                successful_results.append({
                    'agent': agents[i],
                    'result': result
                })
            else:
                logger.error(f"Agent {agents[i]} failed: {result}")
        
        return successful_results
    
    async def optimized_workflow_execution(self, workflow: Dict):
        """优化的工作流执行"""
        # 分析依赖关系，并行执行无依赖的步骤
        dependency_graph = self._build_dependency_graph(workflow)
        execution_plan = self._create_execution_plan(dependency_graph)
        
        results = {}
        for batch in execution_plan:
            # 并行执行当前批次的步骤
            batch_tasks = []
            for step in batch:
                task = self._execute_step(step, results)
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            
            # 更新结果
            for step, result in zip(batch, batch_results):
                results[step['id']] = result
        
        return results
```

#### 智能体响应缓存
```python
class AgentResponseCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = {
            'education_director': 3600,     # 1小时
            'learning_designer': 1800,      # 30分钟
            'creative_technologist': 900,   # 15分钟
            'assessment_specialist': 2700,  # 45分钟
            'community_coordinator': 1200   # 20分钟
        }
    
    async def get_cached_response(self, agent_type: str, query: str, context: Dict):
        """获取缓存的智能体响应"""
        cache_key = self._generate_cache_key(agent_type, query, context)
        cached = await self.redis.get(cache_key)
        
        if cached:
            response = json.loads(cached)
            response['from_cache'] = True
            return response
        
        return None
    
    async def cache_response(self, agent_type: str, query: str, context: Dict, response: Dict):
        """缓存智能体响应"""
        cache_key = self._generate_cache_key(agent_type, query, context)
        ttl = self.cache_ttl.get(agent_type, 1800)
        
        response_data = {
            **response,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(response_data, ensure_ascii=False)
        )
    
    def _generate_cache_key(self, agent_type: str, query: str, context: Dict) -> str:
        """生成缓存键"""
        context_str = json.dumps(context, sort_keys=True)
        content = f"{agent_type}:{query}:{context_str}"
        return f"agent_response:{hashlib.md5(content.encode()).hexdigest()}"
```

## 2. 前端性能优化

### 2.1 代码分割和懒加载

#### 路由级别的代码分割
```tsx
// 路由配置
import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import LoadingSpinner from '@/components/LoadingSpinner';

// 懒加载组件
const CourseDesigner = lazy(() => import('@/pages/CourseDesigner'));
const ProjectManager = lazy(() => import('@/pages/ProjectManager'));
const Analytics = lazy(() => import('@/pages/Analytics'));

const router = createBrowserRouter([
  {
    path: "/course-designer",
    element: (
      <Suspense fallback={<LoadingSpinner />}>
        <CourseDesigner />
      </Suspense>
    ),
  },
  {
    path: "/project-manager",
    element: (
      <Suspense fallback={<LoadingSpinner />}>
        <ProjectManager />
      </Suspense>
    ),
  },
  // ... 其他路由
]);
```

#### 组件级别的懒加载
```tsx
import { lazy, Suspense, useState } from 'react';

const HeavyChart = lazy(() => import('@/components/HeavyChart'));
const AdvancedSettings = lazy(() => import('@/components/AdvancedSettings'));

export function Dashboard() {
  const [showChart, setShowChart] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div>
      <h1>仪表板</h1>
      
      {/* 按需加载图表组件 */}
      <button onClick={() => setShowChart(true)}>
        显示图表
      </button>
      
      {showChart && (
        <Suspense fallback={<div>加载图表中...</div>}>
          <HeavyChart />
        </Suspense>
      )}
      
      {/* 按需加载设置组件 */}
      {showSettings && (
        <Suspense fallback={<div>加载设置中...</div>}>
          <AdvancedSettings />
        </Suspense>
      )}
    </div>
  );
}
```

### 2.2 状态管理优化

#### 智能状态缓存
```tsx
import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';

interface CourseStore {
  courses: Course[];
  selectedCourse: Course | null;
  loading: boolean;
  lastFetch: number;
  
  // Actions
  fetchCourses: () => Promise<void>;
  selectCourse: (id: string) => void;
  updateCourse: (id: string, updates: Partial<Course>) => void;
  invalidateCache: () => void;
}

const useCourseStore = create<CourseStore>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        courses: [],
        selectedCourse: null,
        loading: false,
        lastFetch: 0,
        
        fetchCourses: async () => {
          const now = Date.now();
          const { lastFetch, courses } = get();
          
          // 如果缓存还新鲜（5分钟内），直接返回
          if (now - lastFetch < 5 * 60 * 1000 && courses.length > 0) {
            return;
          }
          
          set({ loading: true });
          
          try {
            const response = await api.getCourses();
            set({
              courses: response.data,
              lastFetch: now,
              loading: false
            });
          } catch (error) {
            set({ loading: false });
            throw error;
          }
        },
        
        selectCourse: (id: string) => {
          const course = get().courses.find(c => c.id === id);
          set({ selectedCourse: course || null });
        },
        
        updateCourse: (id: string, updates: Partial<Course>) => {
          set(state => ({
            courses: state.courses.map(course =>
              course.id === id ? { ...course, ...updates } : course
            ),
            selectedCourse: state.selectedCourse?.id === id
              ? { ...state.selectedCourse, ...updates }
              : state.selectedCourse
          }));
        },
        
        invalidateCache: () => {
          set({ lastFetch: 0 });
        }
      }),
      {
        name: 'course-store',
        // 只持久化部分状态
        partialize: (state) => ({
          courses: state.courses,
          lastFetch: state.lastFetch,
          selectedCourse: state.selectedCourse
        })
      }
    )
  )
);
```

#### 虚拟化长列表
```tsx
import { FixedSizeList as List } from 'react-window';
import { memo } from 'react';

interface CourseItemProps {
  index: number;
  style: React.CSSProperties;
  data: Course[];
}

const CourseItem = memo(({ index, style, data }: CourseItemProps) => {
  const course = data[index];
  
  return (
    <div style={style} className="course-item">
      <h3>{course.title}</h3>
      <p>{course.description}</p>
      <span>{course.duration}周</span>
    </div>
  );
});

export function CourseList({ courses }: { courses: Course[] }) {
  return (
    <List
      height={600}        // 列表高度
      itemCount={courses.length}
      itemSize={120}      // 每项高度
      itemData={courses}  // 传递给子组件的数据
      width="100%"
    >
      {CourseItem}
    </List>
  );
}
```

### 2.3 网络请求优化

#### 智能请求合并
```tsx
import { useCallback, useRef } from 'react';

class RequestBatcher {
  private batches = new Map<string, {
    requests: Array<{ id: string; resolve: Function; reject: Function }>;
    timer: NodeJS.Timeout;
  }>();
  
  private batchDelay = 50; // 50ms内的请求会被合并
  
  batch<T>(key: string, requestFn: (ids: string[]) => Promise<T[]>) {
    return (id: string): Promise<T> => {
      return new Promise((resolve, reject) => {
        let batch = this.batches.get(key);
        
        if (!batch) {
          batch = {
            requests: [],
            timer: setTimeout(() => this.executeBatch(key, requestFn), this.batchDelay)
          };
          this.batches.set(key, batch);
        }
        
        batch.requests.push({ id, resolve, reject });
      });
    };
  }
  
  private async executeBatch<T>(key: string, requestFn: (ids: string[]) => Promise<T[]>) {
    const batch = this.batches.get(key);
    if (!batch) return;
    
    this.batches.delete(key);
    
    try {
      const ids = batch.requests.map(req => req.id);
      const results = await requestFn(ids);
      
      // 将结果分发给各个请求
      batch.requests.forEach((req, index) => {
        req.resolve(results[index]);
      });
    } catch (error) {
      batch.requests.forEach(req => req.reject(error));
    }
  }
}

const requestBatcher = new RequestBatcher();

// 使用示例
const batchedGetCourse = requestBatcher.batch(
  'courses',
  async (ids: string[]) => {
    const response = await api.getCoursesBatch(ids);
    return response.data;
  }
);

export function useBatchedCourse(courseId: string) {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (!courseId) return;
    
    setLoading(true);
    batchedGetCourse(courseId)
      .then(setCourse)
      .finally(() => setLoading(false));
  }, [courseId]);
  
  return { course, loading };
}
```

#### 预取策略
```tsx
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export function usePrefetch() {
  const router = useRouter();
  
  useEffect(() => {
    // 预取可能访问的路由
    const prefetchRoutes = [
      '/course-designer',
      '/project-manager',
      '/analytics'
    ];
    
    prefetchRoutes.forEach(route => {
      router.prefetch(route);
    });
    
    // 预取API数据
    const prefetchData = async () => {
      // 预取用户最近访问的课程
      const recentCourses = getRecentCourses();
      recentCourses.forEach(courseId => {
        queryClient.prefetchQuery({
          queryKey: ['course', courseId],
          queryFn: () => api.getCourse(courseId),
          staleTime: 5 * 60 * 1000 // 5分钟内不重新获取
        });
      });
    };
    
    // 延迟预取，避免影响初始加载
    setTimeout(prefetchData, 2000);
  }, [router]);
}
```

## 3. 数据库性能优化

### 3.1 索引优化策略

```sql
-- 复合索引优化
CREATE INDEX idx_courses_subject_grade_level 
ON courses(subject, grade_level, created_at DESC);

-- 部分索引（针对活跃课程）
CREATE INDEX idx_active_courses 
ON courses(created_at DESC) 
WHERE is_active = true;

-- 表达式索引
CREATE INDEX idx_courses_title_search 
ON courses USING gin(to_tsvector('english', title || ' ' || description));

-- 覆盖索引（包含查询所需的所有列）
CREATE INDEX idx_projects_course_cover 
ON projects(course_id) 
INCLUDE (title, description, type, estimated_hours);
```

### 3.2 查询优化

#### 分页查询优化
```python
# 优化前：OFFSET查询在大数据量时性能差
async def get_courses_pagination_bad(page: int, limit: int):
    offset = (page - 1) * limit
    result = await session.execute(
        select(Course)
        .order_by(Course.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()

# 优化后：基于游标的分页
async def get_courses_pagination_optimized(cursor: Optional[datetime] = None, limit: int = 20):
    query = select(Course).order_by(Course.created_at.desc()).limit(limit)
    
    if cursor:
        query = query.where(Course.created_at < cursor)
    
    result = await session.execute(query)
    courses = result.scalars().all()
    
    next_cursor = courses[-1].created_at if courses else None
    
    return {
        'courses': courses,
        'next_cursor': next_cursor,
        'has_more': len(courses) == limit
    }
```

#### 批量操作优化
```python
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

async def bulk_create_projects_optimized(projects_data: List[dict]):
    """批量创建项目的优化版本"""
    
    # 使用批量插入
    stmt = insert(Project)
    await session.execute(stmt, projects_data)
    
    # PostgreSQL的UPSERT操作
    stmt = pg_insert(Project).values(projects_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['course_id', 'title'],
        set_=dict(
            description=stmt.excluded.description,
            updated_at=func.now()
        )
    )
    await session.execute(stmt)
    
    await session.commit()

async def bulk_update_projects_optimized(updates: List[dict]):
    """批量更新项目"""
    
    # 使用bulk_update_mappings
    await session.bulk_update_mappings(Project, updates)
    await session.commit()
```

### 3.3 连接池和事务优化

```python
from sqlalchemy.ext.asyncio import async_scoped_session
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(
            DATABASE_URL,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            # 连接池优化
            pool_timeout=30,
            pool_reset_on_return='commit'
        )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_read_only_session(self):
        """获取只读会话（用于查询优化）"""
        async with self.session_factory() as session:
            try:
                # 设置为只读事务
                await session.execute(text("SET TRANSACTION READ ONLY"))
                yield session
            finally:
                await session.close()
    
    async def execute_in_transaction(self, operations: List[Callable]):
        """在单个事务中执行多个操作"""
        async with self.get_session() as session:
            results = []
            for operation in operations:
                result = await operation(session)
                results.append(result)
            return results
```

## 4. 缓存架构优化

### 4.1 分布式缓存策略

```python
import redis.asyncio as redis
from typing import Optional, Any, List
import json
import pickle
import zlib

class DistributedCacheManager:
    def __init__(self, redis_nodes: List[str]):
        # Redis集群配置
        self.redis_cluster = redis.RedisCluster(
            startup_nodes=[
                redis.ConnectionPool.from_url(url) for url in redis_nodes
            ],
            decode_responses=False,
            skip_full_coverage_check=True,
            max_connections=100
        )
        
        # 本地缓存（L1）
        self.local_cache = {}
        self.local_cache_max_size = 1000
    
    async def get(self, key: str, use_compression: bool = False) -> Optional[Any]:
        """获取缓存值"""
        # L1缓存检查
        if key in self.local_cache:
            return self.local_cache[key]['data']
        
        # L2缓存检查（Redis）
        try:
            data = await self.redis_cluster.get(key)
            if data:
                if use_compression:
                    data = zlib.decompress(data)
                
                value = pickle.loads(data)
                self._update_local_cache(key, value)
                return value
        except Exception as e:
            logger.error(f"Redis cache error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600, use_compression: bool = False):
        """设置缓存值"""
        try:
            data = pickle.dumps(value)
            
            if use_compression:
                data = zlib.compress(data)
            
            await self.redis_cluster.setex(key, ttl, data)
            self._update_local_cache(key, value)
            
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
    
    async def invalidate_pattern(self, pattern: str):
        """按模式失效缓存"""
        try:
            keys = []
            async for key in self.redis_cluster.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis_cluster.delete(*keys)
                
            # 清理本地缓存
            local_keys_to_remove = [
                k for k in self.local_cache.keys() 
                if self._match_pattern(k, pattern)
            ]
            for k in local_keys_to_remove:
                del self.local_cache[k]
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def _update_local_cache(self, key: str, value: Any):
        """更新本地缓存"""
        if len(self.local_cache) >= self.local_cache_max_size:
            # LRU淘汰
            oldest_key = min(
                self.local_cache.keys(),
                key=lambda k: self.local_cache[k]['timestamp']
            )
            del self.local_cache[oldest_key]
        
        self.local_cache[key] = {
            'data': value,
            'timestamp': time.time()
        }
```

### 4.2 缓存预热策略

```python
class CacheWarmer:
    def __init__(self, cache_manager: DistributedCacheManager):
        self.cache_manager = cache_manager
    
    async def warm_popular_content(self):
        """预热热门内容"""
        # 获取热门课程
        popular_courses = await self._get_popular_courses()
        
        tasks = []
        for course in popular_courses:
            tasks.append(self._warm_course_data(course.id))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _warm_course_data(self, course_id: str):
        """预热单个课程的相关数据"""
        try:
            # 预热课程详情
            course = await course_service.get_by_id(course_id)
            await self.cache_manager.set(
                f"course:{course_id}",
                course,
                ttl=3600
            )
            
            # 预热相关项目
            projects = await project_service.get_by_course_id(course_id)
            await self.cache_manager.set(
                f"course_projects:{course_id}",
                projects,
                ttl=1800
            )
            
            # 预热智能体建议（如果有的话）
            suggestions = await agent_service.get_cached_suggestions(course_id)
            if suggestions:
                await self.cache_manager.set(
                    f"agent_suggestions:{course_id}",
                    suggestions,
                    ttl=900
                )
                
        except Exception as e:
            logger.error(f"Cache warming error for course {course_id}: {e}")
    
    async def _get_popular_courses(self) -> List[Course]:
        """获取热门课程"""
        # 基于访问统计获取热门课程
        popular_course_ids = await analytics_service.get_popular_course_ids(limit=100)
        courses = await course_service.get_by_ids(popular_course_ids)
        return courses
```

## 5. 智能体协作优化

### 5.1 负载均衡和资源调度

```python
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    ERROR = "error"

@dataclass
class AgentMetrics:
    response_time: float
    cpu_usage: float
    memory_usage: float
    active_requests: int
    error_rate: float
    last_update: float

class AgentLoadBalancer:
    def __init__(self):
        self.agents: Dict[str, List[AgentInstance]] = {}
        self.metrics: Dict[str, AgentMetrics] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_agent(self, agent_type: str, agent_instance: AgentInstance):
        """注册智能体实例"""
        if agent_type not in self.agents:
            self.agents[agent_type] = []
        
        self.agents[agent_type].append(agent_instance)
        self.circuit_breakers[agent_instance.id] = CircuitBreaker()
    
    async def get_optimal_agent(self, agent_type: str) -> Optional[AgentInstance]:
        """获取最优智能体实例"""
        available_agents = self.agents.get(agent_type, [])
        if not available_agents:
            return None
        
        # 过滤健康的智能体
        healthy_agents = []
        for agent in available_agents:
            if self.circuit_breakers[agent.id].is_available():
                metrics = self.metrics.get(agent.id)
                if metrics and self._is_agent_healthy(metrics):
                    healthy_agents.append((agent, metrics))
        
        if not healthy_agents:
            return None
        
        # 根据负载选择最优智能体
        best_agent = min(
            healthy_agents,
            key=lambda x: self._calculate_load_score(x[1])
        )
        
        return best_agent[0]
    
    def _is_agent_healthy(self, metrics: AgentMetrics) -> bool:
        """检查智能体是否健康"""
        return (
            metrics.cpu_usage < 80 and
            metrics.memory_usage < 85 and
            metrics.error_rate < 0.1 and
            metrics.active_requests < 10
        )
    
    def _calculate_load_score(self, metrics: AgentMetrics) -> float:
        """计算负载分数（越低越好）"""
        return (
            metrics.cpu_usage * 0.3 +
            metrics.memory_usage * 0.2 +
            metrics.active_requests * 10 +
            metrics.response_time * 0.1 +
            metrics.error_rate * 100
        )
    
    async def update_agent_metrics(self, agent_id: str, metrics: AgentMetrics):
        """更新智能体指标"""
        self.metrics[agent_id] = metrics
        
        # 更新断路器状态
        if metrics.error_rate > 0.2:  # 错误率超过20%
            await self.circuit_breakers[agent_id].open()
        elif metrics.error_rate < 0.05:  # 错误率低于5%
            await self.circuit_breakers[agent_id].close()

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
    
    def is_available(self) -> bool:
        """检查是否可用"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True
    
    async def record_success(self):
        """记录成功"""
        self.failure_count = 0
        self.state = "closed"
    
    async def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    async def open(self):
        """手动打开断路器"""
        self.state = "open"
        self.last_failure_time = time.time()
    
    async def close(self):
        """手动关闭断路器"""
        self.state = "closed"
        self.failure_count = 0
```

### 5.2 智能体缓存和预处理

```python
class AgentResponsePreprocessor:
    def __init__(self, cache_manager: DistributedCacheManager):
        self.cache_manager = cache_manager
        self.response_templates = {}
        
    async def preprocess_common_queries(self):
        """预处理常见查询"""
        common_queries = [
            {
                'agent_type': 'education_director',
                'query': '如何设计一个STEM课程?',
                'context': {'grade_level': 'high_school', 'duration': '12_weeks'}
            },
            {
                'agent_type': 'learning_designer',
                'query': '推荐适合团队协作的学习活动',
                'context': {'team_size': '4-6', 'subject': 'computer_science'}
            },
            # ... 更多常见查询
        ]
        
        tasks = []
        for query_data in common_queries:
            task = self._preprocess_query(
                query_data['agent_type'],
                query_data['query'],
                query_data['context']
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _preprocess_query(self, agent_type: str, query: str, context: Dict):
        """预处理单个查询"""
        try:
            # 生成缓存键
            cache_key = f"preprocessed:{agent_type}:{hashlib.md5((query + str(context)).encode()).hexdigest()}"
            
            # 检查是否已缓存
            cached = await self.cache_manager.get(cache_key)
            if cached:
                return
            
            # 获取智能体响应
            agent = await agent_loader.get_agent(agent_type)
            response = await agent.process_query(query, context)
            
            # 缓存响应
            await self.cache_manager.set(cache_key, response, ttl=7200)  # 2小时
            
            logger.info(f"Preprocessed query for {agent_type}: {query[:50]}...")
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")

class AgentResponseOptimizer:
    def __init__(self):
        self.response_cache = {}
        self.similarity_threshold = 0.85
    
    async def optimize_response(self, agent_type: str, query: str, context: Dict) -> Dict:
        """优化智能体响应"""
        
        # 1. 检查相似查询缓存
        similar_response = await self._find_similar_cached_response(
            agent_type, query, context
        )
        
        if similar_response:
            # 基于相似响应生成个性化回答
            return await self._personalize_response(
                similar_response, query, context
            )
        
        # 2. 正常处理
        agent = await agent_loader.get_agent(agent_type)
        response = await agent.process_query(query, context)
        
        # 3. 缓存响应
        await self._cache_response(agent_type, query, context, response)
        
        return response
    
    async def _find_similar_cached_response(
        self, agent_type: str, query: str, context: Dict
    ) -> Optional[Dict]:
        """查找相似的缓存响应"""
        
        # 获取该智能体的所有缓存响应
        pattern = f"agent_response:{agent_type}:*"
        cached_keys = await cache_manager.redis.keys(pattern)
        
        best_similarity = 0
        best_response = None
        
        for key in cached_keys[:50]:  # 限制检查数量
            try:
                cached_data = await cache_manager.get(key)
                if not cached_data:
                    continue
                
                # 计算查询相似度
                similarity = self._calculate_similarity(
                    query, cached_data.get('original_query', '')
                )
                
                if similarity > self.similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_response = cached_data
                    
            except Exception as e:
                logger.error(f"Error checking similarity: {e}")
        
        return best_response
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简化的相似度计算，实际应该使用更复杂的算法
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    async def _personalize_response(
        self, base_response: Dict, query: str, context: Dict
    ) -> Dict:
        """个性化响应"""
        
        # 基于新的查询和上下文调整响应
        personalized = base_response.copy()
        personalized['personalized'] = True
        personalized['original_query'] = query
        personalized['cache_hit'] = True
        
        # 这里可以添加更复杂的个性化逻辑
        
        return personalized
```

## 6. 监控和性能分析

### 6.1 实时性能监控

```python
import time
import psutil
from prometheus_client import Histogram, Counter, Gauge
from functools import wraps

# Prometheus指标
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'status']
)

AGENT_RESPONSE_TIME = Histogram(
    'agent_response_time_seconds',
    'Agent response time',
    ['agent_type', 'query_type']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Cache hits',
    ['cache_type', 'key_pattern']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Active connections'
)

class PerformanceMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_thresholds = {
            'response_time_p95': 5.0,  # 5秒
            'error_rate': 0.05,        # 5%
            'cpu_usage': 80,           # 80%
            'memory_usage': 85,        # 85%
        }
    
    def monitor_request(self, endpoint: str):
        """请求监控装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    REQUEST_DURATION.labels(
                        method="POST",  # 或从请求中获取
                        endpoint=endpoint,
                        status=status
                    ).observe(duration)
                    
                    # 记录慢请求
                    if duration > 2.0:
                        logger.warning(
                            f"Slow request: {endpoint} took {duration:.2f}s"
                        )
            
            return wrapper
        return decorator
    
    def monitor_agent_response(self, agent_type: str):
        """智能体响应监控装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    query_type = self._classify_query_type(kwargs.get('query', ''))
                    
                    duration = time.time() - start_time
                    AGENT_RESPONSE_TIME.labels(
                        agent_type=agent_type,
                        query_type=query_type
                    ).observe(duration)
                    
                    return result
                except Exception as e:
                    logger.error(f"Agent {agent_type} error: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def _classify_query_type(self, query: str) -> str:
        """分类查询类型"""
        if "设计" in query or "design" in query.lower():
            return "design"
        elif "推荐" in query or "recommend" in query.lower():
            return "recommendation"
        elif "评估" in query or "assess" in query.lower():
            return "assessment"
        else:
            return "general"
    
    async def collect_system_metrics(self):
        """收集系统指标"""
        while True:
            try:
                # CPU和内存使用率
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                # 网络连接数
                connections = len(psutil.net_connections())
                ACTIVE_CONNECTIONS.set(connections)
                
                # 检查阈值并触发告警
                await self._check_thresholds({
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'active_connections': connections
                })
                
                await asyncio.sleep(30)  # 30秒收集一次
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _check_thresholds(self, metrics: Dict[str, float]):
        """检查性能阈值"""
        for metric_name, value in metrics.items():
            threshold = self.alert_thresholds.get(metric_name)
            if threshold and value > threshold:
                await self._trigger_alert(metric_name, value, threshold)
    
    async def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """触发性能告警"""
        alert_message = f"Performance alert: {metric_name} = {value:.2f}, threshold = {threshold}"
        
        # 发送到监控系统
        logger.warning(alert_message)
        
        # 这里可以集成更多告警渠道
        # await slack_notifier.send_alert(alert_message)
        # await email_notifier.send_alert(alert_message)
```

### 6.2 性能分析和优化建议

```python
class PerformanceAnalyzer:
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
        self.analysis_window = 3600  # 1小时窗口
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """分析系统性能"""
        
        analysis_result = {
            'timestamp': datetime.utcnow(),
            'api_performance': await self._analyze_api_performance(),
            'agent_performance': await self._analyze_agent_performance(),
            'resource_usage': await self._analyze_resource_usage(),
            'cache_efficiency': await self._analyze_cache_efficiency(),
            'recommendations': []
        }
        
        # 生成优化建议
        recommendations = await self._generate_recommendations(analysis_result)
        analysis_result['recommendations'] = recommendations
        
        return analysis_result
    
    async def _analyze_api_performance(self) -> Dict[str, Any]:
        """分析API性能"""
        
        # 从Prometheus获取指标
        response_times = await self._get_response_time_metrics()
        error_rates = await self._get_error_rate_metrics()
        
        slow_endpoints = [
            endpoint for endpoint, metrics in response_times.items()
            if metrics['p95'] > 2.0
        ]
        
        high_error_endpoints = [
            endpoint for endpoint, rate in error_rates.items()
            if rate > 0.05
        ]
        
        return {
            'avg_response_time': sum(m['avg'] for m in response_times.values()) / len(response_times),
            'p95_response_time': max(m['p95'] for m in response_times.values()),
            'overall_error_rate': sum(error_rates.values()) / len(error_rates),
            'slow_endpoints': slow_endpoints,
            'high_error_endpoints': high_error_endpoints
        }
    
    async def _analyze_agent_performance(self) -> Dict[str, Any]:
        """分析智能体性能"""
        
        agent_metrics = await self._get_agent_metrics()
        
        performance_issues = []
        for agent_type, metrics in agent_metrics.items():
            if metrics['avg_response_time'] > 10.0:
                performance_issues.append({
                    'agent_type': agent_type,
                    'issue': 'slow_response',
                    'value': metrics['avg_response_time']
                })
            
            if metrics['error_rate'] > 0.1:
                performance_issues.append({
                    'agent_type': agent_type,
                    'issue': 'high_error_rate',
                    'value': metrics['error_rate']
                })
        
        return {
            'agent_metrics': agent_metrics,
            'performance_issues': performance_issues
        }
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        
        recommendations = []
        
        # API性能建议
        api_perf = analysis['api_performance']
        if api_perf['p95_response_time'] > 5.0:
            recommendations.append({
                'category': 'api_performance',
                'priority': 'high',
                'issue': 'High API response time',
                'suggestion': 'Consider implementing response caching and database query optimization',
                'expected_improvement': '30-50% response time reduction'
            })
        
        if api_perf['slow_endpoints']:
            recommendations.append({
                'category': 'api_performance',
                'priority': 'medium',
                'issue': f'Slow endpoints: {", ".join(api_perf["slow_endpoints"])}',
                'suggestion': 'Optimize these specific endpoints with caching or async processing',
                'expected_improvement': '40-60% improvement for affected endpoints'
            })
        
        # 智能体性能建议
        agent_issues = analysis['agent_performance']['performance_issues']
        for issue in agent_issues:
            if issue['issue'] == 'slow_response':
                recommendations.append({
                    'category': 'agent_performance',
                    'priority': 'high',
                    'issue': f"Slow agent response: {issue['agent_type']}",
                    'suggestion': 'Implement agent response caching and optimize LLM calls',
                    'expected_improvement': '50-70% response time reduction'
                })
        
        # 资源使用建议
        resource_usage = analysis['resource_usage']
        if resource_usage['cpu_usage'] > 80:
            recommendations.append({
                'category': 'infrastructure',
                'priority': 'high',
                'issue': 'High CPU usage',
                'suggestion': 'Scale horizontally or optimize CPU-intensive operations',
                'expected_improvement': 'Improved system stability and response times'
            })
        
        # 缓存效率建议
        cache_efficiency = analysis['cache_efficiency']
        if cache_efficiency['hit_rate'] < 0.7:
            recommendations.append({
                'category': 'caching',
                'priority': 'medium',
                'issue': 'Low cache hit rate',
                'suggestion': 'Review cache TTL settings and implement cache warming',
                'expected_improvement': '20-30% reduction in database load'
            })
        
        return recommendations

# 使用示例
performance_monitor = PerformanceMonitor()
performance_analyzer = PerformanceAnalyzer(performance_monitor.metrics_collector)

# 在API端点上应用监控
@performance_monitor.monitor_request("/api/v1/courses")
async def get_courses():
    return await course_service.get_all()

# 在智能体上应用监控
@performance_monitor.monitor_agent_response("education_director")
async def consult_education_director(query: str, context: Dict):
    return await education_director.process_query(query, context)
```

## 总结

这份性能优化指南提供了全面的优化策略，涵盖了系统的各个层面：

1. **后端优化**：数据库查询优化、异步处理、连接池管理、智能缓存
2. **前端优化**：代码分割、虚拟化、状态管理、网络请求优化
3. **数据库优化**：索引策略、查询优化、批量操作
4. **缓存优化**：多层缓存、分布式缓存、缓存预热
5. **智能体优化**：负载均衡、响应缓存、预处理
6. **监控分析**：实时监控、性能分析、优化建议

通过实施这些优化策略，PBL智能助手系统的性能将达到世界级标准，为用户提供快速、稳定、可靠的服务体验。

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "\u8bbe\u8ba1\u5b8c\u6574\u7684\u6d4b\u8bd5\u67b6\u6784\u548c\u7b56\u7565", "status": "completed", "activeForm": "\u8bbe\u8ba1\u6d4b\u8bd5\u67b6\u6784\u548c\u7b56\u7565"}, {"content": "\u521b\u5efa\u540e\u7aef\u6d4b\u8bd5\u5957\u4ef6\uff08\u5355\u5143\u6d4b\u8bd5\u3001\u96c6\u6210\u6d4b\u8bd5\uff09", "status": "completed", "activeForm": "\u521b\u5efa\u540e\u7aef\u6d4b\u8bd5\u5957\u4ef6"}, {"content": "\u521b\u5efa\u524d\u7aef\u6d4b\u8bd5\u5957\u4ef6\uff08\u7ec4\u4ef6\u6d4b\u8bd5\u3001E2E\u6d4b\u8bd5\uff09", "status": "completed", "activeForm": "\u521b\u5efa\u524d\u7aef\u6d4b\u8bd5\u5957\u4ef6"}, {"content": "\u5b9e\u73b0\u591a\u667a\u80fd\u4f53\u534f\u4f5c\u6d4b\u8bd5\u65b9\u6848", "status": "completed", "activeForm": "\u5b9e\u73b0\u591a\u667a\u80fd\u4f53\u534f\u4f5c\u6d4b\u8bd5"}, {"content": "\u914d\u7f6e\u6027\u80fd\u6d4b\u8bd5\u548c\u538b\u529b\u6d4b\u8bd5", "status": "completed", "activeForm": "\u914d\u7f6e\u6027\u80fd\u548c\u538b\u529b\u6d4b\u8bd5"}, {"content": "\u5efa\u7acb\u76d1\u63a7\u548c\u544a\u8b66\u7cfb\u7edf", "status": "completed", "activeForm": "\u5efa\u7acb\u76d1\u63a7\u544a\u8b66\u7cfb\u7edf"}, {"content": "\u914d\u7f6eCI/CD\u81ea\u52a8\u5316\u6d41\u7a0b", "status": "completed", "activeForm": "\u914d\u7f6eCI/CD\u6d41\u7a0b"}, {"content": "\u63d0\u4f9b\u6027\u80fd\u4f18\u5316\u5efa\u8bae\u548c\u5b9e\u65bd\u65b9\u6848", "status": "completed", "activeForm": "\u63d0\u4f9b\u6027\u80fd\u4f18\u5316\u5efa\u8bae"}]