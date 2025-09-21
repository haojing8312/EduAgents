"""
增强版课程设计模式 - 完美适配Maker Space和传统机构需求
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class DurationType(str, Enum):
    """课程时长类型"""
    HALF_DAY = "half_day"      # 半天 (3-4小时)
    ONE_DAY = "one_day"        # 一天 (6-8小时)
    TWO_DAY = "two_day"        # 两天 (12-16小时)
    THREE_DAY = "three_day"    # 三天 (18-24小时)
    WEEKLY = "weekly"          # 按周计算


class InstitutionType(str, Enum):
    """机构类型"""
    MAKER_SPACE = "maker_space"           # 创客空间/实验室
    MUSIC_SCHOOL = "music_school"         # 音乐培训机构
    ART_SCHOOL = "art_school"             # 美术培训机构
    CODING_SCHOOL = "coding_school"       # 少儿编程机构
    STEM_CENTER = "stem_center"           # STEM教育中心
    GENERAL_SCHOOL = "general_school"     # 普通学校
    COMMUNITY_CENTER = "community_center" # 社区教育中心


class AIToolType(str, Enum):
    """AI工具类型"""
    # 对话类
    AI_CHAT = "ai_chat"                  # AI对话 (ChatGPT, Claude)
    AI_ASSISTANT = "ai_assistant"        # AI助手

    # 创作类
    AI_DRAWING = "ai_drawing"            # AI绘画 (Midjourney, DALL-E)
    AI_MUSIC = "ai_music"                # AI音乐 (Suno, Udio)
    AI_VIDEO = "ai_video"                # AI视频 (RunwayML, Pika)
    AI_ANIMATION = "ai_animation"        # AI动画 (即梦, LeiaPix)

    # 3D和建模
    AI_3D_MODELING = "ai_3d_modeling"    # AI 3D建模 (Meshy, Tripo)
    AI_DESIGN = "ai_design"              # AI设计 (Figma AI, Canva)

    # 编程类
    AI_CODING = "ai_coding"              # AI编程 (GitHub Copilot, Cursor)
    AI_WEB_DEV = "ai_web_dev"            # AI网页开发

    # 教育类
    AI_TUTORING = "ai_tutoring"          # AI辅导
    AI_PRESENTATION = "ai_presentation"  # AI演示


class HardwareEquipment(str, Enum):
    """硬件设备类型"""
    COMPUTER = "computer"                # 电脑
    TABLET = "tablet"                    # 平板
    ROBOT_ARM = "robot_arm"              # 机械臂
    PRINTER_3D = "3d_printer"            # 3D打印机
    VR_HEADSET = "vr_headset"            # VR头显
    CAMERA = "camera"                    # 相机
    MICROPHONE = "microphone"            # 麦克风
    PROJECTOR = "projector"              # 投影仪
    SMART_BOARD = "smart_board"          # 智能黑板


class AgeGroup(str, Enum):
    """年龄组"""
    PRESCHOOL = "preschool"              # 学前 (3-5岁)
    PRIMARY_LOWER = "primary_lower"      # 小学低年级 (6-8岁)
    PRIMARY_UPPER = "primary_upper"      # 小学高年级 (9-11岁)
    JUNIOR_HIGH = "junior_high"          # 初中 (12-14岁)
    HIGH_SCHOOL = "high_school"          # 高中 (15-17岁)
    ADULT = "adult"                      # 成人 (18+岁)


class ProjectType(str, Enum):
    """项目类型"""
    CREATIVE_WORK = "creative_work"      # 创意作品 (艺术、音乐)
    DIGITAL_PRODUCT = "digital_product"  # 数字产品 (APP、网站)
    PHYSICAL_PRODUCT = "physical_product" # 实体产品 (3D打印)
    PERFORMANCE = "performance"          # 表演展示
    RESEARCH = "research"                # 研究报告
    GAME = "game"                        # 游戏设计
    STORY = "story"                      # 故事创作


class EnhancedCourseRequest(BaseModel):
    """增强版课程设计请求"""

    # === 基础信息 ===
    title: str = Field(..., description="课程标题")
    theme_concept: str = Field(..., description="主题概念描述",
                              example="我的超能分身：让孩子们想象在平行宇宙中拥有超能力的自己")
    description: Optional[str] = Field(None, description="详细描述")

    # === 参与者信息 ===
    participant_count: int = Field(..., ge=1, le=50, description="参与人数")
    age_group: AgeGroup = Field(..., description="年龄组")

    # === 时长和结构 ===
    duration_type: DurationType = Field(..., description="课程时长类型")
    session_count: Optional[int] = Field(1, description="会话数量")

    # === 机构和环境 ===
    institution_type: InstitutionType = Field(..., description="机构类型")
    available_equipment: List[HardwareEquipment] = Field(default_factory=list,
                                                       description="可用硬件设备")

    # === AI工具和技能 ===
    target_ai_tools: List[AIToolType] = Field(..., description="目标AI工具技能")
    teacher_ai_experience: Literal["beginner", "intermediate", "advanced"] = Field(
        "beginner", description="教师AI经验水平")

    # === 项目成果 ===
    target_outputs: List[ProjectType] = Field(..., description="期望的项目成果类型")
    specific_deliverables: List[str] = Field(default_factory=list,
                                           description="具体交付成果",
                                           example=["身份卡", "3D模型", "演示视频"])

    # === 教学约束 ===
    budget_level: Literal["low", "medium", "high"] = Field("medium", description="预算水平")
    safety_requirements: List[str] = Field(default_factory=list, description="安全要求")

    # === 个性化需求 ===
    custom_requirements: Optional[str] = Field(None, description="特殊定制需求")
    integration_with_existing: Optional[str] = Field(None,
                                                   description="与现有课程的结合方式")


class TimeSlot(BaseModel):
    """时间段"""
    start_time: str = Field(..., description="开始时间", example="09:00")
    end_time: str = Field(..., description="结束时间", example="10:30")
    duration_minutes: int = Field(..., description="持续分钟数")
    activity_type: str = Field(..., description="活动类型")


class DetailedActivity(BaseModel):
    """详细活动"""
    title: str = Field(..., description="活动标题")
    duration_minutes: int = Field(..., description="持续时间(分钟)")
    objective: str = Field(..., description="活动目标")
    materials_needed: List[str] = Field(default_factory=list, description="所需材料")
    ai_tools_used: List[str] = Field(default_factory=list, description="使用的AI工具")
    step_by_step: List[str] = Field(default_factory=list, description="详细步骤")
    teacher_notes: List[str] = Field(default_factory=list, description="教师注意事项")
    troubleshooting: List[str] = Field(default_factory=list, description="故障排除")


class AIToolGuidance(BaseModel):
    """AI工具使用指导"""
    tool_name: str = Field(..., description="工具名称")
    tool_type: AIToolType = Field(..., description="工具类型")
    description: str = Field(..., description="工具描述")
    use_cases: List[str] = Field(default_factory=list, description="使用场景")
    step_by_step_tutorial: List[str] = Field(default_factory=list, description="使用教程")
    common_problems: List[str] = Field(default_factory=list, description="常见问题")
    tips_and_tricks: List[str] = Field(default_factory=list, description="技巧提示")
    safety_considerations: List[str] = Field(default_factory=list, description="安全考虑")


class TeacherPreparation(BaseModel):
    """教师准备指导"""
    skill_requirements: List[str] = Field(default_factory=list, description="技能要求")
    pre_course_preparation: List[str] = Field(default_factory=list, description="课前准备")
    material_checklist: List[str] = Field(default_factory=list, description="材料清单")
    setup_instructions: List[str] = Field(default_factory=list, description="设置说明")
    ai_tools_to_master: List[AIToolGuidance] = Field(default_factory=list,
                                                   description="需要掌握的AI工具")
    backup_plans: List[str] = Field(default_factory=list, description="备用方案")


class InstitutionTemplate(BaseModel):
    """机构模板"""
    institution_type: InstitutionType = Field(..., description="机构类型")
    typical_equipment: List[HardwareEquipment] = Field(default_factory=list,
                                                      description="典型设备")
    recommended_ai_tools: List[AIToolType] = Field(default_factory=list,
                                                 description="推荐AI工具")
    integration_suggestions: List[str] = Field(default_factory=list,
                                             description="整合建议")
    sample_projects: List[str] = Field(default_factory=list, description="示例项目")


class EnhancedCourseResponse(BaseModel):
    """增强版课程设计响应"""

    # === 基础信息 ===
    course_id: str = Field(..., description="课程ID")
    title: str = Field(..., description="课程标题")
    theme_concept: str = Field(..., description="主题概念")

    # === 课程概览 ===
    overview: Dict[str, Any] = Field(default_factory=dict, description="课程概览")
    learning_objectives: List[str] = Field(default_factory=list, description="学习目标")
    driving_question: str = Field(..., description="驱动问题")

    # === 详细时间安排 ===
    schedule: List[TimeSlot] = Field(default_factory=list, description="时间安排")
    detailed_activities: List[DetailedActivity] = Field(default_factory=list,
                                                       description="详细活动")

    # === AI工具集成 ===
    ai_tools_guidance: List[AIToolGuidance] = Field(default_factory=list,
                                                   description="AI工具指导")

    # === 教师支持 ===
    teacher_preparation: TeacherPreparation = Field(..., description="教师准备")
    classroom_management: List[str] = Field(default_factory=list, description="课堂管理")

    # === 评估和成果 ===
    assessment_methods: List[Dict[str, Any]] = Field(default_factory=list,
                                                    description="评估方法")
    expected_outcomes: List[str] = Field(default_factory=list, description="预期成果")

    # === 资源和材料 ===
    required_materials: List[str] = Field(default_factory=list, description="所需材料")
    optional_materials: List[str] = Field(default_factory=list, description="可选材料")

    # === 扩展和适配 ===
    variations: List[str] = Field(default_factory=list, description="变体方案")
    scaling_options: List[str] = Field(default_factory=list, description="扩展选项")

    # === 元数据 ===
    institution_template: Optional[InstitutionTemplate] = Field(None,
                                                               description="机构模板")
    creation_metadata: Dict[str, Any] = Field(default_factory=dict,
                                             description="创建元数据")