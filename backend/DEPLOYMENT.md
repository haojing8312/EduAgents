# PBL课程生成和导出系统 - 部署指南

## 系统概览

本系统是一个完整的PBL（项目式学习）课程生成和导出系统，实现了从AI智能体协作到最终教学资料生成的完整闭环。

### 核心功能

1. **完整的PBL课程数据模型** - 支持完整的项目式学习课程结构
2. **多格式文档生成** - 自动生成PDF、Word、PowerPoint、JSON等格式的教学资料
3. **智能课程模板系统** - 预置多种学科和学段的课程模板
4. **课程质量检查机制** - 自动检测课程设计的完整性和教学有效性
5. **协作分享功能** - 支持课程分享、协作编辑和版本管理
6. **多格式导出API** - RESTful API接口支持各种导出需求

## 技术架构

### 后端技术栈
- **框架**: FastAPI (高性能异步API框架)
- **数据库**: PostgreSQL + Redis
- **文档生成**: WeasyPrint, python-docx, python-pptx
- **模板引擎**: Jinja2
- **认证**: JWT + OAuth2
- **缓存**: Redis
- **任务队列**: Celery
- **容器化**: Docker

### 数据模型设计
- `Course` - 课程主表，包含完整的PBL课程信息
- `Lesson` - 课时表，详细的课时安排
- `Assessment` - 评估表，多样化的评估方式
- `Resource` - 资源表，课程相关资源
- `CourseTemplate` - 模板表，预置课程模板
- `CourseExport` - 导出记录表
- `CourseReview` - 课程评价表
- 协作关联表，支持多人协作

## 环境要求

### 系统要求
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 16+ (前端)

### 依赖安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y \
    postgresql postgresql-contrib \
    redis-server \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libxml2-dev \
    libxslt1-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info
```

### 字体支持（中文PDF生成）
```bash
# 安装中文字体
sudo apt-get install -y fonts-noto-cjk

# 或者手动安装字体文件到系统字体目录
sudo mkdir -p /usr/share/fonts/truetype/custom
sudo cp fonts/*.ttf /usr/share/fonts/truetype/custom/
sudo fc-cache -fv
```

## 配置设置

### 环境变量配置 (.env)
```bash
# 基础配置
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-super-secret-key-here

# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=pbl_user
POSTGRES_PASSWORD=your-password
POSTGRES_DB=pbl_assistant

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 文档生成配置
STORAGE_LOCAL_PATH=./storage
TEMPLATE_PATH=./templates/documents

# API配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 文件上传限制
UPLOAD_MAX_SIZE=10485760  # 10MB
UPLOAD_ALLOWED_EXTENSIONS=.pdf,.docx,.jpg,.jpeg,.png

# 任务队列（Celery）
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 数据库初始化
```bash
# 创建数据库
sudo -u postgres createuser pbl_user
sudo -u postgres createdb pbl_assistant
sudo -u postgres psql -c "ALTER USER pbl_user WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pbl_assistant TO pbl_user;"

# 运行数据库迁移
alembic upgrade head

# 初始化基础数据（可选）
python scripts/init_data.py
```

## 启动服务

### 开发环境
```bash
# 启动Redis
redis-server

# 启动PostgreSQL
sudo systemctl start postgresql

# 启动后端API服务
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery任务队列（新终端）
celery -A app.core.celery worker --loglevel=info

# 启动Celery Beat调度器（可选，新终端）
celery -A app.core.celery beat --loglevel=info
```

### 生产环境
```bash
# 使用Docker Compose（推荐）
docker-compose -f docker-compose.prod.yml up -d

# 或者使用Gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

## Docker部署

### Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p storage/exports storage/uploads templates/documents

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: pbl_user
      POSTGRES_PASSWORD: your-password
      POSTGRES_DB: pbl_assistant
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_SERVER=db
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage
      - ./templates:/app/templates

  celery:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      - POSTGRES_SERVER=db
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage

volumes:
  postgres_data:
```

## API接口使用

### 认证
```bash
# 获取访问令牌
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password"}'
```

### 课程管理
```bash
# 创建课程
curl -X POST "http://localhost:8000/api/v1/courses" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "环保主题STEM项目", "subject": "science", ...}'

# 获取课程列表
curl "http://localhost:8000/api/v1/courses" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 文档导出
```bash
# 导出PDF教案
curl -X POST "http://localhost:8000/api/v1/courses/{course_id}/export" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"format": "pdf_teaching_plan", "options": {"include_objectives": true}}'

# 下载导出文件
curl "http://localhost:8000/api/v1/exports/{export_id}/download" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -o course_plan.pdf
```

### 模板使用
```bash
# 获取模板列表
curl "http://localhost:8000/api/v1/templates?category=stem" \
     -H "Authorization: Bearer YOUR_TOKEN"

# 从模板创建课程
curl -X POST "http://localhost:8000/api/v1/templates/{template_id}/create-course" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "我的STEM项目", "customizations": {...}}'
```

### 质量检查
```bash
# 检查课程质量
curl -X POST "http://localhost:8000/api/v1/quality/check/{course_id}" \
     -H "Authorization: Bearer YOUR_TOKEN"

# 获取质量报告
curl "http://localhost:8000/api/v1/quality/report/{course_id}" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 协作管理
```bash
# 添加协作者
curl -X POST "http://localhost:8000/api/v1/collaboration/{course_id}/collaborators" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user-uuid", "role": "editor"}'

# 分享课程
curl -X POST "http://localhost:8000/api/v1/collaboration/{course_id}/share" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"share_scope": "public", "share_settings": {...}}'
```

## 监控与维护

### 健康检查
```bash
# API健康状态
curl "http://localhost:8000/api/health"

# 详细健康检查
curl "http://localhost:8000/api/health/detailed"
```

### 日志监控
```bash
# 查看应用日志
docker-compose logs -f backend

# 查看Celery日志
docker-compose logs -f celery
```

### 性能监控
- Prometheus指标: `http://localhost:8000/metrics`
- API文档: `http://localhost:8000/docs`

## 故障排除

### 常见问题

1. **PDF生成失败**
   - 检查字体安装: `fc-list | grep -i noto`
   - 检查Cairo库: `python -c "import weasyprint; print('OK')"`

2. **数据库连接失败**
   - 检查PostgreSQL状态: `sudo systemctl status postgresql`
   - 验证连接: `psql -h localhost -U pbl_user -d pbl_assistant`

3. **Redis连接失败**
   - 检查Redis状态: `redis-cli ping`
   - 查看Redis日志: `sudo journalctl -u redis`

4. **文件上传失败**
   - 检查存储目录权限: `ls -la storage/`
   - 查看磁盘空间: `df -h`

### 性能优化

1. **数据库优化**
   ```sql
   -- 创建索引
   CREATE INDEX CONCURRENTLY idx_courses_search ON courses USING gin(to_tsvector('english', title || ' ' || description));
   
   -- 分析查询性能
   EXPLAIN ANALYZE SELECT * FROM courses WHERE subject = 'science';
   ```

2. **缓存策略**
   - 启用Redis缓存
   - 配置适当的TTL
   - 使用CDN缓存静态资源

3. **并发处理**
   - 调整Gunicorn worker数量
   - 配置数据库连接池
   - 优化Celery任务队列

## 安全注意事项

1. **认证安全**
   - 使用强密码策略
   - 定期更新JWT密钥
   - 启用HTTPS

2. **文件安全**
   - 限制上传文件类型
   - 扫描上传文件
   - 隔离文件存储

3. **API安全**
   - 启用速率限制
   - 验证输入数据
   - 记录审计日志

## 备份策略

### 数据库备份
```bash
# 创建备份
pg_dump -h localhost -U pbl_user pbl_assistant > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
psql -h localhost -U pbl_user pbl_assistant < backup_20240115_120000.sql
```

### 文件备份
```bash
# 备份存储目录
tar -czf storage_backup_$(date +%Y%m%d).tar.gz storage/

# 备份模板文件
tar -czf templates_backup_$(date +%Y%m%d).tar.gz templates/
```

## 扩展开发

### 添加新的文档格式
1. 在`document_generator.py`中创建新的生成器类
2. 实现`generate()`方法
3. 在`DocumentGeneratorService`中注册
4. 添加相应的模板文件

### 自定义模板
1. 在`template_service.py`中添加新模板
2. 创建模板数据结构
3. 实现自定义字段和验证

### 质量检查规则
1. 在`quality_checker.py`中添加新检查器
2. 实现检查逻辑
3. 定义问题严重程度和建议

---

以上是PBL课程生成和导出系统的完整部署指南。系统提供了从课程设计、质量检查到文档生成的完整解决方案，支持多种格式导出和协作功能，确保生成完整、高质量的教学资料包。