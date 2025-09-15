#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码检查脚本
使用 uv run scripts/lint.py 进行代码质量检查
"""

import os
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    """运行代码质量检查"""
    backend_dir = Path(__file__).parent.parent

    print("🔍 PBL智能助手代码质量检查...")
    print("🔧 使用uv虚拟环境")
    print("=" * 50)

    checks = [
        {
            "name": "Flake8代码风格检查",
            "cmd": ["uv", "run", "flake8", "app", "tests"],
            "icon": "📝",
        },
        {"name": "MyPy类型检查", "cmd": ["uv", "run", "mypy", "app"], "icon": "🏷️"},
        {
            "name": "Bandit安全检查",
            "cmd": ["uv", "run", "bandit", "-r", "app", "-f", "txt"],
            "icon": "🔒",
        },
    ]

    results = []

    for check in checks:
        print(f"{check['icon']} {check['name']}...")
        try:
            result = subprocess.run(
                check["cmd"], cwd=backend_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"   ✅ 通过")
                results.append(True)
            else:
                print(f"   ❌ 发现问题")
                if result.stdout:
                    print("   📋 输出:")
                    for line in result.stdout.split("\n")[:10]:  # 只显示前10行
                        if line.strip():
                            print(f"      {line}")
                if result.stderr:
                    print("   🚨 错误:")
                    for line in result.stderr.split("\n")[:5]:  # 只显示前5行错误
                        if line.strip():
                            print(f"      {line}")
                results.append(False)

        except Exception as e:
            print(f"   ❌ 检查异常: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if all(results):
        print("✅ 所有代码质量检查通过!")
        return 0
    else:
        print(f"❌ 代码质量检查: {passed}/{total} 通过")
        return 1


if __name__ == "__main__":
    sys.exit(main())
