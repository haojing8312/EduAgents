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

# 函数：停止单个进程
stop_process() {
    local pid=$1
    echo "🔄 正在停止进程 $pid..."

    # 检查进程是否存在
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "⚠️ 进程 $pid 不存在，可能已经停止"
        return 0
    fi

    # 优雅停止进程
    kill "$pid" 2>/dev/null || true

    # 等待进程停止
    for i in {1..5}; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            echo "✅ 进程 $pid 已成功停止"
            return 0
        fi
        sleep 1
    done

    # 强制停止进程
    echo "⚠️ 进程 $pid 优雅停止失败，强制终止..."
    kill -9 "$pid" 2>/dev/null || true
    sleep 1

    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "✅ 进程 $pid 已强制停止"
        return 0
    else
        echo "❌ 无法停止进程 $pid"
        return 1
    fi
}

# 检查PID文件是否存在
if [ -f "$PID_FILE" ]; then
    # 从文件读取PID
    PID=$(cat "$PID_FILE")
    echo "📋 从PID文件读取进程ID: $PID"
    stop_process "$PID"
    rm -f "$PID_FILE"
fi

# 通过端口查找所有相关进程
PIDS=$(lsof -ti:$PORT 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "✅ 端口 $PORT 上没有运行的服务"
    exit 0
fi

echo "📋 通过端口找到进程:"
echo "$PIDS"

# 停止所有找到的进程
success=true
while IFS= read -r pid; do
    if [ -n "$pid" ]; then
        if ! stop_process "$pid"; then
            success=false
        fi
    fi
done <<< "$PIDS"

# 最终检查
remaining_pids=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$remaining_pids" ]; then
    echo "❌ 仍有进程占用端口 $PORT: $remaining_pids"
    exit 1
fi

if [ "$success" = true ]; then
    echo "🎉 所有服务已成功停止"
    exit 0
else
    echo "⚠️ 部分进程停止失败，但端口已释放"
    exit 0
fi