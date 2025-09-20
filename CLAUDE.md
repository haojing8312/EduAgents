# 🚀 AI辅助PBL课程设计平台

## 📖 项目概述

这是一个致力于推动教育公平的AI辅助PBL（项目制学习）课程设计平台。我们运用先进的多智能体协作技术，让每一位教育工作者都能轻松设计出面向AI时代的优质课程，推动创新教育的普及化。

### 核心价值主张
- **技术参考**：Manus AI的多智能体架构
- **影响力对标**：Scratch和可汗学院的教育普及使命
- **使命目标**：让优质PBL课程设计能力人人可及

## 🏗️ 项目架构

### 技术栈
- **后端**: FastAPI + Python 3.11 + LangGraph多智能体框架
- **前端**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **AI模型**: Claude-3.5-Sonnet + GPT-4o双模型策略
- **数据存储**: PostgreSQL + Redis + ChromaDB三层数据架构
- **实时通信**: WebSocket + Server-Sent Events
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

### 项目结构
```
agents/                           # 项目根目录
├── backend/                      # FastAPI后端服务
│   ├── app/
│   │   ├── agents/              # 多智能体系统
│   │   │   ├── core/           # 核心框架（LangGraph编排器）
│   │   │   └── specialists/    # 5个专业智能体
│   │   ├── api/v1/             # RESTful API端点
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic模式
│   │   └── services/           # 业务逻辑服务
│   ├── tests/                  # 后端测试套件
│   └── alembic/                # 数据库迁移
├── frontend/                    # Next.js前端应用
│   ├── src/
│   │   ├── components/         # React组件
│   │   ├── pages/              # 页面路由
│   │   └── services/           # API客户端
│   └── tests/                  # 前端测试套件
├── .github/workflows/          # CI/CD流水线
└── CLAUDE.md                   # 项目文档（本文件）
```

## 🤖 多智能体系统

### 5个专业智能体
1. **教育理论专家** (`education_theorist`) - 教育理论和PBL方法论
2. **课程架构师** (`course_architect`) - 课程结构设计和学习路径
3. **内容设计师** (`content_designer`) - 教学内容和活动设计
4. **评估专家** (`assessment_expert`) - 评价体系和反馈机制
5. **素材创作者** (`material_creator`) - 教学资源和工具制作

### 协作模式
- **LangGraph编排**: 基于状态图的智能体协作流程
- **实时协作**: WebSocket实现的实时状态同步
- **三层交互**: 对话引导 → 可视化协作 → 成果编辑

## 💻 开发命令

### 环境要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 快速启动
```bash
# 启动完整系统（推荐）
docker-compose up -d

# 或者分别启动各服务
cd backend && uv run scripts/dev.py    # 使用uv (推荐)
cd frontend && npm run dev
```

### 开发工作流
```bash
# 后端开发 (使用uv - 推荐)
cd backend
uv sync                          # 安装依赖
uv run scripts/test.py           # 运行测试
uv run scripts/test.py --cov     # 测试覆盖率
uv run scripts/format.py         # 代码格式化
uv run scripts/lint.py           # 代码检查

# 前端开发
cd frontend  
npm install
npm run dev                      # 开发服务器
npm run test                     # 运行测试
npm run build                    # 构建生产版本

# 数据库迁移
cd backend
uv run alembic upgrade head      # 应用迁移
uv run alembic revision -m "描述" # 创建新迁移
```

### 测试命令
```bash
# 后端测试 (使用uv - 推荐)
cd backend && uv run scripts/test.py

# 前端测试
cd frontend && npm run test

# 运行所有测试
npm run test:all  # 如果配置了跨项目测试脚本
```

## 📋 代码规范

### Python代码规范
- 使用Black进行代码格式化
- 遵循PEP 8规范
- 100%类型注解（Type Hints）
- Pydantic模型用于数据验证
- 异步编程模式（async/await）

### TypeScript/React规范  
- 严格TypeScript配置
- 函数式组件 + Hooks
- Tailwind CSS用于样式
- ESLint + Prettier代码质量
- 组件单一职责原则

### 文件命名约定
- Python: `snake_case.py`
- TypeScript: `PascalCase.tsx` (组件), `camelCase.ts` (工具)
- 测试文件: `test_*.py`, `*.test.tsx`

## 🚫 开发限制

### MVP阶段暂不考虑
- 用户认证和授权系统
- 支付和订阅功能  
- 高可用性和容错处理
- 完整的安全审计
- 国际化和本地化

### 禁止操作
- 不要创建不必要的配置文件
- 不要过度工程化简单功能
- 不要偏离核心教育业务逻辑
- 不要使用过时的技术栈

## 🎯 开发重点

### 核心功能优先级
1. **智能体协作系统** - 5个专业智能体的无缝协作
2. **PBL课程生成** - 完整的项目制课程设计流程
3. **实时协作界面** - 可视化的多智能体协作体验
4. **课程导出系统** - 多格式课程包导出功能

### 质量标准
- API响应时间 < 2秒
- 前端首屏加载 < 3秒  
- 智能体协作成功率 > 95%
- 代码测试覆盖率 > 80%

## 📚 重要文档

- `README.md` - 项目介绍和基本使用说明
- `QUICK_START.md` - 5分钟快速部署指南
- `PROJECT_COMPLETION_REPORT.md` - 项目交付报告

## 🔧 故障排除

### 常见问题
1. **智能体响应慢** - 检查AI API配额和网络连接
2. **WebSocket连接失败** - 确认防火墙和代理设置
3. **数据库连接错误** - 验证PostgreSQL服务状态
4. **前端构建失败** - 清理node_modules重新安装

### 日志调试
```bash
# 查看后端日志
cd backend && python -m logging --level=DEBUG

# 查看前端开发日志
cd frontend && npm run dev

# 数据库连接测试
cd backend && python -c "from app.core.database import engine; print('DB连接成功')"
```

---

## 🌟 项目愿景

**让创新教育不再是少数人的特权，而是每个孩子都能享受的权利！**

我们正在开发的不仅仅是一个产品，而是教育公平的推动器。通过先进的多智能体技术，我们将让每一位教育工作者都能拥有设计优质PBL课程的能力，推动创新教育的普及化。

*更新时间：2025年9月20日*
*项目代号：EduAgents*
*使命等级：教育公平推动者* 🌟