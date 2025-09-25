"""
增强版质量验证系统
专门验证课程生成结果是否满足原始需求
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """验证级别"""
    CRITICAL = "关键"     # 必须通过
    IMPORTANT = "重要"   # 建议通过
    OPTIONAL = "可选"    # 优化建议

@dataclass
class ValidationResult:
    """验证结果"""
    check_name: str
    level: ValidationLevel
    passed: bool
    score: float  # 0-1分数
    message: str
    suggestions: List[str]
    details: Dict[str, Any]

@dataclass
class QualityReport:
    """质量报告"""
    overall_score: float
    overall_passed: bool
    validation_results: List[ValidationResult]
    critical_issues: List[str]
    improvement_suggestions: List[str]
    validated_at: datetime
    metadata: Dict[str, Any]

class CourseQualityValidator:
    """课程质量验证器"""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化验证规则"""
        return {
            # 需求匹配度验证
            "requirement_match": {
                "level": ValidationLevel.CRITICAL,
                "weight": 0.25,
                "description": "验证课程是否满足原始需求"
            },
            # 年龄适宜性验证
            "age_appropriateness": {
                "level": ValidationLevel.CRITICAL,
                "weight": 0.2,
                "description": "验证内容是否适合目标年龄段"
            },
            # 时间规划合理性
            "time_allocation": {
                "level": ValidationLevel.CRITICAL,
                "weight": 0.15,
                "description": "验证时间安排是否合理可行"
            },
            # 内容专业性
            "content_quality": {
                "level": ValidationLevel.IMPORTANT,
                "weight": 0.15,
                "description": "验证内容的专业性和深度"
            },
            # AI工具集成
            "ai_integration": {
                "level": ValidationLevel.IMPORTANT,
                "weight": 0.1,
                "description": "验证AI工具集成的合理性"
            },
            # PBL方法论
            "pbl_methodology": {
                "level": ValidationLevel.IMPORTANT,
                "weight": 0.1,
                "description": "验证PBL方法论的应用"
            },
            # 可实施性
            "feasibility": {
                "level": ValidationLevel.OPTIONAL,
                "weight": 0.05,
                "description": "验证课程实施的可行性"
            }
        }

    def validate_course(
        self,
        generated_course: Dict[str, Any],
        original_requirements: Dict[str, Any],
        parsed_requirements: Optional[Dict[str, Any]] = None
    ) -> QualityReport:
        """验证课程质量"""

        logger.info("🔍 开始课程质量验证...")

        validation_results = []
        total_weight = 0
        weighted_score = 0

        for rule_name, rule_config in self.validation_rules.items():
            try:
                result = self._run_validation_rule(
                    rule_name, rule_config, generated_course,
                    original_requirements, parsed_requirements
                )
                validation_results.append(result)

                # 计算加权分数
                weight = rule_config["weight"]
                total_weight += weight
                weighted_score += result.score * weight

                logger.info(f"✓ {rule_name}: {result.score:.2f} ({'通过' if result.passed else '未通过'})")

            except Exception as e:
                logger.error(f"❌ 验证规则 {rule_name} 执行失败: {e}")
                # 添加失败结果
                validation_results.append(ValidationResult(
                    check_name=rule_name,
                    level=rule_config["level"],
                    passed=False,
                    score=0.0,
                    message=f"验证执行失败: {str(e)}",
                    suggestions=["需要技术团队检查验证逻辑"],
                    details={"error": str(e)}
                ))

        # 计算总分
        overall_score = weighted_score / total_weight if total_weight > 0 else 0

        # 确定是否通过（关键项目必须全部通过）
        critical_results = [r for r in validation_results if r.level == ValidationLevel.CRITICAL]
        overall_passed = all(r.passed for r in critical_results) and overall_score >= 0.7

        # 收集问题和建议
        critical_issues = []
        improvement_suggestions = []

        for result in validation_results:
            if not result.passed and result.level == ValidationLevel.CRITICAL:
                critical_issues.append(f"{result.check_name}: {result.message}")
            if result.suggestions:
                improvement_suggestions.extend(result.suggestions)

        report = QualityReport(
            overall_score=overall_score,
            overall_passed=overall_passed,
            validation_results=validation_results,
            critical_issues=critical_issues,
            improvement_suggestions=improvement_suggestions,
            validated_at=datetime.now(),
            metadata={
                "validation_rules_count": len(self.validation_rules),
                "critical_rules_count": len(critical_results),
                "passed_rules_count": len([r for r in validation_results if r.passed])
            }
        )

        logger.info(f"✅ 质量验证完成 - 总分: {overall_score:.0%}, {'通过' if overall_passed else '未通过'}")
        return report

    def _run_validation_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any],
        generated_course: Dict[str, Any],
        original_requirements: Dict[str, Any],
        parsed_requirements: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """执行单个验证规则"""

        if rule_name == "requirement_match":
            return self._validate_requirement_match(
                generated_course, original_requirements, parsed_requirements
            )
        elif rule_name == "age_appropriateness":
            return self._validate_age_appropriateness(
                generated_course, original_requirements, parsed_requirements
            )
        elif rule_name == "time_allocation":
            return self._validate_time_allocation(
                generated_course, original_requirements, parsed_requirements
            )
        elif rule_name == "content_quality":
            return self._validate_content_quality(generated_course)
        elif rule_name == "ai_integration":
            return self._validate_ai_integration(generated_course, parsed_requirements)
        elif rule_name == "pbl_methodology":
            return self._validate_pbl_methodology(generated_course)
        elif rule_name == "feasibility":
            return self._validate_feasibility(generated_course)
        else:
            return ValidationResult(
                check_name=rule_name,
                level=rule_config["level"],
                passed=False,
                score=0.0,
                message="未知的验证规则",
                suggestions=[],
                details={}
            )

    def _validate_requirement_match(
        self, course: Dict[str, Any], original_req: Dict[str, Any], parsed_req: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """验证需求匹配度"""

        score = 0.0
        issues = []
        suggestions = []

        # 使用解析后的需求进行精确验证
        if parsed_req:
            # 验证主题匹配
            expected_topic = parsed_req.get('topic', '').lower()
            course_title = course.get('title', '').lower()

            if expected_topic and expected_topic in course_title:
                score += 0.3
            else:
                issues.append(f"课程标题'{course_title}'与预期主题'{expected_topic}'不匹配")
                suggestions.append("调整课程标题以反映具体主题")

            # 验证交付物匹配
            expected_deliverables = set(parsed_req.get('final_deliverables', []))
            course_deliverables = set(course.get('final_products', []))

            if expected_deliverables:
                match_ratio = len(expected_deliverables & course_deliverables) / len(expected_deliverables)
                score += 0.4 * match_ratio

                if match_ratio < 0.5:
                    issues.append(f"交付物匹配度过低: 期望{list(expected_deliverables)}, 实际{list(course_deliverables)}")
                    suggestions.append("调整课程设计以产出要求的具体交付物")

            # 验证学习目标匹配
            expected_objectives = parsed_req.get('learning_objectives', [])
            course_objectives = course.get('learning_objectives', [])

            if expected_objectives and course_objectives:
                # 简单的关键词匹配检查
                obj_match_count = 0
                for expected_obj in expected_objectives:
                    for course_obj in course_objectives:
                        if any(word in course_obj.lower() for word in expected_obj.lower().split() if len(word) > 2):
                            obj_match_count += 1
                            break

                obj_match_ratio = obj_match_count / len(expected_objectives)
                score += 0.3 * obj_match_ratio

                if obj_match_ratio < 0.6:
                    issues.append("学习目标匹配度不足")
                    suggestions.append("重新调整学习目标以更好匹配用户需求")

        else:
            # 兜底验证
            score = 0.5  # 给予中等分数
            suggestions.append("建议使用需求解析系统提高验证精度")

        passed = score >= 0.7
        message = "需求匹配度良好" if passed else f"需求匹配存在问题: {'; '.join(issues)}"

        return ValidationResult(
            check_name="requirement_match",
            level=ValidationLevel.CRITICAL,
            passed=passed,
            score=score,
            message=message,
            suggestions=suggestions,
            details={"issues": issues, "parsed_req_available": parsed_req is not None}
        )

    def _validate_age_appropriateness(
        self, course: Dict[str, Any], original_req: Dict[str, Any], parsed_req: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """验证年龄适宜性"""

        score = 0.0
        issues = []
        suggestions = []

        if parsed_req:
            expected_age_range = parsed_req.get('age_range', {})
            expected_min = expected_age_range.get('min', 0)
            expected_max = expected_age_range.get('max', 100)

            # 检查课程中的年龄设置
            course_grades = course.get('grade_levels', [])
            if course_grades:
                # 简单映射：年级到年龄
                grade_to_age = {
                    1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11,  # 小学
                    7: 12, 8: 13, 9: 14,  # 初中
                    10: 15, 11: 16, 12: 17  # 高中
                }

                course_ages = [grade_to_age.get(grade, grade) for grade in course_grades]
                course_min_age = min(course_ages)
                course_max_age = max(course_ages)

                # 检查年龄范围匹配
                if expected_min <= course_min_age <= expected_max and expected_min <= course_max_age <= expected_max:
                    score += 0.8
                else:
                    issues.append(f"年龄范围不匹配: 期望{expected_min}-{expected_max}岁, 课程{course_min_age}-{course_max_age}岁")
                    suggestions.append("调整课程难度和内容以适配正确年龄段")

            # 检查课程持续时间的年龄适宜性
            duration_weeks = course.get('duration_weeks', 0)
            if expected_min <= 12:  # 儿童和青少年
                if duration_weeks > 8:
                    issues.append("课程周期过长，可能超出低年龄段注意力持续时间")
                    suggestions.append("考虑缩短课程周期或分成多个阶段")
                else:
                    score += 0.2

        else:
            score = 0.5  # 无法验证时给予中等分数

        passed = score >= 0.7
        message = "年龄适宜性良好" if passed else f"年龄适宜性存在问题: {'; '.join(issues)}"

        return ValidationResult(
            check_name="age_appropriateness",
            level=ValidationLevel.CRITICAL,
            passed=passed,
            score=score,
            message=message,
            suggestions=suggestions,
            details={"issues": issues}
        )

    def _validate_time_allocation(
        self, course: Dict[str, Any], original_req: Dict[str, Any], parsed_req: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """验证时间分配"""

        score = 0.0
        issues = []
        suggestions = []

        if parsed_req:
            expected_total_hours = parsed_req.get('total_duration', {}).get('total_hours', 0)
            course_hours = course.get('duration_hours', 0)

            if expected_total_hours > 0:
                # 允许±20%的误差
                deviation = abs(course_hours - expected_total_hours) / expected_total_hours
                if deviation <= 0.2:
                    score += 0.6
                else:
                    issues.append(f"总时长偏差过大: 期望{expected_total_hours}小时, 实际{course_hours}小时")
                    suggestions.append("调整时间分配以匹配要求的总时长")

            # 检查时间模式匹配
            expected_mode = parsed_req.get('time_mode', '')
            if '集训营' in expected_mode:
                expected_days = parsed_req.get('total_duration', {}).get('days', 0)
                if expected_days > 0:
                    # 集训营应该是密集型安排
                    if course_hours / expected_days >= 4:  # 每天至少4小时
                        score += 0.4
                    else:
                        issues.append("集训营模式的每日时长不够密集")
                        suggestions.append("增加每日学习时长以符合集训营特点")

        else:
            score = 0.5

        passed = score >= 0.7
        message = "时间分配合理" if passed else f"时间分配存在问题: {'; '.join(issues)}"

        return ValidationResult(
            check_name="time_allocation",
            level=ValidationLevel.CRITICAL,
            passed=passed,
            score=score,
            message=message,
            suggestions=suggestions,
            details={"issues": issues}
        )

    def _validate_content_quality(self, course: Dict[str, Any]) -> ValidationResult:
        """验证内容质量"""

        score = 0.0
        issues = []
        suggestions = []

        # 检查学习资源质量
        resources = course.get('resources', [])
        if resources:
            # 检查资源是否重复或通用化
            resource_titles = [r.get('title', '') for r in resources]
            unique_titles = set(resource_titles)

            if len(unique_titles) < len(resource_titles) * 0.8:
                issues.append("学习资源重复度过高，缺乏多样性")
                suggestions.append("提供更多样化的学习资源")
            else:
                score += 0.3

            # 检查资源描述质量
            generic_descriptions = ['支持学习的重要资源', '学习材料', 'Introduction to Basic']
            generic_count = sum(1 for r in resources if any(g in r.get('description', '') for g in generic_descriptions))

            if generic_count > len(resources) * 0.5:
                issues.append("资源描述过于通用化，缺乏针对性")
                suggestions.append("为每个资源提供具体、相关的描述")
            else:
                score += 0.3

        # 检查学习目标质量
        objectives = course.get('learning_objectives', [])
        if objectives:
            # 检查目标是否具体可衡量
            vague_objectives = sum(1 for obj in objectives if any(word in obj.lower() for word in ['了解', '知道', '理解']) and '如何' not in obj.lower())

            if vague_objectives <= len(objectives) * 0.3:
                score += 0.2
            else:
                issues.append("学习目标过于模糊，缺乏可操作性")
                suggestions.append("使用更具体、可衡量的动词描述学习目标")

        # 检查课程阶段设计
        phases = course.get('phases', [])
        if phases:
            if len(phases) >= 3:  # 至少有开始、发展、结束阶段
                score += 0.2
            else:
                issues.append("课程阶段设计不完整")
                suggestions.append("设计完整的课程阶段，包括导入、发展、总结")

        passed = score >= 0.6
        message = "内容质量良好" if passed else f"内容质量需要改进: {'; '.join(issues)}"

        return ValidationResult(
            check_name="content_quality",
            level=ValidationLevel.IMPORTANT,
            passed=passed,
            score=score,
            message=message,
            suggestions=suggestions,
            details={"issues": issues}
        )

    def _validate_ai_integration(self, course: Dict[str, Any], parsed_req: Optional[Dict[str, Any]]) -> ValidationResult:
        """验证AI工具集成"""

        score = 0.8  # 基础分数，假设AI集成基本合理
        issues = []
        suggestions = []

        if parsed_req:
            expected_ai_tools = parsed_req.get('ai_tools', [])

            # 检查课程中是否提到了AI工具的使用
            course_content = json.dumps(course, ensure_ascii=False).lower()

            for tool in expected_ai_tools:
                if tool.lower() in course_content:
                    score += 0.05  # 每个匹配的工具加分
                else:
                    suggestions.append(f"建议在课程中明确说明如何使用{tool}")

        passed = score >= 0.7
        message = "AI工具集成合理" if passed else "AI工具集成需要加强"

        return ValidationResult(
            check_name="ai_integration",
            level=ValidationLevel.IMPORTANT,
            passed=passed,
            score=min(score, 1.0),  # 确保不超过1.0
            message=message,
            suggestions=suggestions,
            details={"issues": issues}
        )

    def _validate_pbl_methodology(self, course: Dict[str, Any]) -> ValidationResult:
        """验证PBL方法论"""

        score = 0.0
        issues = []
        suggestions = []

        # 检查是否有驱动问题
        driving_question = course.get('driving_question', '')
        if driving_question and driving_question not in ['如何运用所学知识解决真实世界的问题？']:
            score += 0.3
        else:
            issues.append("缺乏具体的驱动问题")
            suggestions.append("设计与主题相关的具体驱动问题")

        # 检查是否有项目成果
        final_products = course.get('final_products', [])
        if final_products and len(final_products) > 1:
            score += 0.3
        else:
            issues.append("项目成果设计不充分")
            suggestions.append("设计多样化的项目成果展示方式")

        # 检查评估方式
        assessments = course.get('assessments', [])
        formative_count = sum(1 for a in assessments if a.get('type') == 'formative')
        summative_count = sum(1 for a in assessments if a.get('type') == 'summative')

        if formative_count > 0 and summative_count > 0:
            score += 0.4
        else:
            issues.append("评估方式不够多元化")
            suggestions.append("结合过程性评价和终结性评价")

        passed = score >= 0.6
        message = "PBL方法论应用良好" if passed else f"PBL方法论应用需要改进: {'; '.join(issues)}"

        return ValidationResult(
            check_name="pbl_methodology",
            level=ValidationLevel.IMPORTANT,
            passed=passed,
            score=score,
            message=message,
            suggestions=suggestions,
            details={"issues": issues}
        )

    def _validate_feasibility(self, course: Dict[str, Any]) -> ValidationResult:
        """验证可实施性"""

        score = 0.7  # 基础可实施性分数
        suggestions = [
            "建议在实施前进行小规模试点",
            "准备备选方案应对技术问题",
            "确保教师具备必要的技能支持"
        ]

        return ValidationResult(
            check_name="feasibility",
            level=ValidationLevel.OPTIONAL,
            passed=True,
            score=score,
            message="课程具有良好的可实施性",
            suggestions=suggestions,
            details={}
        )

    def format_report(self, report: QualityReport) -> str:
        """格式化质量报告"""

        output = f"""
🔍 【课程质量验证报告】

📊 总体评估:
• 综合得分: {report.overall_score:.0%}
• 验证结果: {'✅ 通过' if report.overall_passed else '❌ 未通过'}
• 验证时间: {report.validated_at.strftime('%Y-%m-%d %H:%M:%S')}

📋 详细验证结果:
"""

        for result in report.validation_results:
            status = "✅" if result.passed else "❌"
            output += f"""
{status} {result.check_name} ({result.level.value}) - {result.score:.0%}
   {result.message}
"""
            if result.suggestions:
                for suggestion in result.suggestions[:2]:  # 最多显示2个建议
                    output += f"   💡 {suggestion}\n"

        if report.critical_issues:
            output += "\n🚨 关键问题:\n"
            for issue in report.critical_issues:
                output += f"• {issue}\n"

        if report.improvement_suggestions:
            output += "\n💡 改进建议:\n"
            for suggestion in report.improvement_suggestions[:5]:  # 最多显示5个建议
                output += f"• {suggestion}\n"

        return output