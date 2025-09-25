"""
增强版需求解析引擎
专门用于精准解析用户课程设计需求，确保智能体理解准确性
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgeGroup(Enum):
    """年龄组枚举"""
    EARLY_CHILDHOOD = "早期儿童 (3-6岁)"
    ELEMENTARY = "小学生 (6-12岁)"
    MIDDLE_SCHOOL = "中学生 (12-15岁)"
    HIGH_SCHOOL = "高中生 (15-18岁)"
    YOUNG_ADULT = "青年 (18-25岁)"
    ADULT = "成年 (25+岁)"

class TimeMode(Enum):
    """时间模式枚举"""
    INTENSIVE_CAMP = "集训营模式"  # 几天密集训练
    WEEKLY_COURSE = "周课程模式"  # 按周分布
    SEMESTER_LONG = "学期课程模式"  # 整学期
    WORKSHOP = "工作坊模式"  # 单次活动

class InstitutionType(Enum):
    """机构类型枚举"""
    MAKER_SPACE = "创客空间"
    TRADITIONAL_SCHOOL = "传统学校"
    TRAINING_CENTER = "培训机构"
    COMMUNITY_CENTER = "社区中心"

@dataclass
class ParsedRequirement:
    """解析后的标准化需求"""

    # 基础信息
    topic: str
    audience: str
    age_group: AgeGroup
    age_range: Dict[str, int]  # {"min": 8, "max": 15}

    # 时间规划
    time_mode: TimeMode
    total_duration: Dict[str, int]  # {"days": 3, "hours_per_day": 6, "total_hours": 18}

    # 学习目标
    learning_objectives: List[str]

    # 技能要求
    target_skills: List[str]  # 如 ["3D建模", "AI动画", "创新思维"]
    ai_tools: List[str]  # 具体AI工具

    # 成果要求
    final_deliverables: List[str]

    # 约束条件
    class_size: Optional[int]
    equipment: List[str]
    budget_level: str  # "充足", "中等", "有限"

    # 机构环境
    institution_type: InstitutionType
    teaching_context: str

    # 特殊要求
    special_requirements: Dict[str, Any]

    # 元数据
    parsed_at: datetime
    confidence_score: float  # 解析置信度 0-1
    validation_passed: bool


class RequirementParser:
    """需求解析引擎"""

    def __init__(self):
        # 年龄识别模式
        self.age_patterns = {
            r'(\d+)\s*[-到至]\s*(\d+)\s*岁': 'range',
            r'(\d+)\s*岁': 'single',
            r'小学生?': (AgeGroup.ELEMENTARY, {"min": 6, "max": 12}),
            r'中学生?|初中生?': (AgeGroup.MIDDLE_SCHOOL, {"min": 12, "max": 15}),
            r'高中生?': (AgeGroup.HIGH_SCHOOL, {"min": 15, "max": 18}),
            r'幼儿|学前': (AgeGroup.EARLY_CHILDHOOD, {"min": 3, "max": 6}),
        }

        # 时间模式识别
        self.time_patterns = {
            r'(\d+)\s*天.*集训|训练营|夏令营|冬令营': TimeMode.INTENSIVE_CAMP,
            r'(\d+)\s*周': TimeMode.WEEKLY_COURSE,
            r'学期|整学期': TimeMode.SEMESTER_LONG,
            r'工作坊|单次|一次性': TimeMode.WORKSHOP,
        }

        # 技能关键词库
        self.skill_keywords = {
            '3d建模': ['3D建模', 'blender', 'fusion360', '立体建模', '三维建模'],
            '3d打印': ['3D打印', '打印机', '3d printer', '立体打印'],
            'ai动画': ['AI动画', 'ai视频', '虚实融合', '动画制作', 'ai生成视频'],
            '创新思维': ['创新思维', '创造力', '想象力', '创意思维'],
            'ai协作': ['AI协作', '人机协作', 'AI对话', '智能助手'],
            '科学探索': ['科学探索', '科学实验', '探索精神', '科学思维'],
            '问题解决': ['问题解决', '解决问题', 'problem solving'],
        }

        # AI工具库
        self.ai_tool_keywords = {
            'chatgpt': ['chatgpt', 'gpt', '对话ai'],
            'claude': ['claude', 'anthropic'],
            'midjourney': ['midjourney', 'mj', '图像生成'],
            'stable_diffusion': ['stable diffusion', 'sd', 'ai绘图'],
            'runway': ['runway', 'ai视频'],
            'blender_ai': ['blender', '3d建模ai'],
        }

    def parse_requirements(self, raw_requirements: Dict[str, Any]) -> ParsedRequirement:
        """解析原始需求为标准化格式"""

        logger.info(f"🔍 开始解析课程需求: {raw_requirements.get('topic', '未知主题')}")

        try:
            # 1. 解析基础信息
            topic = self._extract_topic(raw_requirements)
            audience = self._extract_audience(raw_requirements)
            age_group, age_range = self._parse_age_info(raw_requirements)

            # 2. 解析时间规划
            time_mode, duration_info = self._parse_time_info(raw_requirements)

            # 3. 解析学习目标和技能
            learning_objectives = self._extract_learning_objectives(raw_requirements)
            target_skills = self._extract_target_skills(raw_requirements)
            ai_tools = self._extract_ai_tools(raw_requirements)

            # 4. 解析成果要求
            final_deliverables = self._extract_deliverables(raw_requirements)

            # 5. 解析约束条件
            class_size = self._extract_class_size(raw_requirements)
            equipment = self._extract_equipment(raw_requirements)
            budget_level = self._extract_budget_level(raw_requirements)

            # 6. 解析机构环境
            institution_type = self._parse_institution_type(raw_requirements)
            teaching_context = self._extract_teaching_context(raw_requirements)

            # 7. 解析特殊要求
            special_requirements = self._extract_special_requirements(raw_requirements)

            # 8. 计算解析置信度
            confidence_score = self._calculate_confidence_score(raw_requirements)

            # 9. 创建解析结果
            parsed_req = ParsedRequirement(
                topic=topic,
                audience=audience,
                age_group=age_group,
                age_range=age_range,
                time_mode=time_mode,
                total_duration=duration_info,
                learning_objectives=learning_objectives,
                target_skills=target_skills,
                ai_tools=ai_tools,
                final_deliverables=final_deliverables,
                class_size=class_size,
                equipment=equipment,
                budget_level=budget_level,
                institution_type=institution_type,
                teaching_context=teaching_context,
                special_requirements=special_requirements,
                parsed_at=datetime.now(),
                confidence_score=confidence_score,
                validation_passed=False  # 待验证
            )

            # 10. 验证解析结果
            parsed_req.validation_passed = self._validate_parsed_requirement(parsed_req, raw_requirements)

            logger.info(f"✅ 需求解析完成，置信度: {confidence_score:.2f}")
            return parsed_req

        except Exception as e:
            logger.error(f"❌ 需求解析失败: {e}")
            # 返回最基础的解析结果
            return self._create_fallback_requirement(raw_requirements)

    def _extract_topic(self, raw_req: Dict[str, Any]) -> str:
        """提取主题"""
        return raw_req.get('topic', raw_req.get('title', '未指定主题'))

    def _extract_audience(self, raw_req: Dict[str, Any]) -> str:
        """提取目标受众"""
        return raw_req.get('audience', raw_req.get('participants', '未指定受众'))

    def _parse_age_info(self, raw_req: Dict[str, Any]) -> Tuple[AgeGroup, Dict[str, int]]:
        """解析年龄信息"""

        # 优先从age_group字段获取
        if 'age_group' in raw_req:
            age_info = raw_req['age_group']
            if isinstance(age_info, dict):
                min_age = age_info.get('min', 10)
                max_age = age_info.get('max', 15)
                return self._determine_age_group(min_age, max_age), {"min": min_age, "max": max_age}

        # 从文本中解析年龄
        text_content = str(raw_req.get('audience', '')) + ' ' + str(raw_req.get('context', ''))

        for pattern, result in self.age_patterns.items():
            if isinstance(result, tuple):  # 预定义年龄组
                if re.search(pattern, text_content, re.IGNORECASE):
                    age_group, age_range = result
                    return age_group, age_range
            elif result == 'range':
                match = re.search(pattern, text_content)
                if match:
                    min_age, max_age = int(match.group(1)), int(match.group(2))
                    return self._determine_age_group(min_age, max_age), {"min": min_age, "max": max_age}

        # 默认值
        return AgeGroup.MIDDLE_SCHOOL, {"min": 10, "max": 15}

    def _determine_age_group(self, min_age: int, max_age: int) -> AgeGroup:
        """根据年龄范围确定年龄组"""
        avg_age = (min_age + max_age) / 2

        if avg_age <= 6:
            return AgeGroup.EARLY_CHILDHOOD
        elif avg_age <= 12:
            return AgeGroup.ELEMENTARY
        elif avg_age <= 15:
            return AgeGroup.MIDDLE_SCHOOL
        elif avg_age <= 18:
            return AgeGroup.HIGH_SCHOOL
        elif avg_age <= 25:
            return AgeGroup.YOUNG_ADULT
        else:
            return AgeGroup.ADULT

    def _parse_time_info(self, raw_req: Dict[str, Any]) -> Tuple[TimeMode, Dict[str, int]]:
        """解析时间信息"""

        duration = raw_req.get('duration', {})
        context = str(raw_req.get('context', ''))

        # 优先从duration字段解析
        if isinstance(duration, dict):
            if 'days' in duration:
                days = duration['days']
                hours_per_day = duration.get('hours_per_day', 6)
                return TimeMode.INTENSIVE_CAMP, {
                    "days": days,
                    "hours_per_day": hours_per_day,
                    "total_hours": days * hours_per_day
                }
            elif 'weeks' in duration:
                weeks = duration['weeks']
                hours_per_week = duration.get('hours_per_week', 4)
                return TimeMode.WEEKLY_COURSE, {
                    "weeks": weeks,
                    "hours_per_week": hours_per_week,
                    "total_hours": weeks * hours_per_week
                }

        # 从文本中解析时间模式
        for pattern, time_mode in self.time_patterns.items():
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                if time_mode == TimeMode.INTENSIVE_CAMP:
                    days = int(match.group(1))
                    return time_mode, {"days": days, "hours_per_day": 6, "total_hours": days * 6}
                elif time_mode == TimeMode.WEEKLY_COURSE:
                    weeks = int(match.group(1))
                    return time_mode, {"weeks": weeks, "hours_per_week": 4, "total_hours": weeks * 4}

        # 默认返回周课程模式
        return TimeMode.WEEKLY_COURSE, {"weeks": 4, "hours_per_week": 4, "total_hours": 16}

    def _extract_learning_objectives(self, raw_req: Dict[str, Any]) -> List[str]:
        """提取学习目标"""
        objectives = raw_req.get('goals', raw_req.get('objectives', []))
        if isinstance(objectives, list):
            return objectives
        elif isinstance(objectives, str):
            return [objectives]
        else:
            return ["培养创新思维和实践能力", "掌握AI时代核心技能"]

    def _extract_target_skills(self, raw_req: Dict[str, Any]) -> List[str]:
        """提取目标技能"""
        all_text = json.dumps(raw_req, ensure_ascii=False).lower()
        detected_skills = []

        for skill, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword.lower() in all_text:
                    detected_skills.append(skill)
                    break

        return detected_skills or ["问题解决", "创新思维", "协作沟通"]

    def _extract_ai_tools(self, raw_req: Dict[str, Any]) -> List[str]:
        """提取AI工具"""
        all_text = json.dumps(raw_req, ensure_ascii=False).lower()
        detected_tools = []

        for tool, keywords in self.ai_tool_keywords.items():
            for keyword in keywords:
                if keyword.lower() in all_text:
                    detected_tools.append(tool)
                    break

        return detected_tools or ["chatgpt", "claude"]

    def _extract_deliverables(self, raw_req: Dict[str, Any]) -> List[str]:
        """提取最终交付物"""
        # 查找各种可能的交付物字段
        deliverables = (raw_req.get('final_deliverables', []) or
                       raw_req.get('deliverables', []) or
                       raw_req.get('outputs', []) or
                       [])

        if isinstance(deliverables, list) and deliverables:
            return deliverables

        # 从special_requirements中查找
        special_req = raw_req.get('special_requirements', {})
        if isinstance(special_req, dict):
            final_dels = special_req.get('final_deliverables', [])
            if final_dels:
                return final_dels

        # 根据主题推断默认交付物
        topic = self._extract_topic(raw_req).lower()
        if '月球' in topic and '装备' in topic:
            return ["月球装备设计方案", "3D打印装备实物", "AI动画展示视频", "装备使用说明书"]
        else:
            return ["项目报告", "作品展示", "学习反思"]

    def _extract_class_size(self, raw_req: Dict[str, Any]) -> Optional[int]:
        """提取班级规模"""
        # 查找各种可能的人数字段
        for field in ['class_size', 'participant_count', 'students_count', 'size']:
            if field in raw_req:
                return raw_req[field]

        # 从special_requirements中查找
        special_req = raw_req.get('special_requirements', {})
        if isinstance(special_req, dict) and 'class_size' in special_req:
            return special_req['class_size']

        return None

    def _extract_equipment(self, raw_req: Dict[str, Any]) -> List[str]:
        """提取可用设备"""
        constraints = raw_req.get('constraints', {})
        if isinstance(constraints, dict):
            equipment = constraints.get('equipment', [])
            if isinstance(equipment, str):
                return [equipment]
            elif isinstance(equipment, list):
                return equipment

        return ["计算机", "网络连接"]

    def _extract_budget_level(self, raw_req: Dict[str, Any]) -> str:
        """提取预算水平"""
        constraints = raw_req.get('constraints', {})
        if isinstance(constraints, dict):
            budget = constraints.get('budget', '中等')
            return budget

        return "中等"

    def _parse_institution_type(self, raw_req: Dict[str, Any]) -> InstitutionType:
        """解析机构类型"""
        context = str(raw_req.get('context', '')).lower()

        if any(word in context for word in ['创客', 'maker', '创客空间']):
            return InstitutionType.MAKER_SPACE
        elif any(word in context for word in ['学校', '中学', '小学', '高中']):
            return InstitutionType.TRADITIONAL_SCHOOL
        elif any(word in context for word in ['培训', '训练营', '夏令营', '冬令营']):
            return InstitutionType.TRAINING_CENTER
        else:
            return InstitutionType.TRAINING_CENTER  # 默认

    def _extract_teaching_context(self, raw_req: Dict[str, Any]) -> str:
        """提取教学环境"""
        return raw_req.get('context', '项目制学习环境')

    def _extract_special_requirements(self, raw_req: Dict[str, Any]) -> Dict[str, Any]:
        """提取特殊要求"""
        return raw_req.get('special_requirements', {})

    def _calculate_confidence_score(self, raw_req: Dict[str, Any]) -> float:
        """计算解析置信度"""
        score = 0.0
        total_checks = 0

        # 检查关键字段存在性
        key_fields = ['topic', 'audience', 'goals', 'context']
        for field in key_fields:
            total_checks += 1
            if field in raw_req and raw_req[field]:
                score += 0.2

        # 检查时间信息完整性
        total_checks += 1
        duration = raw_req.get('duration', {})
        if isinstance(duration, dict) and duration:
            score += 0.2

        # 检查特殊要求详细程度
        total_checks += 1
        special_req = raw_req.get('special_requirements', {})
        if isinstance(special_req, dict) and len(special_req) > 2:
            score += 0.2

        return min(score, 1.0)

    def _validate_parsed_requirement(self, parsed_req: ParsedRequirement, raw_req: Dict[str, Any]) -> bool:
        """验证解析结果"""
        try:
            # 检查必要字段
            if not parsed_req.topic or not parsed_req.audience:
                return False

            # 检查年龄合理性
            if parsed_req.age_range['min'] >= parsed_req.age_range['max']:
                return False

            # 检查时间合理性
            if parsed_req.total_duration.get('total_hours', 0) <= 0:
                return False

            # 检查学习目标数量
            if len(parsed_req.learning_objectives) == 0:
                return False

            return True

        except Exception as e:
            logger.warning(f"⚠️ 验证解析结果时出错: {e}")
            return False

    def _create_fallback_requirement(self, raw_req: Dict[str, Any]) -> ParsedRequirement:
        """创建兜底解析结果"""
        logger.warning("🔄 使用兜底解析方案")

        return ParsedRequirement(
            topic=raw_req.get('topic', '创新项目设计'),
            audience=raw_req.get('audience', '中学生'),
            age_group=AgeGroup.MIDDLE_SCHOOL,
            age_range={"min": 12, "max": 15},
            time_mode=TimeMode.WEEKLY_COURSE,
            total_duration={"weeks": 4, "hours_per_week": 4, "total_hours": 16},
            learning_objectives=["培养创新思维", "掌握基础技能"],
            target_skills=["问题解决", "创新思维"],
            ai_tools=["chatgpt"],
            final_deliverables=["项目报告", "作品展示"],
            class_size=None,
            equipment=["计算机"],
            budget_level="中等",
            institution_type=InstitutionType.TRAINING_CENTER,
            teaching_context="项目制学习",
            special_requirements={},
            parsed_at=datetime.now(),
            confidence_score=0.3,
            validation_passed=True
        )

    def generate_enhanced_prompt(self, parsed_req: ParsedRequirement) -> str:
        """为智能体生成增强版提示词"""

        prompt = f"""
【精准需求解析结果 - 置信度: {parsed_req.confidence_score:.0%}】

=== 核心信息 ===
🎯 课程主题: {parsed_req.topic}
👥 目标受众: {parsed_req.audience} ({parsed_req.age_group.value})
📅 年龄范围: {parsed_req.age_range['min']}-{parsed_req.age_range['max']}岁
⏰ 时间模式: {parsed_req.time_mode.value}
🕒 总时长: {parsed_req.total_duration.get('total_hours', 0)}小时

=== 学习设计 ===
🎯 学习目标:
{chr(10).join('• ' + obj for obj in parsed_req.learning_objectives)}

🔧 目标技能:
{chr(10).join('• ' + skill for skill in parsed_req.target_skills)}

🤖 AI工具集成:
{chr(10).join('• ' + tool for tool in parsed_req.ai_tools)}

=== 成果要求 ===
📦 最终交付物:
{chr(10).join('• ' + deliverable for deliverable in parsed_req.final_deliverables)}

=== 约束条件 ===
👥 班级规模: {parsed_req.class_size or '小班制'}人
🛠️ 可用设备: {', '.join(parsed_req.equipment)}
💰 预算水平: {parsed_req.budget_level}
🏛️ 机构环境: {parsed_req.institution_type.value}

=== 特殊要求 ===
{json.dumps(parsed_req.special_requirements, ensure_ascii=False, indent=2) if parsed_req.special_requirements else '无特殊要求'}

【重要提醒】
请严格按照以上解析结果进行课程设计，确保：
1. 年龄适宜性完全匹配 ({parsed_req.age_range['min']}-{parsed_req.age_range['max']}岁)
2. 时间规划精确对应 ({parsed_req.time_mode.value})
3. 最终交付物完全一致
4. 技能培养目标明确
5. AI工具集成充分体现
"""

        return prompt