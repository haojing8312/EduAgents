#!/usr/bin/env python3
"""
EduAgents 后端测试脚本
针对已启动的后端服务（48284端口）进行测试
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any
import aiohttp

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
        import aiohttp
        logger.info("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖: {e}")
        logger.info("请运行: uv sync")
        return False

async def test_health_check(session: aiohttp.ClientSession, base_url: str) -> bool:
    """健康检查测试"""
    logger = logging.getLogger(__name__)

    try:
        async with session.get(f"{base_url}/health") as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ 健康检查通过: {data}")
                return True
            else:
                logger.error(f"❌ 健康检查失败: {response.status}")
                return False
    except Exception as e:
        logger.error(f"❌ 健康检查异常: {e}")
        return False

async def test_api_docs(session: aiohttp.ClientSession, base_url: str) -> bool:
    """API文档测试"""
    logger = logging.getLogger(__name__)

    try:
        async with session.get(f"{base_url}/docs") as response:
            if response.status == 200:
                logger.info("✅ API文档可访问")
                return True
            else:
                logger.error(f"❌ API文档访问失败: {response.status}")
                return False
    except Exception as e:
        logger.error(f"❌ API文档测试异常: {e}")
        return False

async def test_agents_capabilities(session: aiohttp.ClientSession, base_url: str) -> bool:
    """智能体能力测试"""
    logger = logging.getLogger(__name__)

    try:
        async with session.get(f"{base_url}/api/v1/agents/capabilities") as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ 智能体能力查询成功: {len(data.get('agents', []))} 个智能体")
                return True
            else:
                logger.error(f"❌ 智能体能力查询失败: {response.status}")
                return False
    except Exception as e:
        logger.error(f"❌ 智能体能力测试异常: {e}")
        return False

async def test_course_session_creation(session: aiohttp.ClientSession, base_url: str) -> Dict[str, Any]:
    """课程会话创建测试"""
    logger = logging.getLogger(__name__)

    payload = {
        "subject": "人工智能与机器学习",
        "grade_level": "高中",
        "duration_weeks": 4,
        "learning_objectives": ["理解AI基本概念", "掌握机器学习基础"],
        "special_requirements": "需要实践项目"
    }

    try:
        async with session.post(
            f"{base_url}/api/v1/courses/sessions",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ 课程会话创建成功: {data.get('session_id')}")
                return {"success": True, "data": data}
            else:
                text = await response.text()
                logger.error(f"❌ 课程会话创建失败: {response.status} - {text}")
                return {"success": False, "error": text}
    except Exception as e:
        logger.error(f"❌ 课程会话创建异常: {e}")
        return {"success": False, "error": str(e)}

async def run_comprehensive_test(host: str = "localhost", port: int = 48284) -> bool:
    """运行综合测试"""
    logger = logging.getLogger(__name__)
    base_url = f"http://{host}:{port}"

    logger.info(f"🧪 开始测试后端服务: {base_url}")

    test_results = []

    async with aiohttp.ClientSession() as session:
        # 1. 健康检查测试
        logger.info("1️⃣ 健康检查测试")
        health_ok = await test_health_check(session, base_url)
        test_results.append(("健康检查", health_ok))

        # 2. API文档测试
        logger.info("2️⃣ API文档测试")
        docs_ok = await test_api_docs(session, base_url)
        test_results.append(("API文档", docs_ok))

        # 3. 智能体能力测试
        logger.info("3️⃣ 智能体能力测试")
        agents_ok = await test_agents_capabilities(session, base_url)
        test_results.append(("智能体能力", agents_ok))

        # 4. 课程会话创建测试
        logger.info("4️⃣ 课程会话创建测试")
        session_result = await test_course_session_creation(session, base_url)
        test_results.append(("课程会话创建", session_result["success"]))

    # 汇总测试结果
    logger.info("📊 测试结果汇总:")
    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"📈 测试统计: {passed}/{total} 通过，成功率: {passed/total*100:.1f}%")

    return passed == total

async def run_test_suite():
    """运行测试套件"""
    logger = logging.getLogger(__name__)

    logger.info("🚀 EduAgents 后端服务测试开始")
    logger.info(f"📂 项目目录: {PROJECT_ROOT}")

    # 检查依赖
    if not check_dependencies():
        return False

    # 运行综合测试
    success = await run_comprehensive_test()

    if success:
        logger.info("🎉 所有测试通过！")
    else:
        logger.error("💥 部分测试失败，请检查服务状态")

    return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="EduAgents 后端测试工具")

    # 基础参数
    parser.add_argument("--host", default="localhost", help="测试目标主机 (默认: localhost)")
    parser.add_argument("--port", type=int, default=48284, help="测试目标端口 (默认: 48284)")
    parser.add_argument("--check", action="store_true", help="只检查依赖，不运行测试")

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🌟 EduAgents 后端测试工具")
    logger.info(f"📂 项目目录: {PROJECT_ROOT}")

    # 检查依赖
    if not check_dependencies():
        return 1

    if args.check:
        logger.info("✅ 依赖检查完成")
        return 0

    # 运行异步测试
    try:
        success = asyncio.run(run_comprehensive_test(args.host, args.port))
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("🛑 测试被用户中断")
        return 1
    except Exception as e:
        logger.error(f"❌ 测试执行异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())