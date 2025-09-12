# PBL智能助手 API接口规范

## 概览

PBL智能助手后端提供RESTful API和WebSocket实时通信接口，支持多智能体协作的完整教育解决方案。

### 基础信息

- **版本**: v1.0.0
- **基础URL**: `https://api.pbl-assistant.com/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 状态码约定

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权访问 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求频率过高 |
| 500 | Internal Server Error | 服务器内部错误 |

## 认证接口

### POST /auth/login
用户登录

**请求体**
```json
{
  "username": "teacher01",
  "password": "secure_password"
}
```

**响应**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "username": "teacher01",
    "email": "teacher01@school.edu",
    "role": "teacher",
    "display_name": "张老师"
  }
}
```

### POST /auth/refresh
刷新访问令牌

**请求头**
```
Authorization: Bearer {refresh_token}
```

**响应**
```json
{
  "access_token": "new_access_token",
  "expires_in": 1800
}
```

## 智能体接口

### GET /agents
获取所有可用智能体

**响应**
```json
{
  "agents": {
    "education_director": {
      "name": "教育总监",
      "description": "教育愿景指导、战略决策制定、跨学科整合专家",
      "model": "opus",
      "capabilities": [
        "教育愿景与战略规划",
        "跨学科课程整合",
        "学习者中心设计"
      ],
      "status": "active",
      "expertise_level": "expert",
      "response_time_avg": "2-5秒"
    }
  },
  "total_count": 5,
  "active_count": 5,
  "collaboration_modes": ["sequential", "parallel", "hierarchical"]
}
```

### POST /agents/{agent_name}/chat
与指定智能体对话

**路径参数**
- `agent_name`: 智能体名称 (education_director, pbl_curriculum_designer, etc.)

**请求体**
```json
{
  "message": "请帮我设计一个关于可持续发展的PBL项目",
  "context": {
    "grade_level": "高中",
    "subject": "环境科学",
    "duration": "4周"
  },
  "conversation_id": "optional-conversation-uuid",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**响应**
```json
{
  "agent_name": "pbl_curriculum_designer",
  "content": "我来帮您设计一个高中环境科学的可持续发展PBL项目...",
  "conversation_id": "conversation-uuid",
  "message_id": "message-uuid",
  "metadata": {
    "model_used": "opus",
    "tokens_used": 1250,
    "processing_time": 3.2
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

### POST /agents/collaborate
多智能体协作

**请求体**
```json
{
  "task_description": "为小学三年级设计一个关于'我的家乡'的综合项目，融合语文、数学、科学、艺术等学科",
  "task_type": "course_design",
  "collaboration_mode": "sequential",
  "required_expertise": ["课程设计", "跨学科整合", "项目评估"],
  "context": {
    "grade_level": "小学三年级",
    "duration": "6周",
    "student_count": 30
  },
  "priority": "medium",
  "max_agents": 3,
  "timeout_minutes": 10
}
```

**响应**
```json
{
  "agent_name": "collaboration_team",
  "content": "# 小学三年级'我的家乡'综合项目方案\n\n## 项目概览...",
  "conversation_id": "collaboration-session-uuid",
  "message_id": "task-uuid", 
  "metadata": {
    "participating_agents": [
      "education_director",
      "pbl_curriculum_designer",
      "learning_experience_designer"
    ],
    "collaboration_mode": "sequential",
    "task_type": "course_design",
    "execution_time": 45.2,
    "quality_score": 8.7
  },
  "timestamp": "2024-01-15T10:35:00Z",
  "status": "success"
}
```

### GET /agents/{agent_name}/stream
流式获取智能体响应

**查询参数**
- `message`: 发送给智能体的消息
- `conversation_id`: 可选的对话ID

**响应** (Server-Sent Events)
```
data: {"agent_name": "education_director", "content": "正在分析您的需求...", "type": "thinking"}

data: {"agent_name": "education_director", "content": "基于您的描述", "type": "content"}

data: {"agent_name": "education_director", "content": "，我建议采用以下策略...", "type": "content"}
```

## 对话管理接口

### POST /conversations
创建新对话

**请求体**
```json
{
  "title": "可持续发展项目设计",
  "description": "为高中环境科学课程设计PBL项目",
  "agents": ["education_director", "pbl_curriculum_designer"],
  "initial_context": {
    "subject": "环境科学",
    "grade": "高中"
  },
  "is_private": true
}
```

**响应**
```json
{
  "conversation_id": "conv-uuid",
  "title": "可持续发展项目设计",
  "description": "为高中环境科学课程设计PBL项目", 
  "participants": ["education_director", "pbl_curriculum_designer"],
  "created_at": "2024-01-15T10:00:00Z",
  "status": "active"
}
```

### GET /conversations/{conversation_id}/history
获取对话历史

**查询参数**
- `limit`: 返回消息数量 (默认50, 最大200)
- `offset`: 偏移量 (默认0)

**响应**
```json
{
  "conversation_id": "conv-uuid",
  "messages": [
    {
      "message_id": "msg-uuid-1",
      "role": "user",
      "content": "请帮我设计一个可持续发展的项目",
      "timestamp": "2024-01-15T10:00:00Z",
      "metadata": {}
    },
    {
      "message_id": "msg-uuid-2", 
      "role": "agent",
      "content": "我来帮您设计一个综合性的可持续发展项目...",
      "agent_name": "pbl_curriculum_designer",
      "timestamp": "2024-01-15T10:01:00Z",
      "metadata": {"model": "opus", "tokens": 1250}
    }
  ],
  "total_count": 8,
  "has_more": false
}
```

## 课程管理接口

### GET /courses
获取课程列表

**查询参数**
- `subject`: 学科筛选
- `grade_level`: 年级筛选
- `keyword`: 关键词搜索
- `page`: 页码 (默认1)
- `size`: 每页数量 (默认20)

**响应**
```json
{
  "courses": [
    {
      "id": "course-uuid",
      "title": "可持续发展与环保行动",
      "description": "通过项目式学习探索环境保护的实际行动",
      "subject": "环境科学",
      "grade_level": "高中",
      "duration_weeks": 4,
      "created_by": "teacher-uuid",
      "status": "published",
      "tags": ["PBL", "可持续发展", "环保"],
      "created_at": "2024-01-10T09:00:00Z"
    }
  ],
  "total_count": 156,
  "page": 1,
  "size": 20,
  "total_pages": 8
}
```

### POST /courses
创建新课程

**请求体**
```json
{
  "title": "智能城市设计挑战",
  "description": "学生团队设计未来智能城市的综合项目",
  "subject": "STEAM综合",
  "grade_level": "初中",
  "duration_weeks": 8,
  "driving_question": "如何设计一个既智能又可持续的未来城市？",
  "learning_objectives": [
    "理解城市规划的基本原则",
    "掌握可持续发展的核心概念",
    "培养跨学科问题解决能力"
  ],
  "assessment_plan": {
    "formative": ["周度进展检查", "同伴互评"],
    "summative": ["最终展示", "设计作品集"]
  },
  "resources": [
    "城市规划软件",
    "建筑模型材料",
    "在线研究数据库"
  ],
  "tags": ["STEAM", "城市规划", "可持续发展"]
}
```

## 项目管理接口

### GET /projects
获取项目列表

### POST /projects
创建新项目

### GET /projects/{project_id}
获取项目详情

### PUT /projects/{project_id}
更新项目

### DELETE /projects/{project_id}
删除项目

## 指标和反馈接口

### GET /agents/metrics
获取智能体性能指标

**查询参数**
- `agent_name`: 特定智能体名称 (可选)
- `time_range`: 时间范围 (1h, 6h, 24h, 7d, 30d)

**响应**
```json
{
  "time_range": "24h",
  "agent_name": null,
  "total_requests": 1250,
  "successful_requests": 1198,
  "success_rate": 0.958,
  "average_response_time": 2.3,
  "p95_response_time": 4.1,
  "user_satisfaction": 4.6,
  "error_rate": 0.042,
  "most_common_tasks": [
    {"task": "PBL课程设计", "count": 456},
    {"task": "学习体验优化", "count": 342}
  ],
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### POST /agents/{agent_name}/feedback
提交智能体反馈

**请求体**
```json
{
  "message_id": "msg-uuid",
  "rating": 5,
  "feedback": "回答非常有帮助，提供了具体可行的建议"
}
```

## WebSocket接口

### WebSocket连接
`wss://api.pbl-assistant.com/api/v1/ws`

**连接参数**
- `token`: JWT访问令牌

**消息格式**
```json
{
  "type": "message",
  "agent_name": "education_director",
  "content": "您的消息内容",
  "conversation_id": "conv-uuid",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

**心跳检查**
```json
{
  "type": "ping",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

## 错误处理

### 标准错误格式
```json
{
  "error": "validation_error",
  "message": "输入数据验证失败",
  "field": "message",
  "request_id": "req-uuid-123",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### 智能体特定错误
```json
{
  "error": "agent_error",
  "message": "智能体暂时不可用",
  "agent_type": "education_director",
  "error_code": "AGENT_TIMEOUT",
  "request_id": "req-uuid-123"
}
```

## 速率限制

- **默认限制**: 100请求/分钟
- **认证用户**: 200请求/分钟
- **高级用户**: 500请求/分钟

**限制头部**
```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 195
X-RateLimit-Reset: 1642248000
```

## SDK和工具

### Python SDK示例
```python
from pbl_assistant import PBLClient

client = PBLClient(api_key="your_api_key")

# 与智能体对话
response = await client.chat_with_agent(
    agent="pbl_curriculum_designer",
    message="设计一个关于水质检测的项目"
)

# 多智能体协作
collaboration = await client.collaborate(
    task="为初中生设计STEAM项目",
    mode="sequential"
)
```

### JavaScript SDK示例
```javascript
import { PBLAssistant } from 'pbl-assistant-sdk';

const client = new PBLAssistant({ apiKey: 'your_api_key' });

// 与智能体对话
const response = await client.chatWithAgent('education_director', {
  message: '制定跨学科整合策略',
  context: { grade: '小学', subjects: ['数学', '科学'] }
});
```

## 版本控制

API使用版本前缀进行版本控制：
- **v1**: `/api/v1/` - 当前稳定版本
- **v2**: `/api/v2/` - 下一版本（开发中）

版本变更会提前通知，旧版本会有6个月的维护期。