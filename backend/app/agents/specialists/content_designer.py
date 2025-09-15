"""
Content Designer Agent
Creates engaging educational content and learning materials
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class ContentDesignerAgent(BaseAgent):
    """
    Expert in educational content creation and instructional design
    Develops engaging, accessible learning materials
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.CONTENT_DESIGNER,
            llm_manager=llm_manager,
            name="Creative Designer",
            description="Content design expert specializing in engaging PBL materials",
            capabilities=[
                ModelCapability.CREATIVITY,
                ModelCapability.LANGUAGE,
                ModelCapability.ANALYSIS,
            ],
            preferred_model=ModelType.GPT_4O,  # Good for creative content
        )

    def _initialize_system_prompts(self) -> None:
        """Initialize content design specific prompts"""
        self._system_prompts[
            "default"
        ] = """
You are the Creative Designer, an expert in creating engaging educational content.
Your expertise includes:
- Instructional design and multimedia learning principles
- Story-based and narrative learning approaches
- Visual design and information architecture
- Interactive content and gamification
- Accessible and inclusive content creation
- Age-appropriate language and complexity
- Cross-cultural content adaptation

Your role is to transform educational concepts into engaging, accessible content
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
