"""
Course Persistence Service - 课程设计数据持久化服务
将AI智能体协作产生的课程设计结果保存到数据库
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.course import (
    Assessment,
    Course,
    CourseStatus,
    DifficultyLevel,
    EducationLevel,
    Lesson,
    Resource,
    Subject,
)
from app.models.user import User
from app.utils.cache import get_cache, set_cache
from app.services.vector_service import add_course_to_vectors

logger = logging.getLogger(__name__)


class CoursePersistenceService:
    """
    课程持久化服务
    负责将AI智能体协作的课程设计结果保存到数据库
    """

    def __init__(self):
        """初始化持久化服务"""
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        try:
            self.session = await get_session()
        except Exception as e:
            logger.warning(f"⚠️ 数据库连接失败，将使用缓存模式: {e}")
            self.session = None
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()

    async def save_course_design(
        self,
        session_id: str,
        course_data: Dict[str, Any],
        user_id: Optional[str] = None,
        ai_generated: bool = True
    ) -> Optional[uuid.UUID]:
        """
        保存完整的课程设计到数据库

        Args:
            session_id: 设计会话ID
            course_data: 智能体协作产生的课程数据
            user_id: 用户ID
            ai_generated: 是否为AI生成

        Returns:
            保存的课程ID
        """
        try:
            logger.info(f"💾 开始保存课程设计 - 会话: {session_id}")

            # 检查数据库连接
            if not self.session:
                logger.warning(f"⚠️ 数据库不可用，跳过数据库保存 - 会话: {session_id}")
                # 尝试保存到缓存
                cache_key = f"course_design:{session_id}"
                await set_cache(cache_key, course_data, expire=3600)  # 1小时
                logger.info(f"📱 课程设计已缓存: {cache_key}")
                return None

            # 提取课程基础信息
            course_info = await self._extract_course_info(course_data, session_id)

            # 创建课程主记录
            course = Course(
                id=uuid.uuid4(),
                title=course_info["title"],
                description=course_info["description"],
                subject=course_info["subject"],
                education_level=course_info["education_level"],
                difficulty_level=course_info["difficulty_level"],
                duration_weeks=course_info["duration_weeks"],
                duration_hours=course_info["duration_hours"],
                status=CourseStatus.DRAFT,

                # AI生成标识
                extra_data={
                    "ai_generated": ai_generated,
                    "session_id": session_id,
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "agent_data": course_data
                },

                # 项目式学习特定字段
                project_context=course_info.get("project_context"),
                driving_question=course_info.get("driving_question"),
                learning_objectives=course_info.get("learning_objectives"),
                core_competencies=course_info.get("core_competencies"),

                created_by=uuid.UUID(user_id) if user_id else None,
                updated_by=uuid.UUID(user_id) if user_id else None,
            )

            self.session.add(course)
            await self.session.flush()  # 获取ID

            # 保存课程阶段和模块
            await self._save_course_lessons(course.id, course_data)

            # 保存评估策略
            await self._save_course_assessments(course.id, course_data)

            # 保存学习资源
            await self._save_course_resources(course.id, course_data)

            # 提交事务
            await self.session.commit()

            # 缓存课程数据
            await self._cache_course_data(course.id, course_data)

            # 添加到向量数据库
            await self._add_to_vector_store(course.id, course_info, course_data)

            logger.info(f"✅ 课程设计保存成功 - 课程ID: {course.id}")
            return course.id

        except Exception as e:
            logger.error(f"❌ 课程设计保存失败: {e}")
            if self.session:
                await self.session.rollback()
            raise

    async def _extract_course_info(
        self,
        course_data: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """从AI生成的数据中提取课程基础信息"""

        # 从不同智能体的输出中提取信息
        education_theorist = course_data.get("education_theorist", {})
        course_architect = course_data.get("course_architect", {})
        content_designer = course_data.get("content_designer", {})

        # 提取标题 - 优先从课程架构师获取
        title = "AI时代PBL课程"
        if course_architect.get("course_structure", {}).get("title"):
            title = course_architect["course_structure"]["title"]
        elif content_designer.get("learning_scenarios"):
            scenarios = content_designer["learning_scenarios"]
            if scenarios and len(scenarios) > 0:
                title = f"{scenarios[0].get('title', 'AI伦理')}课程"

        # 提取描述
        description = education_theorist.get("course_requirement_analysis", "")
        if not description and course_architect.get("course_structure", {}).get("description"):
            description = course_architect["course_structure"]["description"]

        # 确定学科
        subject = Subject.INTERDISCIPLINARY  # 默认跨学科
        if "AI伦理" in title or "AI伦理" in description:
            subject = Subject.COMPREHENSIVE
        elif "科学" in title or "技术" in title:
            subject = Subject.SCIENCE

        # 提取项目背景
        project_context = ""
        if content_designer.get("learning_scenarios"):
            scenarios = content_designer["learning_scenarios"]
            if scenarios:
                descriptions = [s.get("description", "") for s in scenarios]
                project_context = "; ".join(descriptions)

        # 提取驱动性问题
        driving_question = education_theorist.get("theory_framework", {}).get("driving_question", "")
        if not driving_question:
            driving_question = f"如何运用{title}解决真实世界的问题？"

        # 提取学习目标
        learning_objectives = education_theorist.get("learning_principles", [])
        if not learning_objectives:
            learning_objectives = [
                "培养AI时代核心素养",
                "发展创造性问题解决能力",
                "提升人机协作能力",
                "建立数字伦理意识"
            ]

        # 提取核心能力
        core_competencies = [
            "人机协作学习能力",
            "元认知与自主学习",
            "创造性问题解决",
            "数字素养与计算思维",
            "情商与人文素养",
            "项目管理与执行"
        ]

        # 计算课程时长
        duration_weeks = 8  # 默认8周
        duration_hours = 32  # 默认32学时

        if course_architect.get("course_structure", {}).get("phases"):
            phases = course_architect["course_structure"]["phases"]
            total_weeks = 0
            for phase in phases:
                if "duration" in phase:
                    duration_str = phase["duration"]
                    if "周" in duration_str:
                        weeks = int(''.join(filter(str.isdigit, duration_str)))
                        total_weeks += weeks
            if total_weeks > 0:
                duration_weeks = total_weeks
                duration_hours = total_weeks * 4  # 每周4学时

        return {
            "title": title[:200],  # 限制长度
            "description": description[:1000] if description else f"基于AI智能体协作设计的{title}",
            "subject": subject,
            "education_level": EducationLevel.SENIOR,  # 默认高中
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "duration_weeks": duration_weeks,
            "duration_hours": duration_hours,
            "project_context": project_context[:2000] if project_context else None,
            "driving_question": driving_question[:1000] if driving_question else None,
            "learning_objectives": learning_objectives,
            "core_competencies": core_competencies,
        }

    async def _save_course_lessons(
        self,
        course_id: uuid.UUID,
        course_data: Dict[str, Any]
    ):
        """保存课程单元"""
        try:
            course_architect = course_data.get("course_architect", {})
            content_designer = course_data.get("content_designer", {})

            phases = course_architect.get("course_structure", {}).get("phases", [])
            scenarios = content_designer.get("learning_scenarios", [])

            lesson_sequence = 1

            # 基于阶段创建单元
            for i, phase in enumerate(phases):
                lesson = Lesson(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title=phase.get("name", f"第{i+1}阶段"),
                    description=phase.get("focus", ""),
                    sequence_number=lesson_sequence,
                    duration_minutes=120,  # 默认2小时
                    phase=phase.get("name", f"phase_{i+1}"),

                    activities={
                        "phase_focus": phase.get("focus", ""),
                        "duration": phase.get("duration", ""),
                        "related_scenarios": [s.get("title", "") for s in scenarios[:2]]
                    },

                    teaching_methods={
                        "approach": "项目式学习",
                        "grouping": "小组合作",
                        "ai_integration": True
                    }
                )

                self.session.add(lesson)
                lesson_sequence += 1

            # 基于学习场景创建具体课时
            for i, scenario in enumerate(scenarios):
                if i < 3:  # 限制最多3个场景
                    lesson = Lesson(
                        id=uuid.uuid4(),
                        course_id=course_id,
                        title=scenario.get("title", f"学习场景{i+1}"),
                        description=scenario.get("description", ""),
                        sequence_number=lesson_sequence,
                        duration_minutes=90,
                        phase="实践应用",

                        activities={
                            "scenario_type": "项目实践",
                            "ai_tools": scenario.get("ai_tools", []),
                            "description": scenario.get("description", ""),
                            "learning_outcomes": ["实践应用", "技能提升", "创新思维"]
                        },

                        materials={
                            "required_tools": scenario.get("ai_tools", []),
                            "resources": ["计算机", "网络", "AI工具账号"]
                        }
                    )

                    self.session.add(lesson)
                    lesson_sequence += 1

            logger.info(f"📚 创建了 {lesson_sequence-1} 个课程单元")

        except Exception as e:
            logger.error(f"❌ 保存课程单元失败: {e}")
            raise

    async def _save_course_assessments(
        self,
        course_id: uuid.UUID,
        course_data: Dict[str, Any]
    ):
        """保存评估策略"""
        try:
            assessment_expert = course_data.get("assessment_expert", {})

            framework = assessment_expert.get("assessment_framework", {})
            rubric = assessment_expert.get("core_competencies_rubric", {})

            # 创建形成性评估
            if framework.get("formative_assessment"):
                assessment = Assessment(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title="过程性评估",
                    description=framework["formative_assessment"],
                    type="formative",
                    criteria={
                        "focus": "学习过程",
                        "methods": ["观察记录", "学习日志", "同伴反馈"],
                        "frequency": "每周"
                    },
                    weight=0.4,
                    estimated_time=30
                )
                self.session.add(assessment)

            # 创建总结性评估
            if framework.get("summative_assessment"):
                assessment = Assessment(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title="成果性评估",
                    description=framework["summative_assessment"],
                    type="summative",
                    criteria={
                        "focus": "能力表现",
                        "methods": ["项目作品", "展示汇报", "反思报告"],
                        "rubric": rubric
                    },
                    weight=0.6,
                    estimated_time=120
                )
                self.session.add(assessment)

            # 创建核心能力评估
            for competency, standard in rubric.items():
                assessment = Assessment(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title=f"{competency}评估",
                    description=standard,
                    type="authentic",
                    criteria={
                        "competency": competency,
                        "standard": standard,
                        "ai_era_focus": True
                    },
                    weight=0.2,
                    estimated_time=45
                )
                self.session.add(assessment)

            logger.info("📊 创建了评估策略和标准")

        except Exception as e:
            logger.error(f"❌ 保存评估策略失败: {e}")
            raise

    async def _save_course_resources(
        self,
        course_id: uuid.UUID,
        course_data: Dict[str, Any]
    ):
        """保存学习资源"""
        try:
            material_creator = course_data.get("material_creator", {})
            content_designer = course_data.get("content_designer", {})

            resources = material_creator.get("digital_resources", [])
            content_types = content_designer.get("content_types", [])

            # 保存数字资源
            for resource in resources:
                course_resource = Resource(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title=resource.get("type", "学习资源"),
                    description=resource.get("description", ""),
                    type="digital",
                    url="#",  # 待生成
                    is_required=True,
                    access_level="public",

                    # 扩展信息存储在extra_data中 (models/base.py中定义)
                    extra_data={
                        "resource_type": resource.get("type"),
                        "tools": resource.get("tools", []),
                        "ai_integration": True,
                        "generated_by": "material_creator_agent"
                    }
                )
                self.session.add(course_resource)

            # 保存内容类型资源
            for i, content_type in enumerate(content_types):
                if i < 5:  # 限制资源数量
                    course_resource = Resource(
                        id=uuid.uuid4(),
                        course_id=course_id,
                        title=f"{content_type}资源",
                        description=f"用于课程的{content_type}类型资源",
                        type=content_type.lower(),
                        is_required=False,
                        access_level="public",

                        extra_data={
                            "content_type": content_type,
                            "ai_enhanced": True,
                            "generated_by": "content_designer_agent"
                        }
                    )
                    self.session.add(course_resource)

            # 添加AI工具使用指南
            if material_creator.get("ai_integration_guide"):
                guide_resource = Resource(
                    id=uuid.uuid4(),
                    course_id=course_id,
                    title="AI工具使用指南",
                    description=material_creator["ai_integration_guide"],
                    type="guide",
                    is_required=True,
                    access_level="public",

                    extra_data={
                        "resource_type": "ai_guide",
                        "target_audience": ["students", "teachers"],
                        "generated_by": "material_creator_agent"
                    }
                )
                self.session.add(guide_resource)

            logger.info("📦 创建了学习资源和工具")

        except Exception as e:
            logger.error(f"❌ 保存学习资源失败: {e}")
            raise

    async def _cache_course_data(
        self,
        course_id: uuid.UUID,
        course_data: Dict[str, Any]
    ):
        """缓存课程数据"""
        try:
            cache_key = f"course_design:{course_id}"
            cache_data = {
                "course_id": str(course_id),
                "agent_data": course_data,
                "cached_at": datetime.utcnow().isoformat()
            }

            await set_cache(cache_key, json.dumps(cache_data), expire=86400)  # 24小时
            logger.info(f"💾 课程数据已缓存: {cache_key}")

        except Exception as e:
            logger.warning(f"⚠️ 缓存课程数据失败: {e}")

    async def _add_to_vector_store(
        self,
        course_id: uuid.UUID,
        course_info: Dict[str, Any],
        course_data: Dict[str, Any]
    ):
        """添加到向量数据库"""
        try:
            # 构建用于向量化的文本内容
            content_parts = [
                course_info["title"],
                course_info["description"],
                " ".join(course_info["learning_objectives"]),
                course_info.get("project_context", ""),
                course_info.get("driving_question", "")
            ]

            # 添加智能体生成的关键内容
            education_theorist = course_data.get("education_theorist", {})
            if education_theorist.get("theory_framework"):
                content_parts.append(str(education_theorist["theory_framework"]))

            content_designer = course_data.get("content_designer", {})
            scenarios = content_designer.get("learning_scenarios", [])
            for scenario in scenarios:
                content_parts.extend([
                    scenario.get("title", ""),
                    scenario.get("description", "")
                ])

            course_content = " ".join(filter(None, content_parts))

            # 构建元数据
            metadata = {
                "course_id": str(course_id),
                "title": course_info["title"],
                "subject": course_info["subject"],
                "education_level": course_info["education_level"],
                "difficulty_level": course_info["difficulty_level"],
                "ai_generated": True,
                "created_at": datetime.utcnow().isoformat(),
                "agents_used": list(course_data.keys())
            }

            # 添加到增强版向量数据库
            success = await add_course_to_vectors(
                course_id=str(course_id),
                course_data={
                    "course_requirement": course_content,
                    "agents_data": course_data,
                    "ai_generated": True,
                    "session_id": course_data.get("session_id", "unknown")
                },
                agent_context=metadata
            )

            if success:
                logger.info(f"🔍 课程已添加到向量数据库: {course_id}")
            else:
                logger.warning(f"⚠️ 向量数据库添加失败: {course_id}")

        except Exception as e:
            logger.warning(f"⚠️ 向量数据库操作失败: {e}")

    async def get_course_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """根据会话ID获取课程"""
        try:
            # 先尝试从缓存获取
            cache_key = f"session_course:{session_id}"
            cached_data = await get_cache(cache_key)
            if cached_data:
                return json.loads(cached_data)

            # 从数据库查询
            stmt = select(Course).where(
                Course.extra_data["session_id"].astext == session_id
            )
            result = await self.session.execute(stmt)
            course = result.scalar_one_or_none()

            if course:
                course_dict = course.to_dict()
                # 缓存结果
                await set_cache(cache_key, json.dumps(course_dict), expire=3600)
                return course_dict

            return None

        except Exception as e:
            logger.error(f"❌ 查询课程失败: {e}")
            return None

    async def update_course_status(
        self,
        course_id: uuid.UUID,
        status: CourseStatus,
        user_id: Optional[str] = None
    ) -> bool:
        """更新课程状态"""
        try:
            stmt = select(Course).where(Course.id == course_id)
            result = await self.session.execute(stmt)
            course = result.scalar_one_or_none()

            if course:
                course.status = status
                if user_id:
                    course.updated_by = uuid.UUID(user_id)

                await self.session.commit()
                logger.info(f"✅ 课程状态已更新: {course_id} -> {status}")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ 更新课程状态失败: {e}")
            return False

    async def get_course_statistics(self) -> Dict[str, Any]:
        """获取课程统计信息"""
        try:
            # 查询AI生成的课程数量
            ai_courses_stmt = select(Course).where(
                Course.extra_data["ai_generated"].astext == "true"
            )
            ai_courses_result = await self.session.execute(ai_courses_stmt)
            ai_courses_count = len(ai_courses_result.scalars().all())

            # 查询总课程数量
            total_courses_stmt = select(Course)
            total_courses_result = await self.session.execute(total_courses_stmt)
            total_courses_count = len(total_courses_result.scalars().all())

            return {
                "total_courses": total_courses_count,
                "ai_generated_courses": ai_courses_count,
                "ai_generation_rate": ai_courses_count / max(total_courses_count, 1),
                "updated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}


# 全局服务实例
async def get_persistence_service() -> CoursePersistenceService:
    """获取持久化服务实例"""
    return CoursePersistenceService()