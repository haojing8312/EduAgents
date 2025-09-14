"""
课程质量检查服务
自动检测课程设计的完整性、一致性和教学有效性
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

from ..models.course import Course, Lesson, Assessment


class QualityLevel(str, Enum):
    """质量等级"""
    EXCELLENT = "excellent"    # 优秀 (90-100分)
    GOOD = "good"             # 良好 (80-89分)
    ACCEPTABLE = "acceptable"  # 合格 (70-79分)
    NEEDS_IMPROVEMENT = "needs_improvement"  # 需要改进 (60-69分)
    POOR = "poor"             # 不合格 (0-59分)


class CheckSeverity(str, Enum):
    """检查严重程度"""
    CRITICAL = "critical"      # 严重问题，必须修复
    WARNING = "warning"        # 警告，建议修复
    SUGGESTION = "suggestion"  # 建议，可选修复
    INFO = "info"             # 信息提示


@dataclass
class QualityIssue:
    """质量问题"""
    category: str              # 问题分类
    severity: CheckSeverity    # 严重程度
    title: str                 # 问题标题
    description: str           # 问题描述
    suggestion: str            # 改进建议
    location: Optional[str] = None  # 问题位置
    score_impact: int = 0      # 对评分的影响


@dataclass
class QualityReport:
    """质量报告"""
    overall_score: float       # 总体评分
    quality_level: QualityLevel  # 质量等级
    issues: List[QualityIssue]  # 问题列表
    strengths: List[str]       # 优势点
    recommendations: List[str]  # 改进建议
    category_scores: Dict[str, float]  # 各类别得分
    generated_at: datetime     # 生成时间


class CourseQualityChecker:
    """课程质量检查器"""
    
    def __init__(self):
        self.checkers = [
            self._check_basic_completeness,
            self._check_learning_objectives,
            self._check_course_structure,
            self._check_pbl_alignment,
            self._check_assessment_design,
            self._check_resource_adequacy,
            self._check_scaffolding_support,
            self._check_differentiation,
            self._check_authentic_context,
            self._check_reflection_opportunities
        ]
    
    def check_course_quality(self, course: Course) -> QualityReport:
        """检查课程质量"""
        issues = []
        category_scores = {}
        
        # 执行所有检查
        for checker in self.checkers:
            category_issues, category_score = checker(course)
            issues.extend(category_issues)
            category_name = checker.__name__.replace('_check_', '').replace('_', ' ').title()
            category_scores[category_name] = category_score
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(category_scores, issues)
        
        # 确定质量等级
        quality_level = self._determine_quality_level(overall_score)
        
        # 生成优势点和建议
        strengths = self._identify_strengths(course, category_scores)
        recommendations = self._generate_recommendations(issues)
        
        return QualityReport(
            overall_score=overall_score,
            quality_level=quality_level,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
            category_scores=category_scores,
            generated_at=datetime.now()
        )
    
    def _check_basic_completeness(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查基础完整性"""
        issues = []
        score = 100
        
        # 检查必填字段
        required_fields = {
            'title': '课程标题',
            'description': '课程描述',
            'learning_objectives': '学习目标',
            'duration_weeks': '课程周数',
            'duration_hours': '总学时',
            'subject': '主学科',
            'education_level': '教育学段'
        }
        
        for field, name in required_fields.items():
            value = getattr(course, field, None)
            if not value or (isinstance(value, list) and len(value) == 0):
                issues.append(QualityIssue(
                    category="基础完整性",
                    severity=CheckSeverity.CRITICAL,
                    title=f"缺少{name}",
                    description=f"课程{name}未填写或为空",
                    suggestion=f"请完善课程的{name}信息",
                    score_impact=15
                ))
                score -= 15
        
        # 检查标题长度
        if course.title and len(course.title) < 5:
            issues.append(QualityIssue(
                category="基础完整性",
                severity=CheckSeverity.WARNING,
                title="课程标题过短",
                description="课程标题应该具有足够的描述性",
                suggestion="建议课程标题至少包含5个字符，并能清楚表达课程内容",
                score_impact=5
            ))
            score -= 5
        
        # 检查描述长度
        if course.description and len(course.description) < 50:
            issues.append(QualityIssue(
                category="基础完整性",
                severity=CheckSeverity.WARNING,
                title="课程描述过简",
                description="课程描述应该详细说明课程内容和特色",
                suggestion="建议课程描述至少包含50个字符，详细介绍课程背景、目标和特色",
                score_impact=5
            ))
            score -= 5
        
        return issues, max(0, score)
    
    def _check_learning_objectives(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查学习目标"""
        issues = []
        score = 100
        
        if not course.learning_objectives:
            issues.append(QualityIssue(
                category="学习目标",
                severity=CheckSeverity.CRITICAL,
                title="缺少学习目标",
                description="课程必须设定明确的学习目标",
                suggestion="请为课程设定3-5个具体、可测量的学习目标",
                score_impact=30
            ))
            return issues, 0
        
        objectives = course.learning_objectives
        
        # 检查目标数量
        if len(objectives) < 3:
            issues.append(QualityIssue(
                category="学习目标",
                severity=CheckSeverity.WARNING,
                title="学习目标数量偏少",
                description=f"当前只有{len(objectives)}个学习目标",
                suggestion="建议设定3-5个学习目标，以全面覆盖课程要求",
                score_impact=10
            ))
            score -= 10
        elif len(objectives) > 7:
            issues.append(QualityIssue(
                category="学习目标",
                severity=CheckSeverity.WARNING,
                title="学习目标数量过多",
                description=f"当前有{len(objectives)}个学习目标",
                suggestion="建议将学习目标控制在3-5个，过多的目标可能导致焦点分散",
                score_impact=5
            ))
            score -= 5
        
        # 检查目标质量
        action_verbs = ['分析', '评估', '创造', '应用', '理解', '记住', '综合', '比较', '设计', '解决']
        measurable_indicators = ['能够', '掌握', '理解', '应用', '分析', '评价', '创造']
        
        for i, objective in enumerate(objectives):
            if len(objective) < 10:
                issues.append(QualityIssue(
                    category="学习目标",
                    severity=CheckSeverity.WARNING,
                    title=f"学习目标{i+1}过于简单",
                    description="学习目标应该具体且可测量",
                    suggestion="请使用具体的动词和明确的评估标准来描述学习目标",
                    location=f"学习目标{i+1}",
                    score_impact=5
                ))
                score -= 5
            
            # 检查是否包含行为动词
            has_action_verb = any(verb in objective for verb in action_verbs)
            if not has_action_verb:
                issues.append(QualityIssue(
                    category="学习目标",
                    severity=CheckSeverity.SUGGESTION,
                    title=f"学习目标{i+1}缺少行为动词",
                    description="学习目标应包含明确的行为动词",
                    suggestion="建议使用'分析'、'评估'、'创造'等具体的行为动词",
                    location=f"学习目标{i+1}",
                    score_impact=3
                ))
                score -= 3
        
        return issues, max(0, score)
    
    def _check_course_structure(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查课程结构"""
        issues = []
        score = 100
        
        # 检查是否有课时
        if not course.lessons or len(course.lessons) == 0:
            issues.append(QualityIssue(
                category="课程结构",
                severity=CheckSeverity.CRITICAL,
                title="缺少课时安排",
                description="课程必须包含具体的课时安排",
                suggestion="请添加具体的课时内容，包括学习活动和时间分配",
                score_impact=40
            ))
            return issues, 0
        
        lessons = course.lessons
        total_lesson_time = sum(lesson.duration_minutes for lesson in lessons)
        expected_time = course.duration_hours * 60  # 转换为分钟
        
        # 检查时间一致性
        if abs(total_lesson_time - expected_time) > expected_time * 0.2:  # 允许20%的差异
            issues.append(QualityIssue(
                category="课程结构",
                severity=CheckSeverity.WARNING,
                title="课时时间不一致",
                description=f"课时总时长({total_lesson_time//60}小时)与设定总学时({course.duration_hours}小时)差异较大",
                suggestion="请检查并调整课时时间分配，确保与总学时一致",
                score_impact=10
            ))
            score -= 10
        
        # 检查课时内容质量
        for i, lesson in enumerate(lessons):
            if not lesson.title:
                issues.append(QualityIssue(
                    category="课程结构",
                    severity=CheckSeverity.CRITICAL,
                    title=f"课时{i+1}缺少标题",
                    description="每个课时都应该有清晰的标题",
                    suggestion="请为每个课时设定描述性的标题",
                    location=f"课时{i+1}",
                    score_impact=5
                ))
                score -= 5
            
            if not lesson.activities or len(lesson.activities) == 0:
                issues.append(QualityIssue(
                    category="课程结构",
                    severity=CheckSeverity.WARNING,
                    title=f"课时{i+1}缺少学习活动",
                    description="每个课时都应该包含具体的学习活动",
                    suggestion="请为课时添加多样化的学习活动",
                    location=f"课时{i+1}",
                    score_impact=8
                ))
                score -= 8
        
        # 检查课程阶段
        if course.phases and len(course.phases) > 0:
            score += 10  # 有阶段规划的奖励分
        else:
            issues.append(QualityIssue(
                category="课程结构",
                severity=CheckSeverity.SUGGESTION,
                title="建议添加课程阶段",
                description="将课程分为不同阶段有助于学习管理",
                suggestion="建议将课程分为引入、探究、实施、反思等阶段",
                score_impact=0
            ))
        
        return issues, max(0, min(100, score))
    
    def _check_pbl_alignment(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查PBL对齐度"""
        issues = []
        score = 100
        
        # 检查驱动性问题
        if not course.driving_question:
            issues.append(QualityIssue(
                category="PBL对齐",
                severity=CheckSeverity.CRITICAL,
                title="缺少驱动性问题",
                description="PBL课程必须有一个核心的驱动性问题",
                suggestion="请设定一个开放性、挑战性的驱动性问题来指导整个项目",
                score_impact=25
            ))
            score -= 25
        else:
            # 检查驱动性问题质量
            question = course.driving_question
            if '?' not in question and '？' not in question:
                issues.append(QualityIssue(
                    category="PBL对齐",
                    severity=CheckSeverity.WARNING,
                    title="驱动性问题格式不当",
                    description="驱动性问题应该是一个问句",
                    suggestion="请确保驱动性问题以疑问句形式表达",
                    score_impact=5
                ))
                score -= 5
            
            if len(question) < 20:
                issues.append(QualityIssue(
                    category="PBL对齐",
                    severity=CheckSeverity.WARNING,
                    title="驱动性问题过于简单",
                    description="驱动性问题应该具有足够的复杂性和挑战性",
                    suggestion="请设计一个更具挑战性和开放性的驱动性问题",
                    score_impact=8
                ))
                score -= 8
        
        # 检查最终产品
        if not course.final_products or len(course.final_products) == 0:
            issues.append(QualityIssue(
                category="PBL对齐",
                severity=CheckSeverity.CRITICAL,
                title="缺少最终产品定义",
                description="PBL课程必须明确最终产品或成果",
                suggestion="请定义学生在项目结束时应该产出的具体成果",
                score_impact=20
            ))
            score -= 20
        
        # 检查真实性情境
        if not course.project_context:
            issues.append(QualityIssue(
                category="PBL对齐",
                severity=CheckSeverity.WARNING,
                title="缺少项目背景",
                description="PBL应该基于真实的情境或问题",
                suggestion="请提供真实的项目背景，让学生能够看到学习的意义",
                score_impact=15
            ))
            score -= 15
        
        # 检查真实性评估
        if not course.authentic_assessment:
            issues.append(QualityIssue(
                category="PBL对齐",
                severity=CheckSeverity.SUGGESTION,
                title="建议增加真实性评估",
                description="PBL应该包含真实性评估方法",
                suggestion="考虑加入表现性评估、作品集评估等真实性评估方法",
                score_impact=5
            ))
            score -= 5
        
        return issues, max(0, score)
    
    def _check_assessment_design(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查评估设计"""
        issues = []
        score = 100
        
        if not course.assessments or len(course.assessments) == 0:
            issues.append(QualityIssue(
                category="评估设计",
                severity=CheckSeverity.CRITICAL,
                title="缺少评估方案",
                description="课程必须包含评估设计",
                suggestion="请添加多样化的评估方法，包括形成性评估和总结性评估",
                score_impact=30
            ))
            return issues, 0
        
        assessments = course.assessments
        assessment_types = [assess.type for assess in assessments if assess.type]
        
        # 检查评估多样性
        unique_types = set(assessment_types)
        if len(unique_types) < 2:
            issues.append(QualityIssue(
                category="评估设计",
                severity=CheckSeverity.WARNING,
                title="评估方法单一",
                description="建议使用多种评估方法",
                suggestion="考虑结合形成性评估、总结性评估、同伴评估等多种方法",
                score_impact=10
            ))
            score -= 10
        
        # 检查评估标准
        for i, assessment in enumerate(assessments):
            if not assessment.criteria:
                issues.append(QualityIssue(
                    category="评估设计",
                    severity=CheckSeverity.WARNING,
                    title=f"评估{i+1}缺少评估标准",
                    description="每个评估任务都应该有明确的评估标准",
                    suggestion="请为评估任务制定清晰、可操作的评估标准",
                    location=f"评估{i+1}",
                    score_impact=8
                ))
                score -= 8
            
            if not assessment.rubric:
                issues.append(QualityIssue(
                    category="评估设计",
                    severity=CheckSeverity.SUGGESTION,
                    title=f"建议为评估{i+1}添加量规",
                    description="评估量规有助于提高评估的一致性",
                    suggestion="考虑为重要的评估任务制定详细的评估量规",
                    location=f"评估{i+1}",
                    score_impact=3
                ))
                score -= 3
        
        return issues, max(0, score)
    
    def _check_resource_adequacy(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查资源充足性"""
        issues = []
        score = 100
        
        # 检查必需资源
        if not course.required_resources:
            issues.append(QualityIssue(
                category="资源配置",
                severity=CheckSeverity.WARNING,
                title="缺少必需资源说明",
                description="应该明确课程实施所需的基本资源",
                suggestion="请列出课程实施必需的资源，如材料、工具、场地等",
                score_impact=10
            ))
            score -= 10
        
        # 检查推荐资源
        if not course.recommended_resources:
            issues.append(QualityIssue(
                category="资源配置",
                severity=CheckSeverity.SUGGESTION,
                title="建议提供推荐资源",
                description="推荐资源可以丰富学习体验",
                suggestion="考虑提供额外的学习资源，如参考书籍、网站、视频等",
                score_impact=5
            ))
            score -= 5
        
        # 检查技术要求
        if not course.technology_requirements:
            issues.append(QualityIssue(
                category="资源配置",
                severity=CheckSeverity.SUGGESTION,
                title="建议明确技术要求",
                description="明确的技术要求有助于课程准备",
                suggestion="如果课程涉及技术工具，请明确技术要求和规格",
                score_impact=5
            ))
            score -= 5
        
        # 检查资源与活动的对应性
        if course.lessons:
            lessons_with_materials = [l for l in course.lessons if l.materials]
            if len(lessons_with_materials) < len(course.lessons) * 0.5:
                issues.append(QualityIssue(
                    category="资源配置",
                    severity=CheckSeverity.WARNING,
                    title="部分课时缺少材料说明",
                    description="超过一半的课时没有明确所需材料",
                    suggestion="请为每个课时明确所需的学习材料和工具",
                    score_impact=15
                ))
                score -= 15
        
        return issues, max(0, score)
    
    def _check_scaffolding_support(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查支架支持"""
        issues = []
        score = 100
        
        if not course.scaffolding_supports:
            issues.append(QualityIssue(
                category="支架支持",
                severity=CheckSeverity.WARNING,
                title="缺少支架支持设计",
                description="PBL课程应该提供适当的学习支架",
                suggestion="请设计支架支持策略，如学习指南、检查清单、模板等",
                score_impact=15
            ))
            score -= 15
        
        # 检查教师准备
        if not course.teacher_preparation:
            issues.append(QualityIssue(
                category="支架支持",
                severity=CheckSeverity.WARNING,
                title="缺少教师准备指南",
                description="应该为教师提供实施指导",
                suggestion="请提供教师准备的具体建议和注意事项",
                score_impact=10
            ))
            score -= 10
        
        # 检查教学策略
        if not course.teaching_strategies:
            issues.append(QualityIssue(
                category="支架支持",
                severity=CheckSeverity.SUGGESTION,
                title="建议明确教学策略",
                description="明确的教学策略有助于课程实施",
                suggestion="请说明推荐的教学方法和策略",
                score_impact=8
            ))
            score -= 8
        
        return issues, max(0, score)
    
    def _check_differentiation(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查差异化教学"""
        issues = []
        score = 100
        
        if not course.differentiation_strategies:
            issues.append(QualityIssue(
                category="差异化教学",
                severity=CheckSeverity.WARNING,
                title="缺少差异化策略",
                description="应该考虑不同学习者的需求",
                suggestion="请提供针对不同能力水平学生的差异化教学策略",
                score_impact=20
            ))
            score -= 20
        
        # 检查班级规模设置的合理性
        if course.class_size_max and course.class_size_min:
            if course.class_size_max - course.class_size_min > 20:
                issues.append(QualityIssue(
                    category="差异化教学",
                    severity=CheckSeverity.SUGGESTION,
                    title="班级规模跨度较大",
                    description=f"班级规模从{course.class_size_min}到{course.class_size_max}人",
                    suggestion="较大的班级规模跨度需要更多的差异化策略",
                    score_impact=5
                ))
                score -= 5
        
        return issues, max(0, score)
    
    def _check_authentic_context(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查真实性情境"""
        issues = []
        score = 100
        
        # 检查项目背景的真实性
        if course.project_context:
            context = course.project_context.lower()
            authentic_indicators = ['社区', '真实', '实际', '现实', '社会', '企业', '机构']
            
            if not any(indicator in context for indicator in authentic_indicators):
                issues.append(QualityIssue(
                    category="真实性情境",
                    severity=CheckSeverity.SUGGESTION,
                    title="项目背景可以更加真实",
                    description="项目背景更贴近真实世界会提高学习意义",
                    suggestion="考虑结合社区、企业或实际问题来设计项目背景",
                    score_impact=10
                ))
                score -= 10
        
        # 检查最终产品的真实性
        if course.final_products:
            products_text = ' '.join(course.final_products).lower()
            real_world_indicators = ['展示', '发布', '应用', '解决', '服务', '帮助']
            
            if any(indicator in products_text for indicator in real_world_indicators):
                score += 10  # 奖励分
            else:
                issues.append(QualityIssue(
                    category="真实性情境",
                    severity=CheckSeverity.SUGGESTION,
                    title="最终产品可以更具实用性",
                    description="最终产品能够服务真实需求会更有意义",
                    suggestion="考虑让最终产品能够解决真实问题或服务社区需求",
                    score_impact=5
                ))
                score -= 5
        
        return issues, max(0, min(110, score))  # 允许超过100分
    
    def _check_reflection_opportunities(self, course: Course) -> Tuple[List[QualityIssue], float]:
        """检查反思机会"""
        issues = []
        score = 100
        
        # 检查里程碑设置
        if not course.milestones or len(course.milestones) == 0:
            issues.append(QualityIssue(
                category="反思机会",
                severity=CheckSeverity.WARNING,
                title="缺少学习里程碑",
                description="学习里程碑有助于学生监控学习进度",
                suggestion="请设置关键的学习里程碑，提供反思和调整的机会",
                score_impact=15
            ))
            score -= 15
        
        # 检查课时中的反思活动
        if course.lessons:
            lessons_with_reflection = []
            for lesson in course.lessons:
                if lesson.activities:
                    activities_text = ' '.join(lesson.activities).lower()
                    if any(word in activities_text for word in ['反思', '总结', '回顾', '评价']):
                        lessons_with_reflection.append(lesson)
            
            reflection_ratio = len(lessons_with_reflection) / len(course.lessons)
            if reflection_ratio < 0.3:
                issues.append(QualityIssue(
                    category="反思机会",
                    severity=CheckSeverity.SUGGESTION,
                    title="反思活动偏少",
                    description=f"只有{len(lessons_with_reflection)}个课时包含反思活动",
                    suggestion="建议在更多课时中加入反思和总结活动",
                    score_impact=10
                ))
                score -= 10
        
        return issues, max(0, score)
    
    def _calculate_overall_score(self, category_scores: Dict[str, float], issues: List[QualityIssue]) -> float:
        """计算总体评分"""
        if not category_scores:
            return 0
        
        # 基础分数（各类别平均分）
        base_score = sum(category_scores.values()) / len(category_scores)
        
        # 根据问题严重程度调整
        critical_issues = [i for i in issues if i.severity == CheckSeverity.CRITICAL]
        warning_issues = [i for i in issues if i.severity == CheckSeverity.WARNING]
        
        # 严重问题额外扣分
        if len(critical_issues) > 3:
            base_score -= 10
        
        # 警告问题过多扣分
        if len(warning_issues) > 5:
            base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """确定质量等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 70:
            return QualityLevel.ACCEPTABLE
        elif score >= 60:
            return QualityLevel.NEEDS_IMPROVEMENT
        else:
            return QualityLevel.POOR
    
    def _identify_strengths(self, course: Course, category_scores: Dict[str, float]) -> List[str]:
        """识别优势点"""
        strengths = []
        
        # 基于评分识别优势
        for category, score in category_scores.items():
            if score >= 90:
                strengths.append(f"{category}设计优秀")
        
        # 基于内容识别优势
        if course.driving_question and len(course.driving_question) > 30:
            strengths.append("驱动性问题设计充分")
        
        if course.final_products and len(course.final_products) >= 3:
            strengths.append("最终产品设计丰富")
        
        if course.learning_objectives and 3 <= len(course.learning_objectives) <= 5:
            strengths.append("学习目标数量适中")
        
        if course.phases and len(course.phases) >= 3:
            strengths.append("课程阶段规划清晰")
        
        return strengths[:5]  # 最多返回5个优势点
    
    def _generate_recommendations(self, issues: List[QualityIssue]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重程度分组
        critical_issues = [i for i in issues if i.severity == CheckSeverity.CRITICAL]
        warning_issues = [i for i in issues if i.severity == CheckSeverity.WARNING]
        
        # 优先处理严重问题
        if critical_issues:
            recommendations.append("优先解决关键问题：" + "；".join([i.title for i in critical_issues[:3]]))
        
        # 处理警告问题
        if warning_issues:
            recommendations.append("改进以下方面：" + "；".join([i.title for i in warning_issues[:3]]))
        
        # 通用建议
        if any(i.category == "PBL对齐" for i in issues):
            recommendations.append("加强PBL特征：确保有驱动性问题、最终产品和真实情境")
        
        if any(i.category == "评估设计" for i in issues):
            recommendations.append("完善评估设计：增加多样化的评估方法和明确的评估标准")
        
        if any(i.category == "课程结构" for i in issues):
            recommendations.append("优化课程结构：确保课时安排合理、活动多样化")
        
        return recommendations[:5]  # 最多返回5个建议


# 全局服务实例
quality_checker = CourseQualityChecker()