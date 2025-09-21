"""
增强版课程设计器 - 专门针对Maker Space和传统机构赋能
完美满足用户的具体需求场景
"""

import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.schemas.enhanced_course import (
    EnhancedCourseRequest, EnhancedCourseResponse,
    DurationType, InstitutionType, AIToolType, HardwareEquipment,
    TimeSlot, DetailedActivity, AIToolGuidance, TeacherPreparation,
    InstitutionTemplate
)
from app.services.real_agent_service import get_real_agent_service


class EnhancedCourseDesigner:
    """增强版PBL课程设计器 - 专门适配实际教学场景"""

    def __init__(self):
        # AI工具数据库
        self.ai_tools_database = self._initialize_ai_tools_database()
        # 机构模板库
        self.institution_templates = self._initialize_institution_templates()
        # 时长配置
        self.duration_configs = self._initialize_duration_configs()

    async def design_enhanced_course(self, request: EnhancedCourseRequest) -> EnhancedCourseResponse:
        """设计增强版课程，完美适配用户需求"""

        start_time = time.time()
        course_id = str(uuid.uuid4())

        try:
            # 1. 获取机构模板
            institution_template = self._get_institution_template(request.institution_type)

            # 2. 构建详细的课程需求描述
            detailed_requirement = self._build_detailed_requirement(request, institution_template)

            # 3. 使用真实智能体协作设计
            agent_service = await get_real_agent_service()
            design_result = await agent_service.execute_complete_course_design(
                course_requirement=detailed_requirement,
                session_id=str(uuid.uuid4()),
                save_to_db=True
            )

            # 4. 转换为增强版课程格式
            enhanced_course = await self._convert_to_enhanced_course(
                request, design_result, course_id, institution_template
            )

            design_time = time.time() - start_time
            enhanced_course.creation_metadata = {
                "design_time": round(design_time, 2),
                "real_agents_used": True,
                "institution_optimized": True,
                "created_at": datetime.now().isoformat()
            }

            return enhanced_course

        except Exception as e:
            # 提供高质量的fallback方案
            return self._create_fallback_enhanced_course(request, course_id, str(e))

    def _build_detailed_requirement(self, request: EnhancedCourseRequest, template: InstitutionTemplate) -> str:
        """构建详细的课程需求描述"""

        # 时长配置
        duration_config = self.duration_configs[request.duration_type]

        requirement = f"""
【课程设计需求 - {request.institution_type.value.upper()}专用】

=== 基础信息 ===
课程标题: {request.title}
主题概念: {request.theme_concept}
机构类型: {request.institution_type.value}
参与人数: {request.participant_count}人
年龄组: {request.age_group.value}
教师AI经验: {request.teacher_ai_experience}

=== 时长和结构 ===
课程时长: {request.duration_type.value}
总时长: {duration_config['total_hours']}小时
建议分段: {duration_config['suggested_sessions']}

=== 可用设备和工具 ===
硬件设备: {', '.join([eq.value for eq in request.available_equipment])}
目标AI工具: {', '.join([tool.value for tool in request.target_ai_tools])}

=== 期望成果 ===
项目类型: {', '.join([pt.value for pt in request.target_outputs])}
具体交付物: {', '.join(request.specific_deliverables)}

=== 机构特色整合 ===
{template.integration_suggestions[0] if template.integration_suggestions else "结合机构特色进行课程设计"}

=== 设计要求 ===
请设计一个完全可执行的PBL课程方案，包含：

1. 【详细时间安排】- 精确到每个时间段的具体活动
2. 【AI工具使用指导】- 针对{request.teacher_ai_experience}水平教师的详细操作步骤
3. 【硬件设备整合】- 如何使用{', '.join([eq.value for eq in request.available_equipment])}
4. 【课堂管理指导】- 让无PBL经验的教师也能顺利执行
5. 【具体项目任务】- 围绕"{request.theme_concept}"设计具体可执行的项目
6. 【评估和展示】- 学生成果的评估和展示方式

特别注意：
- 这是为{request.institution_type.value}环境设计的{duration_config['total_hours']}小时课程
- 需要照顾到{request.participant_count}人的协作组织
- 教师是{request.teacher_ai_experience}水平，需要详细的操作指导
- 必须产出具体的{', '.join(request.specific_deliverables)}

请确保课程设计实用、可执行、有趣且富有教育价值。
"""
        return requirement.strip()

    async def _convert_to_enhanced_course(
        self,
        request: EnhancedCourseRequest,
        design_result: Dict[str, Any],
        course_id: str,
        institution_template: InstitutionTemplate
    ) -> EnhancedCourseResponse:
        """将智能体结果转换为增强版课程格式"""

        agents_data = design_result.get("agents_data", {})

        # 时长配置
        duration_config = self.duration_configs[request.duration_type]

        # 生成详细时间安排
        schedule = self._generate_detailed_schedule(request, duration_config)

        # 生成详细活动
        detailed_activities = self._generate_detailed_activities(request, agents_data)

        # 生成AI工具指导
        ai_tools_guidance = self._generate_ai_tools_guidance(request.target_ai_tools)

        # 生成教师准备指导
        teacher_preparation = self._generate_teacher_preparation(request, ai_tools_guidance)

        return EnhancedCourseResponse(
            course_id=course_id,
            title=request.title,
            theme_concept=request.theme_concept,

            overview={
                "institution_type": request.institution_type.value,
                "duration": duration_config['total_hours'],
                "participants": request.participant_count,
                "age_group": request.age_group.value,
                "equipment_used": [eq.value for eq in request.available_equipment],
                "ai_tools_used": [tool.value for tool in request.target_ai_tools]
            },

            learning_objectives=self._extract_learning_objectives(agents_data, request),
            driving_question=f"如何通过{request.theme_concept}项目，掌握AI时代的核心能力？",

            schedule=schedule,
            detailed_activities=detailed_activities,
            ai_tools_guidance=ai_tools_guidance,
            teacher_preparation=teacher_preparation,

            classroom_management=self._generate_classroom_management(request),

            assessment_methods=self._generate_assessment_methods(request),
            expected_outcomes=request.specific_deliverables,

            required_materials=self._generate_required_materials(request),
            optional_materials=self._generate_optional_materials(request),

            variations=self._generate_variations(request),
            scaling_options=self._generate_scaling_options(request),

            institution_template=institution_template
        )

    def _generate_detailed_schedule(self, request: EnhancedCourseRequest, duration_config: Dict) -> List[TimeSlot]:
        """生成详细的时间安排"""

        schedule = []

        if request.duration_type == DurationType.HALF_DAY:
            schedule = [
                TimeSlot(start_time="09:00", end_time="09:30", duration_minutes=30,
                        activity_type="破冰和项目介绍"),
                TimeSlot(start_time="09:30", end_time="10:30", duration_minutes=60,
                        activity_type="主题探索和AI工具体验"),
                TimeSlot(start_time="10:30", end_time="10:45", duration_minutes=15,
                        activity_type="休息"),
                TimeSlot(start_time="10:45", end_time="11:45", duration_minutes=60,
                        activity_type="项目制作和AI协作"),
                TimeSlot(start_time="11:45", end_time="12:30", duration_minutes=45,
                        activity_type="成果展示和反思")
            ]

        elif request.duration_type == DurationType.ONE_DAY:
            schedule = [
                TimeSlot(start_time="09:00", end_time="09:30", duration_minutes=30,
                        activity_type="开场破冰"),
                TimeSlot(start_time="09:30", end_time="10:30", duration_minutes=60,
                        activity_type="主题探索"),
                TimeSlot(start_time="10:30", end_time="10:45", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="10:45", end_time="12:00", duration_minutes=75,
                        activity_type="AI工具学习和实践"),
                TimeSlot(start_time="12:00", end_time="13:30", duration_minutes=90,
                        activity_type="午餐休息"),
                TimeSlot(start_time="13:30", end_time="15:30", duration_minutes=120,
                        activity_type="项目制作和协作"),
                TimeSlot(start_time="15:30", end_time="15:45", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="15:45", end_time="17:00", duration_minutes=75,
                        activity_type="成果完善和展示")
            ]

        elif request.duration_type == DurationType.TWO_DAY:
            # 第一天
            schedule.extend([
                TimeSlot(start_time="第一天 09:00", end_time="09:30", duration_minutes=30,
                        activity_type="开场和团队建设"),
                TimeSlot(start_time="第一天 09:30", end_time="11:00", duration_minutes=90,
                        activity_type="主题深度探索"),
                TimeSlot(start_time="第一天 11:00", end_time="11:15", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="第一天 11:15", end_time="12:30", duration_minutes=75,
                        activity_type="AI工具深度学习"),
                TimeSlot(start_time="第一天 12:30", end_time="14:00", duration_minutes=90,
                        activity_type="午餐休息"),
                TimeSlot(start_time="第一天 14:00", end_time="16:00", duration_minutes=120,
                        activity_type="项目设计和原型制作"),
                TimeSlot(start_time="第一天 16:00", end_time="16:15", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="第一天 16:15", end_time="17:30", duration_minutes=75,
                        activity_type="第一天总结和次日规划")
            ])
            # 第二天
            schedule.extend([
                TimeSlot(start_time="第二天 09:00", end_time="09:15", duration_minutes=15,
                        activity_type="回顾和热身"),
                TimeSlot(start_time="第二天 09:15", end_time="11:15", duration_minutes=120,
                        activity_type="项目深度开发"),
                TimeSlot(start_time="第二天 11:15", end_time="11:30", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="第二天 11:30", end_time="12:30", duration_minutes=60,
                        activity_type="硬件整合和调试"),
                TimeSlot(start_time="第二天 12:30", end_time="14:00", duration_minutes=90,
                        activity_type="午餐休息"),
                TimeSlot(start_time="第二天 14:00", end_time="15:30", duration_minutes=90,
                        activity_type="成果完善和包装"),
                TimeSlot(start_time="第二天 15:30", end_time="15:45", duration_minutes=15,
                        activity_type="茶歇"),
                TimeSlot(start_time="第二天 15:45", end_time="17:00", duration_minutes=75,
                        activity_type="成果展示和庆祝")
            ])

        return schedule

    def _generate_detailed_activities(self, request: EnhancedCourseRequest, agents_data: Dict) -> List[DetailedActivity]:
        """生成详细活动指导"""

        activities = []

        # 根据主题概念生成具体活动
        if "超能分身" in request.theme_concept or "超能" in request.theme_concept:
            activities = [
                DetailedActivity(
                    title="超能力设定工作坊",
                    duration_minutes=60,
                    objective="帮助学生构思并设定自己的超能力角色",
                    materials_needed=["白纸", "彩笔", "电脑", "AI绘画工具"],
                    ai_tools_used=["ChatGPT", "Midjourney"],
                    step_by_step=[
                        "1. 引导学生思考：如果有超能力，你想拥有什么？(10分钟)",
                        "2. 使用ChatGPT帮助完善超能力设定和背景故事(20分钟)",
                        "3. 用Midjourney生成超能力角色的视觉形象(20分钟)",
                        "4. 小组分享各自的超能力设定(10分钟)"
                    ],
                    teacher_notes=[
                        "鼓励学生发挥想象力，不要限制创意",
                        "帮助学生学会与AI对话的技巧",
                        "注意时间控制，确保每个学生都有机会尝试"
                    ],
                    troubleshooting=[
                        "如果AI生成图像不满意，指导学生修改提示词",
                        "如果有学生不知道想要什么超能力，提供一些启发性问题"
                    ]
                ),

                DetailedActivity(
                    title="身份卡设计制作",
                    duration_minutes=90,
                    objective="使用AI工具制作专业的超能力身份卡",
                    materials_needed=["电脑", "打印机", "卡纸", "设计软件"],
                    ai_tools_used=["Canva AI", "ChatGPT"],
                    step_by_step=[
                        "1. 使用ChatGPT生成身份卡的详细信息(姓名、能力、等级等)(15分钟)",
                        "2. 学习Canva AI的基本操作(15分钟)",
                        "3. 使用Canva AI设计身份卡模板(30分钟)",
                        "4. 添加之前生成的角色图像和信息(20分钟)",
                        "5. 打印和制作实体身份卡(10分钟)"
                    ],
                    teacher_notes=[
                        "提前准备Canva账号，确保学生能够登录",
                        "准备一些身份卡模板作为参考",
                        "指导学生注意排版和配色"
                    ],
                    troubleshooting=[
                        "如果Canva加载慢，准备离线设计软件作为备选",
                        "如果打印机故障，可以先保存数字版本"
                    ]
                ),

                DetailedActivity(
                    title="3D超能力道具建模",
                    duration_minutes=120,
                    objective="为超能力角色设计并3D建模专属道具",
                    materials_needed=["电脑", "3D建模软件", "3D打印机"],
                    ai_tools_used=["Meshy AI", "ChatGPT"],
                    step_by_step=[
                        "1. 与ChatGPT讨论超能力道具的设计思路(15分钟)",
                        "2. 学习Meshy AI的基本操作(20分钟)",
                        "3. 使用文字描述生成3D模型草案(30分钟)",
                        "4. 调整和优化3D模型(30分钟)",
                        "5. 准备3D打印文件(15分钟)",
                        "6. 启动3D打印(如果时间允许)(10分钟)"
                    ],
                    teacher_notes=[
                        "提前测试3D建模软件和打印机",
                        "准备一些简单的3D模型示例",
                        "指导学生选择合适的打印尺寸"
                    ],
                    troubleshooting=[
                        "如果AI生成的模型有问题，指导学生修改描述",
                        "如果3D打印时间太长，可以课后完成"
                    ]
                )
            ]

        # 添加通用活动，确保总数足够
        if len(activities) < 3:
            # 如果特定主题活动不足，添加通用活动
            activities.extend([
                DetailedActivity(
                    title="AI工具体验工作坊",
                    duration_minutes=90,
                    objective="让学生熟悉并掌握基本的AI工具使用技能",
                    materials_needed=["电脑", "网络", "操作指南"],
                    ai_tools_used=["ChatGPT", "Midjourney"],
                    step_by_step=[
                        "1. AI工具介绍和安全使用说明(15分钟)",
                        "2. ChatGPT对话练习，学会提问技巧(30分钟)",
                        "3. Midjourney图像生成体验(30分钟)",
                        "4. 小组讨论AI工具的优缺点(15分钟)"
                    ],
                    teacher_notes=[
                        "强调AI工具的辅助性质",
                        "指导学生学会批判性思考",
                        "注意网络安全和隐私保护"
                    ],
                    troubleshooting=[
                        "如果AI工具访问慢，准备离线演示",
                        "如果学生害怕使用AI，从简单对话开始"
                    ]
                ),

                DetailedActivity(
                    title="创意项目制作",
                    duration_minutes=120,
                    objective="运用学到的AI工具完成具体的创作项目",
                    materials_needed=["电脑", "打印机", "制作材料"],
                    ai_tools_used=["ChatGPT", "Midjourney", "Meshy AI"],
                    step_by_step=[
                        "1. 确定个人项目主题和目标(20分钟)",
                        "2. 使用AI工具收集创意和素材(40分钟)",
                        "3. 进行具体创作和制作(40分钟)",
                        "4. 完善和优化作品(20分钟)"
                    ],
                    teacher_notes=[
                        "鼓励学生发挥创造力",
                        "及时给予指导和反馈",
                        "帮助解决技术问题"
                    ],
                    troubleshooting=[
                        "如果学生创意枯竭，提供一些启发性问题",
                        "如果技术出现问题，协助排除故障"
                    ]
                )
            ])

        # 最后添加展示活动
        activities.append(
            DetailedActivity(
                title="成果展示准备",
                duration_minutes=45,
                objective="准备项目成果的展示和演讲",
                materials_needed=["投影仪", "电脑", "展示台"],
                ai_tools_used=["ChatGPT", "AI演示工具"],
                step_by_step=[
                    "1. 整理项目成果(身份卡、3D模型等)(10分钟)",
                    "2. 使用ChatGPT构思展示演讲内容(15分钟)",
                    "3. 练习演讲和展示(15分钟)",
                    "4. 最后检查和准备(5分钟)"
                ],
                teacher_notes=[
                    "鼓励学生自信展示",
                    "帮助内向的学生克服紧张",
                    "控制每个学生的展示时间"
                ],
                troubleshooting=[
                    "如果学生过于紧张，可以安排小组展示",
                    "准备一些提示问题帮助学生展示"
                ]
            )
        )

        return activities

    def _generate_ai_tools_guidance(self, target_tools: List[AIToolType]) -> List[AIToolGuidance]:
        """生成AI工具使用指导"""

        guidance_list = []

        for tool_type in target_tools:
            if tool_type in self.ai_tools_database:
                tool_info = self.ai_tools_database[tool_type]
                guidance_list.append(AIToolGuidance(**tool_info))

        return guidance_list

    def _generate_teacher_preparation(self, request: EnhancedCourseRequest, ai_guidance: List[AIToolGuidance]) -> TeacherPreparation:
        """生成教师准备指导"""

        skill_requirements = [
            "基本的电脑操作能力",
            "简单的项目管理技能",
            "学生沟通和引导能力"
        ]

        if request.teacher_ai_experience == "beginner":
            skill_requirements.extend([
                "AI工具的基础概念理解",
                "简单的网页操作能力",
                "学会基本的故障排除方法",
                "掌握学生分组和时间管理技巧"
            ])

        pre_course_preparation = [
            "提前注册和测试所有AI工具账号",
            "准备示例项目作为参考",
            "检查所有硬件设备的工作状态",
            "准备材料清单并确保充足库存",
            "设计分组方案和座位安排",
            "制作课程时间表并打印分发",
            "准备应急方案和备用活动",
            "联系技术支持人员待命"
        ]

        if request.teacher_ai_experience == "beginner":
            pre_course_preparation.extend([
                "📺 观看AI工具使用教程视频",
                "👥 找一位AI工具熟练的同事作为协助",
                "📅 提前一周开始每天练习使用AI工具",
                "📋 准备详细的操作步骤卡片",
                "❓ 制作常见问题解答手册",
                "🎯 进行模拟课堂演练",
                "📞 建立技术支持联系群",
                "⏰ 制作详细的时间管理表",
                "🔧 准备故障排除快速指南",
                "👶 为初学者教师制作简化版操作流程"
            ])

        material_checklist = [
            f"电脑 x {request.participant_count}台",
            "稳定的网络连接",
            "投影设备",
            "白纸和彩笔",
            "打印机和纸张"
        ]

        # 添加特定设备
        for equipment in request.available_equipment:
            if equipment == HardwareEquipment.PRINTER_3D:
                material_checklist.extend([
                    "3D打印机耗材(PLA线材)",
                    "3D打印工具套装"
                ])
            elif equipment == HardwareEquipment.ROBOT_ARM:
                material_checklist.append("机械臂控制软件")

        return TeacherPreparation(
            skill_requirements=skill_requirements,
            pre_course_preparation=pre_course_preparation,
            material_checklist=material_checklist,
            setup_instructions=[
                "课前30分钟到达，检查所有设备",
                "确保网络连接稳定",
                "准备AI工具的登录信息",
                "布置教室环境，营造创作氛围",
                "设置投影设备，确保所有学生能看清",
                "分发材料包到每个工作台",
                "准备计时器和提醒音",
                "测试所有AI工具的访问速度"
            ],
            ai_tools_to_master=ai_guidance,
            backup_plans=[
                "如果网络断线，准备离线活动",
                "如果AI工具无法访问，准备传统创作方法",
                "如果硬件故障，调整项目难度",
                "如果学生进度差异大，准备分层活动",
                "如果时间不够，准备简化版本",
                "如果学生对AI工具畏惧，先从简单体验开始",
                "准备纸质版的创作模板作为备选",
                "联系学校IT支持的应急联系方式"
            ]
        )

    def _initialize_ai_tools_database(self) -> Dict[AIToolType, Dict[str, Any]]:
        """初始化AI工具数据库"""

        return {
            AIToolType.AI_CHAT: {
                "tool_name": "ChatGPT",
                "tool_type": AIToolType.AI_CHAT,
                "description": "强大的AI对话助手，帮助头脑风暴和内容创作",
                "use_cases": ["创意构思", "文案写作", "问题解答", "学习辅导"],
                "step_by_step_tutorial": [
                    "1. 访问 chat.openai.com",
                    "2. 注册或登录账号",
                    "3. 在对话框中输入你的问题或需求",
                    "4. 点击发送，等待AI回复",
                    "5. 可以继续对话，深入讨论"
                ],
                "common_problems": [
                    "网络连接问题导致无法访问",
                    "AI回复不够准确或相关",
                    "不知道如何提问"
                ],
                "tips_and_tricks": [
                    "提问要具体和清晰",
                    "可以要求AI扮演特定角色",
                    "利用对话历史进行深入讨论",
                    "可以要求AI提供多个选项"
                ],
                "safety_considerations": [
                    "不要分享个人敏感信息",
                    "验证AI提供的事实信息",
                    "将AI作为辅助工具，不完全依赖"
                ]
            },

            AIToolType.AI_DRAWING: {
                "tool_name": "Midjourney",
                "tool_type": AIToolType.AI_DRAWING,
                "description": "顶级AI绘画工具，可以生成高质量的艺术作品",
                "use_cases": ["角色设计", "场景绘制", "概念图", "插画创作"],
                "step_by_step_tutorial": [
                    "1. 加入Midjourney的Discord服务器",
                    "2. 在指定频道输入 /imagine 命令",
                    "3. 输入英文描述你想要的图像",
                    "4. 等待AI生成4个选项",
                    "5. 选择喜欢的版本进行放大或变体"
                ],
                "common_problems": [
                    "生成的图像与预期不符",
                    "英文描述不够准确",
                    "等待时间较长"
                ],
                "tips_and_tricks": [
                    "使用具体的描述词汇",
                    "加入艺术风格关键词",
                    "使用 --ar 参数控制比例",
                    "可以参考他人的优秀提示词"
                ],
                "safety_considerations": [
                    "遵守社区准则",
                    "不生成不当内容",
                    "尊重版权，仅用于学习"
                ]
            },

            AIToolType.AI_3D_MODELING: {
                "tool_name": "Meshy AI",
                "tool_type": AIToolType.AI_3D_MODELING,
                "description": "AI驱动的3D建模工具，可以从文字描述生成3D模型",
                "use_cases": ["道具建模", "角色模型", "场景建模", "产品原型"],
                "step_by_step_tutorial": [
                    "1. 访问 meshy.ai 网站",
                    "2. 注册并登录账号",
                    "3. 选择 'Text to 3D' 功能",
                    "4. 输入详细的英文描述",
                    "5. 选择模型风格和质量",
                    "6. 等待生成完成",
                    "7. 下载3D模型文件"
                ],
                "common_problems": [
                    "模型细节不够精确",
                    "生成时间较长",
                    "文件格式兼容性问题"
                ],
                "tips_and_tricks": [
                    "描述要包含形状、材质、颜色",
                    "可以参考现实物体进行描述",
                    "选择合适的分辨率平衡质量和速度",
                    "生成后可以在Blender中进一步编辑"
                ],
                "safety_considerations": [
                    "检查模型的3D打印适用性",
                    "注意文件大小和格式",
                    "备份重要的模型文件"
                ]
            },

            AIToolType.AI_MUSIC: {
                "tool_name": "Suno AI",
                "tool_type": AIToolType.AI_MUSIC,
                "description": "AI音乐创作工具，可以根据描述生成完整歌曲",
                "use_cases": ["主题歌创作", "背景音乐", "音效制作", "音乐教学"],
                "step_by_step_tutorial": [
                    "1. 访问 suno.ai 网站",
                    "2. 注册并登录账号",
                    "3. 点击 'Create' 开始创作",
                    "4. 输入歌曲描述或歌词",
                    "5. 选择音乐风格和长度",
                    "6. 点击生成，等待完成",
                    "7. 试听并下载满意的作品"
                ],
                "common_problems": [
                    "生成的风格与预期不符",
                    "歌词与音乐不匹配",
                    "音质不够清晰"
                ],
                "tips_and_tricks": [
                    "明确指定音乐风格",
                    "提供清晰的情感描述",
                    "可以多次生成选择最佳版本",
                    "结合现有歌曲风格进行描述"
                ],
                "safety_considerations": [
                    "尊重音乐版权",
                    "仅用于教育和学习目的",
                    "不要商业使用生成的音乐"
                ]
            },

            AIToolType.AI_VIDEO: {
                "tool_name": "RunwayML",
                "tool_type": AIToolType.AI_VIDEO,
                "description": "强大的AI视频生成和编辑工具",
                "use_cases": ["视频创作", "动画制作", "特效添加", "视频编辑"],
                "step_by_step_tutorial": [
                    "1. 访问 runway.ml 网站",
                    "2. 注册并登录账号",
                    "3. 选择 'Gen-2' 文字转视频功能",
                    "4. 输入视频描述",
                    "5. 选择视频时长和质量",
                    "6. 点击生成，等待处理",
                    "7. 下载生成的视频"
                ],
                "common_problems": [
                    "视频质量不稳定",
                    "生成时间较长",
                    "描述理解偏差"
                ],
                "tips_and_tricks": [
                    "使用具体的场景描述",
                    "指定镜头类型和运动",
                    "提供参考图像效果更好",
                    "短视频效果通常更稳定"
                ],
                "safety_considerations": [
                    "注意版权问题",
                    "不生成不当内容",
                    "遵守平台使用规范"
                ]
            },

            AIToolType.AI_ANIMATION: {
                "tool_name": "即梦 (LeiaPix)",
                "tool_type": AIToolType.AI_ANIMATION,
                "description": "将静态图片转换为动态3D效果的AI工具",
                "use_cases": ["图片动画化", "3D效果制作", "创意展示", "视觉特效"],
                "step_by_step_tutorial": [
                    "1. 访问 convert.leiapix.com",
                    "2. 上传要处理的图片",
                    "3. 选择动画风格和强度",
                    "4. 调整3D深度参数",
                    "5. 预览效果",
                    "6. 导出动画文件"
                ],
                "common_problems": [
                    "某些图片效果不佳",
                    "动画可能显得不自然",
                    "处理时间不确定"
                ],
                "tips_and_tricks": [
                    "选择有明显前后景的图片",
                    "人物肖像效果通常很好",
                    "风景照也容易产生好效果",
                    "避免过于复杂的图片"
                ],
                "safety_considerations": [
                    "尊重图片版权",
                    "不上传他人私人照片",
                    "注意隐私保护"
                ]
            },

            AIToolType.AI_DESIGN: {
                "tool_name": "Canva AI",
                "tool_type": AIToolType.AI_DESIGN,
                "description": "AI辅助的设计平台，快速创建各种视觉设计",
                "use_cases": ["海报设计", "演示文稿", "社交媒体图片", "品牌设计"],
                "step_by_step_tutorial": [
                    "1. 访问 canva.com",
                    "2. 注册并登录账号",
                    "3. 选择设计类型",
                    "4. 使用AI设计助手",
                    "5. 输入设计需求",
                    "6. 选择AI生成的模板",
                    "7. 自定义和调整",
                    "8. 导出设计作品"
                ],
                "common_problems": [
                    "AI生成的设计过于通用",
                    "颜色搭配不够理想",
                    "字体选择有限"
                ],
                "tips_and_tricks": [
                    "明确指定设计风格",
                    "提供详细的设计要求",
                    "利用品牌色彩功能",
                    "结合手动调整优化效果"
                ],
                "safety_considerations": [
                    "注意版权问题",
                    "避免使用受保护的素材",
                    "遵守品牌使用规范"
                ]
            },

            AIToolType.AI_CODING: {
                "tool_name": "GitHub Copilot",
                "tool_type": AIToolType.AI_CODING,
                "description": "AI编程助手，帮助编写和优化代码",
                "use_cases": ["代码生成", "编程学习", "bug修复", "算法优化"],
                "step_by_step_tutorial": [
                    "1. 安装VS Code编辑器",
                    "2. 安装GitHub Copilot插件",
                    "3. 登录GitHub账号",
                    "4. 在代码编辑器中写注释",
                    "5. 观察AI生成的代码建议",
                    "6. 按Tab键接受建议",
                    "7. 调试和测试代码"
                ],
                "common_problems": [
                    "生成的代码可能有错误",
                    "不理解具体业务逻辑",
                    "依赖性问题"
                ],
                "tips_and_tricks": [
                    "写清晰的注释描述",
                    "分步骤编写代码",
                    "及时测试生成的代码",
                    "结合自己的判断使用"
                ],
                "safety_considerations": [
                    "检查代码安全性",
                    "避免泄露敏感信息",
                    "遵守代码许可协议"
                ]
            },

            AIToolType.AI_WEB_DEV: {
                "tool_name": "Cursor",
                "tool_type": AIToolType.AI_WEB_DEV,
                "description": "AI驱动的网页开发工具",
                "use_cases": ["网站建设", "前端开发", "界面设计", "代码优化"],
                "step_by_step_tutorial": [
                    "1. 下载安装Cursor编辑器",
                    "2. 创建新的项目",
                    "3. 使用AI助手描述需求",
                    "4. AI生成基础代码结构",
                    "5. 逐步完善功能",
                    "6. 预览和测试网站",
                    "7. 部署上线"
                ],
                "common_problems": [
                    "生成的界面可能不够美观",
                    "功能实现可能不完整",
                    "兼容性问题"
                ],
                "tips_and_tricks": [
                    "详细描述界面需求",
                    "分模块开发",
                    "及时测试功能",
                    "学习基础网页知识"
                ],
                "safety_considerations": [
                    "注意网站安全性",
                    "保护用户数据",
                    "遵守网络安全规范"
                ]
            }
        }

    def _initialize_institution_templates(self) -> Dict[InstitutionType, InstitutionTemplate]:
        """初始化机构模板"""

        return {
            InstitutionType.MAKER_SPACE: InstitutionTemplate(
                institution_type=InstitutionType.MAKER_SPACE,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.PRINTER_3D,
                    HardwareEquipment.ROBOT_ARM,
                    HardwareEquipment.CAMERA,
                    HardwareEquipment.PROJECTOR
                ],
                recommended_ai_tools=[
                    AIToolType.AI_CHAT,
                    AIToolType.AI_DRAWING,
                    AIToolType.AI_3D_MODELING,
                    AIToolType.AI_CODING
                ],
                integration_suggestions=[
                    "充分利用3D打印机和机械臂等硬件设备",
                    "结合AI工具进行数字化创作",
                    "注重动手实践和创造体验",
                    "培养学生的工程思维和创新能力"
                ],
                sample_projects=[
                    "AI辅助机器人设计",
                    "智能家居原型制作",
                    "3D打印创意产品",
                    "互动装置艺术"
                ]
            ),

            InstitutionType.MUSIC_SCHOOL: InstitutionTemplate(
                institution_type=InstitutionType.MUSIC_SCHOOL,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.MICROPHONE,
                    HardwareEquipment.PROJECTOR
                ],
                recommended_ai_tools=[
                    AIToolType.AI_MUSIC,
                    AIToolType.AI_CHAT,
                    AIToolType.AI_VIDEO
                ],
                integration_suggestions=[
                    "结合传统音乐教学与AI创作",
                    "使用AI工具进行音乐创作和编曲",
                    "培养学生的音乐创新思维",
                    "探索AI在音乐教育中的应用"
                ],
                sample_projects=[
                    "AI协助歌曲创作",
                    "音乐风格融合实验",
                    "智能音乐教学助手",
                    "音乐视频制作"
                ]
            ),

            InstitutionType.ART_SCHOOL: InstitutionTemplate(
                institution_type=InstitutionType.ART_SCHOOL,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.TABLET,
                    HardwareEquipment.CAMERA,
                    HardwareEquipment.PROJECTOR
                ],
                recommended_ai_tools=[
                    AIToolType.AI_DRAWING,
                    AIToolType.AI_ANIMATION,
                    AIToolType.AI_DESIGN,
                    AIToolType.AI_VIDEO
                ],
                integration_suggestions=[
                    "将AI绘画融入传统美术教学",
                    "探索数字艺术创作新方式",
                    "培养学生的视觉创新能力",
                    "结合传统技法与AI工具"
                ],
                sample_projects=[
                    "AI辅助插画设计",
                    "数字艺术作品集",
                    "动画短片制作",
                    "概念艺术创作"
                ]
            ),

            InstitutionType.CODING_SCHOOL: InstitutionTemplate(
                institution_type=InstitutionType.CODING_SCHOOL,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.PROJECTOR,
                    HardwareEquipment.SMART_BOARD
                ],
                recommended_ai_tools=[
                    AIToolType.AI_CODING,
                    AIToolType.AI_CHAT,
                    AIToolType.AI_WEB_DEV,
                    AIToolType.AI_TUTORING
                ],
                integration_suggestions=[
                    "使用AI辅助编程学习",
                    "培养与AI协作编程的能力",
                    "探索AI在软件开发中的应用",
                    "提升编程效率和质量"
                ],
                sample_projects=[
                    "AI聊天机器人开发",
                    "智能网页应用",
                    "游戏AI设计",
                    "自动化工具开发"
                ]
            ),

            InstitutionType.STEM_CENTER: InstitutionTemplate(
                institution_type=InstitutionType.STEM_CENTER,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.PRINTER_3D,
                    HardwareEquipment.ROBOT_ARM,
                    HardwareEquipment.PROJECTOR,
                    HardwareEquipment.SMART_BOARD
                ],
                recommended_ai_tools=[
                    AIToolType.AI_CHAT,
                    AIToolType.AI_3D_MODELING,
                    AIToolType.AI_CODING,
                    AIToolType.AI_DESIGN
                ],
                integration_suggestions=[
                    "结合科学实验与AI工具",
                    "使用AI进行数据分析和建模",
                    "培养科学研究与AI协作能力",
                    "探索AI在STEM领域的应用"
                ],
                sample_projects=[
                    "AI辅助科学实验",
                    "智能环境监测系统",
                    "机器人控制程序",
                    "数据可视化项目"
                ]
            ),

            InstitutionType.GENERAL_SCHOOL: InstitutionTemplate(
                institution_type=InstitutionType.GENERAL_SCHOOL,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.TABLET,
                    HardwareEquipment.PROJECTOR,
                    HardwareEquipment.SMART_BOARD
                ],
                recommended_ai_tools=[
                    AIToolType.AI_CHAT,
                    AIToolType.AI_TUTORING,
                    AIToolType.AI_DRAWING,
                    AIToolType.AI_PRESENTATION
                ],
                integration_suggestions=[
                    "将AI工具融入各学科教学",
                    "培养学生的AI素养",
                    "探索跨学科项目学习",
                    "提升教学效率和趣味性"
                ],
                sample_projects=[
                    "AI辅助学科研究",
                    "多媒体演示制作",
                    "创意写作与AI协作",
                    "跨学科综合项目"
                ]
            ),

            InstitutionType.COMMUNITY_CENTER: InstitutionTemplate(
                institution_type=InstitutionType.COMMUNITY_CENTER,
                typical_equipment=[
                    HardwareEquipment.COMPUTER,
                    HardwareEquipment.PROJECTOR,
                    HardwareEquipment.CAMERA
                ],
                recommended_ai_tools=[
                    AIToolType.AI_CHAT,
                    AIToolType.AI_DRAWING,
                    AIToolType.AI_VIDEO,
                    AIToolType.AI_MUSIC
                ],
                integration_suggestions=[
                    "面向社区居民的AI普及教育",
                    "结合社区文化活动",
                    "培养数字化生活技能",
                    "促进代际间的学习交流"
                ],
                sample_projects=[
                    "社区故事数字化",
                    "AI辅助社区宣传",
                    "数字艺术创作",
                    "智慧生活体验"
                ]
            )
        }

    def _initialize_duration_configs(self) -> Dict[DurationType, Dict[str, Any]]:
        """初始化时长配置"""

        return {
            DurationType.HALF_DAY: {
                "total_hours": 3.5,
                "suggested_sessions": "单次完成",
                "break_count": 1,
                "activity_count": "3-4个"
            },
            DurationType.ONE_DAY: {
                "total_hours": 7,
                "suggested_sessions": "单天完成",
                "break_count": 3,
                "activity_count": "5-6个"
            },
            DurationType.TWO_DAY: {
                "total_hours": 14,
                "suggested_sessions": "连续两天",
                "break_count": 6,
                "activity_count": "8-10个"
            },
            DurationType.THREE_DAY: {
                "total_hours": 21,
                "suggested_sessions": "连续三天",
                "break_count": 9,
                "activity_count": "12-15个"
            },
            DurationType.WEEKLY: {
                "total_hours": 12,
                "suggested_sessions": "每周2小时，连续6周",
                "break_count": 6,
                "activity_count": "15-18个"
            }
        }

    def _get_institution_template(self, institution_type: InstitutionType) -> InstitutionTemplate:
        """获取机构模板"""
        return self.institution_templates.get(institution_type, self.institution_templates[InstitutionType.MAKER_SPACE])

    def _extract_learning_objectives(self, agents_data: Dict, request: EnhancedCourseRequest) -> List[str]:
        """提取学习目标"""

        # 基础目标
        objectives = [
            f"掌握{len(request.target_ai_tools)}种AI工具的基本使用方法",
            "学会与AI协作完成创意项目",
            "培养数字时代的问题解决能力",
            "提升团队协作和沟通表达能力"
        ]

        # 根据具体设备添加目标
        if HardwareEquipment.PRINTER_3D in request.available_equipment:
            objectives.append("掌握3D建模和3D打印的基础技能")

        if HardwareEquipment.ROBOT_ARM in request.available_equipment:
            objectives.append("了解机械臂操作和自动化控制")

        return objectives

    def _generate_classroom_management(self, request: EnhancedCourseRequest) -> List[str]:
        """生成课堂管理指导"""

        management_tips = [
            f"合理分组：建议{request.participant_count}人分成{max(1, request.participant_count//3-4)}组，每组3-4人",
            "时间管理：每个活动设置明确的时间限制，使用计时器提醒",
            "设备管理：提前分配设备，确保每组都有必要的工具",
            "进度监控：定期巡视各组进度，及时提供帮助",
            "安全管理：特别注意3D打印机等设备的安全使用",
            "作品保存：及时保存学生的数字作品，避免丢失",
            "展示环节：给每组充分的展示时间，鼓励互相学习"
        ]

        if request.teacher_ai_experience == "beginner":
            management_tips.extend([
                "准备助教：如有条件，安排AI工具熟练的助教协助",
                "预先练习：课前自己先完整体验一遍所有AI工具",
                "准备应急：准备传统创作方法作为AI工具故障时的替代方案"
            ])

        return management_tips

    def _generate_assessment_methods(self, request: EnhancedCourseRequest) -> List[Dict[str, Any]]:
        """生成评估方法"""

        return [
            {
                "type": "过程评估",
                "weight": "40%",
                "methods": ["观察学生AI工具使用情况", "记录团队协作表现", "检查项目进展"],
                "criteria": ["参与度", "创新性", "协作能力"]
            },
            {
                "type": "成果评估",
                "weight": "40%",
                "methods": ["评价最终作品质量", "检查交付物完整性"],
                "criteria": ["技术实现", "创意水平", "完成度"]
            },
            {
                "type": "展示评估",
                "weight": "20%",
                "methods": ["学生演讲展示", "同伴互评"],
                "criteria": ["表达清晰", "逻辑性", "感染力"]
            }
        ]

    def _generate_required_materials(self, request: EnhancedCourseRequest) -> List[str]:
        """生成必需材料清单"""

        materials = [
            f"电脑 x {request.participant_count}台",
            "稳定的网络连接",
            "投影设备和音响",
            "白纸和彩色笔",
            "打印机和A4纸"
        ]

        for equipment in request.available_equipment:
            if equipment == HardwareEquipment.PRINTER_3D:
                materials.extend(["3D打印机", "PLA打印耗材", "3D打印工具"])
            elif equipment == HardwareEquipment.ROBOT_ARM:
                materials.extend(["机械臂", "控制软件", "安全防护用品"])
            elif equipment == HardwareEquipment.CAMERA:
                materials.extend(["数码相机或摄像设备", "三脚架", "存储卡"])

        return materials

    def _generate_optional_materials(self, request: EnhancedCourseRequest) -> List[str]:
        """生成可选材料清单"""

        return [
            "装饰材料（贴纸、亮片等）",
            "展示用的展板或画架",
            "小礼品作为鼓励奖励",
            "即拍即贴相机记录过程",
            "背景音乐播放设备",
            "茶点和饮料"
        ]

    def _generate_variations(self, request: EnhancedCourseRequest) -> List[str]:
        """生成变体方案"""

        variations = []

        if request.duration_type == DurationType.HALF_DAY:
            variations.extend([
                "压缩版：专注于AI工具体验，减少3D打印环节",
                "体验版：增加更多AI工具试用，减少深度制作"
            ])
        elif request.duration_type == DurationType.ONE_DAY:
            variations.extend([
                "深度版：增加项目复杂度和技术深度",
                "展示版：增加公开展示和媒体记录环节"
            ])

        if request.participant_count > 20:
            variations.append("大班版：增加助教，调整分组策略")
        elif request.participant_count < 8:
            variations.append("小班版：增加个人指导时间")

        return variations

    def _generate_scaling_options(self, request: EnhancedCourseRequest) -> List[str]:
        """生成扩展选项"""

        return [
            "进阶课程：为完成基础课程的学生设计更高级的项目",
            "家长工作坊：邀请家长参与，了解AI教育",
            "教师培训：为其他教师提供AI工具使用培训",
            "社区展示：在社区举办学生作品展览",
            "线上分享：建立线上社群，持续分享学习成果",
            "竞赛活动：组织相关主题的创意竞赛"
        ]

    def _create_fallback_enhanced_course(
        self,
        request: EnhancedCourseRequest,
        course_id: str,
        error: str
    ) -> EnhancedCourseResponse:
        """创建增强版fallback课程"""

        # 获取机构模板
        institution_template = self._get_institution_template(request.institution_type)
        duration_config = self.duration_configs[request.duration_type]

        # 生成基础组件
        schedule = self._generate_detailed_schedule(request, duration_config)
        ai_tools_guidance = self._generate_ai_tools_guidance(request.target_ai_tools)
        teacher_preparation = self._generate_teacher_preparation(request, ai_tools_guidance)

        return EnhancedCourseResponse(
            course_id=course_id,
            title=request.title,
            theme_concept=request.theme_concept,

            overview={
                "institution_type": request.institution_type.value,
                "duration": duration_config['total_hours'],
                "participants": request.participant_count,
                "fallback_mode": True,
                "error": error
            },

            learning_objectives=self._extract_learning_objectives({}, request),
            driving_question=f"如何通过{request.theme_concept}项目，掌握AI时代的核心能力？",

            schedule=schedule,
            detailed_activities=self._generate_detailed_activities(request, {}),
            ai_tools_guidance=ai_tools_guidance,
            teacher_preparation=teacher_preparation,

            classroom_management=self._generate_classroom_management(request),
            assessment_methods=self._generate_assessment_methods(request),
            expected_outcomes=request.specific_deliverables,

            required_materials=self._generate_required_materials(request),
            optional_materials=self._generate_optional_materials(request),

            variations=self._generate_variations(request),
            scaling_options=self._generate_scaling_options(request),

            institution_template=institution_template,
            creation_metadata={
                "fallback_mode": True,
                "error": error,
                "created_at": datetime.now().isoformat()
            }
        )


# 全局实例
enhanced_course_designer = EnhancedCourseDesigner()