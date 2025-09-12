"""
Base Agent Class - Foundation for all specialized agents
Implements core agent behaviors and communication protocols
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import json
from enum import Enum

from .state import AgentState, AgentMessage, MessageType, AgentRole
from .llm_manager import LLMManager, ModelCapability, ModelType


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_FOR_INPUT = "waiting_for_input"
    COLLABORATING = "collaborating"
    ERROR = "error"
    COMPLETED = "completed"


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents
    Provides core functionality for LLM interaction, state management, and communication
    """
    
    def __init__(
        self,
        role: AgentRole,
        llm_manager: LLMManager,
        name: str,
        description: str,
        capabilities: List[ModelCapability],
        preferred_model: Optional[ModelType] = None
    ):
        """Initialize base agent"""
        self.role = role
        self.llm_manager = llm_manager
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.preferred_model = preferred_model
        
        # Agent state
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Dict[str, Any]] = None
        self.task_history: List[Dict[str, Any]] = []
        self.collaboration_requests: List[AgentMessage] = []
        
        # Performance tracking
        self.tasks_completed = 0
        self.total_processing_time = 0
        self.quality_scores: List[float] = []
        
        # System prompts cache
        self._system_prompts: Dict[str, str] = {}
        self._initialize_system_prompts()
    
    @abstractmethod
    def _initialize_system_prompts(self) -> None:
        """Initialize agent-specific system prompts"""
        pass
    
    @abstractmethod
    async def process_task(
        self,
        task: Dict[str, Any],
        state: AgentState,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """Process a specific task - must be implemented by each agent"""
        pass
    
    @abstractmethod
    async def collaborate(
        self,
        message: AgentMessage,
        state: AgentState
    ) -> AgentMessage:
        """Handle collaboration requests from other agents"""
        pass
    
    async def execute(
        self,
        state: AgentState,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None] | Dict[str, Any]:
        """
        Main execution method for the agent
        Processes messages, executes tasks, and updates state
        """
        self.status = AgentStatus.PROCESSING
        state.update_agent_status(self.role, self.status.value)
        
        try:
            # Process incoming messages
            messages = state.get_messages_for_agent(self.role)
            
            for message in messages:
                if message.message_type == MessageType.REQUEST:
                    # Process task request
                    result = await self.process_task(
                        message.content,
                        state,
                        stream
                    )
                    
                    if stream:
                        async for chunk in result:
                            yield chunk
                    else:
                        # Send response
                        response = AgentMessage(
                            sender=self.role,
                            recipient=message.sender,
                            message_type=MessageType.RESPONSE,
                            content=result,
                            parent_message_id=message.id
                        )
                        state.add_message(response)
                        yield result
                
                elif message.message_type == MessageType.COLLABORATION:
                    # Handle collaboration request
                    response = await self.collaborate(message, state)
                    state.add_message(response)
            
            # Clear processed messages
            state.clear_message_queue(self.role)
            
            self.status = AgentStatus.COMPLETED
            state.update_agent_status(self.role, self.status.value)
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            state.update_agent_status(self.role, self.status.value)
            state.log_error(e, self.role, {"task": self.current_task})
            
            # Send error message
            error_message = AgentMessage(
                sender=self.role,
                message_type=MessageType.ERROR,
                content={
                    "error": str(e),
                    "agent": self.role.value,
                    "task": self.current_task
                }
            )
            state.add_message(error_message)
            
            if not stream:
                raise e
    
    async def _generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None] | str:
        """Generate response using LLM"""
        response = await self.llm_manager.generate(
            prompt=prompt,
            system_prompt=system_prompt or self._system_prompts.get("default"),
            model=self.preferred_model,
            temperature=temperature,
            required_capabilities=self.capabilities,
            stream=stream
        )
        
        if stream:
            return response
        else:
            return response.content
    
    async def _generate_structured_response(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured response using LLM"""
        return await self.llm_manager.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_prompt=system_prompt or self._system_prompts.get("structured"),
            model=self.preferred_model
        )
    
    async def request_collaboration(
        self,
        target_agent: AgentRole,
        request: Dict[str, Any],
        state: AgentState
    ) -> None:
        """Request collaboration from another agent"""
        message = AgentMessage(
            sender=self.role,
            recipient=target_agent,
            message_type=MessageType.COLLABORATION,
            content=request,
            requires_response=True
        )
        state.add_message(message)
        self.collaboration_requests.append(message)
    
    async def broadcast_update(
        self,
        update: Dict[str, Any],
        state: AgentState
    ) -> None:
        """Broadcast an update to all agents"""
        message = AgentMessage(
            sender=self.role,
            message_type=MessageType.BROADCAST,
            content=update
        )
        state.add_message(message)
    
    def evaluate_quality(self, result: Dict[str, Any]) -> float:
        """Evaluate the quality of a result (0-1 scale)"""
        # Base implementation - can be overridden by specific agents
        criteria = {
            "completeness": 0.3,
            "accuracy": 0.3,
            "relevance": 0.2,
            "innovation": 0.2
        }
        
        score = 0.0
        for criterion, weight in criteria.items():
            if criterion in result.get("quality_metrics", {}):
                score += result["quality_metrics"][criterion] * weight
            else:
                # Default moderate score if not evaluated
                score += 0.7 * weight
        
        self.quality_scores.append(score)
        return score
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_quality = sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0
        
        return {
            "agent": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "average_quality_score": avg_quality,
            "total_processing_time": self.total_processing_time,
            "current_task": self.current_task
        }
    
    async def validate_input(self, task: Dict[str, Any]) -> bool:
        """Validate task input before processing"""
        required_fields = self._get_required_fields()
        
        for field in required_fields:
            if field not in task:
                raise ValueError(f"Missing required field: {field}")
        
        return True
    
    @abstractmethod
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for task input"""
        pass
    
    def _create_response(
        self,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized response format"""
        return {
            "agent": self.name,
            "role": self.role.value,
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": metadata or {},
            "quality_score": self.evaluate_quality({"content": content})
        }