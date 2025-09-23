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
# 1. 启动后端服务 (默认48284端口)
cd backend
uv sync                              # 安装依赖
./scripts/start.sh                   # 启动后端服务

# 2. 启动前端应用 (默认48285端口)
cd frontend
npm install                          # 安装依赖
npm run dev                          # 启动开发服务器
```

### 后端服务管理
```bash
cd backend

# 🚀 推荐：使用Shell脚本管理服务 (默认48284端口)
./scripts/start.sh                   # 启动服务（后台运行）
./scripts/stop.sh                    # 停止服务
./scripts/restart.sh                 # 重启服务
./scripts/status.sh                  # 检查服务状态

# 📄 查看服务日志
tail -f server.log                   # 实时查看日志

# 🧪 测试和开发
uv run python scripts/test_enhanced.py        # 运行完整测试套件
uv run python scripts/test_enhanced.py --business  # 业务穿越测试

# 🛠️ 直接启动方式（前台运行，用于调试）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 48284
```

### 前端开发工作流
```bash
cd frontend
npm install                          # 安装依赖
npm run dev                          # 开发服务器 (48285端口)
npm run build                        # 构建生产版本
npm run lint                         # 代码检查
```

### 测试命令
```bash
# 后端增强测试套件
cd backend
uv run python scripts/test_enhanced.py              # 运行所有测试
uv run python scripts/test_enhanced.py --unit       # 单元测试
uv run python scripts/test_enhanced.py --integration # 集成测试
uv run python scripts/test_enhanced.py --business   # 业务穿越测试
uv run python scripts/test_enhanced.py --coverage   # 测试覆盖率

# 前端测试
cd frontend && npm run test
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

## 🛡️ 严格质量控制要求

### 🚨 绝对禁止的兜底策略

**核心原则：绝不为了系统稳定性而降低产品质量**

#### 禁止行为
❌ **低质量占位符内容**
```python
# 禁止这样的代码
result[key] = f"[生成失败] {key}"
result["content"] = "内容生成中..."
result["description"] = "由于技术问题，此内容将稍后完善"
```

❌ **误导性的部分结果**
```python
# 禁止返回可能误导用户的不完整方案
fallback_content = {
    "status": "需要完善",
    "content": "基础模板",
    "note": "请手动完善此部分"
}
```

❌ **质量降级的自动回退**
```python
# 禁止为了避免异常而降低输出质量
except Exception:
    return generate_simple_fallback()  # 这是错误的
```

#### 正确做法
✅ **明确失败处理**
```python
# 实现3次重试机制
max_retries = 3
for retry_count in range(max_retries):
    try:
        result = generate_high_quality_content()
        return result
    except Exception as e:
        if retry_count == max_retries - 1:
            # 3次重试都失败，明确抛出错误
            raise Exception(f"内容生成失败，经过{max_retries}次重试仍无法生成合格内容: {e}")
```

✅ **严格的质量门控**
```python
# 检查生成内容的质量
if not validate_content_quality(result):
    raise Exception("生成的内容不符合质量标准，拒绝返回低质量结果")

# 检查必需组件完整性
if successful_components < minimum_required_components:
    raise Exception("关键组件生成失败，无法提供完整的解决方案")
```

### 🎯 质量控制原则

1. **失败透明化** - 开发阶段必须能快速暴露问题
2. **用户诚实性** - 绝不提供可能误导用户的低质量内容
3. **系统完整性** - 部分失败时明确标注，不影响整体判断
4. **调试友好性** - 保留完整的错误信息和协作追踪数据

### 🔧 推荐的错误处理模式

```python
async def generate_course_material(requirements):
    """生成课程素材 - 严格质量控制版本"""

    # 第一步：参数验证
    if not validate_requirements(requirements):
        raise ValueError("输入参数不符合要求，无法生成高质量内容")

    # 第二步：内容生成（带重试）
    max_retries = 3
    for attempt in range(max_retries):
        try:
            content = await ai_generate_content(requirements)

            # 第三步：质量验证
            if validate_content_quality(content):
                return content
            else:
                logger.warning(f"第{attempt+1}次生成的内容质量不达标")

        except Exception as e:
            logger.warning(f"第{attempt+1}次生成失败: {e}")

    # 第四步：所有尝试都失败，明确抛出错误
    raise Exception("经过3次尝试仍无法生成符合质量标准的课程素材")
```

### 📊 质量标准检查清单

在实现任何容错机制时，必须确认：

- [ ] 是否会向用户返回低质量或不完整的内容？
- [ ] 是否会掩盖真实的技术问题？
- [ ] 是否为开发调试提供了充分的错误信息？
- [ ] 失败时用户是否能得到诚实透明的反馈？
- [ ] 重试机制是否有合理的上限（建议3次）？

**记住：在开发阶段，明确的失败比隐蔽的低质量更有价值！**

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
- **🚨 绝对禁止：实现任何会降低产品质量的兜底策略**
- **🚨 绝对禁止：返回占位符、"生成中"等低质量内容给用户**
- **🚨 绝对禁止：为了系统稳定性而掩盖真实的技术问题**

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
- **🛡️ 内容质量标准：绝不返回低质量或占位符内容**
- **🛡️ 失败处理标准：最多3次重试，失败时明确抛出错误**
- **🛡️ 调试友好性：保留完整错误信息，便于问题定位**

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
cd backend
tail -f server.log                   # 实时查看服务日志
./scripts/status.sh                  # 检查服务运行状态

# 查看前端开发日志
cd frontend && npm run dev

# 数据库连接测试
cd backend && python -c "from app.core.database import engine; print('DB连接成功')"

# 服务健康检查
curl http://localhost:48284/health   # 检查后端API健康状态
curl http://localhost:48284/docs     # 访问API文档
```

---

## 🌟 项目愿景

**让创新教育不再是少数人的特权，而是每个孩子都能享受的权利！**

我们正在开发的不仅仅是一个产品，而是教育公平的推动器。通过先进的多智能体技术，我们将让每一位教育工作者都能拥有设计优质PBL课程的能力，推动创新教育的普及化。

*更新时间：2025年9月20日*
*项目代号：EduAgents*
*使命等级：教育公平推动者* 🌟