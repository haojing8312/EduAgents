"""
课程模板服务
提供预定义的PBL课程模板，支持不同学科和学段
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from enum import Enum

from ..models.course import CourseTemplate, Course, Subject, EducationLevel
from ..models.user import User
from ..core.config import settings


class TemplateCategory(str, Enum):
    """模板分类"""
    STEM = "stem"                      # STEM教育
    HUMANITIES = "humanities"          # 人文学科
    ARTS = "arts"                      # 艺术类
    SOCIAL_STUDIES = "social_studies"  # 社会研究
    LANGUAGE = "language"              # 语言类
    INTERDISCIPLINARY = "interdisciplinary"  # 跨学科
    PROJECT_BASED = "project_based"    # 项目式学习
    INQUIRY_BASED = "inquiry_based"    # 探究式学习
    DESIGN_THINKING = "design_thinking"  # 设计思维
    COMMUNITY_SERVICE = "community_service"  # 社区服务


class TemplateService:
    """模板服务类"""
    
    def __init__(self):
        self.template_data_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "templates"
        )
        self._ensure_template_directory()
    
    def _ensure_template_directory(self):
        """确保模板目录存在"""
        os.makedirs(self.template_data_path, exist_ok=True)
    
    async def get_templates(
        self,
        db: AsyncSession,
        category: Optional[TemplateCategory] = None,
        subject: Optional[Subject] = None,
        education_level: Optional[EducationLevel] = None,
        search_query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[CourseTemplate]:
        """获取模板列表"""
        
        query = select(CourseTemplate).where(CourseTemplate.is_deleted == False)
        
        # 分类筛选
        if category:
            query = query.where(CourseTemplate.category == category)
        
        # 学科筛选
        if subject:
            query = query.where(CourseTemplate.subjects.contains([subject]))
        
        # 学段筛选
        if education_level:
            query = query.where(CourseTemplate.education_levels.contains([education_level]))
        
        # 搜索查询
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    CourseTemplate.name.ilike(search_pattern),
                    CourseTemplate.description.ilike(search_pattern)
                )
            )
        
        # 排序和分页
        query = query.order_by(CourseTemplate.rating.desc(), CourseTemplate.use_count.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_template_by_id(self, db: AsyncSession, template_id: UUID) -> Optional[CourseTemplate]:
        """根据ID获取模板"""
        result = await db.execute(
            select(CourseTemplate)
            .options(selectinload(CourseTemplate.course))
            .where(CourseTemplate.id == template_id, CourseTemplate.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def create_template_from_course(
        self,
        db: AsyncSession,
        course: Course,
        template_name: str,
        template_description: str,
        category: TemplateCategory,
        user: User
    ) -> CourseTemplate:
        """从现有课程创建模板"""
        
        # 提取课程结构作为模板数据
        template_data = self._extract_template_data(course)
        
        # 创建模板
        template = CourseTemplate(
            name=template_name,
            description=template_description,
            category=category,
            template_data=template_data,
            subjects=[course.subject] + (course.subjects or []),
            education_levels=[course.education_level],
            course_id=course.id,
            created_by=user.id
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return template
    
    async def create_course_from_template(
        self,
        db: AsyncSession,
        template_id: UUID,
        course_title: str,
        customizations: Dict[str, Any],
        user: User
    ) -> Course:
        """从模板创建新课程"""
        
        # 获取模板
        template = await self.get_template_by_id(db, template_id)
        if not template:
            raise ValueError("模板不存在")
        
        # 应用自定义配置
        course_data = self._apply_customizations(template.template_data, customizations)
        
        # 创建新课程
        course = Course(
            title=course_title,
            **course_data,
            created_by=user.id
        )
        
        db.add(course)
        await db.commit()
        await db.refresh(course)
        
        # 更新模板使用次数
        template.use_count += 1
        await db.commit()
        
        return course
    
    async def get_popular_templates(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[CourseTemplate]:
        """获取热门模板"""
        result = await db.execute(
            select(CourseTemplate)
            .where(CourseTemplate.is_deleted == False)
            .order_by(CourseTemplate.use_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recommended_templates(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 10
    ) -> List[CourseTemplate]:
        """获取推荐模板（基于用户历史）"""
        # 这里可以实现基于用户行为的推荐算法
        # 暂时返回高评分模板
        result = await db.execute(
            select(CourseTemplate)
            .where(CourseTemplate.is_deleted == False)
            .order_by(CourseTemplate.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    def get_predefined_templates(self) -> List[Dict[str, Any]]:
        """获取预定义模板"""
        return [
            self._get_stem_project_template(),
            self._get_language_arts_template(),
            self._get_social_studies_template(),
            self._get_arts_integration_template(),
            self._get_design_thinking_template(),
            self._get_community_service_template(),
            self._get_interdisciplinary_template(),
            self._get_inquiry_based_template()
        ]
    
    async def initialize_default_templates(self, db: AsyncSession):
        """初始化默认模板"""
        predefined_templates = self.get_predefined_templates()
        
        for template_data in predefined_templates:
            # 检查模板是否已存在
            existing = await db.execute(
                select(CourseTemplate)
                .where(CourseTemplate.name == template_data["name"])
            )
            
            if existing.scalar_one_or_none():
                continue  # 已存在，跳过
            
            # 创建新模板
            template = CourseTemplate(
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                template_data=template_data["template_data"],
                subjects=template_data.get("subjects", []),
                education_levels=template_data.get("education_levels", []),
                preview_image=template_data.get("preview_image")
            )
            
            db.add(template)
        
        await db.commit()
    
    def _extract_template_data(self, course: Course) -> Dict[str, Any]:
        """从课程提取模板数据"""
        return {
            "basic_info": {
                "subtitle": course.subtitle,
                "description": course.description,
                "summary": course.summary,
                "subject": course.subject,
                "subjects": course.subjects,
                "education_level": course.education_level,
                "grade_levels": course.grade_levels,
                "difficulty_level": course.difficulty_level,
                "duration_weeks": course.duration_weeks,
                "duration_hours": course.duration_hours,
                "class_size_min": course.class_size_min,
                "class_size_max": course.class_size_max
            },
            "learning_design": {
                "learning_objectives": course.learning_objectives,
                "core_competencies": course.core_competencies,
                "assessment_criteria": course.assessment_criteria,
                "project_context": course.project_context,
                "driving_question": course.driving_question,
                "final_products": course.final_products,
                "authentic_assessment": course.authentic_assessment
            },
            "structure": {
                "phases": course.phases,
                "milestones": course.milestones,
                "scaffolding_supports": course.scaffolding_supports
            },
            "resources": {
                "required_resources": course.required_resources,
                "recommended_resources": course.recommended_resources,
                "technology_requirements": course.technology_requirements
            },
            "teaching_guidance": {
                "teacher_preparation": course.teacher_preparation,
                "teaching_strategies": course.teaching_strategies,
                "differentiation_strategies": course.differentiation_strategies
            },
            "lessons_structure": [
                {
                    "title": lesson.title,
                    "description": lesson.description,
                    "objectives": lesson.objectives,
                    "duration_minutes": lesson.duration_minutes,
                    "phase": lesson.phase,
                    "activities": lesson.activities,
                    "materials": lesson.materials,
                    "teaching_methods": lesson.teaching_methods,
                    "student_grouping": lesson.student_grouping
                }
                for lesson in course.lessons
            ] if course.lessons else [],
            "assessments_structure": [
                {
                    "title": assessment.title,
                    "description": assessment.description,
                    "type": assessment.type,
                    "criteria": assessment.criteria,
                    "rubric": assessment.rubric,
                    "weight": assessment.weight
                }
                for assessment in course.assessments
            ] if course.assessments else []
        }
    
    def _apply_customizations(
        self, 
        template_data: Dict[str, Any], 
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用自定义配置到模板数据"""
        result = template_data.copy()
        
        # 递归合并自定义配置
        def merge_dict(base: Dict, custom: Dict):
            for key, value in custom.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(result, customizations)
        return result
    
    # 预定义模板定义
    
    def _get_stem_project_template(self) -> Dict[str, Any]:
        """STEM项目模板"""
        return {
            "name": "STEM综合项目模板",
            "description": "适用于科学、技术、工程、数学跨学科项目式学习",
            "category": TemplateCategory.STEM,
            "subjects": [Subject.SCIENCE, Subject.MATHEMATICS, Subject.TECHNOLOGY],
            "education_levels": [EducationLevel.JUNIOR, EducationLevel.SENIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "基于真实问题的STEM探究项目",
                    "description": "通过解决真实世界的科技问题，培养学生的科学思维、工程设计能力和数学建模技能",
                    "duration_weeks": 8,
                    "duration_hours": 32,
                    "difficulty_level": "intermediate"
                },
                "learning_design": {
                    "learning_objectives": [
                        "运用科学方法分析和解决实际问题",
                        "掌握工程设计思维和流程",
                        "建立数学模型解决复杂问题",
                        "培养团队协作和沟通能力"
                    ],
                    "driving_question": "如何利用科技创新解决我们社区面临的环境问题？",
                    "final_products": [
                        "科技创新方案设计",
                        "原型制作和测试",
                        "项目展示和答辩"
                    ]
                },
                "structure": {
                    "phases": [
                        {
                            "name": "问题发现",
                            "duration_weeks": 2,
                            "description": "调研社区环境问题，确定项目焦点"
                        },
                        {
                            "name": "方案设计",
                            "duration_weeks": 3,
                            "description": "运用设计思维，制定解决方案"
                        },
                        {
                            "name": "原型制作",
                            "duration_weeks": 2,
                            "description": "制作原型，进行测试和改进"
                        },
                        {
                            "name": "成果展示",
                            "duration_weeks": 1,
                            "description": "展示项目成果，反思学习过程"
                        }
                    ]
                }
            }
        }
    
    def _get_language_arts_template(self) -> Dict[str, Any]:
        """语言艺术模板"""
        return {
            "name": "语言艺术创作项目模板",
            "description": "培养学生语言表达、文学创作和批判性思维能力",
            "category": TemplateCategory.LANGUAGE,
            "subjects": [Subject.CHINESE, Subject.ENGLISH],
            "education_levels": [EducationLevel.PRIMARY, EducationLevel.JUNIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "通过创作表达思想和情感",
                    "description": "以创作为中心，培养学生的语言运用能力、文学素养和表达技巧",
                    "duration_weeks": 6,
                    "duration_hours": 24,
                    "difficulty_level": "beginner"
                },
                "learning_design": {
                    "learning_objectives": [
                        "提高语言表达的准确性和生动性",
                        "培养文学鉴赏和创作能力",
                        "增强批判性思维和独立思考",
                        "学会多样化的表达方式"
                    ],
                    "driving_question": "如何用语言艺术记录和分享我们的成长故事？",
                    "final_products": [
                        "个人成长故事集",
                        "朗诵表演",
                        "文学作品展览"
                    ]
                }
            }
        }
    
    def _get_social_studies_template(self) -> Dict[str, Any]:
        """社会研究模板"""
        return {
            "name": "社会议题调研项目模板",
            "description": "通过调研社会议题，培养公民意识和社会责任感",
            "category": TemplateCategory.SOCIAL_STUDIES,
            "subjects": [Subject.HISTORY, Subject.POLITICS, Subject.GEOGRAPHY],
            "education_levels": [EducationLevel.JUNIOR, EducationLevel.SENIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "关注社会，参与公民生活",
                    "description": "选择社会热点议题进行深入调研，形成独立见解，培养公民素养",
                    "duration_weeks": 10,
                    "duration_hours": 40,
                    "difficulty_level": "advanced"
                },
                "learning_design": {
                    "learning_objectives": [
                        "了解社会议题的复杂性和多面性",
                        "掌握社会调研的方法和技能",
                        "培养批判性思维和理性分析能力",
                        "增强社会责任感和公民意识"
                    ],
                    "driving_question": "我们应该如何参与解决社区面临的社会问题？",
                    "final_products": [
                        "调研报告",
                        "政策建议书",
                        "社区行动方案"
                    ]
                }
            }
        }
    
    def _get_arts_integration_template(self) -> Dict[str, Any]:
        """艺术整合模板"""
        return {
            "name": "艺术整合创作项目模板",
            "description": "将艺术融入其他学科，促进创造性学习",
            "category": TemplateCategory.ARTS,
            "subjects": [Subject.ART, Subject.MUSIC],
            "education_levels": [EducationLevel.PRIMARY, EducationLevel.JUNIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "用艺术表达学习成果",
                    "description": "通过多元艺术形式，整合学科知识，激发创造力",
                    "duration_weeks": 5,
                    "duration_hours": 20,
                    "difficulty_level": "intermediate"
                }
            }
        }
    
    def _get_design_thinking_template(self) -> Dict[str, Any]:
        """设计思维模板"""
        return {
            "name": "设计思维创新项目模板",
            "description": "运用设计思维方法解决问题，培养创新能力",
            "category": TemplateCategory.DESIGN_THINKING,
            "subjects": [Subject.COMPREHENSIVE],
            "education_levels": [EducationLevel.JUNIOR, EducationLevel.SENIOR, EducationLevel.UNIVERSITY],
            "template_data": {
                "basic_info": {
                    "subtitle": "以人为本的创新设计",
                    "description": "学习和应用设计思维的五个阶段，创造性地解决真实问题",
                    "duration_weeks": 7,
                    "duration_hours": 28,
                    "difficulty_level": "intermediate"
                },
                "structure": {
                    "phases": [
                        {"name": "共情", "duration_weeks": 1, "description": "深入了解用户需求"},
                        {"name": "定义", "duration_weeks": 1, "description": "明确问题焦点"},
                        {"name": "构思", "duration_weeks": 2, "description": "产生创意解决方案"},
                        {"name": "原型", "duration_weeks": 2, "description": "制作可测试的原型"},
                        {"name": "测试", "duration_weeks": 1, "description": "验证和改进方案"}
                    ]
                }
            }
        }
    
    def _get_community_service_template(self) -> Dict[str, Any]:
        """社区服务模板"""
        return {
            "name": "社区服务学习项目模板",
            "description": "通过服务社区的实践活动，培养社会责任感",
            "category": TemplateCategory.COMMUNITY_SERVICE,
            "subjects": [Subject.COMPREHENSIVE],
            "education_levels": [EducationLevel.JUNIOR, EducationLevel.SENIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "服务社会，成长自我",
                    "description": "参与社区服务项目，在服务中学习，在实践中成长",
                    "duration_weeks": 12,
                    "duration_hours": 48,
                    "difficulty_level": "intermediate"
                }
            }
        }
    
    def _get_interdisciplinary_template(self) -> Dict[str, Any]:
        """跨学科模板"""
        return {
            "name": "跨学科探究项目模板",
            "description": "整合多个学科知识，解决复杂的现实问题",
            "category": TemplateCategory.INTERDISCIPLINARY,
            "subjects": [Subject.INTERDISCIPLINARY],
            "education_levels": [EducationLevel.JUNIOR, EducationLevel.SENIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "整合知识，解决真实问题",
                    "description": "运用多学科知识和方法，深入探究复杂主题",
                    "duration_weeks": 9,
                    "duration_hours": 36,
                    "difficulty_level": "advanced"
                }
            }
        }
    
    def _get_inquiry_based_template(self) -> Dict[str, Any]:
        """探究式学习模板"""
        return {
            "name": "探究式学习项目模板",
            "description": "以问题为导向，培养学生的探究能力和科学精神",
            "category": TemplateCategory.INQUIRY_BASED,
            "subjects": [Subject.SCIENCE],
            "education_levels": [EducationLevel.PRIMARY, EducationLevel.JUNIOR],
            "template_data": {
                "basic_info": {
                    "subtitle": "提出问题，探索未知",
                    "description": "引导学生提出问题，自主探究，发现规律",
                    "duration_weeks": 6,
                    "duration_hours": 24,
                    "difficulty_level": "beginner"
                }
            }
        }


# 全局服务实例
template_service = TemplateService()