#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
使用 uv run scripts/test.py 运行测试
"""

import os
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    """运行测试套件"""
    backend_dir = Path(__file__).parent.parent

    print("🧪 运行PBL智能助手测试套件...")
    print("🔧 使用uv虚拟环境")
    print("=" * 50)

    # 基础测试命令
    cmd = ["uv", "run", "pytest"]

    # 检查命令行参数
    if len(sys.argv) > 1:
        if "--cov" in sys.argv or "--coverage" in sys.argv:
            cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])

        if "--unit" in sys.argv:
            cmd.extend(["-m", "unit"])
        elif "--integration" in sys.argv:
            cmd.extend(["-m", "integration"])
        elif "--e2e" in sys.argv:
            cmd.extend(["-m", "e2e"])

        if "--verbose" in sys.argv or "-v" in sys.argv:
            cmd.append("-v")

        if "--parallel" in sys.argv:
            cmd.extend(["-n", "auto"])
    else:
        # 默认配置
        cmd.extend(["-v", "--tb=short"])

    try:
        result = subprocess.run(cmd, cwd=backend_dir)

        if result.returncode == 0:
            print("\n✅ 所有测试通过!")
        else:
            print(f"\n❌ 测试失败 (退出码: {result.returncode})")

        return result.returncode

    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
