"""
智能时间分配调度器
专门处理各种时间模式的课程安排和优化
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TimeMode(Enum):
    """时间模式枚举"""
    INTENSIVE_CAMP = "集训营模式"     # 几天密集训练
    WEEKLY_COURSE = "周课程模式"     # 按周分布
    SEMESTER_LONG = "学期课程模式"   # 整学期
    WORKSHOP = "工作坊模式"         # 单次活动

class LearningPhase(Enum):
    """学习阶段枚举"""
    INTRODUCTION = "导入阶段"
    EXPLORATION = "探索阶段"
    DEVELOPMENT = "深化阶段"
    SYNTHESIS = "综合阶段"
    PRESENTATION = "展示阶段"
    REFLECTION = "反思阶段"

@dataclass
class TimeBlock:
    """时间块定义"""
    phase: LearningPhase
    duration_minutes: int
    optimal_duration_minutes: int  # 最佳时长
    description: str
    activities: List[str]
    ai_tools: List[str]
    break_after: bool = False

    def get_hours(self) -> float:
        return self.duration_minutes / 60.0

@dataclass
class ScheduleTemplate:
    """课程安排模板"""
    mode: TimeMode
    age_range: Tuple[int, int]
    total_duration: Dict[str, int]
    session_blocks: List[TimeBlock]
    break_schedule: List[Dict[str, int]]  # 休息安排
    daily_structure: Dict[str, List[str]]  # 每日结构
    flexibility_options: List[str]

class TimeScheduler:
    """智能时间分配调度器"""

    def __init__(self):
        self.age_attention_spans = {
            (3, 6): {"focus_minutes": 15, "break_ratio": 0.3, "max_session": 90},
            (6, 12): {"focus_minutes": 25, "break_ratio": 0.25, "max_session": 120},
            (12, 15): {"focus_minutes": 35, "break_ratio": 0.2, "max_session": 180},
            (15, 18): {"focus_minutes": 45, "break_ratio": 0.15, "max_session": 240},
            (18, 25): {"focus_minutes": 60, "break_ratio": 0.1, "max_session": 300},
        }

        # PBL学习阶段时间分配比例
        self.pbl_phase_ratios = {
            LearningPhase.INTRODUCTION: 0.1,     # 导入10%
            LearningPhase.EXPLORATION: 0.25,    # 探索25%
            LearningPhase.DEVELOPMENT: 0.35,    # 深化35%
            LearningPhase.SYNTHESIS: 0.2,       # 综合20%
            LearningPhase.PRESENTATION: 0.08,   # 展示8%
            LearningPhase.REFLECTION: 0.02,     # 反思2%
        }

    def create_schedule(
        self,
        time_mode: str,
        age_range: Tuple[int, int],
        total_duration: Dict[str, int],
        topic: str,
        target_skills: List[str],
        final_deliverables: List[str]
    ) -> ScheduleTemplate:
        """创建智能课程安排"""

        logger.info(f"🕒 开始创建智能时间安排 - 模式: {time_mode}, 年龄: {age_range}")

        try:
            # 1. 确定时间模式
            mode = self._parse_time_mode(time_mode)

            # 2. 获取年龄相关的时间参数
            age_params = self._get_age_parameters(age_range)

            # 3. 创建时间块
            session_blocks = self._create_session_blocks(
                mode, age_params, total_duration, topic, target_skills
            )

            # 4. 设计休息安排
            break_schedule = self._design_break_schedule(mode, age_params, session_blocks)

            # 5. 构建每日结构
            daily_structure = self._build_daily_structure(mode, total_duration, session_blocks)

            # 6. 生成灵活性选项
            flexibility_options = self._generate_flexibility_options(mode, age_range, topic)

            schedule = ScheduleTemplate(
                mode=mode,
                age_range=age_range,
                total_duration=total_duration,
                session_blocks=session_blocks,
                break_schedule=break_schedule,
                daily_structure=daily_structure,
                flexibility_options=flexibility_options
            )

            logger.info(f"✅ 时间安排创建完成 - 共{len(session_blocks)}个时间块")
            return schedule

        except Exception as e:
            logger.error(f"❌ 时间安排创建失败: {e}")
            return self._create_fallback_schedule(time_mode, age_range, total_duration)

    def _parse_time_mode(self, time_mode: str) -> TimeMode:
        """解析时间模式"""
        mode_mapping = {
            "集训营模式": TimeMode.INTENSIVE_CAMP,
            "周课程模式": TimeMode.WEEKLY_COURSE,
            "学期课程模式": TimeMode.SEMESTER_LONG,
            "工作坊模式": TimeMode.WORKSHOP,
        }
        return mode_mapping.get(time_mode, TimeMode.WEEKLY_COURSE)

    def _get_age_parameters(self, age_range: Tuple[int, int]) -> Dict[str, int]:
        """获取年龄相关的时间参数"""
        min_age, max_age = age_range

        # 找到最匹配的年龄段
        for (age_min, age_max), params in self.age_attention_spans.items():
            if age_min <= min_age <= age_max or age_min <= max_age <= age_max:
                return params

        # 如果是跨年龄段，取平均值
        relevant_params = [
            params for (age_min, age_max), params in self.age_attention_spans.items()
            if not (age_max < min_age or age_min > max_age)
        ]

        if relevant_params:
            return {
                "focus_minutes": int(sum(p["focus_minutes"] for p in relevant_params) / len(relevant_params)),
                "break_ratio": sum(p["break_ratio"] for p in relevant_params) / len(relevant_params),
                "max_session": int(sum(p["max_session"] for p in relevant_params) / len(relevant_params)),
            }

        # 默认参数
        return {"focus_minutes": 30, "break_ratio": 0.2, "max_session": 150}

    def _create_session_blocks(
        self,
        mode: TimeMode,
        age_params: Dict[str, int],
        total_duration: Dict[str, int],
        topic: str,
        target_skills: List[str]
    ) -> List[TimeBlock]:
        """创建学习时间块"""

        total_minutes = total_duration.get("total_hours", 16) * 60
        focus_time = int(total_minutes * (1 - age_params["break_ratio"]))  # 扣除休息时间

        blocks = []

        # 根据PBL阶段分配时间
        for phase, ratio in self.pbl_phase_ratios.items():
            duration = int(focus_time * ratio)
            optimal_duration = duration

            # 根据主题和阶段调整活动
            activities = self._get_phase_activities(phase, topic, target_skills)
            ai_tools = self._get_phase_ai_tools(phase, target_skills)

            blocks.append(TimeBlock(
                phase=phase,
                duration_minutes=duration,
                optimal_duration_minutes=optimal_duration,
                description=f"{phase.value} - {topic}专项",
                activities=activities,
                ai_tools=ai_tools,
                break_after=(duration > age_params["focus_minutes"])
            ))

        # 调整时间块以适应具体模式
        return self._adjust_blocks_for_mode(blocks, mode, age_params, total_duration)

    def _get_phase_activities(self, phase: LearningPhase, topic: str, skills: List[str]) -> List[str]:
        """获取阶段性活动"""
        base_activities = {
            LearningPhase.INTRODUCTION: [
                "主题导入和问题提出", "兴趣激发活动", "背景知识建构", "团队组建"
            ],
            LearningPhase.EXPLORATION: [
                "问题分析和拆解", "资料调研", "初步方案探讨", "可行性分析"
            ],
            LearningPhase.DEVELOPMENT: [
                "核心技能学习", "方案深化设计", "原型制作", "测试和改进"
            ],
            LearningPhase.SYNTHESIS: [
                "方案整合优化", "成果完善", "质量检验", "准备展示"
            ],
            LearningPhase.PRESENTATION: [
                "成果展示", "同伴评议", "专家点评", "经验分享"
            ],
            LearningPhase.REFLECTION: [
                "学习反思", "过程总结", "改进建议", "未来规划"
            ],
        }

        # 根据主题定制活动
        customized_activities = base_activities[phase].copy()
        if "月球" in topic and "装备" in topic:
            if phase == LearningPhase.DEVELOPMENT:
                customized_activities.extend([
                    "月球环境研究", "装备3D建模", "AI动画制作", "虚实融合视频创作"
                ])

        return customized_activities

    def _get_phase_ai_tools(self, phase: LearningPhase, skills: List[str]) -> List[str]:
        """获取阶段AI工具"""
        phase_tools = {
            LearningPhase.INTRODUCTION: ["ChatGPT问答", "Claude文档整理"],
            LearningPhase.EXPLORATION: ["研究助手AI", "信息整理工具"],
            LearningPhase.DEVELOPMENT: ["3D建模AI", "代码生成助手", "创作AI工具"],
            LearningPhase.SYNTHESIS: ["文档AI", "演示制作工具"],
            LearningPhase.PRESENTATION: ["演示AI助手", "反馈收集工具"],
            LearningPhase.REFLECTION: ["反思AI导师", "学习分析工具"],
        }

        base_tools = phase_tools[phase]

        # 根据目标技能定制AI工具
        if "3d建模" in skills:
            if phase in [LearningPhase.DEVELOPMENT, LearningPhase.SYNTHESIS]:
                base_tools.append("Blender AI插件")
        if "ai动画" in skills:
            if phase == LearningPhase.DEVELOPMENT:
                base_tools.append("Runway AI视频")

        return base_tools

    def _adjust_blocks_for_mode(
        self,
        blocks: List[TimeBlock],
        mode: TimeMode,
        age_params: Dict[str, int],
        total_duration: Dict[str, int]
    ) -> List[TimeBlock]:
        """根据时间模式调整时间块"""

        if mode == TimeMode.INTENSIVE_CAMP:
            # 集训营模式：压缩时间，增加强度
            days = total_duration.get("days", 3)
            hours_per_day = total_duration.get("hours_per_day", 6)

            # 将时间块按天分组
            daily_minutes = hours_per_day * 60
            break_time = int(daily_minutes * age_params["break_ratio"])
            focus_time_per_day = daily_minutes - break_time

            # 重新分配每个阶段在每天的时间
            return self._distribute_blocks_over_days(blocks, days, focus_time_per_day)

        elif mode == TimeMode.WEEKLY_COURSE:
            # 周课程模式：标准分配
            return blocks

        elif mode == TimeMode.WORKSHOP:
            # 工作坊模式：精简核心阶段
            core_phases = [LearningPhase.EXPLORATION, LearningPhase.DEVELOPMENT, LearningPhase.PRESENTATION]
            return [block for block in blocks if block.phase in core_phases]

        return blocks

    def _distribute_blocks_over_days(
        self, blocks: List[TimeBlock], days: int, daily_focus_minutes: int
    ) -> List[TimeBlock]:
        """将时间块分布到多天"""
        daily_blocks = []

        # 计算每天应该覆盖的阶段
        total_focus_time = sum(block.duration_minutes for block in blocks)
        scale_factor = (daily_focus_minutes * days) / total_focus_time

        for day in range(days):
            for block in blocks:
                # 计算这个阶段在这一天的时间
                daily_duration = int(block.duration_minutes * scale_factor / days)
                if daily_duration > 0:
                    day_block = TimeBlock(
                        phase=block.phase,
                        duration_minutes=daily_duration,
                        optimal_duration_minutes=block.optimal_duration_minutes,
                        description=f"Day {day+1}: {block.description}",
                        activities=block.activities,
                        ai_tools=block.ai_tools,
                        break_after=block.break_after
                    )
                    daily_blocks.append(day_block)

        return daily_blocks

    def _design_break_schedule(
        self, mode: TimeMode, age_params: Dict[str, int], blocks: List[TimeBlock]
    ) -> List[Dict[str, int]]:
        """设计休息安排"""
        breaks = []
        focus_limit = age_params["focus_minutes"]

        cumulative_time = 0
        for i, block in enumerate(blocks):
            cumulative_time += block.duration_minutes

            if cumulative_time >= focus_limit or block.break_after:
                if cumulative_time < focus_limit:
                    break_duration = 5  # 短休息
                elif cumulative_time < focus_limit * 2:
                    break_duration = 15  # 中等休息
                else:
                    break_duration = 30  # 长休息

                breaks.append({
                    "after_block": i,
                    "duration_minutes": break_duration,
                    "type": "focus_break" if break_duration <= 5 else "active_break"
                })
                cumulative_time = 0

        return breaks

    def _build_daily_structure(
        self, mode: TimeMode, total_duration: Dict[str, int], blocks: List[TimeBlock]
    ) -> Dict[str, List[str]]:
        """构建每日结构"""
        structure = {}

        if mode == TimeMode.INTENSIVE_CAMP:
            days = total_duration.get("days", 3)
            for day in range(1, days + 1):
                day_blocks = [b for b in blocks if f"Day {day}" in b.description]
                structure[f"第{day}天"] = [
                    f"{block.phase.value}: {block.get_hours():.1f}小时"
                    for block in day_blocks
                ]
        else:
            # 其他模式的标准结构
            structure["标准课时"] = [
                f"{block.phase.value}: {block.get_hours():.1f}小时"
                for block in blocks
            ]

        return structure

    def _generate_flexibility_options(
        self, mode: TimeMode, age_range: Tuple[int, int], topic: str
    ) -> List[str]:
        """生成灵活性选项"""
        options = [
            "可根据学生兴趣动态调整时间分配",
            "支持个性化学习进度安排",
            "提供快慢班分层教学方案"
        ]

        if mode == TimeMode.INTENSIVE_CAMP:
            options.extend([
                "支持半天/全天灵活安排",
                "可插入户外活动时间",
                "应急时间预留方案"
            ])

        if age_range[1] - age_range[0] > 5:  # 跨年龄段
            options.append("提供年龄分组的差异化时间安排")

        return options

    def _create_fallback_schedule(
        self, time_mode: str, age_range: Tuple[int, int], total_duration: Dict[str, int]
    ) -> ScheduleTemplate:
        """创建兜底时间安排"""
        logger.warning("🔄 使用兜底时间安排方案")

        # 创建基本时间块
        total_hours = total_duration.get("total_hours", 16)
        basic_blocks = [
            TimeBlock(
                phase=LearningPhase.INTRODUCTION,
                duration_minutes=int(total_hours * 60 * 0.1),
                optimal_duration_minutes=int(total_hours * 60 * 0.1),
                description="课程导入",
                activities=["问题导入", "兴趣激发"],
                ai_tools=["ChatGPT"],
                break_after=False
            ),
            TimeBlock(
                phase=LearningPhase.DEVELOPMENT,
                duration_minutes=int(total_hours * 60 * 0.7),
                optimal_duration_minutes=int(total_hours * 60 * 0.7),
                description="核心学习",
                activities=["技能学习", "项目制作"],
                ai_tools=["AI创作工具"],
                break_after=True
            ),
            TimeBlock(
                phase=LearningPhase.PRESENTATION,
                duration_minutes=int(total_hours * 60 * 0.2),
                optimal_duration_minutes=int(total_hours * 60 * 0.2),
                description="成果展示",
                activities=["作品展示", "学习总结"],
                ai_tools=["演示工具"],
                break_after=False
            ),
        ]

        return ScheduleTemplate(
            mode=TimeMode.WEEKLY_COURSE,
            age_range=age_range,
            total_duration=total_duration,
            session_blocks=basic_blocks,
            break_schedule=[{"after_block": 1, "duration_minutes": 15, "type": "active_break"}],
            daily_structure={"标准安排": [f"{block.phase.value}: {block.get_hours():.1f}小时" for block in basic_blocks]},
            flexibility_options=["支持灵活时间调整"]
        )

    def format_schedule_for_display(self, schedule: ScheduleTemplate) -> str:
        """格式化时间安排用于显示"""
        output = f"""
🕒 【智能时间安排方案】

📋 基本信息:
• 模式: {schedule.mode.value}
• 年龄范围: {schedule.age_range[0]}-{schedule.age_range[1]}岁
• 总时长: {schedule.total_duration.get('total_hours', 0)}小时

⏰ 时间块分配:
"""
        for i, block in enumerate(schedule.session_blocks, 1):
            output += f"""
{i}. {block.phase.value} ({block.get_hours():.1f}小时)
   📝 活动: {', '.join(block.activities[:3])}
   🤖 AI工具: {', '.join(block.ai_tools)}
"""

        output += f"""
🔄 灵活性选项:
{chr(10).join('• ' + option for option in schedule.flexibility_options)}
"""
        return output