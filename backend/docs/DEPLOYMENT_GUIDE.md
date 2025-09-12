# PBL智能助手 - 部署指南

## 概述

本指南详细介绍如何在不同环境中部署PBL智能助手后端系统，包括本地开发、测试环境和生产环境的完整部署流程。

## 系统要求

### 最低配置
- **CPU**: 4核心 2.4GHz
- **内存**: 8GB RAM
- **存储**: 50GB可用空间
- **操作系统**: Ubuntu 20.04+, CentOS 8+, 或 Docker支持的系统

### 推荐配置（生产环境）
- **CPU**: 8核心 3.0GHz
- **内存**: 16GB+ RAM
- **存储**: 200GB+ SSD
- **网络**: 千兆网络连接
- **备份**: 自动备份策略

### 依赖服务版本要求
- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Python**: 3.11+ (如果本地安装)
- **PostgreSQL**: 15+
- **Redis**: 7.0+
- **Nginx**: 1.20+ (生产环境)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-org/pbl-intelligent-assistant.git
cd pbl-intelligent-assistant
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**必填配置项**:
```env
# 应用基础配置
SECRET_KEY=your-32-char-secret-key-here
POSTGRES_PASSWORD=strong_postgres_password
REDIS_PASSWORD=strong_redis_password

# AI服务配置
OPENAI_API_KEY=sk-your-openai-api-key
# 或者
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# 域名配置（生产环境）
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

### 3. 启动服务
```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose up -d
```

### 4. 初始化数据库
```bash
# 运行数据库迁移
docker-compose exec api alembic upgrade head

# 创建初始用户（可选）
docker-compose exec api python scripts/create_admin.py
```

### 5. 验证部署
```bash
# 检查服务状态
docker-compose ps

# 测试API
curl http://localhost:8000/health

# 查看日志
docker-compose logs -f api
```

## 开发环境部署

### 使用Docker Compose (推荐)

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 查看实时日志
docker-compose -f docker-compose.dev.yml logs -f api

# 重启服务（代码热重载已启用）
docker-compose -f docker-compose.dev.yml restart api
```

### 本地Python环境

```bash
# 安装Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安装依赖
poetry install

# 启动依赖服务
docker-compose -f docker-compose.dev.yml up -d postgres redis chromadb

# 设置环境变量
export DATABASE_URL="postgresql+asyncpg://pbl_user:password@localhost:5432/pbl_assistant"
export REDIS_URL="redis://:password@localhost:6379/0"

# 运行数据库迁移
poetry run alembic upgrade head

# 启动开发服务器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 生产环境部署

### 单服务器部署

#### 1. 系统准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以应用docker组权限
exit
```

#### 2. 部署应用
```bash
# 创建部署目录
sudo mkdir -p /opt/pbl-assistant
sudo chown $USER:$USER /opt/pbl-assistant
cd /opt/pbl-assistant

# 克隆项目
git clone https://github.com/your-org/pbl-intelligent-assistant.git .

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 创建必要的目录
mkdir -p logs uploads

# 构建并启动服务
docker-compose up -d

# 等待服务启动
sleep 30

# 初始化数据库
docker-compose exec api alembic upgrade head

# 创建管理员用户
docker-compose exec api python scripts/create_admin.py
```

#### 3. 配置SSL证书
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 4. 配置防火墙
```bash
# 启用UFW
sudo ufw enable

# 允许SSH
sudo ufw allow ssh

# 允许HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

### Kubernetes部署

#### 1. 准备Kubernetes清单
```bash
# 应用所有Kubernetes配置
kubectl apply -f k8s/
```

#### 2. 创建Secrets
```bash
# 创建数据库密码
kubectl create secret generic postgres-secret \
  --from-literal=password=your-postgres-password

# 创建AI服务密钥
kubectl create secret generic ai-secrets \
  --from-literal=openai-api-key=sk-your-key \
  --from-literal=anthropic-api-key=sk-ant-your-key

# 创建应用密钥
kubectl create secret generic app-secrets \
  --from-literal=secret-key=your-32-char-secret
```

#### 3. 部署应用
```bash
# 部署数据库
kubectl apply -f k8s/postgres.yaml

# 部署Redis
kubectl apply -f k8s/redis.yaml

# 部署ChromaDB
kubectl apply -f k8s/chromadb.yaml

# 部署应用
kubectl apply -f k8s/deployment.yaml

# 创建服务
kubectl apply -f k8s/service.yaml

# 配置Ingress
kubectl apply -f k8s/ingress.yaml
```

#### 4. 验证部署
```bash
# 检查Pod状态
kubectl get pods

# 查看服务
kubectl get svc

# 查看日志
kubectl logs -f deployment/pbl-assistant-api
```

### 云平台部署

#### AWS ECS部署

1. **创建ECS集群**
```bash
aws ecs create-cluster --cluster-name pbl-assistant
```

2. **构建并推送镜像**
```bash
# 构建镜像
docker build -t pbl-assistant .

# 标记镜像
docker tag pbl-assistant:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/pbl-assistant:latest

# 推送到ECR
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/pbl-assistant:latest
```

3. **创建任务定义和服务**
```json
{
  "family": "pbl-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/pbl-assistant:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    }
  ]
}
```

## 配置管理

### 环境变量配置

#### 开发环境
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 测试环境
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_HOSTS=staging.your-domain.com
```

#### 生产环境
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=ERROR
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

### 数据库配置

#### 连接池配置
```env
# PostgreSQL连接池
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=0
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600
```

#### Redis配置
```env
# Redis连接
REDIS_POOL_SIZE=10
REDIS_HEALTH_CHECK_INTERVAL=30
```

### 安全配置

#### SSL/TLS设置
```nginx
# Nginx SSL配置
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
```

#### API安全
```env
# JWT设置
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 速率限制
RATE_LIMIT_CALLS=200
RATE_LIMIT_PERIOD=60
```

## 监控和日志

### 应用监控

#### Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pbl-assistant'
    static_configs:
      - targets: ['api:8000']
```

#### Grafana仪表板
```json
{
  "dashboard": {
    "title": "PBL Assistant Metrics",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])"
          }
        ]
      }
    ]
  }
}
```

### 日志管理

#### 日志配置
```python
# app/utils/logger.py
import structlog

logger = structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ]
)
```

#### 日志轮转
```bash
# /etc/logrotate.d/pbl-assistant
/opt/pbl-assistant/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose exec api kill -USR1 1
    endscript
}
```

## 备份和恢复

### 数据库备份

#### 自动备份脚本
```bash
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="pbl_assistant_backup_${TIMESTAMP}.sql"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
docker-compose exec -T postgres pg_dump -U pbl_user pbl_assistant > "$BACKUP_DIR/$BACKUP_FILE"

# 压缩备份文件
gzip "$BACKUP_DIR/$BACKUP_FILE"

# 清理7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE.gz"
```

#### 设置定时备份
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/pbl-assistant/scripts/backup_db.sh
```

### 数据恢复

```bash
#!/bin/bash
# scripts/restore_db.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file.sql.gz>"
    exit 1
fi

# 解压备份文件
gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U pbl_user -d pbl_assistant

echo "数据库恢复完成"
```

## 性能优化

### 数据库优化

#### PostgreSQL调优
```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

#### 索引优化
```sql
-- 创建常用查询索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_agents_status ON agents(status) WHERE status = 'active';
```

### 应用优化

#### 缓存策略
```python
# 多层缓存配置
CACHE_STRATEGIES = {
    'user_sessions': {'ttl': 1800, 'backend': 'redis'},
    'agent_responses': {'ttl': 3600, 'backend': 'memory'},
    'course_data': {'ttl': 7200, 'backend': 'redis'}
}
```

#### 连接池配置
```python
# 数据库连接池
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 0,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U pbl_user

# 查看数据库日志
docker-compose logs postgres

# 重置数据库密码
docker-compose exec postgres psql -U postgres -c "ALTER USER pbl_user PASSWORD 'new_password';"
```

#### 2. Redis连接问题
```bash
# 测试Redis连接
docker-compose exec redis redis-cli ping

# 查看Redis配置
docker-compose exec redis redis-cli config get "*"

# 清空Redis缓存
docker-compose exec redis redis-cli flushall
```

#### 3. 智能体响应超时
```bash
# 检查API服务状态
curl -f http://localhost:8000/health

# 查看服务日志
docker-compose logs api | grep -i "timeout\|error"

# 重启API服务
docker-compose restart api
```

#### 4. 内存使用过高
```bash
# 监控容器资源使用
docker stats

# 查看内存使用详情
docker-compose exec api python -c "
import psutil
print(f'内存使用: {psutil.virtual_memory().percent}%')
print(f'可用内存: {psutil.virtual_memory().available / 1024**3:.2f} GB')
"

# 清理无用的Docker镜像
docker system prune -a
```

### 日志分析

#### 查看关键错误
```bash
# API错误日志
docker-compose logs api | grep -i "error\|exception"

# 数据库错误
docker-compose logs postgres | grep -i "error\|fatal"

# Redis错误
docker-compose logs redis | grep -i "error\|warning"
```

#### 性能分析
```bash
# API响应时间分析
docker-compose logs api | grep "response_time" | tail -100

# 数据库查询分析
docker-compose exec postgres psql -U pbl_user -d pbl_assistant -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
"
```

## 升级指南

### 滚动升级

```bash
#!/bin/bash
# scripts/rolling_upgrade.sh

echo "开始滚动升级..."

# 拉取最新镜像
docker-compose pull

# 依次重启服务
for service in worker api nginx; do
    echo "重启服务: $service"
    docker-compose up -d --no-deps $service
    sleep 30
    
    # 健康检查
    if ! curl -f http://localhost:8000/health; then
        echo "升级失败，回滚服务: $service"
        docker-compose restart $service
        exit 1
    fi
done

echo "升级完成"
```

### 数据库迁移

```bash
# 创建数据库备份
./scripts/backup_db.sh

# 运行迁移
docker-compose exec api alembic upgrade head

# 验证迁移
docker-compose exec api python scripts/verify_migration.py
```

## 安全加固

### 系统安全

#### 防火墙配置
```bash
# 配置iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT  
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

#### 系统更新
```bash
# 自动安全更新
echo 'Unattended-Upgrade::Automatic-Reboot "true";' >> /etc/apt/apt.conf.d/50unattended-upgrades
```

### 应用安全

#### API安全头
```nginx
# nginx安全配置
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

#### 密钥轮换
```bash
#!/bin/bash
# scripts/rotate_secrets.sh

# 生成新的SECRET_KEY
NEW_SECRET=$(openssl rand -hex 32)

# 更新环境变量
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET/" .env

# 重启服务
docker-compose restart api
```

这个完整的部署指南涵盖了从开发到生产的所有部署场景，包括监控、备份、故障排除等运维要点，确保系统的稳定可靠运行。