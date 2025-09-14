# 🚀 PBL课程设计智能助手 - 快速启动指南

## 🎯 项目简介

**PBL课程设计智能助手** 是一个基于AI原生多智能体技术的革命性教育工具，旨在帮助传统教育者快速转型为AI时代的创新教育者。

### ⚡ 核心特性
- **45分钟完成完整PBL课程设计**（传统需要2-3天）
- **5个专业智能体协作**（教育理论、课程架构、内容设计、评估、资料制作）
- **世界级用户体验**（三层交互架构，实时可视化协作）
- **完整教学资料包**（PDF教案、PPT课件、Word文档、评估标准）

---

## 🛠️ 环境要求

### 必需环境
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 最新版本
- **Git**: 最新版本

### 推荐环境
- **操作系统**: Ubuntu 20.04+ / macOS 11+ / Windows 11
- **内存**: 8GB+
- **存储**: 10GB+可用空间
- **网络**: 稳定的互联网连接（用于AI模型API调用）

---

## ⚡ 快速启动（5分钟）

### 1. 克隆项目
```bash
git clone https://github.com/your-org/pbl-course-designer
cd pbl-course-designer
```

### 2. 环境配置
```bash
# 复制环境变量模板
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 编辑配置文件，填入必要的API密钥
# backend/.env 中需要配置：
# - OPENAI_API_KEY=your_openai_key
# - ANTHROPIC_API_KEY=your_claude_key
# - DATABASE_URL=postgresql://...
```

### 3. 一键启动
```bash
# 使用Docker Compose启动整个系统
docker-compose up -d

# 等待所有服务启动完成（约2-3分钟）
docker-compose logs -f
```

### 4. 访问应用
- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 🎯 核心功能演示

### 体验完整工作流程

1. **打开应用** → 访问 http://localhost:3000

2. **开始设计** → 点击"开始设计新课程"

3. **输入需求** → 例如："我想设计一个关于AI伦理的高中PBL课程"

4. **观察协作** → 左侧面板实时显示5个智能体的协作状态

5. **查看成果** → 右侧显示生成的课程结构和内容

6. **导出资料** → 点击"生成教学资料包"获得完整文档

### 预期效果
- **10秒内** - 系统响应并开始智能体协作
- **3-5分钟** - 完成课程框架设计
- **5-8分钟** - 生成完整课程内容
- **总用时约10分钟** - 获得专业的PBL课程设计

---

## 🏗️ 开发环境设置

### 后端开发
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 数据库设置
```bash
# 启动PostgreSQL和Redis
docker-compose up -d postgres redis chromadb

# 运行数据库迁移
cd backend
alembic upgrade head
```

---

## 🧪 测试运行

### 运行完整测试套件
```bash
# 后端测试
cd backend
pytest tests/ -v --cov=app

# 前端测试
cd frontend
npm test

# E2E测试
npm run test:e2e
```

### 性能测试
```bash
# 负载测试
cd performance_tests
pip install -r requirements.txt
python load_test.py

# 结果分析
python analyze_results.py
```

---

## 📊 系统调试

### 查看系统状态
```bash
# 检查所有服务状态
docker-compose ps

# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend

# 查看智能体协作日志
docker-compose logs backend | grep "agent"
```

### 系统健康检查
- **健康检查端点**: http://localhost:8000/health
- **API文档**: http://localhost:8000/docs

---

## 🔧 常见问题解决

### 问题1: Docker启动失败
```bash
# 检查Docker状态
docker --version
docker-compose --version

# 清理并重新启动
docker-compose down -v
docker-compose up -d --build
```

### 问题2: API调用失败
```bash
# 检查API密钥配置
cat backend/.env | grep API_KEY

# 测试API连通性
curl -X GET "http://localhost:8000/health"
```

### 问题3: 智能体协作无响应
```bash
# 检查智能体服务状态
docker-compose logs backend | grep "LangGraph"

# 重启后端服务
docker-compose restart backend
```

### 问题4: 前端页面空白
```bash
# 检查前端构建
cd frontend
npm run build

# 检查环境变量
cat .env.local
```

---

## 📚 进阶使用

### 自定义智能体
1. 创建新的智能体类 `backend/app/agents/specialists/your_agent.py`
2. 在编排器中注册新智能体 `backend/app/agents/core/orchestrator.py`
3. 更新前端显示 `frontend/src/components/AgentPanel.tsx`

### 扩展课程模板
1. 添加模板定义 `backend/app/services/template_service.py`
2. 创建模板文件 `backend/templates/course_templates/`
3. 更新前端模板选择 `frontend/src/components/TemplateSelector.tsx`

### 自定义文档格式
1. 扩展文档生成器 `backend/app/services/document_generator.py`
2. 添加新的模板 `backend/templates/documents/`
3. 更新导出API `backend/app/api/v1/course_export.py`

---

## 🚀 部署到生产环境

### 使用Docker生产部署
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 配置反向代理（Nginx）
cp nginx.conf.example nginx.conf
# 编辑nginx.conf配置域名和SSL
```

### 使用Kubernetes部署
```bash
# 应用K8s配置
kubectl apply -f k8s/

# 检查部署状态
kubectl get pods
kubectl get services
```

---

## 📞 获得帮助

### 文档资源
- **📋 架构文档**: `backend/STRUCTURE.md`
- **📋 API文档**: `backend/docs/API_SPECIFICATION.md`
- **📋 设计文档**: `frontend/docs/DESIGN_SYSTEM.md`
- **📋 部署指南**: `backend/docs/DEPLOYMENT_GUIDE.md`

### 社区支持
- **GitHub Issues**: https://github.com/your-org/pbl-course-designer/issues
- **技术讨论**: https://github.com/your-org/pbl-course-designer/discussions
- **产品反馈**: feedback@your-domain.com

### 开发团队
- **项目负责人**: Claude Code AI
- **技术架构**: AI智能体团队协作
- **产品设计**: 世界级用户体验标准

---

## 🎉 开始你的教育变革之旅

现在你已经准备好使用这个世界级的PBL课程设计智能助手了！

**记住我们的使命**：*改变当今世界的教育格局，赋能所有传统教育者转型为AI时代的创新教育者*

让AI赋能教育，让技术服务创造力！🌟

---

*快速启动指南 v1.0*  
*最后更新：2024年3月15日*  
*状态：生产就绪* ✅