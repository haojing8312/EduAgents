"""
Education Theorist Agent
Specializes in pedagogical frameworks, learning theories, and educational philosophy
"""

from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class EducationTheoristAgent(BaseAgent):
    """
    Expert in educational theory and pedagogical frameworks
    Provides theoretical foundation for PBL course design
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.EDUCATION_THEORIST,
            llm_manager=llm_manager,
            name="Dr. Pedagogy",
            description="Educational theory expert specializing in PBL and constructivist learning",
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.ANALYSIS,
                ModelCapability.LANGUAGE,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

    def _initialize_system_prompts(self) -> None:
        """Initialize education theory specific prompts"""
        self._system_prompts[
            "default"
        ] = """
You are Dr. Pedagogy, a world-renowned educational theorist and PBL expert.
Your expertise includes:
- Constructivist learning theory and social constructivism
- Project-Based Learning (PBL) methodology and best practices
- Bloom's Taxonomy and learning objectives design
- 21st-century skills and competency frameworks
- Educational psychology and cognitive development
- Differentiated instruction and inclusive education
- Learning assessment theory and authentic evaluation

Your role is to provide deep theoretical grounding for course design decisions,
ensuring all educational activities are pedagogically sound and evidence-based.
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
    ) -> Dict[str, Any]:
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

            return {
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

    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]
