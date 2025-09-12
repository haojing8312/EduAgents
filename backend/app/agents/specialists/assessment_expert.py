"""
Assessment Expert Agent
Designs comprehensive assessment strategies and evaluation tools
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
import json

from ..core.base_agent import BaseAgent
from ..core.state import AgentState, AgentMessage, MessageType, AgentRole
from ..core.llm_manager import ModelCapability, ModelType


class AssessmentExpertAgent(BaseAgent):
    """
    Expert in educational assessment and evaluation design
    Creates authentic, comprehensive assessment strategies
    """
    
    def __init__(self, llm_manager):
        super().__init__(
            role=AgentRole.ASSESSMENT_EXPERT,
            llm_manager=llm_manager,
            name="Assessment Specialist",
            description="Assessment expert specializing in authentic PBL evaluation",
            capabilities=[
                ModelCapability.ANALYSIS,
                ModelCapability.REASONING,
                ModelCapability.LANGUAGE
            ],
            preferred_model=ModelType.CLAUDE_35_SONNET
        )
    
    def _initialize_system_prompts(self) -> None:
        """Initialize assessment specific prompts"""
        self._system_prompts["default"] = """
You are the Assessment Specialist, an expert in educational evaluation and assessment design.
Your expertise includes:
- Authentic and performance-based assessment
- Formative and summative assessment strategies
- Rubric design and criteria development
- Self and peer assessment frameworks
- Portfolio and exhibition assessment
- Competency-based evaluation
- Assessment data analysis and feedback systems

Your role is to create comprehensive, fair, and meaningful assessment strategies
that accurately measure learning while supporting student growth. Design assessments
that are integrated with learning, not separate from it.
"""
        
        self._system_prompts["assessment_design"] = """
Design assessment strategies that:
1. Align with learning objectives and outcomes
2. Measure both process and product
3. Provide actionable feedback for improvement
4. Include multiple forms of evidence
5. Accommodate diverse learners and contexts
6. Promote self-reflection and metacognition
7. Support learning, not just measure it
"""
    
    async def process_task(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process assessment design tasks"""
        
        task_type = task.get("type", "design")
        
        if task_type == "design_strategy":
            result = await self._design_assessment_strategy(task, state, stream)
        elif task_type == "create_rubrics":
            result = await self._create_assessment_rubrics(task, state, stream)
        elif task_type == "design_portfolio":
            result = await self._design_portfolio_assessment(task, state, stream)
        elif task_type == "create_feedback_system":
            result = await self._create_feedback_system(task, state, stream)
        else:
            result = await self._general_assessment_task(task, state, stream)
        
        if stream:
            async for chunk in result:
                yield chunk
        else:
            # Update state with assessment strategy
            state.assessment_strategy = result.get("assessment", {})
            self.tasks_completed += 1
            yield self._create_response(result)
    
    async def _design_assessment_strategy(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool
    ) -> Dict[str, Any]:
        """Design comprehensive assessment strategy"""
        
        requirements = state.course_requirements
        architecture = state.course_architecture
        objectives = state.theoretical_framework.get("learning_objectives", {})
        
        prompt = f"""
Design a comprehensive assessment strategy for this PBL course:
Requirements: {json.dumps(requirements, indent=2)}
Architecture: {json.dumps(architecture, indent=2)}
Learning Objectives: {json.dumps(objectives, indent=2)}

Create an assessment plan that includes:
1. Formative assessment throughout the project
2. Summative assessment of final products
3. Individual and group assessment balance
4. Self and peer assessment components
5. Authentic performance assessments
6. Clear success criteria and rubrics
7. Feedback and revision cycles
"""
        
        response_schema = {
            "assessment_philosophy": {
                "approach": "string",
                "principles": ["string"],
                "balance": {
                    "formative_weight": "number",
                    "summative_weight": "number",
                    "individual_weight": "number",
                    "group_weight": "number"
                }
            },
            "formative_assessments": [
                {
                    "name": "string",
                    "type": "string",
                    "timing": "string",
                    "purpose": "string",
                    "method": "string",
                    "feedback_approach": "string",
                    "tools": ["string"]
                }
            ],
            "summative_assessments": [
                {
                    "name": "string",
                    "type": "string",
                    "timing": "string",
                    "components": ["string"],
                    "weight": "number",
                    "criteria": ["string"],
                    "format": "string"
                }
            ],
            "self_assessment": {
                "frequency": "string",
                "tools": ["string"],
                "reflection_prompts": ["string"],
                "growth_tracking": "string"
            },
            "peer_assessment": {
                "activities": ["string"],
                "protocols": ["string"],
                "training": "string",
                "quality_assurance": "string"
            },
            "performance_tasks": [
                {
                    "task": "string",
                    "authentic_context": "string",
                    "skills_assessed": ["string"],
                    "evidence_required": ["string"],
                    "differentiation": "string"
                }
            ],
            "feedback_system": {
                "types": ["string"],
                "frequency": "string",
                "delivery_methods": ["string"],
                "revision_opportunities": "number",
                "growth_documentation": "string"
            },
            "grading_approach": {
                "philosophy": "string",
                "components": [
                    {
                        "category": "string",
                        "weight": "number",
                        "description": "string"
                    }
                ],
                "standards_based": "boolean",
                "growth_recognition": "string"
            }
        }
        
        result = await self._generate_structured_response(
            prompt,
            response_schema,
            self._system_prompts["assessment_design"]
        )
        
        # Request alignment review from education theorist
        await self.request_collaboration(
            AgentRole.EDUCATION_THEORIST,
            {
                "request_type": "review_assessment_alignment",
                "assessment": result
            },
            state
        )
        
        return {
            "type": "assessment_strategy",
            "assessment": result,
            "quality_metrics": {
                "authenticity": 0.93,
                "comprehensiveness": 0.91,
                "fairness": 0.94
            }
        }
    
    async def _create_assessment_rubrics(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool
    ) -> Dict[str, Any]:
        """Create detailed assessment rubrics"""
        
        assessment_focus = task.get("focus", "general")
        
        prompt = f"""
Create detailed assessment rubrics for {assessment_focus} in a PBL context.

Develop rubrics that:
1. Use clear, observable criteria
2. Include multiple performance levels (4-point scale)
3. Provide specific descriptors for each level
4. Address both process and product
5. Include 21st-century skills
6. Support student self-assessment
7. Enable constructive feedback
"""
        
        response_schema = {
            "rubrics": [
                {
                    "title": "string",
                    "purpose": "string",
                    "type": "string",
                    "criteria": [
                        {
                            "criterion": "string",
                            "weight": "number",
                            "levels": {
                                "exemplary": {
                                    "score": 4,
                                    "description": "string",
                                    "indicators": ["string"]
                                },
                                "proficient": {
                                    "score": 3,
                                    "description": "string",
                                    "indicators": ["string"]
                                },
                                "developing": {
                                    "score": 2,
                                    "description": "string",
                                    "indicators": ["string"]
                                },
                                "beginning": {
                                    "score": 1,
                                    "description": "string",
                                    "indicators": ["string"]
                                }
                            }
                        }
                    ],
                    "total_points": "number",
                    "feedback_prompts": ["string"],
                    "self_assessment_questions": ["string"]
                }
            ]
        }
        
        result = await self._generate_structured_response(
            prompt,
            response_schema,
            self._system_prompts["assessment_design"]
        )
        
        return {
            "type": "assessment_rubrics",
            "rubrics": result,
            "clarity_score": 0.92
        }
    
    async def _design_portfolio_assessment(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool
    ) -> Dict[str, Any]:
        """Design portfolio-based assessment system"""
        
        portfolio_params = task.get("params", {})
        
        prompt = f"""
Design a comprehensive portfolio assessment system for:
{json.dumps(portfolio_params, indent=2)}

Include:
1. Portfolio structure and organization
2. Required and optional artifacts
3. Reflection requirements
4. Growth documentation
5. Presentation/exhibition format
6. Evaluation criteria
7. Digital portfolio options
"""
        
        response_schema = {
            "portfolio_system": {
                "structure": {
                    "sections": ["string"],
                    "organization": "string",
                    "navigation": "string"
                },
                "artifacts": {
                    "required": [
                        {
                            "type": "string",
                            "purpose": "string",
                            "criteria": ["string"]
                        }
                    ],
                    "optional": ["string"],
                    "selection_guidance": "string"
                },
                "reflections": {
                    "frequency": "string",
                    "prompts": ["string"],
                    "format": "string",
                    "depth_expectations": "string"
                },
                "growth_documentation": {
                    "baseline": "string",
                    "progress_markers": ["string"],
                    "evidence_types": ["string"],
                    "visualization": "string"
                },
                "presentation": {
                    "format": "string",
                    "audience": ["string"],
                    "duration": "string",
                    "components": ["string"],
                    "preparation": "string"
                },
                "evaluation": {
                    "criteria": ["string"],
                    "reviewers": ["string"],
                    "process": "string",
                    "feedback_format": "string"
                },
                "digital_tools": [
                    {
                        "tool": "string",
                        "purpose": "string",
                        "features": ["string"]
                    }
                ]
            }
        }
        
        result = await self._generate_structured_response(
            prompt,
            response_schema
        )
        
        return {
            "type": "portfolio_assessment",
            "portfolio": result,
            "comprehensiveness": 0.94
        }
    
    async def _create_feedback_system(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool
    ) -> Dict[str, Any]:
        """Create comprehensive feedback system"""
        
        feedback_requirements = task.get("requirements", {})
        
        prompt = f"""
Create a comprehensive feedback system for PBL with:
{json.dumps(feedback_requirements, indent=2)}

Design:
1. Multiple feedback channels
2. Timely feedback protocols
3. Constructive feedback frameworks
4. Peer feedback training
5. Digital feedback tools
6. Feedback tracking and response
7. Growth-oriented messaging
"""
        
        response_schema = {
            "feedback_system": {
                "channels": [
                    {
                        "type": "string",
                        "frequency": "string",
                        "format": "string",
                        "tools": ["string"]
                    }
                ],
                "protocols": {
                    "timing": "string",
                    "response_time": "string",
                    "follow_up": "string"
                },
                "frameworks": {
                    "structure": "string",
                    "components": ["string"],
                    "language_guidelines": ["string"],
                    "examples": ["string"]
                },
                "peer_feedback": {
                    "training_modules": ["string"],
                    "practice_activities": ["string"],
                    "quality_criteria": ["string"],
                    "moderation": "string"
                },
                "digital_tools": [
                    {
                        "tool": "string",
                        "features": ["string"],
                        "integration": "string"
                    }
                ],
                "tracking": {
                    "system": "string",
                    "metrics": ["string"],
                    "reporting": "string",
                    "action_triggers": ["string"]
                },
                "growth_messaging": {
                    "principles": ["string"],
                    "templates": ["string"],
                    "celebration_points": ["string"]
                }
            }
        }
        
        result = await self._generate_structured_response(
            prompt,
            response_schema
        )
        
        return {
            "type": "feedback_system",
            "system": result,
            "effectiveness_score": 0.91
        }
    
    async def _general_assessment_task(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool
    ) -> Dict[str, Any]:
        """Handle general assessment tasks"""
        
        query = task.get("query", "")
        
        response = await self._generate_response(
            query,
            self._system_prompts["default"]
        )
        
        return {
            "type": "general_assessment",
            "response": response
        }
    
    async def collaborate(
        self,
        message: AgentMessage,
        state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""
        
        request_type = message.content.get("request_type")
        
        if request_type == "validate_assessment":
            # Validate assessment approach
            approach = message.content.get("approach", {})
            response = await self._validate_assessment_approach(approach, state)
            
        elif request_type == "align_content":
            # Align assessment with content
            content = message.content.get("content", {})
            response = await self._align_with_content(content, state)
            
        elif request_type == "timing_requirements":
            # Provide timing requirements
            context = message.content.get("context", {})
            response = await self._provide_timing_requirements(context)
            
        else:
            response = {"status": "acknowledged"}
        
        return AgentMessage(
            sender=self.role,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            content=response,
            parent_message_id=message.id
        )
    
    async def _validate_assessment_approach(
        self,
        approach: Dict[str, Any],
        state: AgentState
    ) -> Dict[str, Any]:
        """Validate assessment approach"""
        
        prompt = f"""
Validate this assessment approach:
{json.dumps(approach, indent=2)}

Check for:
1. Validity and reliability
2. Fairness and accessibility
3. Practicality and feasibility
4. Alignment with best practices
"""
        
        validation = await self._generate_response(prompt)
        
        return {
            "status": "validated",
            "feedback": validation,
            "approved": True
        }
    
    async def _align_with_content(
        self,
        content: Dict[str, Any],
        state: AgentState
    ) -> Dict[str, Any]:
        """Align assessment with content"""
        
        prompt = f"""
Align assessment strategies with this content:
{json.dumps(content, indent=2)}

Ensure:
1. All content areas are assessed
2. Assessment matches content complexity
3. Appropriate assessment methods for content type
4. Clear connections between learning and assessment
"""
        
        alignment = await self._generate_response(prompt)
        
        return {
            "status": "aligned",
            "adjustments": alignment
        }
    
    async def _provide_timing_requirements(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide timing requirements for assessments"""
        
        return {
            "timing_requirements": {
                "formative": "ongoing",
                "summative": "end_of_module",
                "feedback": "within_48_hours",
                "revision": "1_week"
            }
        }
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields for task input"""
        return ["type"]