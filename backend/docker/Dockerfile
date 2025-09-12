# 多阶段构建Dockerfile - 生产环境优化
FROM python:3.11-slim as builder

# 设置构建参数
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# 添加标签
LABEL \
    maintainer="PBL Assistant Team" \
    description="PBL智能助手后端API服务" \
    version="${VERSION}" \
    build_date="${BUILD_DATE}" \
    vcs_ref="${VCS_REF}"

# 设置工作目录
WORKDIR /build

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖管理工具
RUN pip install --no-cache-dir poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 配置Poetry
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# 安装依赖
RUN poetry install --only=main --no-dev

# 生产环境镜像
FROM python:3.11-slim as production

# 创建非root用户
RUN groupadd -r pbl && useradd -r -g pbl pbl

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 从builder阶段复制Python环境
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY app/ ./app/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/

# 创建必要的目录
RUN mkdir -p logs uploads temp \
    && chown -R pbl:pbl /app

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# 切换到非root用户
USER pbl

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# 开发环境镜像
FROM python:3.11-slim as development

# 安装开发依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install --no-cache-dir poetry

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 配置Poetry并安装所有依赖（包括开发依赖）
RUN poetry config virtualenvs.create false \
    && poetry install

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=development \
    DEBUG=true

# 暴露端口和调试端口
EXPOSE 8000 5678

# 开发环境启动命令（支持热重载）
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]