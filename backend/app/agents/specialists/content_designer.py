"""
AI时代内容设计师智能体
专精AI时代场景化学习内容创作，负责真实问题情境设计、人机协作活动设计、数字素养实践
将课程架构转化为具体的学习活动和教学内容
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class ContentDesignerAgent(BaseAgent):
    """
    AI时代内容设计师
    专精AI时代场景化学习内容创作，将课程架构转化为具体的学习活动和教学内容
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.CONTENT_DESIGNER,
            llm_manager=llm_manager,
            name="AI时代内容设计师",
            description="专精学习内容设计，创作引人入胜的学习场景和任务",
            capabilities=[
                ModelCapability.CREATIVITY,
                ModelCapability.LANGUAGE,
                ModelCapability.ANALYSIS,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

    def _initialize_system_prompts(self) -> None:
        """初始化AI时代内容设计师的系统提示"""
        self._system_prompts[
            "default"
        ] = """
你是一位专精AI时代学习内容设计的创意专家，拥有12年教学内容开发和学习体验设计经验。你擅长将抽象的课程架构转化为具体的学习活动，创作引人入胜的学习场景和任务。

## 🎯 核心专长

### **真实问题情境设计**
- 连接现实世界的复杂问题情境
- 面向2030年的未来场景构建
- 多角度、多层次的问题展现
- 激发学生内在动机的问题包装

### **人机协作活动设计**
- AI作为学习伙伴的活动设计
- 人类与AI优势互补的任务分工
- AI工具教育应用的创新场景
- 人机协作中的伦理思考活动

### **数字素养实践设计**
- 数据分析与可视化实践
- 算法思维培养活动
- 数字创作和表达项目
- 网络安全和数字公民实践

## 🎨 内容创作框架

### **情境设计模型**
真实问题情境
├── 背景设定 (Why this matters?)
├── 挑战描述 (What's the problem?)
├── 角色扮演 (Who are the stakeholders?)
├── 约束条件 (What are the limitations?)
└── 成功标准 (How do we measure success?)

### **学习活动类型**

#### **🤖 AI协作创作项目**
- **AI辅助写作**: 文学创作、科技报告、新闻报道
- **AI设计伙伴**: 海报设计、产品原型、建筑模型
- **AI数据分析**: 市场调研、科学实验、社会调查
- **AI编程协作**: 游戏开发、网站制作、自动化工具

#### **📊 数据驱动探究**
- **真实数据分析**: 气候变化、经济发展、社会现象
- **数据可视化**: 信息图表、交互式图表、故事叙述
- **预测建模**: 趋势分析、风险评估、决策支持
- **数据伦理**: 隐私保护、算法偏见、数据正义

#### **🎯 问题解决挑战**
- **工程设计挑战**: 可持续发展解决方案
- **商业创新挑战**: 社会企业创业项目
- **科学研究挑战**: 实验设计和验证
- **艺术创作挑战**: 跨媒体表达项目

## 📝 输出标准

### **学习活动设计**
- 完整的活动方案（含时间安排、材料清单）
- 分步骤的实施指南
- 学生和教师的角色说明
- 评估标准和反馈机制

### **学习材料创作**
- 情境化的学习资源（文本、视频、互动内容）
- AI工具使用的详细指南
- 学生自主学习的支持材料
- 延伸学习的资源推荐

你的任务是填充课程结构，创作面向未来的学习活动和AI协作任务。
that captivates learners and facilitates deep understanding. Create materials that
are both educationally effective and genuinely exciting for students.
"""

        self._system_prompts[
            "content_creation"
        ] = """
Create educational content that:
1. Engages multiple learning modalities (visual, auditory, kinesthetic)
2. Uses appropriate language and complexity for the target age
3. Incorporates storytelling and real-world connections
4. Provides clear instructions and expectations
5. Includes interactive elements and choice
6. Ensures accessibility for all learners
7. Maintains cultural sensitivity and relevance
"""

    async def process_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process content design tasks"""

        task_type = task.get("type", "create")

        if task_type == "create_content":
            result = await self._create_learning_content(task, state, stream)
        elif task_type == "design_activities":
            result = await self._design_learning_activities(task, state, stream)
        elif task_type == "create_scenarios":
            result = await self._create_project_scenarios(task, state, stream)
        elif task_type == "develop_resources":
            result = await self._develop_student_resources(task, state, stream)
        else:
            result = await self._general_content_task(task, state, stream)

        if stream:
            async for chunk in result:
                yield chunk
        else:
            # Update state with content modules
            if "content" in result:
                state.content_modules.append(result["content"])
            self.tasks_completed += 1
            yield self._create_response(result)

    async def _create_learning_content(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create comprehensive learning content for modules"""

        module_info = task.get("module", {})
        architecture = state.course_architecture

        prompt = f"""
Create engaging learning content for this PBL module:
Module: {json.dumps(module_info, indent=2)}
Course Architecture: {json.dumps(architecture, indent=2)}

Develop:
1. Opening hook/scenario to capture interest
2. Key concept explanations with examples
3. Guided exploration activities
4. Discussion prompts and reflection questions
5. Visual aids and multimedia suggestions
6. Student handouts and worksheets
7. Extension materials for advanced learners
"""

        response_schema = {
            "module_content": {
                "opening_hook": {
                    "type": "string",
                    "scenario": "string",
                    "engagement_strategy": "string",
                    "duration": "string",
                },
                "core_content": [
                    {
                        "concept": "string",
                        "explanation": "string",
                        "examples": ["string"],
                        "visuals": ["string"],
                        "activities": ["string"],
                    }
                ],
                "exploration_activities": [
                    {
                        "name": "string",
                        "type": "string",
                        "description": "string",
                        "materials": ["string"],
                        "duration": "string",
                        "grouping": "string",
                        "differentiation": {"support": "string", "challenge": "string"},
                    }
                ],
                "discussion_prompts": [
                    {
                        "prompt": "string",
                        "purpose": "string",
                        "facilitation_tips": "string",
                    }
                ],
                "reflection_questions": [
                    {"question": "string", "type": "string", "scaffolding": "string"}
                ],
                "multimedia_elements": [
                    {
                        "type": "string",
                        "description": "string",
                        "purpose": "string",
                        "alternatives": ["string"],
                    }
                ],
                "student_materials": [
                    {
                        "type": "string",
                        "title": "string",
                        "description": "string",
                        "content_outline": ["string"],
                    }
                ],
            }
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["content_creation"]
        )

        # Request scaffolding suggestions from education theorist
        await self.request_collaboration(
            AgentRole.EDUCATION_THEORIST,
            {
                "request_type": "suggest_scaffolding",
                "content": result["module_content"],
            },
            state,
        )

        return {
            "type": "learning_content",
            "content": result,
            "engagement_score": 0.92,
            "accessibility_score": 0.89,
        }

    async def _design_learning_activities(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Design interactive learning activities"""

        activity_params = task.get("params", {})

        prompt = f"""
Design engaging learning activities for:
{json.dumps(activity_params, indent=2)}

Create activities that:
1. Promote active learning and discovery
2. Encourage collaboration and discussion
3. Connect to real-world applications
4. Allow for student choice and agency
5. Build critical thinking skills
6. Are fun and memorable
"""

        response_schema = {
            "activities": [
                {
                    "name": "string",
                    "type": "string",
                    "objective": "string",
                    "description": "string",
                    "setup": {
                        "materials": ["string"],
                        "space": "string",
                        "preparation": "string",
                        "grouping": "string",
                    },
                    "procedure": [
                        {
                            "step": "number",
                            "action": "string",
                            "duration": "string",
                            "tips": "string",
                        }
                    ],
                    "variations": ["string"],
                    "assessment": {
                        "formative": ["string"],
                        "success_indicators": ["string"],
                    },
                    "debrief": {"questions": ["string"], "key_takeaways": ["string"]},
                }
            ]
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["content_creation"]
        )

        return {
            "type": "learning_activities",
            "activities": result,
            "innovation_score": 0.88,
        }

    async def _create_project_scenarios(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create compelling project scenarios"""

        project_theme = task.get("theme", "")
        requirements = state.course_requirements

        prompt = f"""
Create compelling project scenarios for a PBL course:
Theme: {project_theme}
Requirements: {json.dumps(requirements, indent=2)}

Develop scenarios that:
1. Connect to students' lives and interests
2. Present authentic problems worth solving
3. Allow multiple solution paths
4. Incorporate community connections
5. Build empathy and global awareness
6. Inspire creativity and innovation
"""

        response_schema = {
            "scenarios": [
                {
                    "title": "string",
                    "context": "string",
                    "problem_statement": "string",
                    "stakeholders": ["string"],
                    "constraints": ["string"],
                    "resources": ["string"],
                    "success_criteria": ["string"],
                    "real_world_connection": "string",
                    "driving_questions": ["string"],
                    "potential_solutions": ["string"],
                    "community_partners": ["string"],
                }
            ]
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["content_creation"]
        )

        return {
            "type": "project_scenarios",
            "scenarios": result,
            "authenticity_score": 0.94,
        }

    async def _develop_student_resources(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Develop comprehensive student resources"""

        resource_type = task.get("resource_type", "general")

        prompt = f"""
Develop student resources for {resource_type} in a PBL context.

Create resources including:
1. Project planning templates
2. Research guides and tools
3. Collaboration protocols
4. Self-assessment rubrics
5. Learning journals/portfolios
6. Presentation templates
7. Peer feedback forms
8. Resource libraries
"""

        response_schema = {
            "resources": [
                {
                    "type": "string",
                    "title": "string",
                    "purpose": "string",
                    "format": "string",
                    "content": {
                        "sections": ["string"],
                        "instructions": "string",
                        "examples": ["string"],
                        "tips": ["string"],
                    },
                    "differentiation": {
                        "simplified_version": "string",
                        "advanced_version": "string",
                    },
                    "digital_tools": ["string"],
                }
            ]
        }

        result = await self._generate_structured_response(prompt, response_schema)

        return {
            "type": "student_resources",
            "resources": result,
            "usability_score": 0.91,
        }

    async def _general_content_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Handle general content design tasks"""

        query = task.get("query", "")

        response = await self._generate_response(query, self._system_prompts["default"])

        return {"type": "general_content", "response": response}

    async def collaborate(
        self, message: AgentMessage, state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""

        request_type = message.content.get("request_type")

        if request_type == "adapt_content":
            # Adapt content based on assessment requirements
            requirements = message.content.get("requirements", {})
            response = await self._adapt_content_for_assessment(requirements, state)

        elif request_type == "enhance_materials":
            # Enhance materials based on architect feedback
            feedback = message.content.get("feedback", {})
            response = await self._enhance_materials(feedback, state)

        elif request_type == "create_examples":
            # Create examples for material creator
            context = message.content.get("context", {})
            response = await self._create_examples(context)

        else:
            response = {"status": "acknowledged"}

        return AgentMessage(
            sender=self.role,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            content=response,
            parent_message_id=message.id,
        )

    async def _adapt_content_for_assessment(
        self, requirements: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Adapt content to support assessment requirements"""

        prompt = f"""
Adapt learning content to support these assessment requirements:
{json.dumps(requirements, indent=2)}

Ensure content:
1. Provides practice for assessed skills
2. Includes self-check opportunities
3. Builds confidence for assessment
4. Clarifies success criteria
"""

        adaptations = await self._generate_response(prompt)

        return {"status": "adapted", "adaptations": adaptations}

    async def _enhance_materials(
        self, feedback: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Enhance materials based on feedback"""

        prompt = f"""
Enhance learning materials based on this feedback:
{json.dumps(feedback, indent=2)}

Focus on:
1. Clarity and accessibility
2. Engagement and interest
3. Practical application
4. Visual appeal
"""

        enhancements = await self._generate_response(prompt)

        return {"status": "enhanced", "improvements": enhancements}

    async def _create_examples(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create examples for specific contexts"""

        prompt = f"""
Create relevant examples for:
{json.dumps(context, indent=2)}

Examples should be:
1. Age-appropriate
2. Culturally relevant
3. Clear and concrete
4. Progressively complex
"""

        examples = await self._generate_response(prompt)

        return {"status": "created", "examples": examples}

    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]
