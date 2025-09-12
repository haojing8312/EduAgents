# 项目目录结构

```
pbl-intelligent-assistant/
├── 📁 app/                           # 主应用代码
│   ├── 📁 api/                       # API路由模块
│   │   ├── 📁 v1/                    # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── agents.py             # 智能体相关接口
│   │   │   ├── auth.py               # 认证接口
│   │   │   ├── courses.py            # 课程管理接口
│   │   │   ├── projects.py           # 项目管理接口
│   │   │   ├── websocket.py          # WebSocket接口
│   │   │   └── health.py             # 健康检查
│   │   └── __init__.py
│   ├── 📁 core/                      # 核心配置和工具
│   │   ├── __init__.py
│   │   ├── config.py                 # 应用配置
│   │   ├── dependencies.py           # 依赖注入
│   │   ├── exceptions.py             # 自定义异常
│   │   ├── middleware.py             # 中间件
│   │   └── security.py               # 安全相关
│   ├── 📁 models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础模型
│   │   ├── user.py                   # 用户模型
│   │   ├── course.py                 # 课程模型
│   │   ├── project.py                # 项目模型
│   │   ├── agent.py                  # 智能体模型
│   │   └── session.py                # 会话模型
│   ├── 📁 schemas/                   # Pydantic模式
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础模式
│   │   ├── user.py                   # 用户相关模式
│   │   ├── course.py                 # 课程相关模式
│   │   ├── project.py                # 项目相关模式
│   │   ├── agent.py                  # 智能体模式
│   │   └── websocket.py              # WebSocket消息模式
│   ├── 📁 services/                  # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py           # 认证服务
│   │   ├── course_service.py         # 课程服务
│   │   ├── project_service.py        # 项目服务
│   │   ├── agent_orchestrator.py     # 智能体编排服务
│   │   └── websocket_manager.py      # WebSocket管理
│   ├── 📁 agents/                    # 智能体实现
│   │   ├── __init__.py
│   │   ├── base_agent.py             # 基础智能体类
│   │   ├── education_director.py     # 教育总监
│   │   ├── pbl_curriculum_designer.py # PBL课程设计师
│   │   ├── learning_experience_designer.py # 学习体验设计师
│   │   ├── creative_technologist.py  # 创意技术专家
│   │   ├── makerspace_manager.py     # 创客空间管理员
│   │   └── agent_factory.py          # 智能体工厂
│   ├── 📁 db/                        # 数据库相关
│   │   ├── __init__.py
│   │   ├── base.py                   # 数据库基础配置
│   │   ├── session.py                # 数据库会话
│   │   └── migrations/               # Alembic迁移文件
│   ├── 📁 utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py                 # 日志配置
│   │   ├── cache.py                  # 缓存工具
│   │   ├── vector_store.py           # 向量存储工具
│   │   └── file_handler.py           # 文件处理
│   ├── 📁 tasks/                     # 异步任务
│   │   ├── __init__.py
│   │   ├── agent_tasks.py            # 智能体任务
│   │   └── background_tasks.py       # 后台任务
│   └── main.py                       # 应用入口
├── 📁 tests/                         # 测试代码
│   ├── 📁 unit/                      # 单元测试
│   │   ├── test_agents/
│   │   ├── test_services/
│   │   └── test_models/
│   ├── 📁 integration/               # 集成测试
│   │   ├── test_api/
│   │   └── test_websocket/
│   ├── 📁 e2e/                       # 端到端测试
│   └── conftest.py                   # pytest配置
├── 📁 scripts/                       # 部署和运维脚本
│   ├── init_db.py                    # 数据库初始化
│   ├── migrate.py                    # 数据迁移
│   └── seed_data.py                  # 测试数据填充
├── 📁 docker/                        # Docker配置
│   ├── Dockerfile                    # 生产镜像
│   ├── Dockerfile.dev                # 开发镜像
│   └── nginx/                        # Nginx配置
├── 📁 k8s/                          # Kubernetes配置
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── ingress.yaml
├── 📁 monitoring/                    # 监控配置
│   ├── prometheus.yml
│   ├── grafana/
│   └── alerts.yml
├── 📁 docs/                         # 项目文档
│   ├── api.md                       # API文档
│   ├── deployment.md                # 部署文档
│   └── architecture.md              # 架构文档
├── .env.example                     # 环境变量示例
├── .gitignore                       # Git忽略文件
├── docker-compose.yml               # 生产环境compose
├── docker-compose.dev.yml           # 开发环境compose
├── pyproject.toml                   # Poetry配置
├── poetry.lock                      # 依赖锁定文件
├── alembic.ini                      # Alembic配置
├── requirements.txt                 # pip依赖（兼容）
└── README.md                        # 项目说明
```

## 目录说明

### 📁 app/ - 主应用代码

#### api/ - API路由层
- **v1/**: API版本控制，便于后续迭代升级
- **agents.py**: 智能体交互接口，支持同步和异步调用
- **websocket.py**: 实时通信接口，支持多用户协作

#### core/ - 核心基础设施
- **config.py**: 统一配置管理，支持多环境配置
- **dependencies.py**: FastAPI依赖注入，包括数据库、缓存等
- **middleware.py**: 请求处理中间件，包括CORS、日志等
- **security.py**: 安全认证，JWT令牌管理

#### models/ - 数据模型层
- 使用SQLAlchemy ORM定义数据库模型
- 支持关系映射和数据验证
- 包含审计字段（创建时间、更新时间等）

#### schemas/ - 数据模式层
- Pydantic模型定义API输入输出格式
- 自动生成OpenAPI文档
- 数据验证和序列化

#### services/ - 业务逻辑层
- **agent_orchestrator.py**: 智能体编排核心，支持复杂工作流
- **websocket_manager.py**: WebSocket连接管理和消息路由
- 业务逻辑与数据访问分离

#### agents/ - 智能体实现层
- **base_agent.py**: 智能体基类，定义统一接口
- 各专业智能体实现，继承自基类
- **agent_factory.py**: 工厂模式创建智能体实例

#### db/ - 数据库层
- SQLAlchemy配置和会话管理
- Alembic数据库版本控制
- 支持读写分离和连接池

#### utils/ - 工具函数层
- **logger.py**: 结构化日志配置
- **cache.py**: Redis缓存封装
- **vector_store.py**: ChromaDB向量操作

#### tasks/ - 异步任务层
- 基于Redis Streams的任务队列
- 支持任务重试和错误处理
- 智能体长时间运行任务异步化

### 📁 tests/ - 测试代码
- **unit/**: 单元测试，覆盖率要求80%+
- **integration/**: 集成测试，测试模块间交互
- **e2e/**: 端到端测试，模拟完整用户流程

### 📁 docker/ - 容器化配置
- 多阶段构建优化镜像大小
- 开发和生产环境分离
- Nginx反向代理配置

### 📁 k8s/ - Kubernetes部署
- 支持水平扩展
- 配置热更新
- 服务发现和负载均衡

### 📁 monitoring/ - 监控配置
- Prometheus指标采集
- Grafana可视化面板
- 告警规则配置

## 设计原则

### 1. 分层架构
- **表现层**: API路由和WebSocket
- **业务层**: 服务逻辑和智能体编排
- **数据层**: 模型定义和数据访问
- **基础设施层**: 配置、缓存、日志等

### 2. 依赖倒置
- 高层模块不依赖低层模块
- 通过接口和依赖注入解耦
- 便于单元测试和模块替换

### 3. 单一职责
- 每个模块职责明确
- 功能内聚，降低耦合
- 便于维护和扩展

### 4. 开闭原则
- 对扩展开放，对修改关闭
- 通过继承和组合实现功能扩展
- 插件化智能体架构

### 5. 接口隔离
- 客户端不依赖不需要的接口
- API版本控制
- 智能体接口标准化

## 扩展性考虑

### 水平扩展
- 无状态服务设计
- 会话信息存储在Redis
- 支持多实例部署

### 智能体扩展
- 基于接口的智能体规范
- 动态加载新智能体
- 支持外部智能体接入

### 存储扩展
- 数据库读写分离
- 缓存分层设计
- 向量数据库水平分片

### 功能扩展
- 插件化架构
- 微服务拆分准备
- API网关支持