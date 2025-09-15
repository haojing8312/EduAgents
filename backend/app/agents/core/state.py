"""
State Management for Multi-Agent System
Implements advanced state tracking and inter-agent communication
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class MessageType(Enum):
    """Types of messages in the agent communication system"""

    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    STATUS = "status"
    ERROR = "error"
    COLLABORATION = "collaboration"
    REVIEW = "review"
    APPROVAL = "approval"


class AgentRole(Enum):
    """Specialized roles for agents in the system"""

    EDUCATION_THEORIST = "education_theorist"
    COURSE_ARCHITECT = "course_architect"
    CONTENT_DESIGNER = "content_designer"
    ASSESSMENT_EXPERT = "assessment_expert"
    MATERIAL_CREATOR = "material_creator"
    ORCHESTRATOR = "orchestrator"


class WorkflowPhase(Enum):
    """Phases of the PBL course design workflow"""

    INITIALIZATION = "initialization"
    THEORETICAL_FOUNDATION = "theoretical_foundation"
    ARCHITECTURE_DESIGN = "architecture_design"
    CONTENT_CREATION = "content_creation"
    ASSESSMENT_DESIGN = "assessment_design"
    MATERIAL_PRODUCTION = "material_production"
    REVIEW_ITERATION = "review_iteration"
    FINALIZATION = "finalization"


class AgentMessage(BaseModel):
    """Structured message for inter-agent communication"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: AgentRole
    recipient: Optional[AgentRole] = None  # None for broadcasts
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_response: bool = False
    parent_message_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class AgentState:
    """
    Comprehensive state management for the multi-agent system
    Tracks all aspects of the course design process
    """

    # Workflow Management
    current_phase: WorkflowPhase = WorkflowPhase.INITIALIZATION
    workflow_history: List[WorkflowPhase] = field(default_factory=list)

    # Course Design State
    course_requirements: Dict[str, Any] = field(default_factory=dict)
    theoretical_framework: Dict[str, Any] = field(default_factory=dict)
    course_architecture: Dict[str, Any] = field(default_factory=dict)
    content_modules: List[Dict[str, Any]] = field(default_factory=list)
    assessment_strategy: Dict[str, Any] = field(default_factory=dict)
    learning_materials: List[Dict[str, Any]] = field(default_factory=list)

    # Agent Collaboration State
    active_agents: Set[AgentRole] = field(default_factory=set)
    agent_statuses: Dict[AgentRole, str] = field(default_factory=dict)
    message_queue: List[AgentMessage] = field(default_factory=list)
    message_history: List[AgentMessage] = field(default_factory=list)

    # Consensus and Decision Tracking
    pending_decisions: List[Dict[str, Any]] = field(default_factory=list)
    consensus_items: List[Dict[str, Any]] = field(default_factory=list)
    approval_chain: List[Dict[str, Any]] = field(default_factory=list)

    # Quality Metrics
    quality_scores: Dict[str, float] = field(default_factory=dict)
    iteration_count: int = 0
    revision_history: List[Dict[str, Any]] = field(default_factory=list)

    # Real-time Updates
    last_update: datetime = field(default_factory=datetime.utcnow)
    update_subscribers: List[str] = field(default_factory=list)
    streaming_enabled: bool = True

    # Error Handling and Recovery
    error_log: List[Dict[str, Any]] = field(default_factory=list)
    recovery_checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    fallback_strategies: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    total_tokens_used: int = 0
    api_calls_made: int = 0

    def transition_phase(self, new_phase: WorkflowPhase) -> None:
        """Transition to a new workflow phase with history tracking"""
        self.workflow_history.append(self.current_phase)
        self.current_phase = new_phase
        self.last_update = datetime.utcnow()

    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the queue and history"""
        self.message_queue.append(message)
        self.message_history.append(message)
        self.last_update = datetime.utcnow()

    def get_messages_for_agent(self, agent_role: AgentRole) -> List[AgentMessage]:
        """Get all pending messages for a specific agent"""
        return [
            msg
            for msg in self.message_queue
            if msg.recipient == agent_role or msg.recipient is None
        ]

    def clear_message_queue(self, agent_role: AgentRole) -> None:
        """Clear processed messages for an agent"""
        self.message_queue = [
            msg for msg in self.message_queue if msg.recipient != agent_role
        ]

    def update_agent_status(self, agent_role: AgentRole, status: str) -> None:
        """Update the status of an agent"""
        self.agent_statuses[agent_role] = status
        self.active_agents.add(agent_role)
        self.last_update = datetime.utcnow()

    def add_quality_score(self, metric: str, score: float) -> None:
        """Track quality metrics for the course design"""
        self.quality_scores[metric] = score
        self.last_update = datetime.utcnow()

    def create_checkpoint(self) -> Dict[str, Any]:
        """Create a recovery checkpoint of the current state"""
        checkpoint = {
            "timestamp": datetime.utcnow(),
            "phase": self.current_phase,
            "course_state": {
                "requirements": self.course_requirements,
                "framework": self.theoretical_framework,
                "architecture": self.course_architecture,
                "content": self.content_modules,
                "assessment": self.assessment_strategy,
                "materials": self.learning_materials,
            },
            "quality_scores": self.quality_scores,
            "iteration": self.iteration_count,
        }
        self.recovery_checkpoints.append(checkpoint)
        return checkpoint

    def log_error(
        self, error: Exception, agent_role: AgentRole, context: Dict[str, Any]
    ) -> None:
        """Log errors for debugging and recovery"""
        self.error_log.append(
            {
                "timestamp": datetime.utcnow(),
                "agent": agent_role,
                "error": str(error),
                "context": context,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "current_phase": self.current_phase.value,
            "course_requirements": self.course_requirements,
            "theoretical_framework": self.theoretical_framework,
            "course_architecture": self.course_architecture,
            "content_modules": self.content_modules,
            "assessment_strategy": self.assessment_strategy,
            "learning_materials": self.learning_materials,
            "quality_scores": self.quality_scores,
            "iteration_count": self.iteration_count,
            "active_agents": [agent.value for agent in self.active_agents],
            "agent_statuses": {k.value: v for k, v in self.agent_statuses.items()},
            "total_tokens_used": self.total_tokens_used,
            "api_calls_made": self.api_calls_made,
            "last_update": self.last_update.isoformat(),
        }
