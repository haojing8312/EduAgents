#!/bin/bash

# EduAgents 后端服务启动脚本
# 默认端口: 48284

set -e

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# 服务配置
HOST="0.0.0.0"
PORT=48284
PID_FILE="$BACKEND_DIR/.server.pid"

echo "🚀 启动 EduAgents 后端服务..."
echo "📂 项目目录: $BACKEND_DIR"
echo "📍 服务地址: http://$HOST:$PORT"
echo "📚 API文档: http://$HOST:$PORT/docs"

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ 端口 $PORT 已被占用"
    echo "💡 请先运行 ./scripts/stop.sh 停止现有服务"
    exit 1
fi

# 进入项目目录
cd "$BACKEND_DIR"

# 检查依赖
echo "🔍 检查项目依赖..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，请先安装 uv"
    echo "💡 安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 同步依赖
echo "📦 同步项目依赖..."
uv sync

# 启动服务
echo "🔄 启动开发服务器 (热重载模式)..."
echo "💻 执行命令: uv run uvicorn app.main:app --reload --host $HOST --port $PORT"

# 后台启动服务并保存PID
nohup uv run uvicorn app.main:app --reload --host "$HOST" --port "$PORT" > server.log 2>&1 &
SERVER_PID=$!

# 保存PID到文件
echo $SERVER_PID > "$PID_FILE"

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务是否成功启动
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo "📋 进程ID: $SERVER_PID"
    echo "📄 日志文件: $BACKEND_DIR/server.log"
    echo ""
    echo "🛠️ 管理命令:"
    echo "  查看日志: tail -f server.log"
    echo "  停止服务: ./scripts/stop.sh"
    echo "  重启服务: ./scripts/restart.sh"
else
    echo "❌ 服务启动失败"
    echo "📄 请查看日志: $BACKEND_DIR/server.log"
    rm -f "$PID_FILE"
    exit 1
fi