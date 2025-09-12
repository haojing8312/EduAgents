"""
智能体相关的Pydantic数据模式定义
用于API请求/响应的数据验证和序列化
"""

from typing import Dict, List, Optional, Any, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class AgentType(str, Enum):
    """智能体类型枚举"""
    EDUCATION_DIRECTOR = "education_director"
    PBL_CURRICULUM_DESIGNER = "pbl_curriculum_designer"
    LEARNING_EXPERIENCE_DESIGNER = "learning_experience_designer"
    CREATIVE_TECHNOLOGIST = "creative_technologist"
    MAKERSPACE_MANAGER = "makerspace_manager"


class CollaborationMode(str, Enum):
    """协作模式枚举"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"     # 并行执行
    HIERARCHICAL = "hierarchical"  # 分层执行
    DEBATE = "debate"         # 辩论模式
    CONSENSUS = "consensus"   # 共识模式


class TaskType(str, Enum):
    """任务类型枚举"""
    COURSE_DESIGN = "course_design"
    PROJECT_PLANNING = "project_planning"
    ASSESSMENT_DESIGN = "assessment_design"
    CURRICULUM_REVIEW = "curriculum_review"
    LEARNING_OPTIMIZATION = "learning_optimization"
    TECHNOLOGY_INTEGRATION = "technology_integration"
    SPACE_PLANNING = "space_planning"


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


# 基础请求模式
class AgentRequest(BaseModel):
    """智能体请求模式"""
    message: str = Field(..., min_length=1, max_length=10000, description="用户消息内容")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")
    conversation_id: Optional[str] = Field(default=None, description="对话ID")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="回答随机性")
    max_tokens: Optional[int] = Field(default=4000, ge=100, le=8000, description="最大令牌数")
    
    @validator('message')
    def validate_message(cls, v):
        """验证消息内容"""
        if not v or v.isspace():
            raise ValueError("消息内容不能为空")
        return v.strip()


class AgentResponse(BaseModel):
    """智能体响应模式"""
    agent_name: str = Field(..., description="智能体名称")
    content: str = Field(..., description="响应内容")
    conversation_id: str = Field(..., description="对话ID")
    message_id: str = Field(..., description="消息ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    status: Literal["success", "error", "partial"] = Field(default="success", description="响应状态")
    usage: Optional[Dict[str, int]] = Field(default=None, description="令牌使用情况")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentStatus(BaseModel):
    """智能体状态模式"""
    agent_name: str = Field(..., description="智能体名称")
    status: Literal["active", "busy", "maintenance", "offline"] = Field(description="状态")
    current_load: int = Field(ge=0, le=100, description="当前负载百分比")
    queue_size: int = Field(ge=0, description="队列大小")
    average_response_time: float = Field(ge=0, description="平均响应时间（秒）")
    last_health_check: datetime = Field(description="最后健康检查时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 协作相关模式
class AgentCollaborationRequest(BaseModel):
    """多智能体协作请求"""
    task_description: str = Field(..., min_length=10, description="任务描述")
    task_type: TaskType = Field(..., description="任务类型")
    collaboration_mode: CollaborationMode = Field(default=CollaborationMode.SEQUENTIAL, description="协作模式")
    required_expertise: Optional[List[str]] = Field(default=None, description="所需专业技能")
    context: Optional[Dict[str, Any]] = Field(default=None, description="任务上下文")
    priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium", description="优先级")
    max_agents: int = Field(default=3, ge=1, le=5, description="最大参与智能体数量")
    timeout_minutes: int = Field(default=10, ge=1, le=60, description="超时时间（分钟）")


class CollaborationResult(BaseModel):
    """协作结果模式"""
    session_id: str = Field(..., description="协作会话ID")
    task_id: str = Field(..., description="任务ID")
    final_output: str = Field(..., description="最终输出")
    agents_involved: List[str] = Field(..., description="参与的智能体")
    execution_time: float = Field(..., description="执行时间（秒）")
    quality_score: Optional[float] = Field(default=None, ge=0, le=10, description="质量评分")
    individual_contributions: Dict[str, str] = Field(..., description="各智能体贡献")
    collaboration_summary: str = Field(..., description="协作总结")


# 对话相关模式
class ConversationMessage(BaseModel):
    """对话消息模式"""
    message_id: str = Field(..., description="消息ID")
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    agent_name: Optional[str] = Field(default=None, description="智能体名称（如果是智能体消息）")
    timestamp: datetime = Field(..., description="消息时间")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="消息元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationCreate(BaseModel):
    """创建对话请求"""
    title: str = Field(..., min_length=1, max_length=200, description="对话标题")
    description: Optional[str] = Field(default=None, max_length=1000, description="对话描述")
    agents: Optional[List[AgentType]] = Field(default=None, description="参与的智能体")
    initial_context: Optional[Dict[str, Any]] = Field(default=None, description="初始上下文")
    is_private: bool = Field(default=True, description="是否私人对话")


class ConversationResponse(BaseModel):
    """对话响应模式"""
    conversation_id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    description: Optional[str] = Field(default=None, description="对话描述")
    participants: List[str] = Field(..., description="参与者列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    status: Literal["active", "paused", "completed", "archived"] = Field(description="对话状态")
    message_count: Optional[int] = Field(default=0, description="消息数量")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationHistory(BaseModel):
    """对话历史记录"""
    conversation_id: str = Field(..., description="对话ID")
    messages: List[ConversationMessage] = Field(..., description="消息列表")
    total_count: int = Field(..., description="总消息数")
    has_more: bool = Field(..., description="是否还有更多消息")
    
    
# 指标和反馈模式
class AgentMetrics(BaseModel):
    """智能体性能指标"""
    time_range: str = Field(..., description="时间范围")
    agent_name: Optional[str] = Field(default=None, description="智能体名称")
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    success_rate: float = Field(..., ge=0, le=1, description="成功率")
    average_response_time: float = Field(..., ge=0, description="平均响应时间（秒）")
    p95_response_time: float = Field(..., ge=0, description="95%响应时间（秒）")
    user_satisfaction: float = Field(..., ge=0, le=5, description="用户满意度")
    error_rate: float = Field(..., ge=0, le=1, description="错误率")
    most_common_tasks: List[Dict[str, Union[str, int]]] = Field(..., description="最常见任务")
    timestamp: datetime = Field(..., description="指标时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentFeedback(BaseModel):
    """智能体反馈模式"""
    agent_name: str = Field(..., description="智能体名称")
    message_id: str = Field(..., description="消息ID")
    rating: int = Field(..., ge=1, le=5, description="评分（1-5）")
    feedback: Optional[str] = Field(default=None, max_length=1000, description="反馈内容")
    categories: Optional[List[str]] = Field(default=None, description="反馈分类")
    is_helpful: Optional[bool] = Field(default=None, description="是否有帮助")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="反馈时间")
    
    @validator('rating')
    def validate_rating(cls, v):
        """验证评分范围"""
        if not 1 <= v <= 5:
            raise ValueError("评分必须在1-5之间")
        return v


# WebSocket消息模式
class WebSocketMessage(BaseModel):
    """WebSocket消息模式"""
    type: Literal["message", "status", "error", "ping", "pong"] = Field(..., description="消息类型")
    agent_name: Optional[str] = Field(default=None, description="智能体名称")
    content: Optional[str] = Field(default=None, description="消息内容")
    conversation_id: Optional[str] = Field(default=None, description="对话ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="消息时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 批量处理模式
class BatchRequest(BaseModel):
    """批量请求模式"""
    requests: List[AgentRequest] = Field(..., min_items=1, max_items=100, description="请求列表")
    batch_id: Optional[str] = Field(default=None, description="批次ID")
    priority: Literal["low", "medium", "high"] = Field(default="medium", description="优先级")
    max_concurrency: int = Field(default=5, ge=1, le=10, description="最大并发数")
    
    @validator('requests')
    def validate_requests_not_empty(cls, v):
        """验证请求列表不为空"""
        if not v:
            raise ValueError("请求列表不能为空")
        return v


class BatchResponse(BaseModel):
    """批量响应模式"""
    batch_id: str = Field(..., description="批次ID")
    total_requests: int = Field(..., description="总请求数")
    completed_requests: int = Field(..., description="已完成请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    status: Literal["processing", "completed", "failed", "cancelled"] = Field(description="批次状态")
    results: Optional[List[AgentResponse]] = Field(default=None, description="结果列表")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }