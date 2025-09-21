"""
PBL课程数据模型
包含完整的项目式学习课程结构定义
"""

import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

from .base import Base, BaseModel


# 学段枚举
class EducationLevel(str, Enum):
    """教育学段"""

    PRIMARY = "primary"  # 小学
    JUNIOR = "junior"  # 初中
    SENIOR = "senior"  # 高中
    UNIVERSITY = "university"  # 大学
    ADULT = "adult"  # 成人教育


# 学科枚举
class Subject(str, Enum):
    """学科分类"""

    CHINESE = "chinese"  # 语文
    MATHEMATICS = "mathematics"  # 数学
    ENGLISH = "english"  # 英语
    PHYSICS = "physics"  # 物理
    CHEMISTRY = "chemistry"  # 化学
    BIOLOGY = "biology"  # 生物
    HISTORY = "history"  # 历史
    GEOGRAPHY = "geography"  # 地理
    POLITICS = "politics"  # 政治
    SCIENCE = "science"  # 科学（综合）
    TECHNOLOGY = "technology"  # 技术
    ART = "art"  # 艺术
    MUSIC = "music"  # 音乐
    PE = "pe"  # 体育
    COMPREHENSIVE = "comprehensive"  # 综合实践
    INTERDISCIPLINARY = "interdisciplinary"  # 跨学科


# 课程状态枚举
class CourseStatus(str, Enum):
    """课程状态"""

    DRAFT = "draft"  # 草稿
    DESIGNING = "designing"  # 设计中
    REVIEWING = "reviewing"  # 审核中
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"  # 已归档
    SUSPENDED = "suspended"  # 已暂停


# 难度等级枚举
class DifficultyLevel(str, Enum):
    """难度等级"""

    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家级


# 评估类型枚举
class AssessmentType(str, Enum):
    """评估类型"""

    FORMATIVE = "formative"  # 形成性评估
    SUMMATIVE = "summative"  # 总结性评估
    PEER = "peer"  # 同伴评估
    SELF = "self"  # 自我评估
    AUTHENTIC = "authentic"  # 真实性评估


# 资源类型枚举
class ResourceType(str, Enum):
    """资源类型"""

    DOCUMENT = "document"  # 文档
    VIDEO = "video"  # 视频
    AUDIO = "audio"  # 音频
    IMAGE = "image"  # 图片
    LINK = "link"  # 链接
    TOOL = "tool"  # 工具
    TEMPLATE = "template"  # 模板


# 多对多关联表：课程-标签
course_tags = Table(
    "course_tags",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("pbl_core.tags.id"), primary_key=True),
    schema="pbl_core"
)

# 多对多关联表：课程-协作者
course_collaborators = Table(
    "course_collaborators",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("pbl_core.users.id"), primary_key=True),
    Column(
        "role", String(50), default="collaborator"
    ),  # owner, editor, viewer, collaborator
    Column("permissions", JSON, default=dict),  # 权限配置
    schema="pbl_core"
)


class Course(BaseModel):
    """PBL课程主表"""

    __tablename__ = "courses"

    # 基础信息
    title = Column(String(200), nullable=False, comment="课程标题")
    subtitle = Column(String(500), nullable=True, comment="课程副标题")
    description = Column(Text, nullable=True, comment="课程描述")
    summary = Column(Text, nullable=True, comment="课程摘要")

    # 分类信息
    subject = Column(String(50), nullable=False, comment="主学科")
    subjects = Column(ARRAY(String), nullable=True, comment="涉及学科（跨学科）")
    education_level = Column(String(20), nullable=False, comment="教育学段")
    grade_levels = Column(ARRAY(Integer), nullable=True, comment="适用年级")

    # 课程属性
    status = Column(
        String(20), default=CourseStatus.DRAFT, nullable=False, comment="课程状态"
    )
    difficulty_level = Column(
        String(20), default=DifficultyLevel.INTERMEDIATE, comment="难度等级"
    )
    duration_weeks = Column(Integer, nullable=False, comment="总周数")
    duration_hours = Column(Integer, nullable=False, comment="总学时")
    class_size_min = Column(Integer, default=15, comment="最小班级规模")
    class_size_max = Column(Integer, default=35, comment="最大班级规模")

    # 课程目标
    learning_objectives = Column(JSON, nullable=True, comment="学习目标")
    core_competencies = Column(JSON, nullable=True, comment="核心素养")
    assessment_criteria = Column(JSON, nullable=True, comment="评估标准")

    # 项目信息
    project_context = Column(Text, nullable=True, comment="项目背景")
    driving_question = Column(Text, nullable=True, comment="驱动性问题")
    final_products = Column(JSON, nullable=True, comment="最终产品/成果")
    authentic_assessment = Column(JSON, nullable=True, comment="真实性评估")

    # 课程结构
    phases = Column(JSON, nullable=True, comment="课程阶段")
    milestones = Column(JSON, nullable=True, comment="关键里程碑")
    scaffolding_supports = Column(JSON, nullable=True, comment="支架支持")

    # 资源配置
    required_resources = Column(JSON, nullable=True, comment="必需资源")
    recommended_resources = Column(JSON, nullable=True, comment="推荐资源")
    technology_requirements = Column(JSON, nullable=True, comment="技术要求")

    # 教师指导
    teacher_preparation = Column(JSON, nullable=True, comment="教师准备")
    teaching_strategies = Column(JSON, nullable=True, comment="教学策略")
    differentiation_strategies = Column(JSON, nullable=True, comment="差异化策略")

    # 质量指标
    quality_score = Column(Float, default=0.0, comment="质量评分")
    completion_rate = Column(Float, default=0.0, comment="完成率")
    satisfaction_score = Column(Float, default=0.0, comment="满意度")

    # 发布信息
    is_public = Column(Boolean, default=False, comment="是否公开")
    is_template = Column(Boolean, default=False, comment="是否为模板")
    template_category = Column(String(100), nullable=True, comment="模板分类")

    # 版本控制
    version_number = Column(String(20), default="1.0.0", comment="版本号")
    parent_course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=True, comment="父课程ID"
    )

    # 统计信息
    view_count = Column(Integer, default=0, comment="浏览次数")
    use_count = Column(Integer, default=0, comment="使用次数")
    like_count = Column(Integer, default=0, comment="点赞次数")

    # 关联关系
    lessons = relationship(
        "Lesson", back_populates="course", cascade="all, delete-orphan"
    )
    assessments = relationship(
        "Assessment", back_populates="course", cascade="all, delete-orphan"
    )
    resources = relationship(
        "Resource", back_populates="course", cascade="all, delete-orphan"
    )
    templates = relationship("CourseTemplate", back_populates="course")
    exports = relationship("CourseExport", back_populates="course")
    collaborations = relationship(
        "User", secondary=course_collaborators, back_populates="collaborated_courses"
    )
    tags = relationship("Tag", secondary=course_tags, back_populates="courses")
    reviews = relationship("CourseReview", back_populates="course")

    # 子课程关系
    parent_course = relationship(
        "Course", remote_side="Course.id", backref="child_courses"
    )

    @hybrid_property
    def is_template_course(self):
        """是否为模板课程"""
        return self.is_template

    @hybrid_property
    def total_lessons(self):
        """总课时数"""
        return len(self.lessons) if self.lessons else 0

    def get_collaborator_role(self, user_id: uuid.UUID) -> Optional[str]:
        """获取协作者角色"""
        # 查询协作者角色的逻辑
        pass

    def calculate_quality_score(self) -> float:
        """计算课程质量评分"""
        # 质量评分算法
        pass


class Lesson(BaseModel):
    """课程单元/课时"""

    __tablename__ = "lessons"

    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=False, comment="所属课程"
    )
    title = Column(String(200), nullable=False, comment="单元标题")
    description = Column(Text, nullable=True, comment="单元描述")
    objectives = Column(JSON, nullable=True, comment="学习目标")

    # 顺序和时间
    sequence_number = Column(Integer, nullable=False, comment="序号")
    duration_minutes = Column(Integer, nullable=False, comment="时长（分钟）")
    phase = Column(String(50), nullable=True, comment="所属阶段")

    # 内容结构
    activities = Column(JSON, nullable=True, comment="活动内容")
    materials = Column(JSON, nullable=True, comment="所需材料")
    homework = Column(JSON, nullable=True, comment="作业安排")

    # 教学设计
    teaching_methods = Column(JSON, nullable=True, comment="教学方法")
    student_grouping = Column(String(50), nullable=True, comment="学生分组方式")
    teacher_notes = Column(Text, nullable=True, comment="教师备注")

    # 关联关系
    course = relationship("Course", back_populates="lessons")
    assessments = relationship("Assessment", back_populates="lesson")
    resources = relationship("Resource", back_populates="lesson")


class Assessment(BaseModel):
    """评估任务"""

    __tablename__ = "assessments"

    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=False, comment="所属课程"
    )
    lesson_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.lessons.id"), nullable=True, comment="所属单元"
    )

    title = Column(String(200), nullable=False, comment="评估标题")
    description = Column(Text, nullable=True, comment="评估描述")
    type = Column(String(20), nullable=False, comment="评估类型")

    # 评估配置
    criteria = Column(JSON, nullable=True, comment="评估标准")
    rubric = Column(JSON, nullable=True, comment="评估量规")
    weight = Column(Float, default=1.0, comment="权重")

    # 时间安排
    due_date_offset = Column(Integer, nullable=True, comment="截止时间偏移（天）")
    estimated_time = Column(Integer, nullable=True, comment="预估用时（分钟）")

    # 关联关系
    course = relationship("Course", back_populates="assessments")
    lesson = relationship("Lesson", back_populates="assessments")


class Resource(BaseModel):
    """课程资源"""

    __tablename__ = "resources"

    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=False, comment="所属课程"
    )
    lesson_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.lessons.id"), nullable=True, comment="所属单元"
    )

    title = Column(String(200), nullable=False, comment="资源标题")
    description = Column(Text, nullable=True, comment="资源描述")
    type = Column(String(20), nullable=False, comment="资源类型")

    # 资源信息
    url = Column(String(500), nullable=True, comment="资源链接")
    file_path = Column(String(500), nullable=True, comment="文件路径")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")

    # 使用配置
    is_required = Column(Boolean, default=False, comment="是否必需")
    access_level = Column(String(20), default="public", comment="访问级别")

    # 关联关系
    course = relationship("Course", back_populates="resources")
    lesson = relationship("Lesson", back_populates="resources")


class CourseTemplate(BaseModel):
    """课程模板"""

    __tablename__ = "course_templates"

    name = Column(String(200), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    category = Column(String(100), nullable=False, comment="模板分类")

    # 模板配置
    template_data = Column(JSON, nullable=False, comment="模板数据")
    preview_image = Column(String(500), nullable=True, comment="预览图")

    # 适用范围
    subjects = Column(ARRAY(String), nullable=True, comment="适用学科")
    education_levels = Column(ARRAY(String), nullable=True, comment="适用学段")

    # 使用统计
    use_count = Column(Integer, default=0, comment="使用次数")
    rating = Column(Float, default=0.0, comment="评分")

    # 关联模板课程（可选）
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=True, comment="关联课程"
    )
    course = relationship("Course", back_populates="templates")


class CourseExport(BaseModel):
    """课程导出记录"""

    __tablename__ = "course_exports"

    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=False, comment="课程ID"
    )
    format = Column(String(20), nullable=False, comment="导出格式")
    status = Column(String(20), default="pending", comment="导出状态")

    # 导出配置
    export_options = Column(JSON, nullable=True, comment="导出选项")
    file_path = Column(String(500), nullable=True, comment="导出文件路径")
    file_size = Column(Integer, nullable=True, comment="文件大小")

    # 导出信息
    started_at = Column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 关联关系
    course = relationship("Course", back_populates="exports")


class Tag(BaseModel):
    """标签"""

    __tablename__ = "tags"

    name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    description = Column(Text, nullable=True, comment="标签描述")
    color = Column(String(7), nullable=True, comment="标签颜色")

    # 使用统计
    use_count = Column(Integer, default=0, comment="使用次数")

    # 关联关系
    courses = relationship("Course", secondary=course_tags, back_populates="tags")


class CourseReview(BaseModel):
    """课程评价"""

    __tablename__ = "course_reviews"

    course_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.courses.id"), nullable=False, comment="课程ID"
    )
    reviewer_id = Column(
        UUID(as_uuid=True), ForeignKey("pbl_core.users.id"), nullable=False, comment="评价者ID"
    )

    rating = Column(Integer, nullable=False, comment="评分（1-5）")
    title = Column(String(200), nullable=True, comment="评价标题")
    content = Column(Text, nullable=True, comment="评价内容")

    # 详细评分
    content_quality = Column(Integer, nullable=True, comment="内容质量评分")
    teaching_design = Column(Integer, nullable=True, comment="教学设计评分")
    resource_richness = Column(Integer, nullable=True, comment="资源丰富度评分")
    practicality = Column(Integer, nullable=True, comment="实用性评分")

    # 状态
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    is_featured = Column(Boolean, default=False, comment="是否精选")

    # 关联关系
    course = relationship("Course", back_populates="reviews")
    # reviewer = relationship("User", back_populates="reviews")
