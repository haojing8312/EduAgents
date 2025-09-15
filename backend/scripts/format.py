#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码格式化脚本
使用 uv run scripts/format.py 格式化代码
"""

import os
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"


def main():
    """格式化代码"""
    backend_dir = Path(__file__).parent.parent

    print("格式化PBL智能助手代码...")
    print("使用uv虚拟环境")
    print("=" * 50)

    commands = [
        {
            "name": "Black格式化",
            "cmd": ["uv", "run", "black", "app", "tests", "scripts"],
            "icon": "[BLACK]",
        },
        {
            "name": "isort导入排序",
            "cmd": ["uv", "run", "isort", "app", "tests", "scripts"],
            "icon": "[ISORT]",
        },
    ]

    overall_success = True

    for task in commands:
        print(f"{task['icon']} {task['name']}...")
        try:
            result = subprocess.run(
                task["cmd"], cwd=backend_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"   [OK] {task['name']} 完成")
                if result.stdout:
                    print(f"   输出: {result.stdout.strip()}")
            else:
                print(f"   [ERROR] {task['name']} 失败")
                if result.stderr:
                    print(f"   错误: {result.stderr.strip()}")
                overall_success = False

        except Exception as e:
            print(f"   [ERROR] {task['name']} 异常: {e}")
            overall_success = False

    print("\n" + "=" * 50)
    if overall_success:
        print("[SUCCESS] 代码格式化完成!")
        return 0
    else:
        print("[ERROR] 部分格式化任务失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
