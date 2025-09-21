"""
课程相关的Pydantic数据模式定义
用于API请求/响应的数据验证和序列化
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GradeLevel(str, Enum):
    """年级水平枚举"""

    ELEMENTARY = "elementary"  # 小学
    MIDDLE_SCHOOL = "middle_school"  # 初中
    HIGH_SCHOOL = "high_school"  # 高中
    UNIVERSITY = "university"  # 大学
    ADULT = "adult"  # 成人


class SubjectArea(str, Enum):
    """学科领域枚举"""

    SCIENCE = "science"  # 科学
    TECHNOLOGY = "technology"  # 技术
    ENGINEERING = "engineering"  # 工程
    MATHEMATICS = "mathematics"  # 数学
    ARTS = "arts"  # 艺术
    LANGUAGE = "language"  # 语言
    SOCIAL_STUDIES = "social_studies"  # 社会研究
    INTERDISCIPLINARY = "interdisciplinary"  # 跨学科


class CourseDesignRequest(BaseModel):
    """课程设计请求模型"""

    course_title: str = Field(..., description="课程标题")
    subject_area: str = Field(..., description="学科领域")
    grade_level: str = Field(..., description="年级水平")
    duration_weeks: int = Field(default=8, description="课程持续周数", ge=1, le=52)
    learning_objectives: List[str] = Field(default_factory=list, description="学习目标")
    description: str = Field(..., description="课程描述和具体需求")
    special_requirements: List[str] = Field(default_factory=list, description="特殊要求")

    class Config:
        json_schema_extra = {
            "example": {
                "course_title": "AI时代的可持续发展项目",
                "subject_area": "interdisciplinary",
                "grade_level": "high_school",
                "duration_weeks": 8,
                "learning_objectives": [
                    "培养AI时代核心能力",
                    "提升人机协作能力",
                    "发展创造性问题解决技能"
                ],
                "description": "为高中生设计一个关于可持续发展的跨学科PBL课程，融合科学、技术、社会研究等多个领域",
                "special_requirements": ["需要AI工具集成", "项目式学习"]
            }
        }


class CourseDesignResponse(BaseModel):
    """课程设计响应模型"""

    course_id: str = Field(..., description="课程ID")
    title: str = Field(..., description="课程标题")
    status: str = Field(..., description="设计状态")
    agent_results: Dict[str, Any] = Field(default_factory=dict, description="智能体结果")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CourseModule(BaseModel):
    """课程模块模型"""

    module_id: str = Field(..., description="模块ID")
    title: str = Field(..., description="模块标题")
    description: str = Field(..., description="模块描述")
    duration_hours: int = Field(..., description="模块时长（小时）")
    learning_objectives: List[str] = Field(default_factory=list, description="学习目标")
    activities: List[Dict[str, Any]] = Field(default_factory=list, description="学习活动")
    assessments: List[Dict[str, Any]] = Field(default_factory=list, description="评估活动")
    resources: List[Dict[str, Any]] = Field(default_factory=list, description="学习资源")


class CourseStructure(BaseModel):
    """课程结构模型"""

    course_overview: str = Field(..., description="课程概述")
    total_duration_weeks: int = Field(..., description="总持续周数")
    modules: List[CourseModule] = Field(default_factory=list, description="课程模块")
    learning_path: str = Field(..., description="学习路径说明")
    prerequisite: Optional[str] = Field(default=None, description="先修要求")


class LearningActivity(BaseModel):
    """学习活动模型"""

    activity_id: str = Field(..., description="活动ID")
    title: str = Field(..., description="活动标题")
    type: str = Field(..., description="活动类型")
    description: str = Field(..., description="活动描述")
    duration_minutes: int = Field(..., description="活动时长（分钟）")
    difficulty_level: int = Field(default=1, description="难度等级", ge=1, le=5)
    ai_tools_required: List[str] = Field(default_factory=list, description="所需AI工具")
    materials: List[str] = Field(default_factory=list, description="所需材料")
    expected_outcomes: List[str] = Field(default_factory=list, description="预期成果")


class AssessmentRubric(BaseModel):
    """评估标准模型"""

    criterion_name: str = Field(..., description="评估标准名称")
    description: str = Field(..., description="标准描述")
    levels: Dict[str, str] = Field(..., description="评估等级")
    weight: float = Field(default=1.0, description="权重", ge=0.0, le=1.0)


class CourseExportRequest(BaseModel):
    """课程导出请求模型"""

    course_id: str = Field(..., description="课程ID")
    export_format: str = Field(..., description="导出格式", pattern="^(pdf|docx|html|json)$")
    include_resources: bool = Field(default=True, description="是否包含资源文件")
    include_assessments: bool = Field(default=True, description="是否包含评估文件")


class CourseExportResponse(BaseModel):
    """课程导出响应模型"""

    export_id: str = Field(..., description="导出ID")
    download_url: str = Field(..., description="下载链接")
    file_size_mb: float = Field(..., description="文件大小（MB）")
    export_format: str = Field(..., description="导出格式")
    expires_at: datetime = Field(..., description="过期时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }