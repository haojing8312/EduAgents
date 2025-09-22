#!/bin/bash

# EduAgents 后端服务停止脚本

set -e

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# 配置
PORT=48284
PID_FILE="$BACKEND_DIR/.server.pid"

echo "🛑 停止 EduAgents 后端服务..."

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️ 未找到PID文件，尝试通过端口查找进程..."

    # 通过端口查找进程
    PID=$(lsof -ti:$PORT 2>/dev/null || true)

    if [ -z "$PID" ]; then
        echo "✅ 端口 $PORT 上没有运行的服务"
        exit 0
    else
        echo "📋 找到进程: $PID"
    fi
else
    # 从文件读取PID
    PID=$(cat "$PID_FILE")
    echo "📋 从PID文件读取进程ID: $PID"
fi

# 检查进程是否存在
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️ 进程 $PID 不存在，可能已经停止"
    rm -f "$PID_FILE"
    exit 0
fi

# 优雅停止进程
echo "🔄 正在停止进程 $PID..."
kill "$PID" 2>/dev/null || true

# 等待进程停止
echo "⏳ 等待进程停止..."
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ 服务已成功停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 强制停止进程
echo "⚠️ 优雅停止失败，强制终止进程..."
kill -9 "$PID" 2>/dev/null || true

# 再次检查
sleep 1
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ 服务已强制停止"
    rm -f "$PID_FILE"
else
    echo "❌ 无法停止进程 $PID"
    exit 1
fi