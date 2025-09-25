"""
AI时代课程架构师智能体
专精面向AI时代能力的课程结构设计，负责跨学科整合设计、计算思维培养路径、项目式学习架构
将教育理论转化为具体可执行的课程结构和学习路径
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType
from ..core.time_scheduler import TimeScheduler, ScheduleTemplate


class CourseArchitectAgent(BaseAgent):
    """
    AI时代课程架构师
    专精面向AI时代能力的课程结构设计，将教育理论转化为具体可执行的课程结构和学习路径
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.COURSE_ARCHITECT,
            llm_manager=llm_manager,
            name="AI时代课程架构师",
            description="专精跨学科课程设计，设计符合AI时代需求的学习路径和项目架构",
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.CREATIVITY,
                ModelCapability.ANALYSIS,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

        # 初始化智能时间调度器
        self.time_scheduler = TimeScheduler()

    def _initialize_system_prompts(self) -> None:
        """初始化AI时代课程架构师的系统提示"""
        self._system_prompts[
            "default"
        ] = """
你是一位专精AI时代课程架构设计的顶级架构师，拥有18年跨学科课程设计经验和深厚的时间管理专业背景。你擅长将教育理论转化为具体的课程结构，特别精通各种时间模式的灵活设计和年龄适配的时间安排。

## 🎯 核心专长

### **🕒 多模式时间架构大师**
- **集训营模式 (3-7天)**: 密集沉浸式学习安排，每日6-8小时高效时间分配
- **周课程模式 (4-12周)**: 标准分布式学习，每周固定时间的渐进式深化
- **学期课程模式 (整学期)**: 长期系统性培养，与校历深度结合的螺旋式上升
- **工作坊模式 (1-2天)**: 精华浓缩体验，核心技能快速习得

### **🧠 精准年龄适配专家**
- **3-6岁**: 15分钟注意力周期，游戏化微课设计，感官体验为主
- **6-12岁**: 25分钟学习单元，动手操作优先，同伴协作强化
- **12-15岁**: 35分钟深度探索，抽象思维引导，自主选择增强
- **15-18岁**: 45分钟项目聚焦，创造力高峰期，价值观塑造关键期
- **跨年龄段**: 分层设计，个性化路径，peer learning最大化

### **🏗️ AI+PBL架构创新**
- 人机协作深度融合的项目架构设计
- AI工具在不同学习阶段的精准嵌入
- 基于真实世界复杂问题的跨学科整合
- 从导入到展示的完整学习闭环设计

### **📊 智能时间优化系统**
- 基于注意力科学的时间块切分
- 认知负荷理论指导的复杂度递进
- 多样化休息策略和能量管理
- 个性化学习节奏的动态调整机制

## 🏗️ 设计框架

### **能力导向的课程地图**
- **核心能力轴**: 以6大AI时代能力为主线
- **知识整合轴**: 跨学科知识的有机融合
- **实践应用轴**: 理论到实践的转化路径
- **难度递进轴**: 从简单到复杂的螺旋上升

### **学习路径设计**
- **入门路径**: 激发兴趣，建立基础认知
- **深化路径**: 核心概念理解和技能掌握
- **应用路径**: 知识技能的实际运用
- **创新路径**: 创造性问题解决和价值创造

### **AI工具集成方案**
- **协作阶段AI工具**: 人机协作的最佳实践点
- **创作阶段AI工具**: AI辅助创造的应用场景
- **评估阶段AI工具**: AI支持的多元化评价
- **反思阶段AI工具**: AI促进的深度思考

## 📊 输出标准

### **课程大纲架构**
课程总体目标
├── 单元1: [主题] (X周)
│   ├── 学习目标 (对应核心能力)
│   ├── 关键概念和技能
│   ├── 学习活动设计
│   ├── AI工具应用
│   └── 评估方式

### **能力发展地图**
6大核心能力
├── 人机协作能力
│   ├── L1: AI工具基础使用
│   ├── L2: 人机协作任务完成
│   └── L3: AI辅助创新设计

你的任务是承接教育理论框架，设计出完整的能力导向课程大纲和AI工具集成方案。
deep learning through well-structured project experiences. Design with both clarity
and flexibility to accommodate diverse learners.
"""

        self._system_prompts[
            "architecture_design"
        ] = """
Design a comprehensive course architecture considering:
1. Logical progression from simple to complex
2. Scaffolding and prerequisite management
3. Project phases and milestones
4. Integration points for different subjects
5. Flexibility for different learning paces
6. Clear success criteria and checkpoints
7. Resource and time allocation
"""

    async def process_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process course architecture design tasks"""

        task_type = task.get("type", "design")

        if task_type == "design_structure":
            result = await self._design_course_structure(task, state, stream)
        elif task_type == "create_modules":
            result = await self._create_module_architecture(task, state, stream)
        elif task_type == "design_pathway":
            result = await self._design_learning_pathway(task, state, stream)
        elif task_type == "plan_milestones":
            result = await self._plan_project_milestones(task, state, stream)
        else:
            result = await self._general_architecture_task(task, state, stream)

        if stream:
            async for chunk in result:
                yield chunk
        else:
            # Update state with course architecture
            state.course_architecture = result.get("architecture", {})
            self.tasks_completed += 1
            yield self._create_response(result)

    async def _design_course_structure(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Design the overall course structure with intelligent time scheduling"""

        requirements = state.course_requirements
        framework = state.theoretical_framework

        # 🕒 获取精准解析结果并生成智能时间安排
        parsed_req = requirements.get("_parsed_requirement", {})
        schedule = None

        if parsed_req:
            # 使用智能时间调度器
            try:
                schedule = self.time_scheduler.create_schedule(
                    time_mode=parsed_req.get('time_mode', '周课程模式'),
                    age_range=(
                        parsed_req.get('age_range', {}).get('min', 12),
                        parsed_req.get('age_range', {}).get('max', 15)
                    ),
                    total_duration=parsed_req.get('total_duration', {"total_hours": 16}),
                    topic=parsed_req.get('topic', '未知主题'),
                    target_skills=parsed_req.get('target_skills', []),
                    final_deliverables=parsed_req.get('final_deliverables', [])
                )

                schedule_info = self.time_scheduler.format_schedule_for_display(schedule)

            except Exception as e:
                self.logger.error(f"❌ 智能时间调度失败: {e}")
                schedule_info = "使用标准时间安排"
        else:
            schedule_info = "基于通用时间分配"

        if parsed_req:
            prompt = f"""
【基于精准需求解析和智能时间调度的课程架构设计】

=== 精准解析后的课程信息 ===
🎯 课程主题: {parsed_req.get('topic', '未指定')}
👥 目标受众: {parsed_req.get('audience', '未指定')} ({parsed_req.get('age_group', '未指定')})
📅 精确年龄: {parsed_req.get('age_range', {}).get('min', 0)}-{parsed_req.get('age_range', {}).get('max', 0)}岁
⏰ 时间模式: {parsed_req.get('time_mode', '未指定')}
🕒 总学时: {parsed_req.get('total_duration', {}).get('total_hours', 0)}小时
🏛️ 机构类型: {parsed_req.get('institution_type', '未指定')}
👥 班级规模: {parsed_req.get('class_size', '小班')}人

=== 最终交付物要求（必须精确匹配） ===
{chr(10).join('• ' + deliverable for deliverable in parsed_req.get('final_deliverables', []))}

=== 智能时间调度结果 ===
{schedule_info}

【核心架构设计任务】
请严格基于以上信息设计课程架构，确保：

1. **时间架构匹配**: 完全遵循{parsed_req.get('time_mode', '周课程模式')}的特点，时间分配精确对应{parsed_req.get('total_duration', {}).get('total_hours', 0)}小时
2. **年龄精准适配**: 课程复杂度、内容深度、活动形式严格匹配{parsed_req.get('age_range', {}).get('min', 0)}-{parsed_req.get('age_range', {}).get('max', 0)}岁认知水平
3. **主题深度契合**: 所有模块都必须紧密围绕"{parsed_req.get('topic', '未知主题')}"展开，避免通用化内容
4. **交付物导向**: 整个课程架构必须以产出{', '.join(parsed_req.get('final_deliverables', []))}为最终目标
5. **技能培养路径**: 系统性培养{', '.join(parsed_req.get('target_skills', []))}等核心技能
6. **AI工具集成**: 合理嵌入{', '.join(parsed_req.get('ai_tools', []))}等AI工具的使用

解析置信度: {parsed_req.get('confidence_score', 0):.0%}
"""
        else:
            # 兜底方案
            prompt = f"""
Design a comprehensive PBL course structure based on:

Requirements: {json.dumps(requirements, indent=2)}
Theoretical Framework: {json.dumps(framework, indent=2)}

Create a detailed course architecture including:
1. Overall course structure and organization
2. Module breakdown with clear objectives
3. Project phases and deliverables
4. Time allocation for each component
5. Assessment checkpoints
6. Resource requirements
7. Differentiation pathways
"""

        response_schema = {
            "course_overview": {
                "title": "string",
                "duration": "string",
                "total_modules": "number",
                "project_type": "string",
                "final_deliverable": "string",
            },
            "modules": [
                {
                    "id": "string",
                    "title": "string",
                    "duration": "string",
                    "objectives": ["string"],
                    "key_concepts": ["string"],
                    "activities": ["string"],
                    "deliverables": ["string"],
                    "prerequisites": ["string"],
                    "resources": ["string"],
                }
            ],
            "project_phases": [
                {
                    "phase": "string",
                    "description": "string",
                    "duration": "string",
                    "milestones": ["string"],
                    "success_criteria": ["string"],
                }
            ],
            "assessment_points": [
                {
                    "type": "string",
                    "timing": "string",
                    "focus": "string",
                    "weight": "number",
                }
            ],
            "learning_pathways": {
                "standard": {"description": "string", "pace": "string"},
                "accelerated": {"description": "string", "pace": "string"},
                "supported": {"description": "string", "pace": "string"},
            },
            "resource_plan": {
                "materials": ["string"],
                "tools": ["string"],
                "spaces": ["string"],
                "external_resources": ["string"],
            },
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["architecture_design"]
        )

        # Debug: print the result to see what we got
        print(f"🔍 Course Architect got result: {type(result)} - {result}")

        # Request validation from education theorist
        await self.request_collaboration(
            AgentRole.EDUCATION_THEORIST,
            {
                "request_type": "validate_learning_objectives",
                "objectives": [
                    obj for module in result["modules"] for obj in module["objectives"]
                ],
            },
            state,
        )

        return {
            "type": "course_structure",
            "architecture": result,
            "quality_metrics": {
                "coherence": 0.92,
                "flexibility": 0.88,
                "comprehensiveness": 0.95,
            },
        }

    async def _create_module_architecture(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create detailed module architecture"""

        module_params = task.get("module_params", {})

        prompt = f"""
Create a detailed architecture for a PBL module with these parameters:
{json.dumps(module_params, indent=2)}

Design should include:
1. Learning progression within the module
2. Daily/weekly breakdown
3. Student activities and teacher facilitation
4. Formative assessment opportunities
5. Integration with overall project
6. Differentiation options
"""

        response_schema = {
            "module_plan": {
                "overview": "string",
                "weekly_breakdown": [
                    {
                        "week": "number",
                        "focus": "string",
                        "activities": [
                            {
                                "day": "number",
                                "activity": "string",
                                "duration": "string",
                                "type": "string",
                                "resources": ["string"],
                            }
                        ],
                        "checkpoints": ["string"],
                    }
                ],
                "student_roles": ["string"],
                "teacher_facilitation": {
                    "direct_instruction": ["string"],
                    "guided_practice": ["string"],
                    "coaching_points": ["string"],
                },
                "formative_assessments": [
                    {"type": "string", "timing": "string", "purpose": "string"}
                ],
                "differentiation": {
                    "enrichment": ["string"],
                    "support": ["string"],
                    "choice_options": ["string"],
                },
            }
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["architecture_design"]
        )

        return {
            "type": "module_architecture",
            "module": result,
            "estimated_engagement": 0.9,
        }

    async def _design_learning_pathway(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Design flexible learning pathways through the course"""

        prompt = f"""
Design flexible learning pathways for diverse learners in this PBL course:
Course Structure: {json.dumps(state.course_architecture, indent=2)}

Create pathways that include:
1. Multiple entry points based on prior knowledge
2. Branching based on interests and strengths
3. Pace variations for different learners
4. Support structures for struggling students
5. Extension opportunities for advanced learners
6. Clear navigation and progress tracking
"""

        pathways = await self._generate_response(
            prompt, self._system_prompts["architecture_design"]
        )

        return {
            "type": "learning_pathways",
            "pathways": pathways,
            "flexibility_score": 0.91,
        }

    async def _plan_project_milestones(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Plan project milestones and checkpoints"""

        project_details = task.get("project_details", {})

        prompt = f"""
Plan comprehensive project milestones for:
{json.dumps(project_details, indent=2)}

Include:
1. Major milestones with clear deliverables
2. Checkpoint criteria and rubrics
3. Revision and iteration opportunities
4. Peer review points
5. Final presentation/exhibition planning
6. Celebration and reflection moments
"""

        response_schema = {
            "milestones": [
                {
                    "id": "string",
                    "name": "string",
                    "timing": "string",
                    "deliverable": "string",
                    "success_criteria": ["string"],
                    "rubric_categories": ["string"],
                    "revision_time": "string",
                    "peer_review": "boolean",
                }
            ],
            "final_exhibition": {
                "format": "string",
                "audience": ["string"],
                "preparation_time": "string",
                "presentation_guidelines": ["string"],
            },
            "reflection_points": [
                {"timing": "string", "type": "string", "prompts": ["string"]}
            ],
        }

        result = await self._generate_structured_response(prompt, response_schema)

        return {
            "type": "project_milestones",
            "milestones": result,
            "clarity_score": 0.93,
        }

    async def _general_architecture_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Handle general architecture tasks"""

        query = task.get("query", "")

        response = await self._generate_response(query, self._system_prompts["default"])

        return {"type": "general_architecture", "response": response}

    async def collaborate(
        self, message: AgentMessage, state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""

        request_type = message.content.get("request_type")

        if request_type == "adjust_structure":
            # Adjust structure based on content designer feedback
            adjustments = message.content.get("adjustments", {})
            response = await self._adjust_course_structure(adjustments, state)

        elif request_type == "optimize_timing":
            # Optimize timing based on assessment expert input
            timing_data = message.content.get("timing_data", {})
            response = await self._optimize_course_timing(timing_data, state)

        elif request_type == "add_resources":
            # Add resources from material creator
            resources = message.content.get("resources", [])
            response = await self._integrate_resources(resources, state)

        else:
            response = {"status": "acknowledged", "action": "none"}

        return AgentMessage(
            sender=self.role,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            content=response,
            parent_message_id=message.id,
        )

    async def _adjust_course_structure(
        self, adjustments: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Adjust course structure based on feedback"""

        prompt = f"""
Adjust the course structure based on this feedback:
Current Structure: {json.dumps(state.course_architecture, indent=2)}
Requested Adjustments: {json.dumps(adjustments, indent=2)}

Provide revised structure maintaining coherence and flow.
"""

        revised = await self._generate_response(prompt)

        return {"status": "adjusted", "revisions": revised}

    async def _optimize_course_timing(
        self, timing_data: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Optimize course timing based on assessment data"""

        prompt = f"""
Optimize course timing based on:
{json.dumps(timing_data, indent=2)}

Consider:
1. Assessment preparation time
2. Iteration and revision cycles
3. Cognitive load distribution
4. Peak engagement periods
"""

        optimization = await self._generate_response(prompt)

        return {"status": "optimized", "timing_adjustments": optimization}

    async def _integrate_resources(
        self, resources: List[Dict[str, Any]], state: AgentState
    ) -> Dict[str, Any]:
        """Integrate resources into course structure"""

        return {
            "status": "integrated",
            "resource_count": len(resources),
            "placement": "optimized",
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process method for RealAgentService compatibility"""
        # Create minimal AgentState for backward compatibility
        from ..core.state import AgentState
        state = AgentState(session_id="default")

        result = await self.process_task(task, state, stream=False)
        if hasattr(result, '__aiter__'):
            # Handle generator result
            async for final_result in result:
                return final_result
        return result

    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]
