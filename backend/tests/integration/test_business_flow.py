"""
完整业务穿越测试脚本
模拟前端业务流程，测试核心API接口的完整性和可用性
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
import pytest
from faker import Faker

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化faker
fake = Faker('zh_CN')


class BusinessFlowTester:
    """业务流程测试器"""

    def __init__(self, base_url: str = "http://localhost:48284"):
        self.base_url = base_url
        # 创建httpx客户端时禁用环境变量代理，避免测试时的网络问题
        self.client = httpx.AsyncClient(timeout=60.0, trust_env=False)
        self.session_data = {}
        self.test_results = {}

    async def cleanup(self):
        """清理资源"""
        await self.client.aclose()

    async def wait_and_check_health(self, retries: int = 30, delay: float = 2.0) -> bool:
        """等待服务启动并检查健康状态"""
        logger.info("等待后端服务启动...")

        for i in range(retries):
            try:
                response = await self.client.get(f"{self.base_url}/api/health")
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info(f"服务健康检查通过: {health_data}")
                    return True
            except Exception as e:
                logger.info(f"等待服务启动 ({i+1}/{retries}): {str(e)}")

            if i < retries - 1:
                await asyncio.sleep(delay)

        logger.error("服务启动超时或健康检查失败")
        return False

    def log_test_result(self, test_name: str, success: bool, details: Optional[Dict] = None):
        """记录测试结果"""
        result = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results[test_name] = result
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")

    async def test_root_endpoint(self) -> bool:
        """测试根端点"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            success = response.status_code == 200 and "PBL智能助手 API" in response.json().get("service", "")
            self.log_test_result("根端点测试", success, {"status_code": response.status_code})
            return success
        except Exception as e:
            self.log_test_result("根端点测试", False, {"error": str(e)})
            return False

    async def test_system_capabilities(self) -> bool:
        """测试系统能力查询"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/agents/capabilities")
            success = response.status_code == 200
            data = response.json()

            if success:
                agents = data.get("data", {}).get("agents", [])
                success = len(agents) >= 5  # 至少5个智能体

            self.log_test_result("系统能力查询", success, {
                "status_code": response.status_code,
                "agents_count": len(agents) if success else 0
            })
            return success
        except Exception as e:
            self.log_test_result("系统能力查询", False, {"error": str(e)})
            return False

    # 删除非核心模板测试方法 - 专注核心多智能体协作功能

    async def test_course_design_session_flow(self) -> bool:
        """测试完整的课程设计会话流程"""
        try:
            # 1. 创建课程设计会话
            session_request = {
                "requirements": {
                    "topic": "人工智能基础与应用",
                    "audience": "高中生",
                    "age_group": {"min": 16, "max": 18},
                    "duration": {"weeks": 8, "hours_per_week": 4},
                    "goals": [
                        "理解人工智能的基本概念和发展历程",
                        "掌握机器学习的基础算法原理",
                        "能够使用Python实现简单的AI项目",
                        "培养批判性思维和科技伦理意识"
                    ],
                    "context": "高中信息技术课程，结合STEAM教育理念",
                    "constraints": {
                        "budget": "中等",
                        "equipment": "计算机机房",
                        "time_limit": "学期内完成"
                    },
                    "preferences": {
                        "teaching_style": "项目驱动",
                        "assessment_type": "多元化评价"
                    }
                },
                "mode": "full_course",
                "config": {
                    "streaming": True,
                    "max_iterations": 3,
                    "model_preference": "claude",
                    "temperature": 0.7
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/sessions",
                json=session_request,
                headers={"Authorization": "Bearer mock_token"}  # 模拟认证
            )

            if response.status_code != 200:
                self.log_test_result("创建设计会话", False, {
                    "status_code": response.status_code,
                    "error": response.text
                })
                return False

            session_data = response.json()["data"]
            session_id = session_data["session_id"]
            self.session_data["session_id"] = session_id

            # 2. 启动设计流程（非流式）
            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/start",
                headers={"Authorization": "Bearer mock_token"}
            )

            if response.status_code not in [200, 202]:  # 接受异步处理
                self.log_test_result("启动设计流程", False, {"status_code": response.status_code})
                return False

            # 3. 获取会话状态
            await asyncio.sleep(2)  # 等待处理
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/status",
                headers={"Authorization": "Bearer mock_token"}
            )

            if response.status_code != 200:
                self.log_test_result("查询会话状态", False, {"status_code": response.status_code})
                return False

            status_data = response.json()["data"]

            # 4. 获取设计结果
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/result",
                headers={"Authorization": "Bearer mock_token"}
            )

            if response.status_code != 200:
                self.log_test_result("获取设计结果", False, {"status_code": response.status_code})
                return False

            result_data = response.json()["data"]
            self.session_data["design_result"] = result_data

            self.log_test_result("课程设计会话流程", True, {
                "session_id": session_id,
                "status": status_data.get("status"),
                "has_result": bool(result_data)
            })
            return True

        except Exception as e:
            self.log_test_result("课程设计会话流程", False, {"error": str(e)})
            return False

    async def test_course_iteration_flow(self) -> bool:
        """测试课程设计迭代流程"""
        session_id = self.session_data.get("session_id")
        if not session_id:
            self.log_test_result("课程迭代流程", False, {"error": "缺少会话ID"})
            return False

        try:
            # 提供反馈进行迭代
            feedback_request = {
                "aspects": {
                    "learning_objectives": "学习目标需要更加具体和可衡量",
                    "project_design": "项目任务可以更加贴近学生实际生活",
                    "assessment": "评估方式可以增加peer review环节"
                },
                "priorities": [
                    "优化项目任务设计",
                    "完善评估标准"
                ],
                "additional_requirements": {
                    "add_ethics_module": True,
                    "include_industry_cases": True
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/iterate",
                json=feedback_request,
                headers={"Authorization": "Bearer mock_token"}
            )

            success = response.status_code == 200

            if success:
                iteration_result = response.json()["data"]
                self.session_data["iteration_result"] = iteration_result

            self.log_test_result("课程迭代流程", success, {"status_code": response.status_code})
            return success

        except Exception as e:
            self.log_test_result("课程迭代流程", False, {"error": str(e)})
            return False

    async def test_course_export_flow(self) -> bool:
        """测试课程导出流程"""
        session_id = self.session_data.get("session_id")
        if not session_id:
            self.log_test_result("课程导出流程", False, {"error": "缺少会话ID"})
            return False

        try:
            # 测试JSON格式导出
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/export?format=json",
                headers={"Authorization": "Bearer mock_token"}
            )

            json_success = response.status_code == 200

            # 测试PDF格式导出
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/export?format=pdf",
                headers={"Authorization": "Bearer mock_token"}
            )

            pdf_success = response.status_code == 200

            # 测试ZIP格式导出
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/export?format=zip",
                headers={"Authorization": "Bearer mock_token"}
            )

            zip_success = response.status_code == 200

            overall_success = json_success or pdf_success or zip_success

            self.log_test_result("课程导出流程", overall_success, {
                "json_export": json_success,
                "pdf_export": pdf_success,
                "zip_export": zip_success
            })
            return overall_success

        except Exception as e:
            self.log_test_result("课程导出流程", False, {"error": str(e)})
            return False

    # 删除非核心质量检查测试方法 - 专注核心多智能体协作功能

    # 删除非核心协作功能测试方法 - 专注核心多智能体协作功能

    async def test_agent_metrics(self) -> bool:
        """测试智能体指标"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/agents/metrics",
                headers={"Authorization": "Bearer mock_token"}
            )

            success = response.status_code == 200

            if success:
                metrics_data = response.json()["data"]

            self.log_test_result("智能体指标", success, {"status_code": response.status_code})
            return success

        except Exception as e:
            self.log_test_result("智能体指标", False, {"error": str(e)})
            return False

    async def test_session_cleanup(self) -> bool:
        """测试会话清理"""
        session_id = self.session_data.get("session_id")
        if not session_id:
            self.log_test_result("会话清理", True, {"message": "没有需要清理的会话"})
            return True

        try:
            response = await self.client.delete(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}",
                headers={"Authorization": "Bearer mock_token"}
            )

            success = response.status_code == 200

            self.log_test_result("会话清理", success, {"status_code": response.status_code})
            return success

        except Exception as e:
            self.log_test_result("会话清理", False, {"error": str(e)})
            return False

    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])

        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": f"{(successful_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
                "test_time": datetime.now().isoformat()
            },
            "results": self.test_results,
            "session_data": self.session_data
        }

        return report

    async def run_complete_business_flow(self) -> Dict[str, Any]:
        """运行完整业务流程测试"""
        logger.info("🚀 开始完整业务流程测试")
        start_time = time.time()

        # 等待服务启动
        if not await self.wait_and_check_health():
            logger.error("❌ 服务健康检查失败，测试终止")
            return {"error": "服务不可用"}

        # 按业务流程顺序执行测试
        test_flows = [
            ("基础连通性测试", self.test_root_endpoint),
            ("系统能力查询", self.test_system_capabilities),
            # 删除非核心功能测试，专注核心多智能体协作
            ("课程设计会话流程", self.test_course_design_session_flow),
            ("课程迭代优化流程", self.test_course_iteration_flow),
            ("课程导出功能", self.test_course_export_flow),
            # 保留核心指标监控
            ("智能体性能指标", self.test_agent_metrics),
            ("会话清理", self.test_session_cleanup),
        ]

        # 执行所有测试
        for test_name, test_func in test_flows:
            logger.info(f"📋 执行测试: {test_name}")
            try:
                await test_func()
            except Exception as e:
                logger.error(f"测试异常: {test_name} - {str(e)}")
                self.log_test_result(test_name, False, {"error": str(e)})

            # 测试间隔
            await asyncio.sleep(0.5)

        # 生成测试报告
        report = self.generate_test_report()
        execution_time = time.time() - start_time
        report["execution_time_seconds"] = round(execution_time, 2)

        # 输出测试结果
        logger.info(f"🎉 测试完成，耗时: {execution_time:.2f}秒")
        logger.info(f"📊 成功率: {report['summary']['success_rate']}")

        return report


async def main():
    """主函数"""
    # 从环境变量获取配置
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:48284")

    # 创建测试器
    tester = BusinessFlowTester(base_url)

    try:
        # 运行测试
        report = await tester.run_complete_business_flow()

        # 保存测试报告
        report_path = Path(__file__).parent / "test_reports" / f"business_flow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 测试报告已保存: {report_path}")

        # 输出关键结果
        if "summary" in report:
            summary = report["summary"]
            print("\n" + "="*60)
            print("🎯 业务流程测试结果汇总")
            print("="*60)
            print(f"总测试数: {summary['total_tests']}")
            print(f"成功测试: {summary['successful_tests']}")
            print(f"失败测试: {summary['failed_tests']}")
            print(f"成功率: {summary['success_rate']}")
            print(f"执行时间: {report.get('execution_time_seconds', 0)}秒")
            print("="*60)

            # 失败的测试详情
            failed_tests = [name for name, result in report["results"].items() if not result["success"]]
            if failed_tests:
                print("❌ 失败的测试:")
                for test_name in failed_tests:
                    details = report["results"][test_name].get("details", {})
                    error = details.get("error", "未知错误")
                    print(f"  - {test_name}: {error}")
            else:
                print("✅ 所有测试通过!")
        else:
            print("❌ 测试异常结束")
            print(json.dumps(report, indent=2, ensure_ascii=False))

        return 0 if report.get("summary", {}).get("failed_tests", 1) == 0 else 1

    except KeyboardInterrupt:
        logger.info("用户中断测试")
        return 130
    except Exception as e:
        logger.error(f"测试执行异常: {str(e)}")
        return 1
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)