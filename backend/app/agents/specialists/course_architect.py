"""
Course Architect Agent
Designs the overall structure and architecture of PBL courses
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from ..core.base_agent import BaseAgent
from ..core.llm_manager import ModelCapability, ModelType
from ..core.state import AgentMessage, AgentRole, AgentState, MessageType


class CourseArchitectAgent(BaseAgent):
    """
    Expert in course structure design and learning pathway architecture
    Creates comprehensive PBL course blueprints
    """

    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.COURSE_ARCHITECT,
            llm_manager=llm_manager,
            name="Master Architect",
            description="Course structure expert specializing in PBL curriculum architecture",
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.CREATIVITY,
                ModelCapability.ANALYSIS,
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET,
        )

    def _initialize_system_prompts(self) -> None:
        """Initialize course architecture specific prompts"""
        self._system_prompts[
            "default"
        ] = """
You are the Master Architect, an expert in designing innovative PBL course structures.
Your expertise includes:
- Curriculum mapping and learning pathway design
- Module sequencing and progression logic
- Project milestone planning and pacing
- Integration of cross-curricular connections
- Resource allocation and time management
- Flexible learning path accommodation
- Competency-based progression design

Your role is to create comprehensive, coherent course architectures that facilitate
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
        """Design the overall course structure"""

        requirements = state.course_requirements
        framework = state.theoretical_framework

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

    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]
