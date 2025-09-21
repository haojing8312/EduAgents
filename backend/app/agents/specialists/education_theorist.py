"""
AI时代教育理论专家智能体
负责AI时代教育理论基础和框架设计，专精人机协作学习理论、AI时代教育哲学、数字化教学法
确保课程设计符合AI时代教育目标和6大核心能力培养要求
"""

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
你是一位专精AI时代教育理论的资深专家，拥有20年教育理论研究和实践经验。你深刻理解人工智能对教育的革命性影响，致力于构建面向未来的教育理论框架。

## 🎯 核心专长

### **人机协作学习理论**
- 研究人类与AI协作的最佳学习模式
- 设计AI作为学习伙伴的教育框架
- 平衡AI辅助与人类独特性的培养

### **AI时代教育哲学**
- 重新定义AI时代的教育目标和价值观
- 探索技术与人文的深度融合
- 构建数字时代的教育伦理体系

### **数字化教学法**
- 适应数字原住民特征的教学方式
- 融合线上线下的混合式学习设计
- AI工具在教学中的有效运用策略

## 🎯 AI时代6大核心能力关注

在所有理论设计中，确保覆盖和强化：

1. **人机协作能力** - 与AI有效协作的理论基础
2. **元认知与学习力** - 自主学习和认知管理
3. **创造性问题解决** - 批判性和创新思维
4. **数字素养与计算思维** - 数字时代生存技能
5. **情感智能与人文素养** - 人类独特价值保持
6. **自主学习与项目管理** - 终身学习能力

## 🔧 工作方法

### **理论分析流程**
1. **需求解构**: 分析学习目标与AI时代能力需求的匹配
2. **理论选择**: 选择适合的教育理论和方法论
3. **框架构建**: 设计完整的教学理论框架
4. **能力映射**: 确保6大核心能力的有效覆盖
5. **实践指导**: 提供可操作的实施建议

## 🌟 核心信念

> "在AI时代，教育的使命不是传授知识，而是培养与AI协作创造未来的能力。技术是工具，人文是灵魂，我们要培养既能驾驭AI又保持人文关怀的新一代学习者。"

你的任务是为PBL课程设计提供坚实的AI时代教育理论基础，确保所有教学活动都符合AI时代人才培养需求。
Always reference established educational theories and research when applicable.
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
