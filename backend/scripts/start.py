#!/usr/bin/env python3
"""
EduAgents 后端启动脚本
提供便捷的服务启动和管理功能
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """检查依赖"""
    logger = logging.getLogger(__name__)

    try:
        import uvicorn
        import fastapi
        logger.info("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖: {e}")
        logger.info("请运行: uv sync")
        return False

def start_backend(host="0.0.0.0", port=8000, reload=True, workers=1):
    """启动后端服务"""
    logger = logging.getLogger(__name__)

    logger.info("🚀 启动 EduAgents 后端服务...")
    logger.info(f"📍 地址: http://{host}:{port}")
    logger.info(f"📚 文档: http://{host}:{port}/docs")

    # 构建启动命令
    cmd = [
        "uv", "run", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port)
    ]

    if reload:
        cmd.append("--reload")
        logger.info("🔄 开启热重载模式")

    if workers > 1:
        cmd.extend(["--workers", str(workers)])
        logger.info(f"👥 使用 {workers} 个工作进程")

    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_ROOT)

    try:
        # 启动服务
        logger.info(f"💻 执行命令: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=BACKEND_ROOT, env=env, check=True)
    except KeyboardInterrupt:
        logger.info("🛑 服务已停止")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 服务启动失败: {e}")
        return False

    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="EduAgents 后端启动工具")

    # 基础参数
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="端口号 (默认: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数 (默认: 1)")

    # 环境参数
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="运行环境")
    parser.add_argument("--check", action="store_true", help="只检查依赖，不启动服务")

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🌟 EduAgents 后端启动工具")
    logger.info(f"📂 项目目录: {PROJECT_ROOT}")

    # 检查依赖
    if not check_dependencies():
        return 1

    if args.check:
        logger.info("✅ 依赖检查完成")
        return 0

    # 根据环境调整参数
    if args.env == "prod":
        reload = False
        workers = max(2, args.workers)
        logger.info("🏭 生产环境模式")
    else:
        reload = not args.no_reload
        workers = args.workers
        logger.info("🛠️ 开发环境模式")

    # 启动服务
    success = start_backend(
        host=args.host,
        port=args.port,
        reload=reload,
        workers=workers
    )

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())