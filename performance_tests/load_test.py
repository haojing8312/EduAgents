"""
性能和负载测试脚本
使用Locust进行负载测试
"""
import time
import json
import random
from locust import HttpUser, task, between, events
from locust.clients import HttpSession
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PBLSystemUser(HttpUser):
    """PBL系统用户模拟"""
    
    wait_time = between(1, 3)  # 用户操作间隔
    
    def on_start(self):
        """用户会话开始时的设置"""
        self.login()
        self.course_id = None
        self.project_id = None
        self.session_id = None
    
    def login(self):
        """用户登录"""
        login_data = {
            "username": f"testuser_{random.randint(1, 10000)}",
            "password": "testpassword"
        }
        
        with self.client.post("/api/v1/auth/login", 
                             json=login_data, 
                             catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.client.headers.update({"Authorization": f"Bearer {token}"})
                response.success()
            else:
                response.failure(f"登录失败: {response.status_code}")
    
    @task(5)
    def browse_courses(self):
        """浏览课程列表"""
        with self.client.get("/api/v1/courses/", 
                           params={"page": 1, "limit": 20},
                           catch_response=True) as response:
            if response.status_code == 200:
                courses = response.json().get("items", [])
                if courses:
                    self.course_id = random.choice(courses)["id"]
                response.success()
            else:
                response.failure(f"获取课程列表失败: {response.status_code}")
    
    @task(3)
    def view_course_detail(self):
        """查看课程详情"""
        if self.course_id:
            with self.client.get(f"/api/v1/courses/{self.course_id}",
                               catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"获取课程详情失败: {response.status_code}")
    
    @task(2)
    def create_course(self):
        """创建新课程"""
        course_data = {
            "title": f"测试课程 {random.randint(1, 10000)}",
            "description": "这是一个性能测试用的课程",
            "subject": random.choice(["数学", "物理", "计算机科学", "工程"]),
            "grade_level": random.choice(["小学", "初中", "高中", "大学"]),
            "duration_weeks": random.randint(4, 20),
            "learning_objectives": [
                f"学习目标 {i}" for i in range(1, random.randint(3, 8))
            ]
        }
        
        with self.client.post("/api/v1/courses/", 
                            json=course_data,
                            catch_response=True) as response:
            if response.status_code == 201:
                self.course_id = response.json()["id"]
                response.success()
            else:
                response.failure(f"创建课程失败: {response.status_code}")
    
    @task(4)
    def consult_agent(self):
        """咨询智能体"""
        agent_types = [
            "education_director", "learning_designer", "creative_technologist",
            "assessment_specialist", "community_coordinator"
        ]
        
        consultation_data = {
            "agent_type": random.choice(agent_types),
            "query": f"请帮我设计一个关于{random.choice(['AI', '机器人', '环保', '创新'])}的PBL课程",
            "context": {
                "grade_level": random.choice(["初中", "高中"]),
                "duration": "12周",
                "class_size": random.randint(20, 40)
            }
        }
        
        with self.client.post("/api/v1/agents/consult",
                            json=consultation_data,
                            catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"智能体咨询失败: {response.status_code}")
    
    @task(1)
    def start_agent_collaboration(self):
        """启动智能体协作"""
        if self.course_id:
            collaboration_data = {
                "task": "design_complete_course",
                "course_requirements": {
                    "course_id": self.course_id,
                    "complexity": random.choice(["simple", "medium", "complex"]),
                    "focus_areas": ["实践项目", "团队协作", "创新思维"]
                },
                "agents": [
                    "education_director",
                    "learning_designer", 
                    "creative_technologist"
                ]
            }
            
            with self.client.post("/api/v1/agents/collaborate",
                                json=collaboration_data,
                                catch_response=True) as response:
                if response.status_code == 202:
                    task_id = response.json().get("task_id")
                    if task_id:
                        self.check_collaboration_status(task_id)
                    response.success()
                else:
                    response.failure(f"启动协作失败: {response.status_code}")
    
    def check_collaboration_status(self, task_id):
        """检查协作状态"""
        max_checks = 10
        for _ in range(max_checks):
            with self.client.get(f"/api/v1/agents/tasks/{task_id}",
                               catch_response=True) as response:
                if response.status_code == 200:
                    status = response.json().get("status")
                    if status in ["completed", "failed"]:
                        response.success()
                        break
                    elif status == "processing":
                        time.sleep(2)  # 等待处理完成
                        continue
                else:
                    response.failure(f"检查协作状态失败: {response.status_code}")
                    break
    
    @task(2)
    def search_projects(self):
        """搜索项目"""
        search_terms = ["人工智能", "机器学习", "web开发", "移动应用", "数据分析"]
        search_term = random.choice(search_terms)
        
        with self.client.get("/api/v1/projects/search",
                           params={"q": search_term, "limit": 10},
                           catch_response=True) as response:
            if response.status_code == 200:
                projects = response.json().get("items", [])
                if projects:
                    self.project_id = random.choice(projects)["id"]
                response.success()
            else:
                response.failure(f"搜索项目失败: {response.status_code}")


class WebSocketUser(HttpUser):
    """WebSocket连接测试用户"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """建立WebSocket连接"""
        self.ws_connection = None
        self.connect_websocket()
    
    def connect_websocket(self):
        """连接WebSocket"""
        try:
            # 注意：这里使用简化的WebSocket模拟
            # 实际实现需要使用websocket-client库
            headers = {"Authorization": "Bearer test_token"}
            with self.client.get("/ws/agents", 
                               headers=headers,
                               catch_response=True) as response:
                if response.status_code == 101:  # WebSocket upgrade
                    response.success()
                else:
                    response.failure(f"WebSocket连接失败: {response.status_code}")
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
    
    @task
    def send_websocket_message(self):
        """发送WebSocket消息"""
        message = {
            "type": "agent_query",
            "data": {
                "agent": "education_director",
                "query": f"随机查询 {random.randint(1, 1000)}"
            }
        }
        
        # 模拟WebSocket消息发送
        with self.client.post("/api/v1/websocket/simulate",
                            json=message,
                            catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"WebSocket消息发送失败: {response.status_code}")


class DatabaseStressUser(HttpUser):
    """数据库压力测试用户"""
    
    wait_time = between(0.5, 1.5)
    
    @task(10)
    def database_read_operations(self):
        """数据库读操作"""
        operations = [
            ("/api/v1/courses/", "GET"),
            ("/api/v1/projects/", "GET"),
            ("/api/v1/users/profile", "GET"),
            ("/api/v1/analytics/dashboard", "GET"),
        ]
        
        endpoint, method = random.choice(operations)
        
        with self.client.request(method, endpoint,
                               catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"数据库读操作失败: {response.status_code}")
    
    @task(3)
    def database_write_operations(self):
        """数据库写操作"""
        # 创建课程
        course_data = {
            "title": f"压力测试课程 {random.randint(1, 100000)}",
            "description": "数据库压力测试",
            "subject": "测试",
            "grade_level": "测试",
            "duration_weeks": 1
        }
        
        with self.client.post("/api/v1/courses/",
                            json=course_data,
                            catch_response=True) as response:
            if response.status_code == 201:
                # 立即更新
                course_id = response.json()["id"]
                update_data = {"description": "更新的描述"}
                
                with self.client.put(f"/api/v1/courses/{course_id}",
                                   json=update_data,
                                   catch_response=True) as update_response:
                    if update_response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"更新课程失败: {update_response.status_code}")
            else:
                response.failure(f"创建课程失败: {response.status_code}")


# 自定义负载测试场景
class ScenarioMixin:
    """测试场景混合类"""
    
    @task
    def complete_course_design_scenario(self):
        """完整课程设计场景"""
        # 1. 创建课程
        course_data = {
            "title": f"完整场景课程 {random.randint(1, 10000)}",
            "description": "完整的课程设计场景测试",
            "subject": "计算机科学",
            "grade_level": "高中",
            "duration_weeks": 12,
            "learning_objectives": ["目标1", "目标2", "目标3"]
        }
        
        course_response = self.client.post("/api/v1/courses/", json=course_data)
        if course_response.status_code != 201:
            return
        
        course_id = course_response.json()["id"]
        
        # 2. 启动智能体协作
        collaboration_data = {
            "task": "design_complete_course",
            "course_requirements": {"course_id": course_id},
            "agents": ["education_director", "learning_designer"]
        }
        
        collab_response = self.client.post("/api/v1/agents/collaborate", 
                                         json=collaboration_data)
        if collab_response.status_code != 202:
            return
        
        task_id = collab_response.json()["task_id"]
        
        # 3. 监控协作进度
        for _ in range(5):
            status_response = self.client.get(f"/api/v1/agents/tasks/{task_id}")
            if status_response.status_code == 200:
                status = status_response.json().get("status")
                if status in ["completed", "failed"]:
                    break
            time.sleep(1)
        
        # 4. 获取最终结果
        self.client.get(f"/api/v1/courses/{course_id}")


class HighConcurrencyUser(PBLSystemUser, ScenarioMixin):
    """高并发测试用户"""
    
    wait_time = between(0.1, 0.5)  # 高频操作
    weight = 3


class NormalUser(PBLSystemUser):
    """普通用户"""
    
    wait_time = between(2, 5)
    weight = 5


class HeavyUser(DatabaseStressUser, ScenarioMixin):
    """重度用户"""
    
    wait_time = between(1, 2)
    weight = 2


# 性能指标收集
@events.request.add_listener
def request_handler(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """请求性能指标收集"""
    if exception:
        logger.error(f"请求失败: {name} - {exception}")
    else:
        # 记录响应时间
        if response_time > 5000:  # 超过5秒的慢请求
            logger.warning(f"慢请求: {name} - {response_time}ms")


@events.test_start.add_listener
def test_start_handler(environment, **kwargs):
    """测试开始时的处理"""
    logger.info("=== 性能测试开始 ===")
    logger.info(f"目标主机: {environment.host}")
    logger.info(f"用户数: {environment.runner.target_user_count}")


@events.test_stop.add_listener  
def test_stop_handler(environment, **kwargs):
    """测试结束时的处理"""
    logger.info("=== 性能测试结束 ===")
    
    # 输出统计信息
    stats = environment.runner.stats
    logger.info(f"总请求数: {stats.total.num_requests}")
    logger.info(f"失败请求数: {stats.total.num_failures}")
    logger.info(f"平均响应时间: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"95%响应时间: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    logger.info(f"99%响应时间: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    logger.info(f"RPS: {stats.total.current_rps:.2f}")


# 自定义性能测试配置
def create_performance_test_config():
    """创建性能测试配置"""
    return {
        "users": {
            "normal_users": 50,      # 普通用户
            "heavy_users": 10,       # 重度用户
            "concurrent_users": 20,  # 高并发用户
        },
        "spawn_rate": 5,            # 每秒启动用户数
        "run_time": "10m",          # 测试运行时间
        "thresholds": {
            "avg_response_time": 2000,   # 平均响应时间阈值 (ms)
            "p95_response_time": 5000,   # 95%响应时间阈值 (ms)
            "error_rate": 0.05,          # 错误率阈值 (5%)
            "min_rps": 100,              # 最小RPS
        }
    }


if __name__ == "__main__":
    # 运行性能测试的命令示例
    # locust -f load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=5m
    print("性能测试脚本已准备就绪")
    print("运行命令: locust -f load_test.py --host=http://localhost:8000")