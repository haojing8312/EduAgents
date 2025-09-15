"""
测试数据工厂
使用factory_boy创建测试数据
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import factory
import factory.fuzzy
from faker import Faker

fake = Faker("zh_CN")


class BaseFactory(factory.Factory):
    """基础工厂类"""

    class Meta:
        abstract = True

    @classmethod
    def build_dict(cls, **kwargs) -> Dict[str, Any]:
        """构建字典数据"""
        return factory.build(dict, FACTORY_FOR=cls, **kwargs)


class UserFactory(BaseFactory):
    """用户数据工厂"""

    id = factory.Sequence(lambda n: n)
    email = factory.LazyAttribute(lambda obj: f"user{obj.id}@example.com")
    username = factory.LazyAttribute(lambda obj: f"user{obj.id}")
    full_name = factory.LazyFunction(lambda: fake.name())
    password_hash = factory.LazyFunction(
        lambda: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/7.5q5O1nG"  # "testpass"
    )
    is_active = True
    is_superuser = False
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class AdminUserFactory(UserFactory):
    """管理员用户工厂"""

    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    username = factory.Sequence(lambda n: f"admin{n}")


class CourseFactory(BaseFactory):
    """课程数据工厂"""

    id = factory.Sequence(lambda n: n)
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=500))
    subject = factory.fuzzy.FuzzyChoice(
        ["数学", "物理", "化学", "生物", "计算机科学", "工程", "艺术", "语言"]
    )
    grade_level = factory.fuzzy.FuzzyChoice(["小学", "初中", "高中", "大学"])
    duration_weeks = factory.fuzzy.FuzzyInteger(4, 20)
    difficulty_level = factory.fuzzy.FuzzyChoice(
        ["beginner", "intermediate", "advanced"]
    )
    learning_objectives = factory.LazyFunction(
        lambda: [fake.sentence() for _ in range(3, 6)]
    )
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class ProjectFactory(BaseFactory):
    """项目数据工厂"""

    id = factory.Sequence(lambda n: n)
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=800))
    type = factory.fuzzy.FuzzyChoice(
        ["research", "design", "engineering", "creative", "analysis"]
    )
    complexity_level = factory.fuzzy.FuzzyChoice(
        ["beginner", "intermediate", "advanced"]
    )
    estimated_hours = factory.fuzzy.FuzzyInteger(10, 100)
    required_skills = factory.LazyFunction(
        lambda: fake.words(nb=factory.fuzzy.FuzzyInteger(2, 8).fuzz())
    )
    resources = factory.LazyFunction(lambda: [fake.url() for _ in range(2, 5)])
    course = factory.SubFactory(CourseFactory)
    created_at = factory.LazyFunction(datetime.utcnow)


class AgentMessageFactory(BaseFactory):
    """智能体消息工厂"""

    id = factory.Sequence(lambda n: n)
    agent_type = factory.fuzzy.FuzzyChoice(
        [
            "education_director",
            "learning_designer",
            "creative_technologist",
            "assessment_specialist",
            "community_coordinator",
        ]
    )
    message_type = factory.fuzzy.FuzzyChoice(
        ["suggestion", "question", "analysis", "recommendation"]
    )
    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=300))
    metadata = factory.LazyFunction(
        lambda: {
            "confidence": fake.pyfloat(min_value=0.5, max_value=1.0),
            "priority": fake.random_int(min=1, max=5),
        }
    )
    session_id = factory.LazyFunction(lambda: fake.uuid4())
    created_at = factory.LazyFunction(datetime.utcnow)


class WebSocketMessageFactory(BaseFactory):
    """WebSocket消息工厂"""

    type = factory.fuzzy.FuzzyChoice(
        ["agent_message", "course_update", "project_update", "user_action"]
    )
    data = factory.LazyFunction(
        lambda: {
            "message": fake.sentence(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": fake.random_int(min=1, max=1000),
        }
    )
    session_id = factory.LazyFunction(lambda: fake.uuid4())


class PerformanceMetricFactory(BaseFactory):
    """性能指标工厂"""

    metric_name = factory.fuzzy.FuzzyChoice(
        [
            "api_response_time",
            "database_query_time",
            "ai_processing_time",
            "websocket_latency",
            "memory_usage",
            "cpu_usage",
        ]
    )
    value = factory.LazyFunction(lambda: fake.pyfloat(min_value=1, max_value=1000))
    unit = factory.fuzzy.FuzzyChoice(["ms", "seconds", "MB", "percent"])
    timestamp = factory.LazyFunction(datetime.utcnow)
    tags = factory.LazyFunction(
        lambda: {
            "environment": "test",
            "service": fake.word(),
            "version": fake.numerify("v#.#.#"),
        }
    )


class ErrorLogFactory(BaseFactory):
    """错误日志工厂"""

    level = factory.fuzzy.FuzzyChoice(["ERROR", "CRITICAL", "WARNING"])
    message = factory.LazyFunction(lambda: fake.sentence())
    traceback = factory.LazyFunction(lambda: fake.text(max_nb_chars=1000))
    module = factory.LazyFunction(lambda: fake.word())
    function = factory.LazyFunction(lambda: fake.word())
    line_number = factory.fuzzy.FuzzyInteger(1, 500)
    timestamp = factory.LazyFunction(datetime.utcnow)
    user_id = factory.LazyAttribute(lambda obj: fake.random_int(min=1, max=1000))
    session_id = factory.LazyFunction(lambda: fake.uuid4())


# 批量数据生成器
class DataGenerator:
    """批量测试数据生成器"""

    @staticmethod
    def create_users(count: int = 10) -> List[Dict[str, Any]]:
        """创建多个用户"""
        return [UserFactory.build_dict() for _ in range(count)]

    @staticmethod
    def create_courses_with_projects(
        course_count: int = 5, projects_per_course: int = 3
    ):
        """创建课程和相关项目"""
        courses = []
        for _ in range(course_count):
            course = CourseFactory.build_dict()
            course["projects"] = [
                ProjectFactory.build_dict() for _ in range(projects_per_course)
            ]
            courses.append(course)
        return courses

    @staticmethod
    def create_agent_conversation(message_count: int = 10, agents: List[str] = None):
        """创建智能体对话"""
        if agents is None:
            agents = [
                "education_director",
                "learning_designer",
                "creative_technologist",
            ]

        messages = []
        session_id = fake.uuid4()

        for i in range(message_count):
            agent = fake.random_element(agents)
            message = AgentMessageFactory.build_dict(
                agent_type=agent, session_id=session_id
            )
            messages.append(message)

        return messages

    @staticmethod
    def create_performance_data(days: int = 7, metrics_per_day: int = 24):
        """创建性能监控数据"""
        metrics = []
        start_date = datetime.utcnow() - timedelta(days=days)

        for day in range(days):
            for hour in range(metrics_per_day):
                timestamp = start_date + timedelta(days=day, hours=hour)
                metric = PerformanceMetricFactory.build_dict(timestamp=timestamp)
                metrics.append(metric)

        return metrics


# 边界数据生成器
class EdgeCaseDataGenerator:
    """边界条件数据生成器"""

    @staticmethod
    def empty_data():
        """空数据"""
        return {
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {},
            "none_value": None,
        }

    @staticmethod
    def large_data():
        """大数据量"""
        return {
            "long_text": "x" * 10000,
            "large_list": list(range(1000)),
            "deep_dict": {"level_" + str(i): {"value": i} for i in range(100)},
        }

    @staticmethod
    def special_characters():
        """特殊字符"""
        return {
            "unicode": "测试数据 🚀 🎯 ⚡",
            "special_chars": "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/",
            "sql_injection": "'; DROP TABLE users; --",
            "xss": "<script>alert('XSS')</script>",
            "path_traversal": "../../../etc/passwd",
        }

    @staticmethod
    def boundary_values():
        """边界值"""
        return {
            "max_int": 2**31 - 1,
            "min_int": -(2**31),
            "zero": 0,
            "negative": -1,
            "float_precision": 0.123456789012345,
            "very_small": 1e-10,
            "very_large": 1e10,
        }
