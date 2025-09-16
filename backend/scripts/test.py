#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
支持多种测试模式：单元测试、集成测试、业务流程测试等
使用 uv run scripts/test.py [选项] 运行测试
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"


def run_pytest_tests(test_path: str = "", coverage: bool = False, parallel: bool = False,
                    verbose: bool = False, markers: str = "") -> int:
    """运行pytest测试"""
    backend_dir = Path(__file__).parent.parent

    cmd = ["uv", "run", "pytest"]

    # 添加测试路径
    if test_path:
        cmd.append(test_path)

    # 添加标记过滤
    if markers:
        cmd.extend(["-m", markers])

    # 添加覆盖率
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])

    # 并行执行
    if parallel:
        cmd.extend(["-n", "auto"])

    # 详细输出
    if verbose:
        cmd.append("-v")
    else:
        cmd.extend(["-v", "--tb=short"])

    try:
        result = subprocess.run(cmd, cwd=backend_dir)
        return result.returncode
    except Exception as e:
        print(f"❌ pytest运行失败: {e}")
        return 1


async def run_business_flow_test() -> int:
    """运行业务流程测试"""
    backend_dir = Path(__file__).parent.parent
    test_runner = backend_dir / "scripts" / "run_business_flow_test.py"

    if not test_runner.exists():
        print(f"❌ 找不到业务流程测试脚本: {test_runner}")
        return 1

    print("🎯 运行业务流程测试...")

    try:
        cmd = ["uv", "run", "python", str(test_runner)]

        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时输出日志
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())

        return_code = process.wait()
        return return_code

    except Exception as e:
        print(f"❌ 业务流程测试失败: {e}")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PBL智能助手测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  uv run scripts/test.py                    # 运行所有测试
  uv run scripts/test.py --unit            # 只运行单元测试
  uv run scripts/test.py --integration     # 只运行集成测试
  uv run scripts/test.py --business        # 只运行业务流程测试
  uv run scripts/test.py --cov             # 运行测试并生成覆盖率报告
  uv run scripts/test.py --parallel        # 并行运行测试
        """
    )

    # 测试类型选项
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--unit", action="store_true", help="只运行单元测试")
    test_group.add_argument("--integration", action="store_true", help="只运行集成测试")
    test_group.add_argument("--business", action="store_true", help="只运行业务流程测试")
    test_group.add_argument("--api", action="store_true", help="只运行API测试")

    # 其他选项
    parser.add_argument("--cov", "--coverage", action="store_true", help="生成测试覆盖率报告")
    parser.add_argument("--parallel", action="store_true", help="并行运行测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    print("🧪 PBL智能助手测试套件")
    print("🔧 使用uv虚拟环境")
    print("=" * 50)

    exit_code = 0

    try:
        if args.business:
            # 运行业务流程测试
            exit_code = asyncio.run(run_business_flow_test())

        elif args.unit:
            # 运行单元测试
            print("🧪 运行单元测试...")
            exit_code = run_pytest_tests(
                test_path="tests/unit/",
                coverage=args.cov,
                parallel=args.parallel,
                verbose=args.verbose,
                markers="unit"
            )

        elif args.integration:
            # 运行集成测试
            print("🔗 运行集成测试...")
            exit_code = run_pytest_tests(
                test_path="tests/integration/",
                coverage=args.cov,
                parallel=args.parallel,
                verbose=args.verbose,
                markers="integration"
            )

        elif args.api:
            # 运行API测试
            print("🌐 运行API测试...")
            exit_code = run_pytest_tests(
                test_path="tests/api/",
                coverage=args.cov,
                parallel=args.parallel,
                verbose=args.verbose,
                markers="api"
            )

        else:
            # 运行所有pytest测试
            print("🎭 运行所有pytest测试...")
            exit_code = run_pytest_tests(
                coverage=args.cov,
                parallel=args.parallel,
                verbose=args.verbose
            )

            # 如果pytest测试通过，运行业务流程测试
            if exit_code == 0:
                print("\n" + "="*50)
                print("✅ Pytest测试通过，开始业务流程测试")
                print("="*50)
                business_exit_code = asyncio.run(run_business_flow_test())

                if business_exit_code != 0:
                    exit_code = business_exit_code

        # 输出最终结果
        print("\n" + "="*50)
        if exit_code == 0:
            print("🎉 所有测试通过!")
        else:
            print(f"❌ 测试失败 (退出码: {exit_code})")
        print("="*50)

        return exit_code

    except KeyboardInterrupt:
        print("\n用户中断测试")
        return 130
    except Exception as e:
        print(f"❌ 测试运行异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
