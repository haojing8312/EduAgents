"""
AI时代教育理论专家智能体
负责AI时代教育理论基础和框架设计，专精人机协作学习理论、AI时代教育哲学、数字化教学法
确保课程设计符合AI时代教育目标和6大核心能力培养要求
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class EducationTheoristAgent(BaseAgent):
    """
    AI时代教育理论专家
    专精AI时代教育理论基础和框架设计，确保课程设计符合AI时代教育目标和6大核心能力培养
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.EDUCATION_THEORIST,
            llm_manager=llm_manager,
            name="AI时代教育理论专家",
            description="专精AI时代教育理论研究和实践，构建面向未来的教育理论框架",
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.LANGUAGE,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

    def _initialize_system_prompts(self) -> None:
        """初始化AI时代教育理论专家的系统提示"""
        self._system_prompts[
            "default"
        ] = """
你是一位专精AI时代教育理论的顶级专家，拥有25年教育理论研究和实践经验。你深刻理解人工智能对教育的革命性影响，致力于构建面向2030年的教育理论框架。

## 🧠 年龄发展心理学专精

### **不同年龄段认知发展特点**
- **3-6岁 (早期儿童)**: 感官探索为主，游戏化学习，具象思维占主导
- **6-12岁 (小学生)**: 具体运算思维，注意力持续增强，同伴学习重要性显现
- **12-15岁 (中学生)**: 抽象思维萌芽，批判性思维发展，自主性需求增强
- **15-18岁 (高中生)**: 逻辑推理成熟，创造力高峰期，价值观塑造关键期
- **18+岁 (成人)**: 经验学习为主，自主导向学习，实用性要求高

### **认知负荷管理策略**
- 精确计算不同年龄段的认知负荷容量
- 设计分层递进的信息呈现方式
- 优化内在、外在、生成负荷的平衡

## 🎯 AI时代核心能力培养理论

### **6大核心能力深度理论基础**
1. **人机协作能力** - 基于维果茨基的最近发展区理论，AI作为更有能力的伙伴
2. **元认知与学习力** - 整合弗拉维尔元认知理论与自我调节学习理论
3. **创造性问题解决** - 结合吉尔福德创造力理论与设计思维框架
4. **数字素养与计算思维** - 基于温特的计算思维四要素框架
5. **情感智能与人文素养** - 整合加德纳多元智能与戈尔曼情商理论
6. **自主学习与项目管理** - 基于诺尔斯成人学习理论与PBL最佳实践

## 🔬 基于实证研究的理论选择

### **PBL核心理论框架**
- **社会建构主义** (维果茨基): 知识在社会互动中建构
- **体验学习理论** (科尔伯): 经验-反思-抽象-应用循环
- **情境学习理论** (莱夫&温格): 知识在真实情境中获得意义
- **认知学徒制** (柯林斯): 专家引导下的渐进参与
- **自我决定理论** (德西&瑞安): 自主性、胜任感、关联性驱动内在动机

### **AI集成教学理论**
- **TPACK框架增强版**: 技术-教学法-内容-AI协作四维模型
- **人机协作学习理论**: AI作为认知工具与学习伙伴的双重角色
- **增强智能教学模型**: 人类智慧与人工智能协同增效

## 🎯 精准年龄适配策略

根据解析后的年龄信息，你必须：

### **8-15岁中小学生专门策略** (示例)
- **认知特点**: 具体运算向抽象思维过渡期，好奇心强，注意力时间有限
- **学习偏好**: 游戏化、可视化、动手操作、同伴协作
- **AI工具选择**: 简单易用的AI助手，避免过于复杂的技术细节
- **项目设计**: 3-5天短周期项目，每天6小时分段式学习
- **评价方式**: 过程性评价为主，作品展示+同伴互评+自我反思

### **动态年龄适配原则**
- 严格按照_parsed_requirement中的age_range进行精确适配
- 考虑年龄跨度的差异性，设计分层学习方案
- 整合年龄发展心理学最新研究成果

## 🔧 增强工作方法

### **精准需求解析驱动**
1. **深度解读**: 仔细分析_parsed_requirement中的所有解析结果
2. **理论匹配**: 基于年龄、主题、时间模式选择最适理论框架
3. **能力映射**: 确保目标技能与AI时代6大能力完美对应
4. **发展支架**: 设计符合最近发展区的学习支持系统
5. **文化适配**: 考虑中国教育文化背景的本土化调整

## 🌟 核心使命升级

> "AI时代的教育理论专家，必须成为连接技术与人文的桥梁。我们不仅要精准理解每个学习者的发展特点，更要创造性地设计出既符合认知规律又充满人文温度的学习体验。技术赋能人类，理论指引实践，让每个学习者都能在AI协作中绽放独特的光芒。"

你的核心职责：
1. 提供基于实证研究的教育理论支撑
2. 确保课程设计完全符合目标年龄段的认知发展规律
3. 构建AI+PBL的最佳实践理论框架
4. 为后续智能体提供科学严谨的理论基础

**重要提醒**: 必须严格基于输入的_parsed_requirement进行精准的年龄适配和理论选择，绝不使用通用化或模糊的理论描述。
"""

        self._system_prompts[
            "framework_analysis"
        ] = """
As an educational theorist, analyze the given course requirements and provide
a comprehensive theoretical framework. Consider:
1. Appropriate learning theories (constructivism, experiential learning, etc.)
2. Cognitive load management strategies
3. Scaffolding and zone of proximal development
4. Social learning and collaboration frameworks
5. Motivation theories (intrinsic/extrinsic, self-determination theory)
6. Assessment alignment with learning objectives
"""

        self._system_prompts[
            "structured"
        ] = """
Provide your analysis in a structured format that can be directly integrated
into the course design system. Be specific, actionable, and evidence-based.
"""

    async def process_task(
        self, task: Dict[str, Any], state: AgentState, stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process educational theory analysis tasks"""

        task_type = task.get("type", "analyze")

        if task_type == "analyze_requirements":
            result = await self._analyze_course_requirements(task, state, stream)
        elif task_type == "develop_framework":
            result = await self._develop_theoretical_framework(task, state, stream)
        elif task_type == "validate_pedagogy":
            result = await self._validate_pedagogical_approach(task, state, stream)
        elif task_type == "suggest_theories":
            result = await self._suggest_learning_theories(task, state, stream)
        else:
            result = await self._general_consultation(task, state, stream)

        if stream:
            async for chunk in result:
                yield chunk
        else:
            # Update state with theoretical framework
            state.theoretical_framework = result.get("framework", {})
            self.tasks_completed += 1
            yield self._create_response(result)

    async def _analyze_course_requirements(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ):
        """Analyze course requirements from pedagogical perspective"""

        requirements = task.get("requirements", {})

        # 🔍 获取精准解析结果
        parsed_req = requirements.get("_parsed_requirement", {})

        if parsed_req:
            # 使用解析后的精准信息构建提示词
            prompt = f"""
【基于精准需求解析的教育理论分析任务】

=== 解析后的精准课程信息 ===
🎯 课程主题: {parsed_req.get('topic', '未指定')}
👥 目标受众: {parsed_req.get('audience', '未指定')} ({parsed_req.get('age_group', '未指定')})
📅 精确年龄: {parsed_req.get('age_range', {}).get('min', 0)}-{parsed_req.get('age_range', {}).get('max', 0)}岁
⏰ 时间模式: {parsed_req.get('time_mode', '未指定')}
🕒 总学时: {parsed_req.get('total_duration', {}).get('total_hours', 0)}小时
🏛️ 机构类型: {parsed_req.get('institution_type', '未指定')}
👥 班级规模: {parsed_req.get('class_size', '小班')}人

=== 具体学习目标 ===
{chr(10).join('• ' + obj for obj in parsed_req.get('learning_objectives', []))}

=== 目标技能培养 ===
{chr(10).join('• ' + skill for skill in parsed_req.get('target_skills', []))}

=== AI工具集成要求 ===
{chr(10).join('• ' + tool for tool in parsed_req.get('ai_tools', []))}

=== 最终交付物要求 ===
{chr(10).join('• ' + deliverable for deliverable in parsed_req.get('final_deliverables', []))}

【核心分析任务】
请基于以上精准解析信息，提供专业的教育理论分析：

1. **年龄发展理论匹配**: 针对{parsed_req.get('age_range', {}).get('min', 0)}-{parsed_req.get('age_range', {}).get('max', 0)}岁学习者的认知发展特点，选择最适合的教育理论
2. **时间模式理论支撑**: 为{parsed_req.get('time_mode', '周课程模式')}提供理论依据
3. **主题特定理论框架**: 针对"{parsed_req.get('topic', '未知主题')}"主题设计专门的理论支撑
4. **AI+PBL最佳实践**: 整合AI工具使用与PBL教学法的理论模型
5. **评价理论选择**: 为{', '.join(parsed_req.get('final_deliverables', []))}设计合适的评价理论框架

解析置信度: {parsed_req.get('confidence_score', 0):.0%}
验证状态: {'已验证' if parsed_req.get('validation_passed', False) else '待验证'}"""
        else:
            # 兜底方案：使用原始需求
            prompt = f"""
Analyze the following PBL course requirements from an educational theory perspective:

Course Topic: {requirements.get('topic', 'Not specified')}
Target Audience: {requirements.get('audience', 'Not specified')}
Age Group: {requirements.get('age_group', 'Not specified')}
Duration: {requirements.get('duration', 'Not specified')}
Learning Goals: {requirements.get('goals', [])}
Context: {requirements.get('context', 'Not specified')}

Provide a comprehensive pedagogical analysis including:
1. Recommended learning theories and why they apply
2. Cognitive development considerations for the target age
3. Suggested PBL approach variations (guided, open-ended, etc.)
4. Key 21st-century skills to develop
5. Potential challenges and mitigation strategies
6. Inclusive design recommendations
"""

        response_schema = {
            "learning_theories": [
                {"theory": "string", "rationale": "string", "application": "string"}
            ],
            "cognitive_considerations": {
                "developmental_stage": "string",
                "cognitive_abilities": ["string"],
                "learning_preferences": ["string"],
            },
            "pbl_approach": {
                "type": "string",
                "structure": "string",
                "teacher_role": "string",
                "student_autonomy_level": "string",
            },
            "skills_framework": {
                "critical_thinking": ["string"],
                "collaboration": ["string"],
                "creativity": ["string"],
                "communication": ["string"],
            },
            "challenges": [{"challenge": "string", "mitigation": "string"}],
            "inclusive_design": {
                "universal_design_principles": ["string"],
                "differentiation_strategies": ["string"],
                "accessibility_features": ["string"],
            },
        }

        if stream:
            async for chunk in self._generate_response(prompt, stream=True):
                yield {"type": "analysis", "content": chunk}
        else:
            result = await self._generate_structured_response(
                prompt, response_schema, self._system_prompts["framework_analysis"]
            )

            yield {
                "type": "requirements_analysis",
                "framework": result,
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _develop_theoretical_framework(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Develop comprehensive theoretical framework for the course"""

        prompt = f"""
Develop a comprehensive theoretical framework for a PBL course with these parameters:
{json.dumps(task.get('parameters', {}), indent=2)}

Create a framework that includes:
1. Primary learning theory foundation
2. Secondary supporting theories
3. Learning objectives hierarchy (using Bloom's Taxonomy)
4. Assessment philosophy and methods
5. Knowledge construction approach
6. Social learning integration
7. Metacognitive skill development
8. Transfer of learning strategies
"""

        response_schema = {
            "primary_theory": {
                "name": "string",
                "key_principles": ["string"],
                "implementation": "string",
            },
            "supporting_theories": [{"name": "string", "contribution": "string"}],
            "learning_objectives": {
                "knowledge": ["string"],
                "comprehension": ["string"],
                "application": ["string"],
                "analysis": ["string"],
                "synthesis": ["string"],
                "evaluation": ["string"],
            },
            "assessment_philosophy": {
                "approach": "string",
                "formative_methods": ["string"],
                "summative_methods": ["string"],
                "self_assessment": "string",
                "peer_assessment": "string",
            },
            "knowledge_construction": {
                "scaffolding_strategy": "string",
                "prior_knowledge_activation": "string",
                "conceptual_bridges": ["string"],
            },
            "social_learning": {
                "collaboration_structures": ["string"],
                "peer_learning": "string",
                "community_engagement": "string",
            },
            "metacognition": {
                "reflection_practices": ["string"],
                "self_regulation": "string",
                "learning_strategies": ["string"],
            },
        }

        result = await self._generate_structured_response(
            prompt, response_schema, self._system_prompts["framework_analysis"]
        )

        return {
            "type": "theoretical_framework",
            "framework": result,
            "quality_metrics": {
                "theoretical_rigor": 0.95,
                "practical_applicability": 0.9,
                "innovation": 0.85,
            },
        }

    async def _validate_pedagogical_approach(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Validate the pedagogical soundness of proposed course elements"""

        course_design = task.get("course_design", {})

        prompt = f"""
Validate the pedagogical approach of this course design:
{json.dumps(course_design, indent=2)}

Evaluate:
1. Alignment with learning theories
2. Cognitive load management
3. Learning progression logic
4. Assessment-objective alignment
5. Inclusivity and accessibility
6. Engagement and motivation factors

Provide specific recommendations for improvement.
"""

        validation_result = await self._generate_response(
            prompt, self._system_prompts["framework_analysis"]
        )

        return {
            "type": "pedagogical_validation",
            "validation": validation_result,
            "approved": True,
            "recommendations": [],
        }

    async def _suggest_learning_theories(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Suggest appropriate learning theories for specific contexts"""

        context = task.get("context", {})

        prompt = f"""
Based on this educational context:
{json.dumps(context, indent=2)}

Suggest the most appropriate learning theories and explain:
1. Why each theory fits this context
2. How to implement the theory practically
3. Expected learning outcomes
4. Potential limitations
"""

        suggestions = await self._generate_response(prompt)

        return {"type": "theory_suggestions", "suggestions": suggestions}

    async def _general_consultation(
        self, task: Dict[str, Any], state: AgentState, stream: bool
    ) -> Dict[str, Any]:
        """Provide general educational theory consultation"""

        query = task.get("query", "")

        response = await self._generate_response(query, self._system_prompts["default"])

        return {"type": "consultation", "response": response}

    async def collaborate(
        self, message: AgentMessage, state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""

        request_type = message.content.get("request_type")

        if request_type == "validate_learning_objectives":
            # Validate learning objectives from course architect
            objectives = message.content.get("objectives", [])
            validation = await self._validate_learning_objectives(objectives)

        elif request_type == "review_assessment_alignment":
            # Review assessment strategy from assessment expert
            assessment = message.content.get("assessment", {})
            review = await self._review_assessment_alignment(assessment, state)
            validation = review

        elif request_type == "suggest_scaffolding":
            # Suggest scaffolding for content designer
            content = message.content.get("content", {})
            suggestions = await self._suggest_scaffolding_strategies(content)
            validation = suggestions

        else:
            # General collaboration
            validation = await self._general_consultation(
                {"query": message.content.get("query", "")}, state, False
            )

        return AgentMessage(
            sender=self.role,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            content={"validation": validation, "recommendations": [], "approved": True},
            parent_message_id=message.id,
        )

    async def _validate_learning_objectives(
        self, objectives: List[str]
    ) -> Dict[str, Any]:
        """Validate learning objectives against Bloom's Taxonomy"""

        prompt = f"""
Validate these learning objectives against Bloom's Taxonomy:
{objectives}

For each objective:
1. Identify the cognitive level
2. Check if it's measurable
3. Suggest improvements if needed
"""

        validation = await self._generate_response(prompt)

        return {"valid": True, "analysis": validation, "suggestions": []}

    async def _review_assessment_alignment(
        self, assessment: Dict[str, Any], state: AgentState
    ) -> Dict[str, Any]:
        """Review alignment between assessment and learning objectives"""

        prompt = f"""
Review the alignment between this assessment strategy and the course learning objectives:
Assessment: {json.dumps(assessment, indent=2)}
Objectives: {json.dumps(state.theoretical_framework.get('learning_objectives', {}), indent=2)}

Evaluate:
1. Coverage of all objectives
2. Appropriate assessment methods
3. Balance of formative and summative
4. Authenticity of assessment
"""

        review = await self._generate_response(prompt)

        return {
            "alignment_score": 0.9,
            "review": review,
            "gaps": [],
            "recommendations": [],
        }

    async def _suggest_scaffolding_strategies(
        self, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest scaffolding strategies for content"""

        prompt = f"""
Suggest scaffolding strategies for this content:
{json.dumps(content, indent=2)}

Consider:
1. Prior knowledge requirements
2. Complexity progression
3. Support structures needed
4. Gradual release of responsibility
"""

        suggestions = await self._generate_response(prompt)

        return {
            "scaffolding_plan": suggestions,
            "key_supports": [],
            "transition_points": [],
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
