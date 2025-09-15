#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发服务器启动脚本
使用 uv run scripts/dev.py 启动
"""

import os
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    """启动开发服务器"""
    try:
        # 确保在backend目录下运行
        backend_dir = Path(__file__).parent.parent

        print("🚀 启动PBL智能助手开发服务器...")
        print("📍 端口: http://localhost:8000")
        print("📖 API文档: http://localhost:8000/docs")
        print("🔧 使用uv虚拟环境")
        print("=" * 50)

        # 使用uv run启动开发服务器
        cmd = [
            "uv",
            "run",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
            "--reload-dir",
            "app",
        ]

        result = subprocess.run(cmd, cwd=backend_dir)
        return result.returncode

    except KeyboardInterrupt:
        print("\n👋 开发服务器已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
