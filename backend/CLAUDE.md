# 🔧 PBL智能体系统 - 后端模块

## 模块概述

FastAPI后端服务，实现多智能体协作的PBL课程设计系统。基于LangGraph框架的智能体编排，提供RESTful API和WebSocket实时通信。

## 🏗️ 架构设计

### 核心组件
- **多智能体系统** (`app/agents/`) - 5个专业智能体协作框架
- **API层** (`app/api/v1/`) - RESTful API端点
- **数据层** (`app/models/`) - SQLAlchemy ORM模型
- **服务层** (`app/services/`) - 业务逻辑服务
- **配置层** (`app/core/`) - 应用配置和依赖注入

### 智能体架构
```
agents/
├── core/
│   ├── base_agent.py        # 智能体基类
│   ├── orchestrator.py      # LangGraph编排器
│   ├── state.py            # 共享状态管理
│   └── llm_manager.py      # AI模型管理
└── specialists/
    ├── education_theorist.py    # 教育理论专家
    ├── course_architect.py      # 课程架构师
    ├── content_designer.py      # 内容设计师
    ├── assessment_expert.py     # 评估专家
    └── material_creator.py      # 素材创作者
```

## 💻 开发命令

### 环境设置 (使用uv - 推荐)
```bash
cd backend

# uv会自动创建虚拟环境并安装依赖
uv sync

# 或者手动创建虚拟环境
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 传统环境设置 (如果没有uv)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 开发服务器
```bash
# 🚀 推荐：使用uv运行开发脚本
uv run scripts/dev.py

# 或者直接使用uv run
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 传统方式（需要激活虚拟环境）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试
```bash
# 🧪 推荐：使用uv运行测试脚本
uv run scripts/test.py           # 基础测试
uv run scripts/test.py --cov     # 包含覆盖率
uv run scripts/test.py --unit    # 只运行单元测试
uv run scripts/test.py --parallel # 并行测试

# 或者直接使用uv run
uv run pytest tests/ -v
uv run pytest tests/ --cov=app --cov-report=html

# 传统方式
python -m pytest tests/
```

### 代码质量
```bash
# 🎨 代码格式化
uv run scripts/format.py

# 🔍 代码检查
uv run scripts/lint.py

# 或者单独运行
uv run black app tests scripts     # 代码格式化
uv run isort app tests scripts     # 导入排序
uv run flake8 app tests            # 风格检查
uv run mypy app                    # 类型检查
uv run bandit -r app               # 安全检查
```

### 数据库操作
```bash
# 使用uv运行数据库迁移
uv run alembic revision --autogenerate -m "描述"
uv run alembic upgrade head
uv run alembic downgrade -1

# 传统方式（需要激活虚拟环境）
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1
```

## 📋 代码规范

### Python规范
- 严格遵循PEP 8
- 使用Black自动格式化：`black app/ tests/`
- 使用isort排序导入：`isort app/ tests/`
- 100%类型注解，使用mypy检查：`mypy app/`

### 异步编程
- 所有数据库操作使用异步SQLAlchemy
- AI API调用使用异步客户端
- WebSocket处理使用异步生成器

### 错误处理
```python
from fastapi import HTTPException
from app.core.exceptions import AgentCollaborationError

# API错误处理
if not result:
    raise HTTPException(status_code=404, detail="资源未找到")

# 业务逻辑错误
try:
    result = await agent_service.collaborate(task)
except AgentCollaborationError as e:
    logger.error(f"智能体协作失败: {e}")
    raise HTTPException(status_code=500, detail="智能体协作失败")
```

## 🤖 智能体开发指南

### 创建新智能体
```python
from app.agents.core.base_agent import BaseAgent
from app.agents.core.state import AgentState

class NewSpecialistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_type="new_specialist",
            name="新专家智能体",
            description="专业描述"
        )
    
    async def process(self, state: AgentState) -> AgentState:
        # 智能体处理逻辑
        response = await self.llm_manager.chat(
            messages=state.messages,
            system_prompt=self.get_system_prompt()
        )
        
        state.add_agent_response(self.agent_type, response)
        return state
```

### 智能体协作
- 使用LangGraph定义协作流程
- 通过共享状态(AgentState)传递信息
- 支持串行、并行、条件分支协作模式

## 🔐 环境配置

### 必需环境变量
```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost/pbl_assistant
REDIS_URL=redis://localhost:6379

# AI API密钥
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# 应用配置
ENVIRONMENT=development
API_PREFIX=/api/v1
```

### 可选配置
```bash
# 监控
SENTRY_DSN=your_sentry_dsn

# 日志
LOG_LEVEL=INFO
LOG_FORMAT=json

# 性能
WORKER_CONNECTIONS=1000
KEEP_ALIVE=2
```

## 🚨 常见问题

### 智能体协作问题
```python
# 问题：智能体响应超时
# 解决：增加超时配置，优化Prompt
LLM_TIMEOUT = 60  # 秒

# 问题：状态管理混乱
# 解决：确保状态不可变，使用深拷贝
state = state.copy(deep=True)
```

### 数据库连接问题
```python
# 问题：连接池耗尽
# 解决：正确使用异步上下文管理器
async with get_db() as db:
    result = await db.execute(query)
```

### API性能问题
```python
# 问题：响应慢
# 解决：使用Redis缓存，异步处理
from fastapi_cache.decorator import cache

@cache(expire=300)
async def get_course_templates():
    return await course_service.get_templates()
```

## 📊 性能监控

### 关键指标
- API响应时间 < 2秒
- 智能体协作成功率 > 95%
- 数据库查询时间 < 100ms
- 内存使用 < 512MB

### 监控工具
- Prometheus + Grafana
- APM监控（New Relic/DataDog）
- 日志聚合（ELK Stack）

## 🔧 调试技巧

### 日志调试
```python
import logging
logger = logging.getLogger(__name__)

# 智能体协作调试
logger.info(f"智能体 {agent_type} 开始处理任务")
logger.debug(f"输入状态: {state.dict()}")
```

### 测试调试
```bash
# 调试特定测试
python -m pytest tests/test_agents.py::test_collaboration -vvv -s

# 使用pdb调试
python -m pytest tests/test_agents.py --pdb
```

---

*后端模块专属文档 | 更新时间: 2024年9月14日*