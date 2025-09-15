"""
PBL Course Design Multi-Agent System
World-class AI-powered collaborative agents for educational innovation
"""

from .core.orchestrator import PBLOrchestrator
from .core.state import AgentState, MessageType
from .specialists import (
    AssessmentExpertAgent,
    ContentDesignerAgent,
    CourseArchitectAgent,
    EducationTheoristAgent,
    MaterialCreatorAgent,
)

__all__ = [
    "PBLOrchestrator",
    "AgentState",
    "MessageType",
    "EducationTheoristAgent",
    "CourseArchitectAgent",
    "ContentDesignerAgent",
    "AssessmentExpertAgent",
    "MaterialCreatorAgent",
]

__version__ = "1.0.0"
