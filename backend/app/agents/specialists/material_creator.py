"""
AI时代素材创作者智能体
专精AI时代数字化资源生成，负责多媒体内容制作、交互式工具开发、AI工具使用指南
将所有设计内容转化为具体可用的教学资源和学习材料
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class MaterialCreatorAgent(BaseAgent):
    """
    AI时代素材创作者
    专精AI时代数字化资源生成，将所有设计内容转化为具体可用的教学资源和学习材料
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.MATERIAL_CREATOR,
            llm_manager=llm_manager,
            name="AI时代素材创作者",
            description="专精AI时代数字化资源生成，拥有10年数字化教学资源开发经验",
            capabilities=[
                ModelCapability.CREATIVITY,
                ModelCapability.LANGUAGE,
                ModelCapability.CODING,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

    def _initialize_system_prompts(self) -> None:
        """初始化AI时代素材创作者的系统提示"""
        self._system_prompts[
            "default"
        ] = """
你是一位专精AI时代教学资源创作的多媒体专家，拥有10年数字化教学资源开发经验。你擅长将教育设计转化为具体可用的学习材料，熟练运用各种数字化工具和AI技术。

## 🎯 核心专长

### **多媒体内容制作**
- 适应数字原住民学习习惯的多媒体设计
- 交互式数字教材和学习模块
- 教育视频、音频、动画内容创作
- AR/VR沉浸式学习体验开发

### **交互式工具开发**
- 增强学习体验的互动工具设计
- 游戏化学习元素的技术实现
- 自适应学习系统的资源配置
- 跨平台兼容的学习工具开发

### **AI工具使用指南**
- 师生AI工具操作的详细指南
- AI工具教育应用场景设计
- AI协作工作流程的可视化说明
- AI伦理使用规范的具体指导

## 🛠️ 创作工具箱

### **内容制作技术栈**

#### **📹 视频音频制作**
- **微课视频**: 3-8分钟概念解释和演示
- **访谈录制**: 专家对话和学生分享
- **动画制作**: 抽象概念的可视化呈现
- **播客音频**: 深度学习和思考内容

#### **🎨 视觉设计工具**
- **信息图表**: 复杂信息的简洁呈现
- **思维导图**: 知识结构的可视化
- **流程图表**: 步骤过程的清晰展示
- **交互界面**: 学习工具的用户界面

#### **💻 数字化平台**
- **在线课程**: 结构化的学习路径
- **互动电子书**: 富媒体数字教材
- **学习游戏**: 教育目标驱动的游戏设计
- **虚拟实验**: 安全可控的探索环境

### **AI辅助创作流程**

#### **🤖 AI创作伙伴**
- **内容生成**: 使用AI辅助创作初稿和素材
- **图像创作**: AI生成的教学图片和插图
- **视频制作**: AI辅助的视频编辑和特效
- **音频处理**: AI语音合成和音效制作

#### **🔄 人机协作模式**
创作流程
├── 需求分析 (人类主导)
├── 素材生成 (AI辅助)
├── 内容整合 (人机协作)
├── 质量优化 (人类把关)
└── 效果评估 (数据驱动)

## 📦 资源包开发

### **完整课程资源包结构**

#### **📚 学生学习包**
学生资源/
├── 📖 学习指南/
│   ├── 课程概览.pdf
│   ├── 学习目标.md
│   └── 成功标准.pdf
├── 📹 学习视频/
│   ├── 概念介绍视频/
│   ├── 操作演示视频/
│   └── 专家访谈视频/
├── 🛠️ 工具指南/
│   ├── AI工具使用手册/
│   ├── 在线平台操作指南/
│   └── 协作工具说明/
├── 📝 学习活动/
│   ├── 个人任务清单/
│   ├── 小组活动指南/
│   └── 项目模板/
└── 📊 自评工具/
    ├── 反思问卷/
    ├── 进度追踪表/
    └── 作品集模板/

#### **👨‍🏫 教师教学包**
教师资源/
├── 📋 教学指南/
│   ├── 课程实施手册.pdf
│   ├── 时间安排建议.md
│   └── 常见问题FAQ.pdf
├── 🎯 教学材料/
│   ├── PPT演示文稿/
│   ├── 教学视频资源/
│   └── 互动活动设计/
├── 📊 评估工具/
│   ├── 评价量规/
│   ├── 观察记录表/
│   └── 反馈模板/
├── 🔧 技术支持/
│   ├── 平台配置指南/
│   ├── 故障排除手册/
│   └── 技术资源清单/
└── 📈 效果追踪/
    ├── 数据收集工具/
    ├── 分析报告模板/
    └── 改进建议框架/

## 🌟 创作理念

> "优秀的教学资源应该像一位贴心的导师，既能在学习者需要时提供帮助，又能在适当的时候退居幕后，让学习者成为学习的主角。技术是手段，学习是目的，育人是根本。"

你的任务是最终产出，生成数字化学习资源包、AI工具清单和格式化输出。

Your role is to transform educational concepts and designs into production-ready
materials that teachers can immediately use in their classrooms. Create professional,
engaging, and accessible resources that support effective learning.
"""

        self._system_prompts[
            "material_production"
        ] = """
Create educational materials that are:
1. Immediately usable without modification
2. Professionally formatted and visually appealing
3. Clear in instructions and expectations
4. Accessible to all learners
5. Available in multiple formats
6. Easy to adapt and customize
7. Aligned with learning objectives
"""

    async def process_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process material creation tasks"""

        task_type = task.get("type", "create")

        if task_type == "create_worksheets":
            result = await self._create_worksheets(task, state, stream)
        elif task_type == "create_presentations":
            result = await self._create_presentations(task, state, stream)
        elif task_type == "create_templates":
            result = await self._create_project_templates(task, state, stream)
        elif task_type == "create_guides":
            result = await self._create_teacher_guides(task, state, stream)
        elif task_type == "create_digital":
            result = await self._create_digital_resources(task, state, stream)
        else:
            result = await self._general_material_task(task, state, stream)

        if stream:
            async for chunk in result:
                yield chunk
        else:
            # Update state with learning materials
            if "materials" in result:
                state.learning_materials.extend(result["materials"])
            self.tasks_completed += 1
            yield self._create_response(result)

    async def _create_worksheets(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create ready-to-use worksheets"""

        worksheet_specs = task.get("specifications", {})
        content_modules = state.content_modules

        prompt = f"""
Create production-ready worksheets based on:
Specifications: {json.dumps(worksheet_specs, indent=2)}
Content Modules: {json.dumps(content_modules, indent=2)}

Produce worksheets including:
1. Clear headers with learning objectives
2. Engaging warm-up activities
3. Main content sections with examples
4. Practice problems with varying difficulty
5. Reflection questions
6. Extension challenges
7. Visual elements and graphics descriptions
8. Answer keys for teachers
"""

        response_schema = {
            "worksheets": [
                {
                    "title": "string",
                    "grade_level": "string",
                    "subject": "string",
                    "duration": "string",
                    "learning_objectives": ["string"],
                    "materials_needed": ["string"],
                    "sections": [
                        {
                            "type": "string",
                            "title": "string",
                            "content": "string",
                            "instructions": "string",
                            "examples": ["string"],
                            "problems": [
                                {
                                    "question": "string",
                                    "difficulty": "string",
                                    "space_needed": "string",
                                    "answer": "string",
                                }
                            ],
                            "visuals": ["string"],
                        }
                    ],
                    "differentiation": {
                        "support": ["string"],
                        "challenge": ["string"],
                        "accommodations": ["string"],
                    },
                    "answer_key": {
                        "solutions": ["string"],
                        "rubric": "string",
                        "common_errors": ["string"],
                    },
                    "teacher_notes": ["string"],
                    "formatting": {
                        "layout": "string",
                        "font_recommendations": "string",
                        "spacing": "string",
                        "visual_elements": ["string"],
                    },
                }
            ]
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["material_production"]
        )

        return {
            "type": "worksheets",
            "materials": result["worksheets"],
            "production_quality": 0.93,
        }

    async def _create_presentations(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create presentation materials"""

        presentation_topic = task.get("topic", "")
        audience = task.get("audience", "students")

        prompt = f"""
Create a complete presentation for:
Topic: {presentation_topic}
Audience: {audience}

Develop presentation with:
1. Title slide with objectives
2. Agenda/roadmap slide
3. Content slides with key points
4. Interactive activity slides
5. Discussion prompt slides
6. Summary/recap slide
7. Resources/next steps slide
8. Visual descriptions for each slide
"""

        response_schema = {
            "presentation": {
                "title": "string",
                "total_slides": "number",
                "duration": "string",
                "slides": [
                    {
                        "number": "number",
                        "type": "string",
                        "title": "string",
                        "content": {
                            "main_points": ["string"],
                            "speaker_notes": "string",
                            "visuals": ["string"],
                            "animations": ["string"],
                        },
                        "interaction": {
                            "type": "string",
                            "instructions": "string",
                            "timing": "string",
                        },
                        "design": {
                            "layout": "string",
                            "color_scheme": "string",
                            "fonts": "string",
                            "graphics": ["string"],
                        },
                    }
                ],
                "supplementary_materials": {
                    "handouts": ["string"],
                    "activities": ["string"],
                    "references": ["string"],
                },
                "delivery_tips": ["string"],
                "technical_requirements": ["string"],
            }
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["material_production"]
        )

        return {
            "type": "presentation",
            "materials": [result["presentation"]],
            "engagement_score": 0.91,
        }

    async def _create_project_templates(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create project planning and tracking templates"""

        project_type = task.get("project_type", "general")

        prompt = f"""
Create comprehensive project templates for {project_type} PBL.

Develop templates including:
1. Project planning template
2. Research organizer
3. Timeline and milestone tracker
4. Team roles and responsibilities
5. Daily/weekly progress logs
6. Resource tracking sheet
7. Presentation planning template
8. Reflection journal template
"""

        response_schema = {
            "templates": [
                {
                    "name": "string",
                    "purpose": "string",
                    "format": "string",
                    "sections": [
                        {
                            "title": "string",
                            "description": "string",
                            "fields": [
                                {
                                    "label": "string",
                                    "type": "string",
                                    "instructions": "string",
                                    "example": "string",
                                }
                            ],
                            "tips": ["string"],
                        }
                    ],
                    "instructions": {"student": ["string"], "teacher": ["string"]},
                    "customization": {
                        "editable_elements": ["string"],
                        "adaptation_suggestions": ["string"],
                    },
                    "digital_version": {
                        "platform": "string",
                        "features": ["string"],
                        "sharing": "string",
                    },
                }
            ]
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["material_production"]
        )

        return {
            "type": "templates",
            "materials": result["templates"],
            "usability_score": 0.94,
        }

    async def _create_teacher_guides(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create comprehensive teacher guides"""

        guide_focus = task.get("focus", "implementation")

        prompt = f"""
Create a comprehensive teacher guide for {guide_focus} in PBL.

Include:
1. Overview and objectives
2. Preparation checklist
3. Day-by-day implementation plan
4. Facilitation strategies
5. Common challenges and solutions
6. Assessment guidelines
7. Differentiation suggestions
8. Parent communication templates
"""

        response_schema = {
            "teacher_guide": {
                "title": "string",
                "overview": {
                    "purpose": "string",
                    "objectives": ["string"],
                    "duration": "string",
                    "key_concepts": ["string"],
                },
                "preparation": {
                    "checklist": ["string"],
                    "materials": ["string"],
                    "setup": "string",
                    "pre_assessment": "string",
                },
                "implementation": {
                    "daily_plans": [
                        {
                            "day": "number",
                            "objectives": ["string"],
                            "activities": [
                                {
                                    "time": "string",
                                    "activity": "string",
                                    "facilitation": "string",
                                    "materials": ["string"],
                                }
                            ],
                            "assessment": "string",
                            "homework": "string",
                        }
                    ],
                    "pacing_guide": "string",
                    "flexibility_notes": ["string"],
                },
                "facilitation": {
                    "strategies": ["string"],
                    "questioning_techniques": ["string"],
                    "group_management": ["string"],
                    "student_support": ["string"],
                },
                "troubleshooting": [
                    {
                        "challenge": "string",
                        "solutions": ["string"],
                        "prevention": "string",
                    }
                ],
                "assessment": {
                    "formative": ["string"],
                    "summative": ["string"],
                    "rubrics": ["string"],
                    "recording": "string",
                },
                "differentiation": {
                    "advanced": ["string"],
                    "struggling": ["string"],
                    "ell": ["string"],
                    "special_needs": ["string"],
                },
                "communication": {
                    "parent_letter": "string",
                    "updates": ["string"],
                    "showcase_planning": "string",
                },
                "resources": {
                    "additional_reading": ["string"],
                    "websites": ["string"],
                    "professional_development": ["string"],
                },
            }
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["material_production"]
        )

        return {
            "type": "teacher_guide",
            "materials": [result["teacher_guide"]],
            "comprehensiveness": 0.96,
        }

    async def _create_digital_resources(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Create digital learning resources"""

        resource_type = task.get("resource_type", "interactive")

        prompt = f"""
Create digital {resource_type} resources for PBL.

Develop:
1. Interactive learning modules
2. Digital collaboration tools
3. Online assessment forms
4. Virtual presentation formats
5. Digital portfolio structures
6. Resource libraries
7. Tutorial videos scripts
8. Online discussion prompts
"""

        response_schema = {
            "digital_resources": [
                {
                    "type": "string",
                    "name": "string",
                    "platform": "string",
                    "purpose": "string",
                    "features": {
                        "interactive_elements": ["string"],
                        "collaboration": ["string"],
                        "assessment": ["string"],
                        "tracking": ["string"],
                    },
                    "content": {
                        "modules": ["string"],
                        "activities": ["string"],
                        "resources": ["string"],
                    },
                    "implementation": {
                        "setup": "string",
                        "student_onboarding": "string",
                        "management": "string",
                        "troubleshooting": ["string"],
                    },
                    "accessibility": {
                        "features": ["string"],
                        "alternatives": ["string"],
                        "support": "string",
                    },
                    "data_privacy": {
                        "considerations": ["string"],
                        "permissions": "string",
                        "storage": "string",
                    },
                }
            ]
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["material_production"]
        )

        return {
            "type": "digital_resources",
            "materials": result["digital_resources"],
            "innovation_score": 0.89,
        }

    async def _general_material_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Handle general material creation tasks"""

        query = task.get("query", "")

        response = await self._generate_response(query, self._system_prompts["default"])

        return {"type": "general_material", "response": response}

    async def collaborate(
        self, message: AgentMessage, state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""

        request_type = message.content.get("request_type")

        if request_type == "format_content":
            # Format content from content designer
            content = message.content.get("content", {})
            response = await self._format_content(content)

        elif request_type == "create_visuals":
            # Create visual aids
            specs = message.content.get("specifications", {})
            response = await self._create_visual_aids(specs)

        elif request_type == "adapt_materials":
            # Adapt materials for different formats
            materials = message.content.get("materials", [])
            response = await self._adapt_materials(materials)

        else:
            response = {"status": "acknowledged"}

        return AgentMessage(
            sender=self.role,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            content=response,
            parent_message_id=message.id,
        )

    async def _format_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format content into production-ready materials"""

        prompt = f"""
Format this content into production-ready materials:
{json.dumps(content, indent=2)}

Create:
1. Clean, professional layout
2. Clear typography and spacing
3. Visual hierarchy
4. Consistent styling
"""

        formatted = await self._generate_response(prompt)

        return {"status": "formatted", "materials": formatted}

    async def _create_visual_aids(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Create visual aids based on specifications"""

        prompt = f"""
Create visual aids based on:
{json.dumps(specs, indent=2)}

Design:
1. Clear, informative graphics
2. Age-appropriate visuals
3. Accessibility considerations
4. Multiple format options
"""

        visuals = await self._generate_response(prompt)

        return {"status": "created", "visuals": visuals}

    async def _adapt_materials(self, materials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adapt materials for different formats"""

        prompt = f"""
Adapt these materials for multiple formats:
{json.dumps(materials, indent=2)}

Create versions for:
1. Print (PDF)
2. Digital (interactive)
3. Mobile (responsive)
4. Accessibility (screen readers)
"""

        adaptations = await self._generate_response(prompt)

        return {"status": "adapted", "formats": adaptations}

    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]
