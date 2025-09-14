# 多阶段构建的后端Dockerfile
FROM python:3.11-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry==$POETRY_VERSION

# 配置Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock ./

# 安装依赖（仅生产依赖）
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# 开发阶段
FROM base as development

# 安装开发依赖
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 8000

# 开发环境启动命令
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 生产阶段
FROM base as production

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制源代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 生产环境启动命令
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# 测试阶段
FROM development as test

# 安装测试依赖
RUN poetry install --with test

# 运行测试
RUN poetry run pytest tests/ --cov=app --cov-report=xml --cov-report=html

# 优化的生产镜像
FROM python:3.11-slim as optimized-production

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv

# 从base阶段复制虚拟环境
COPY --from=base /app/.venv /opt/venv

# 创建应用用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建应用目录
WORKDIR /app

# 复制应用代码
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser templates/ ./templates/

# 创建日志目录
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# 切换到应用用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]