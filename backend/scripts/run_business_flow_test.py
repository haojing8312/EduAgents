#!/usr/bin/env python3
"""
业务流程测试运行脚本
用于启动后端服务并执行完整的业务穿越测试
"""

import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessFlowTestRunner:
    """业务流程测试运行器"""

    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.project_root = Path(__file__).parent.parent
        self.test_script = self.project_root / "tests" / "integration" / "test_business_flow.py"

    def setup_environment(self):
        """设置测试环境"""
        # 设置环境变量
        test_env = {
            **os.environ,
            "ENVIRONMENT": "test",
            "DATABASE_URL": "sqlite:///./test.db",  # 使用SQLite进行测试
            "REDIS_URL": "redis://localhost:6379/1",  # 使用不同的Redis数据库
            "TEST_BASE_URL": "http://localhost:48282",
            "PYTHONPATH": str(self.project_root),
            "LOG_LEVEL": "INFO",
        }

        # 只为测试清理代理设置，避免影响httpx
        proxy_vars = ["http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]
        for var in proxy_vars:
            test_env[var] = ""

        # 设置AI API密钥（如果存在）
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
            if key in os.environ:
                test_env[key] = os.environ[key]

        return test_env

    async def start_backend_server(self, env: dict) -> bool:
        """启动后端服务器"""
        logger.info("🚀 启动后端服务器...")

        try:
            # 使用uv运行后端服务器
            cmd = [
                "uv", "run", "uvicorn", "app.simple_test_main:app",
                "--host", "0.0.0.0",
                "--port", "48282",
                "--reload"
            ]

            self.backend_process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 等待服务器启动
            logger.info("⏳ 等待后端服务器启动...")
            await asyncio.sleep(5)

            # 检查进程是否还在运行
            if self.backend_process.poll() is not None:
                # 进程已经退出，读取错误信息
                stdout, stderr = self.backend_process.communicate()
                logger.error(f"后端服务器启动失败:")
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return False

            logger.info("✅ 后端服务器启动成功")
            return True

        except Exception as e:
            logger.error(f"启动后端服务器时出错: {str(e)}")
            return False

    def stop_backend_server(self):
        """停止后端服务器"""
        if self.backend_process:
            logger.info("🛑 停止后端服务器...")
            try:
                # 发送SIGTERM信号
                self.backend_process.terminate()

                # 等待进程结束
                try:
                    self.backend_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # 如果进程没有在10秒内结束，强制杀死
                    logger.warning("强制终止后端服务器进程")
                    self.backend_process.kill()
                    self.backend_process.wait()

                logger.info("✅ 后端服务器已停止")

            except Exception as e:
                logger.error(f"停止后端服务器时出错: {str(e)}")

            self.backend_process = None

    async def run_business_flow_test(self, env: dict) -> int:
        """运行业务流程测试"""
        logger.info("🧪 开始执行业务流程测试...")

        try:
            # 运行测试脚本
            cmd = ["uv", "run", "python", str(self.test_script)]

            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 实时输出日志
            stdout_lines = []
            stderr_lines = []

            while True:
                # 检查进程是否结束
                if process.poll() is not None:
                    break

                # 读取输出
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        print(line.rstrip())
                        stdout_lines.append(line)

                # 读取错误输出
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        print(line.rstrip(), file=sys.stderr)
                        stderr_lines.append(line)

                await asyncio.sleep(0.1)

            # 获取最终结果
            return_code = process.wait()

            if return_code == 0:
                logger.info("✅ 业务流程测试通过")
            else:
                logger.error(f"❌ 业务流程测试失败，退出码: {return_code}")

            return return_code

        except Exception as e:
            logger.error(f"执行业务流程测试时出错: {str(e)}")
            return 1

    async def run_complete_test_suite(self) -> int:
        """运行完整的测试套件"""
        logger.info("🎯 开始完整的业务流程测试")
        start_time = time.time()

        try:
            # 1. 设置环境
            env = self.setup_environment()

            # 2. 启动后端服务器
            if not await self.start_backend_server(env):
                logger.error("❌ 后端服务器启动失败，测试终止")
                return 1

            # 3. 运行业务流程测试
            test_result = await self.run_business_flow_test(env)

            # 4. 输出总结
            execution_time = time.time() - start_time
            logger.info(f"🎉 测试完成，总耗时: {execution_time:.2f}秒")

            return test_result

        except KeyboardInterrupt:
            logger.info("用户中断测试")
            return 130

        except Exception as e:
            logger.error(f"测试执行异常: {str(e)}")
            return 1

        finally:
            # 清理资源
            self.stop_backend_server()

    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info("收到中断信号，正在清理...")
            self.stop_backend_server()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


def check_dependencies():
    """检查依赖"""
    required_commands = ["uv"]

    for cmd in required_commands:
        if not subprocess.run(["which", cmd], capture_output=True).returncode == 0:
            logger.error(f"❌ 缺少必需的命令: {cmd}")
            logger.error("请安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
            return False

    return True


async def main():
    """主函数"""
    print("="*60)
    print("🚀 PBL智能助手 - 业务流程测试")
    print("="*60)

    # 检查依赖
    if not check_dependencies():
        return 1

    # 创建测试运行器
    runner = BusinessFlowTestRunner()
    runner.setup_signal_handlers()

    try:
        # 运行完整测试
        exit_code = await runner.run_complete_test_suite()

        if exit_code == 0:
            print("\n" + "="*60)
            print("🎉 所有测试通过！系统功能正常")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ 部分测试失败，请检查日志")
            print("="*60)

        return exit_code

    except Exception as e:
        logger.error(f"测试运行器异常: {str(e)}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(130)