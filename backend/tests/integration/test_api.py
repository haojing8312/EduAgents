"""
API集成测试
"""
import pytest
import json
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory, CourseFactory, ProjectFactory


class TestUserAPI:
    """用户API测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建用户"""
        user_data = UserFactory.build_dict()
        user_data.pop("id", None)  # 移除ID，让数据库自动生成
        user_data.pop("created_at", None)
        user_data.pop("updated_at", None)
        user_data["password"] = "testpassword123"
        
        response = await client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "password" not in data  # 密码不应该在响应中
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试获取用户信息"""
        # 先创建用户
        user_data = UserFactory.build_dict()
        user_data["password"] = "testpassword123"
        
        create_response = await client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # 获取用户信息
        response = await client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试更新用户信息"""
        # 创建用户
        user_data = UserFactory.build_dict()
        user_data["password"] = "testpassword123"
        
        create_response = await client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # 更新用户信息
        update_data = {"full_name": "Updated Name"}
        response = await client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, db_session: AsyncSession):
        """测试删除用户"""
        # 创建用户
        user_data = UserFactory.build_dict()
        user_data["password"] = "testpassword123"
        
        create_response = await client.post("/api/v1/users/", json=user_data)
        user_id = create_response.json()["id"]
        
        # 删除用户
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204
        
        # 验证用户已删除
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404


class TestCourseAPI:
    """课程API测试"""
    
    @pytest.fixture
    async def authenticated_user(self, client: AsyncClient, db_session: AsyncSession):
        """认证用户fixture"""
        user_data = UserFactory.build_dict()
        user_data["password"] = "testpassword123"
        
        # 创建用户
        response = await client.post("/api/v1/users/", json=user_data)
        user = response.json()
        
        # 登录获取token
        login_data = {"username": user["username"], "password": "testpassword123"}
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        return user, token
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_course(self, client: AsyncClient, authenticated_user):
        """测试创建课程"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        
        course_data = CourseFactory.build_dict()
        course_data.pop("id", None)
        course_data.pop("created_by", None)
        course_data.pop("created_at", None)
        course_data.pop("updated_at", None)
        
        response = await client.post("/api/v1/courses/", json=course_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == course_data["title"]
        assert data["created_by"]["id"] == user["id"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_courses(self, client: AsyncClient, authenticated_user):
        """测试获取课程列表"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建多个课程
        for _ in range(3):
            course_data = CourseFactory.build_dict()
            await client.post("/api/v1/courses/", json=course_data, headers=headers)
        
        # 获取课程列表
        response = await client.get("/api/v1/courses/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 3
        assert "total" in data
        assert "page" in data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_course_detail(self, client: AsyncClient, authenticated_user):
        """测试获取课程详情"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建课程
        course_data = CourseFactory.build_dict()
        create_response = await client.post("/api/v1/courses/", json=course_data, headers=headers)
        course_id = create_response.json()["id"]
        
        # 获取课程详情
        response = await client.get(f"/api/v1/courses/{course_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert "learning_objectives" in data
        assert "projects" in data


class TestProjectAPI:
    """项目API测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, db_session: AsyncSession):
        """测试创建项目"""
        # 先创建课程
        course_data = CourseFactory.build_dict()
        course_response = await client.post("/api/v1/courses/", json=course_data)
        course_id = course_response.json()["id"]
        
        # 创建项目
        project_data = ProjectFactory.build_dict()
        project_data["course_id"] = course_id
        project_data.pop("course", None)
        
        response = await client.post("/api/v1/projects/", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == course_id
        assert data["title"] == project_data["title"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_project_search(self, client: AsyncClient, db_session: AsyncSession):
        """测试项目搜索"""
        # 创建多个项目
        search_term = "人工智能"
        project_titles = [
            f"{search_term}基础项目",
            "Web开发项目",
            f"机器学习与{search_term}应用"
        ]
        
        for title in project_titles:
            project_data = ProjectFactory.build_dict()
            project_data["title"] = title
            await client.post("/api/v1/projects/", json=project_data)
        
        # 搜索项目
        response = await client.get(f"/api/v1/projects/search?q={search_term}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2  # 应该找到2个包含"人工智能"的项目
        
        for item in data["items"]:
            assert search_term in item["title"]


class TestAgentAPI:
    """智能体API测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_consultation(self, client: AsyncClient, mock_ai_service):
        """测试智能体咨询"""
        consultation_data = {
            "agent_type": "education_director",
            "query": "如何设计一个关于机器学习的PBL课程？",
            "context": {
                "grade_level": "高中",
                "duration": "12周",
                "class_size": 30
            }
        }
        
        response = await client.post("/api/v1/agents/consult", json=consultation_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "agent_type" in data
        assert data["agent_type"] == "education_director"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self, client: AsyncClient, mock_ai_service):
        """测试多智能体协作"""
        collaboration_data = {
            "task": "design_complete_course",
            "course_requirements": CourseFactory.build_dict(),
            "agents": [
                "education_director",
                "learning_designer",
                "creative_technologist",
                "assessment_specialist"
            ]
        }
        
        response = await client.post("/api/v1/agents/collaborate", json=collaboration_data)
        
        assert response.status_code == 202  # Accepted for async processing
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "processing"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_task_status(self, client: AsyncClient):
        """测试智能体任务状态查询"""
        # 先启动一个协作任务
        collaboration_data = {
            "task": "design_complete_course",
            "course_requirements": CourseFactory.build_dict(),
            "agents": ["education_director", "learning_designer"]
        }
        
        start_response = await client.post("/api/v1/agents/collaborate", json=collaboration_data)
        task_id = start_response.json()["task_id"]
        
        # 查询任务状态
        status_response = await client.get(f"/api/v1/agents/tasks/{task_id}")
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data
        assert "progress" in status_data
        assert status_data["status"] in ["processing", "completed", "failed"]


class TestWebSocketAPI:
    """WebSocket API测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_websocket_connection(self, client: AsyncClient):
        """测试WebSocket连接"""
        async with client.websocket_connect("/ws/agents") as websocket:
            # 发送消息
            test_message = {
                "type": "agent_query",
                "data": {
                    "agent": "education_director",
                    "query": "测试查询"
                }
            }
            
            await websocket.send_json(test_message)
            
            # 接收响应
            response = await websocket.receive_json()
            
            assert "type" in response
            assert "data" in response
            assert response["type"] in ["agent_response", "error"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_websocket_agent_collaboration(self, client: AsyncClient, mock_ai_service):
        """测试WebSocket智能体协作"""
        async with client.websocket_connect("/ws/collaboration") as websocket:
            # 启动协作会话
            collaboration_request = {
                "type": "start_collaboration",
                "data": {
                    "agents": ["education_director", "learning_designer"],
                    "task": "课程设计",
                    "context": CourseFactory.build_dict()
                }
            }
            
            await websocket.send_json(collaboration_request)
            
            # 接收协作开始确认
            start_response = await websocket.receive_json()
            assert start_response["type"] == "collaboration_started"
            
            # 接收智能体消息
            agent_messages = []
            for _ in range(2):  # 预期收到2个智能体的消息
                message = await websocket.receive_json()
                if message["type"] == "agent_message":
                    agent_messages.append(message)
            
            assert len(agent_messages) >= 1
            assert all(msg["data"]["agent"] in ["education_director", "learning_designer"] 
                      for msg in agent_messages)


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_transactions(self, db_session: AsyncSession):
        """测试数据库事务"""
        from app.models.user import User
        from app.models.course import Course
        
        # 开始事务
        async with db_session.begin():
            # 创建用户
            user_data = UserFactory.build_dict()
            user = User(**user_data)
            db_session.add(user)
            await db_session.flush()  # 获取ID但不提交
            
            # 创建课程
            course_data = CourseFactory.build_dict()
            course_data["created_by_id"] = user.id
            course = Course(**course_data)
            db_session.add(course)
            
            # 模拟错误情况
            if False:  # 设置为True来测试回滚
                raise Exception("模拟错误")
        
        # 验证数据已保存
        from sqlalchemy import select
        
        user_result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        saved_user = user_result.scalar_one_or_none()
        assert saved_user is not None
        
        course_result = await db_session.execute(
            select(Course).where(Course.created_by_id == saved_user.id)
        )
        saved_course = course_result.scalar_one_or_none()
        assert saved_course is not None
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_constraints(self, db_session: AsyncSession):
        """测试数据库约束"""
        from app.models.user import User
        from sqlalchemy.exc import IntegrityError
        
        # 测试唯一约束
        user_data = UserFactory.build_dict()
        
        # 创建第一个用户
        user1 = User(**user_data)
        db_session.add(user1)
        await db_session.commit()
        
        # 尝试创建相同邮箱的用户
        user2 = User(**user_data)
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_relationships(self, db_session: AsyncSession):
        """测试数据库关系"""
        from app.models.user import User
        from app.models.course import Course
        from app.models.project import Project
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # 创建用户
        user_data = UserFactory.build_dict()
        user = User(**user_data)
        db_session.add(user)
        await db_session.flush()
        
        # 创建课程
        course_data = CourseFactory.build_dict()
        course_data["created_by_id"] = user.id
        course = Course(**course_data)
        db_session.add(course)
        await db_session.flush()
        
        # 创建项目
        project_data = ProjectFactory.build_dict()
        project_data["course_id"] = course.id
        project = Project(**project_data)
        db_session.add(project)
        await db_session.commit()
        
        # 验证关系
        result = await db_session.execute(
            select(User)
            .options(selectinload(User.courses))
            .where(User.id == user.id)
        )
        loaded_user = result.scalar_one()
        
        assert len(loaded_user.courses) == 1
        assert loaded_user.courses[0].id == course.id


class TestCacheIntegration:
    """缓存集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_cache(self, redis_client):
        """测试Redis缓存"""
        # 设置缓存
        await redis_client.set("test_key", "test_value", ex=60)
        
        # 获取缓存
        value = await redis_client.get("test_key")
        assert value.decode() == "test_value"
        
        # 测试过期
        ttl = await redis_client.ttl("test_key")
        assert 0 < ttl <= 60
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_response_caching(self, client: AsyncClient, redis_client):
        """测试API响应缓存"""
        # 第一次请求
        response1 = await client.get("/api/v1/courses/")
        assert response1.status_code == 200
        
        # 检查缓存是否存在
        cache_key = "courses:list:page_1"
        cached_data = await redis_client.get(cache_key)
        
        if cached_data:
            # 第二次请求应该更快（从缓存获取）
            import time
            start_time = time.time()
            response2 = await client.get("/api/v1/courses/")
            end_time = time.time()
            
            assert response2.status_code == 200
            assert response1.json() == response2.json()
            assert (end_time - start_time) < 0.1  # 缓存响应应该很快