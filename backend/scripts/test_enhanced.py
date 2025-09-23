#!/usr/bin/env python3
"""
增强版测试脚本
提供更好的测试体验和完整的测试套件管理
"""

import argparse
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT


class TestRunner:
    """增强版测试运行器"""

    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}

    def run_command(self, cmd: List[str], description: str, cwd: Optional[Path] = None, timeout: int = 300) -> bool:
        """运行命令并记录结果"""
        print(f"\n🔄 {description}")
        print(f"📂 工作目录: {cwd or BACKEND_ROOT}")
        print(f"💻 执行命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or BACKEND_ROOT,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                print(f"✅ {description} - 成功")
                self.test_results[description] = "成功"
                if result.stdout.strip():
                    print(f"📄 输出:\n{result.stdout}")
                return True
            else:
                print(f"❌ {description} - 失败 (退出码: {result.returncode})")
                self.test_results[description] = f"失败 (退出码: {result.returncode})"
                if result.stderr.strip():
                    print(f"🚨 错误:\n{result.stderr}")
                if result.stdout.strip():
                    print(f"📄 输出:\n{result.stdout}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - 超时")
            self.test_results[description] = "超时"
            return False
        except Exception as e:
            print(f"💥 {description} - 异常: {e}")
            self.test_results[description] = f"异常: {e}"
            return False

    def run_unit_tests(self, pattern: Optional[str] = None) -> bool:
        """运行单元测试"""
        cmd = ["uv", "run", "pytest", "tests/unit/", "-v"]
        if pattern:
            cmd.extend(["-k", pattern])

        return self.run_command(cmd, "单元测试")

    def run_integration_tests(self, pattern: Optional[str] = None) -> bool:
        """运行集成测试"""
        cmd = ["uv", "run", "pytest", "tests/integration/", "-v"]
        if pattern:
            cmd.extend(["-k", pattern])

        return self.run_command(cmd, "集成测试")

    def run_business_flow_test(self) -> bool:
        """运行业务穿越测试"""
        script_path = PROJECT_ROOT / "tests" / "integration" / "test_business_flow.py"
        cmd = ["uv", "run", "python", str(script_path)]
        return self.run_command(cmd, "业务穿越测试")

    def run_business_tracking_test(self) -> bool:
        """运行增强版业务测试 - 集成协作追踪验证"""
        script_path = PROJECT_ROOT / "scripts" / "test_business_with_tracking.py"
        cmd = ["uv", "run", "python", str(script_path)]
        return self.run_command(cmd, "业务追踪测试 - 完整协作验证", timeout=1200)  # 20分钟超时

    def run_api_tests(self) -> bool:
        """运行API测试"""
        cmd = ["uv", "run", "pytest", "tests/integration/test_simple_api.py", "-v"]
        return self.run_command(cmd, "API端点测试")

    def run_coverage_test(self) -> bool:
        """运行测试覆盖率分析"""
        cmd = [
            "uv", "run", "pytest",
            "tests/integration/test_simple_api.py",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-report=xml"
        ]
        return self.run_command(cmd, "测试覆盖率分析")

    def run_performance_tests(self) -> bool:
        """运行性能测试"""
        cmd = [
            "uv", "run", "pytest",
            "tests/integration/test_simple_api.py::TestPerformance",
            "-v"
        ]
        return self.run_command(cmd, "性能测试")

    def run_linting(self) -> bool:
        """运行代码检查"""
        commands = [
            (["uv", "run", "black", "--check", "app", "tests"], "代码格式检查"),
            (["uv", "run", "isort", "--check-only", "app", "tests"], "导入排序检查"),
            (["uv", "run", "flake8", "app", "tests"], "代码风格检查"),
        ]

        all_passed = True
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                all_passed = False

        return all_passed

    def run_type_checking(self) -> bool:
        """运行类型检查"""
        cmd = ["uv", "run", "mypy", "app"]
        return self.run_command(cmd, "类型检查")

    def run_security_scan(self) -> bool:
        """运行安全扫描"""
        cmd = ["uv", "run", "bandit", "-r", "app"]
        return self.run_command(cmd, "安全扫描")

    def cleanup_test_artifacts(self) -> bool:
        """清理测试产物"""
        artifacts = [
            BACKEND_ROOT / "test.db",
            BACKEND_ROOT / ".coverage",
            BACKEND_ROOT / "coverage.xml",
            BACKEND_ROOT / "htmlcov",
            BACKEND_ROOT / ".pytest_cache",
            BACKEND_ROOT / "__pycache__",
        ]

        for artifact in artifacts:
            if artifact.exists():
                if artifact.is_file():
                    artifact.unlink()
                    print(f"🧹 删除文件: {artifact}")
                elif artifact.is_dir():
                    import shutil
                    shutil.rmtree(artifact)
                    print(f"🧹 删除目录: {artifact}")

        return True

    def print_summary(self):
        """打印测试结果总结"""
        execution_time = time.time() - self.start_time
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result == "成功")

        print("\n" + "="*80)
        print("🎯 测试执行结果总结")
        print("="*80)
        print(f"⏱️  总执行时间: {execution_time:.2f}秒")
        print(f"📊 总测试数量: {total_tests}")
        print(f"✅ 成功测试: {successful_tests}")
        print(f"❌ 失败测试: {total_tests - successful_tests}")
        print(f"📈 成功率: {(successful_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%")

        print("\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result == "成功" else "❌"
            print(f"  {status} {test_name}: {result}")

        print("\n" + "="*80)

        if successful_tests == total_tests:
            print("🎉 所有测试通过！系统质量良好。")
        else:
            print("⚠️  部分测试失败，请检查问题并修复。")

        return successful_tests == total_tests


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="EduAgents 增强版测试工具")

    # 测试类型选项
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--api", action="store_true", help="运行API测试")
    parser.add_argument("--business", action="store_true", help="运行业务穿越测试")
    parser.add_argument("--tracking", action="store_true", help="运行业务追踪测试 - 完整协作验证")
    parser.add_argument("--coverage", action="store_true", help="运行测试覆盖率分析")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")

    # 质量检查选项
    parser.add_argument("--lint", action="store_true", help="运行代码检查")
    parser.add_argument("--type", action="store_true", help="运行类型检查")
    parser.add_argument("--security", action="store_true", help="运行安全扫描")
    parser.add_argument("--quality", action="store_true", help="运行所有质量检查")

    # 工具选项
    parser.add_argument("--cleanup", action="store_true", help="清理测试产物")
    parser.add_argument("--pattern", type=str, help="测试过滤模式")
    parser.add_argument("--fast", action="store_true", help="快速测试模式（跳过慢速测试）")
    parser.add_argument("--parallel", action="store_true", help="并行执行测试")

    args = parser.parse_args()

    # 创建测试运行器
    runner = TestRunner()

    print("🚀 EduAgents 增强版测试工具启动")
    print(f"📂 项目目录: {PROJECT_ROOT}")

    # 清理选项
    if args.cleanup:
        runner.cleanup_test_artifacts()

    # 确定要运行的测试
    tests_to_run = []

    if args.all:
        tests_to_run = ["unit", "integration", "api", "business", "coverage"]
    else:
        if args.unit:
            tests_to_run.append("unit")
        if args.integration:
            tests_to_run.append("integration")
        if args.api:
            tests_to_run.append("api")
        if args.business:
            tests_to_run.append("business")
        if args.tracking:
            tests_to_run.append("tracking")
        if args.coverage:
            tests_to_run.append("coverage")
        if args.performance:
            tests_to_run.append("performance")

    # 质量检查
    quality_checks = []
    if args.quality:
        quality_checks = ["lint", "type", "security"]
    else:
        if args.lint:
            quality_checks.append("lint")
        if args.type:
            quality_checks.append("type")
        if args.security:
            quality_checks.append("security")

    # 如果没有指定任何测试，运行基础测试套件
    if not tests_to_run and not quality_checks:
        tests_to_run = ["api", "integration"]
        print("ℹ️  未指定测试类型，运行默认测试套件")

    # 执行质量检查
    for check in quality_checks:
        if check == "lint":
            runner.run_linting()
        elif check == "type":
            runner.run_type_checking()
        elif check == "security":
            runner.run_security_scan()

    # 执行测试
    for test_type in tests_to_run:
        if test_type == "unit":
            runner.run_unit_tests(args.pattern)
        elif test_type == "integration":
            runner.run_integration_tests(args.pattern)
        elif test_type == "api":
            runner.run_api_tests()
        elif test_type == "business":
            runner.run_business_flow_test()
        elif test_type == "tracking":
            runner.run_business_tracking_test()
        elif test_type == "coverage":
            runner.run_coverage_test()
        elif test_type == "performance":
            runner.run_performance_tests()

    # 打印总结并退出
    success = runner.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()