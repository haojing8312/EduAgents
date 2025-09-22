#!/bin/bash

# EduAgents 后端服务重启脚本

set -e

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 重启 EduAgents 后端服务..."

# 停止服务
echo "1️⃣ 停止现有服务..."
"$SCRIPT_DIR/stop.sh"

# 等待一下确保端口释放
echo "⏳ 等待端口释放..."
sleep 2

# 启动服务
echo "2️⃣ 启动新服务..."
"$SCRIPT_DIR/start.sh"

echo "✅ 服务重启完成！"