"""
Custom Exception Classes for PBL Assistant
Provides specialized exception handling for different components
"""

from typing import Optional, Any


class PBLAssistantException(Exception):
    """Base exception class for PBL Assistant"""

    def __init__(self, message: str, error_code: Optional[str] = None, **kwargs):
        self.message = message
        self.error_code = error_code
        self.details = kwargs
        super().__init__(self.message)


class AgentException(PBLAssistantException):
    """Exception raised when agent operations fail"""

    def __init__(
        self,
        message: str,
        agent_type: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        **kwargs
    ):
        self.agent_type = agent_type
        self.status_code = status_code
        super().__init__(message, error_code, **kwargs)

    @property
    def detail(self) -> str:
        return self.message


class ValidationException(PBLAssistantException):
    """Exception raised when data validation fails"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        error_code: Optional[str] = None,
        **kwargs
    ):
        self.field = field
        super().__init__(message, error_code, **kwargs)

    @property
    def detail(self) -> str:
        return self.message


class AuthenticationException(PBLAssistantException):
    """Exception raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)

    @property
    def detail(self) -> str:
        return self.message


class AgentCollaborationError(AgentException):
    """Exception raised when agent collaboration fails"""

    def __init__(self, message: str, agents: list, **kwargs):
        self.agents = agents
        super().__init__(
            message=message,
            agent_type="collaboration",
            error_code="COLLABORATION_FAILED",
            **kwargs
        )


class CourseGenerationError(PBLAssistantException):
    """Exception raised when course generation fails"""

    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        self.stage = stage
        super().__init__(message, error_code="COURSE_GENERATION_FAILED", **kwargs)


class LLMException(AgentException):
    """Exception raised when LLM operations fail"""

    def __init__(self, message: str, model: str, **kwargs):
        self.model = model
        super().__init__(
            message=message,
            agent_type="llm",
            error_code="LLM_ERROR",
            **kwargs
        )


class StateManagementError(PBLAssistantException):
    """Exception raised when state management operations fail"""

    def __init__(self, message: str, state_key: Optional[str] = None, **kwargs):
        self.state_key = state_key
        super().__init__(message, error_code="STATE_ERROR", **kwargs)