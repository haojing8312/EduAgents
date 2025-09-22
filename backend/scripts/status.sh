#!/bin/bash

# EduAgents 后端服务状态检查脚本

set -e

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# 配置
PORT=48284
PID_FILE="$BACKEND_DIR/.server.pid"
HOST="localhost"

echo "📊 EduAgents 后端服务状态检查"
echo "================================"

# 检查端口占用
echo "🔍 检查端口 $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID_FROM_PORT=$(lsof -ti:$PORT)
    echo "✅ 端口 $PORT 正在被进程 $PID_FROM_PORT 使用"
else
    echo "❌ 端口 $PORT 未被占用"
    PID_FROM_PORT=""
fi

# 检查PID文件
echo ""
echo "📄 检查PID文件..."
if [ -f "$PID_FILE" ]; then
    PID_FROM_FILE=$(cat "$PID_FILE")
    echo "✅ PID文件存在: $PID_FROM_FILE"

    # 检查进程是否存在
    if ps -p "$PID_FROM_FILE" > /dev/null 2>&1; then
        echo "✅ 进程 $PID_FROM_FILE 正在运行"
    else
        echo "❌ 进程 $PID_FROM_FILE 不存在（僵尸PID文件）"
    fi
else
    echo "❌ PID文件不存在"
    PID_FROM_FILE=""
fi

# 检查服务健康状态
echo ""
echo "🏥 检查服务健康状态..."
if command -v curl >/dev/null 2>&1; then
    if curl -s -f "http://$HOST:$PORT/health" >/dev/null 2>&1; then
        echo "✅ 服务健康检查通过"

        # 获取服务信息
        SERVICE_INFO=$(curl -s "http://$HOST:$PORT/health" 2>/dev/null || echo "{}")
        echo "📋 服务信息: $SERVICE_INFO"
    else
        echo "❌ 服务健康检查失败"
    fi
else
    echo "⚠️ curl 未安装，跳过健康检查"
fi

# 汇总状态
echo ""
echo "📈 状态汇总:"
echo "------------"

if [ -n "$PID_FROM_PORT" ] && [ -n "$PID_FROM_FILE" ] && [ "$PID_FROM_PORT" = "$PID_FROM_FILE" ]; then
    echo "✅ 服务状态: 正常运行"
    echo "📋 进程ID: $PID_FROM_PORT"
    echo "🌐 服务地址: http://$HOST:$PORT"
    echo "📚 API文档: http://$HOST:$PORT/docs"
elif [ -n "$PID_FROM_PORT" ]; then
    echo "⚠️ 服务状态: 运行中但PID文件不匹配"
    echo "📋 实际进程ID: $PID_FROM_PORT"
    echo "💡 建议: 运行 ./scripts/stop.sh 然后 ./scripts/start.sh"
else
    echo "❌ 服务状态: 未运行"
    echo "💡 启动命令: ./scripts/start.sh"
fi

# 显示日志文件信息
echo ""
echo "📄 日志文件:"
LOG_FILE="$BACKEND_DIR/server.log"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "✅ 日志文件: $LOG_FILE ($LOG_SIZE)"
    echo "💡 查看命令: tail -f server.log"
else
    echo "❌ 日志文件不存在"
fi