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
    """业务流程测试器 - 增强版，集成协作追踪功能验证"""

    def __init__(self, base_url: str = "http://localhost:48284"):
        self.base_url = base_url
        # 创建httpx客户端时禁用环境变量代理，避免测试时的网络问题
        self.client = httpx.AsyncClient(timeout=60.0, trust_env=False)
        self.session_data = {}
        self.test_results = {}
        self.collaboration_data = {}

        # 创建exports目录结构
        self.exports_dir = Path(__file__).parent.parent.parent / "exports" / "business_tests"
        self.test_start_time = datetime.now()
        self.test_run_dir = self.exports_dir / f"test_run_{self.test_start_time.strftime('%Y%m%d_%H%M%S')}"
        self.test_run_dir.mkdir(parents=True, exist_ok=True)

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

    async def export_collaboration_data(self, session_id: str):
        """导出协作追踪数据"""
        try:
            logger.info("🔍 导出协作追踪数据...")

            # 导出协作流程数据
            try:
                response = await self.client.get(f"{self.base_url}/api/v1/collaboration/sessions/{session_id}/flow")
                if response.status_code == 200:
                    flow_data = response.json()
                    with open(self.test_run_dir / "collaboration_flow.json", 'w', encoding='utf-8') as f:
                        json.dump(flow_data, f, ensure_ascii=False, indent=2)
                    logger.info("✅ 协作流程数据导出成功")
                    self.collaboration_data["flow"] = flow_data
                else:
                    logger.warning(f"⚠️ 协作流程数据导出失败: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ 协作流程数据导出异常: {e}")

            # 导出AI调用分析数据
            try:
                response = await self.client.get(f"{self.base_url}/api/v1/collaboration/sessions/{session_id}/ai-calls")
                if response.status_code == 200:
                    ai_data = response.json()
                    with open(self.test_run_dir / "ai_calls_analytics.json", 'w', encoding='utf-8') as f:
                        json.dump(ai_data, f, ensure_ascii=False, indent=2)
                    logger.info("✅ AI调用分析数据导出成功")
                    self.collaboration_data["ai_calls"] = ai_data
                else:
                    logger.warning(f"⚠️ AI调用分析数据导出失败: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ AI调用分析数据导出异常: {e}")

            # 导出交付物追踪数据
            try:
                response = await self.client.get(f"{self.base_url}/api/v1/collaboration/sessions/{session_id}/deliverables")
                if response.status_code == 200:
                    deliverable_data = response.json()
                    with open(self.test_run_dir / "deliverable_traceability.json", 'w', encoding='utf-8') as f:
                        json.dump(deliverable_data, f, ensure_ascii=False, indent=2)
                    logger.info("✅ 交付物追踪数据导出成功")
                    self.collaboration_data["deliverables"] = deliverable_data
                else:
                    logger.warning(f"⚠️ 交付物追踪数据导出失败: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ 交付物追踪数据导出异常: {e}")

            # 导出完整的协作报告
            try:
                response = await self.client.get(f"{self.base_url}/api/v1/collaboration/sessions/{session_id}/export?format_type=json")
                if response.status_code == 200:
                    export_data = response.json()
                    with open(self.test_run_dir / "complete_collaboration_report.json", 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    logger.info("✅ 完整协作报告导出成功")
                    self.collaboration_data["complete_report"] = export_data
                else:
                    logger.warning(f"⚠️ 完整协作报告导出失败: HTTP {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ 完整协作报告导出异常: {e}")

            # 记录协作追踪数据导出结果
            exported_files = []
            for filename in ["collaboration_flow.json", "ai_calls_analytics.json", "deliverable_traceability.json", "complete_collaboration_report.json"]:
                filepath = self.test_run_dir / filename
                if filepath.exists():
                    exported_files.append(filename)

            self.log_test_result("协作数据导出", len(exported_files) > 0, {
                "exported_files": exported_files,
                "export_count": len(exported_files)
            })

        except Exception as e:
            logger.error(f"❌ 协作数据导出失败: {e}")
            self.log_test_result("协作数据导出", False, {"error": str(e)})

    async def _handle_failed_session(self, session_id: str, error_msg: str):
        """处理失败的会话，记录失败信息并尝试导出协作追踪数据（用于问题分析）"""
        try:
            # 记录失败信息
            failure_info = {
                "status": "failed",
                "error": error_msg,
                "session_id": session_id,
                "failure_timestamp": datetime.now().isoformat(),
                "note": "此会话已失败，无法提供课程设计结果。以下协作数据仅用于问题分析。"
            }

            # 保存失败记录（明确标注为失败，不包含任何可能误导的结果）
            with open(self.test_run_dir / "session_failure_record.json", 'w', encoding='utf-8') as f:
                json.dump(failure_info, f, ensure_ascii=False, indent=2)
            logger.info("📝 失败记录已保存")

            # 尝试导出协作追踪数据（仅用于调试和问题分析）
            logger.info("🔍 尝试导出协作追踪数据用于问题分析...")
            await self.export_collaboration_data(session_id)

        except Exception as e:
            logger.warning(f"⚠️ 处理失败会话时出现异常: {e}")

    def _validate_course_design_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证课程设计结果的质量"""
        quality_check = {
            "has_overview": bool(result_data.get("course_overview")),
            "has_content": bool(result_data.get("content")),
            "has_assessment": bool(result_data.get("assessment")),
            "has_materials": bool(result_data.get("materials")),
            "overall_quality": "poor"
        }

        # 检查课程概览质量
        overview = result_data.get("course_overview", {})
        if overview:
            quality_check["overview_details"] = {
                "has_requirements": bool(overview.get("requirements")),
                "has_theoretical_foundation": bool(overview.get("theoretical_foundation")),
                "has_architecture": bool(overview.get("architecture"))
            }

        # 检查内容质量
        content = result_data.get("content", {})
        if content:
            modules = content.get("modules", [])
            quality_check["content_details"] = {
                "module_count": len(modules),
                "has_modules": len(modules) > 0
            }

        # 综合质量评估
        quality_score = sum([
            quality_check["has_overview"],
            quality_check["has_content"],
            quality_check["has_assessment"],
            quality_check["has_materials"]
        ])

        if quality_score >= 4:
            quality_check["overall_quality"] = "excellent"
        elif quality_score >= 3:
            quality_check["overall_quality"] = "good"
        elif quality_score >= 2:
            quality_check["overall_quality"] = "fair"

        return quality_check

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

                # 保存智能体能力数据
                with open(self.test_run_dir / "agents_capabilities.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            self.log_test_result("系统能力查询", success, {
                "status_code": response.status_code,
                "agents_count": len(agents) if success else 0
            })
            return success
        except Exception as e:
            self.log_test_result("系统能力查询", False, {"error": str(e)})
            return False

    async def test_collaboration_tracking_apis(self) -> bool:
        """测试协作追踪API端点"""
        try:
            # 测试协作会话列表API
            response = await self.client.get(f"{self.base_url}/api/v1/collaboration/sessions")
            sessions_success = response.status_code == 200
            if sessions_success:
                sessions_data = response.json()
                with open(self.test_run_dir / "collaboration_sessions.json", 'w', encoding='utf-8') as f:
                    json.dump(sessions_data, f, ensure_ascii=False, indent=2)

            # 测试协作分析概览API
            response = await self.client.get(f"{self.base_url}/api/v1/collaboration/analytics/overview")
            analytics_success = response.status_code == 200
            if analytics_success:
                analytics_data = response.json()
                with open(self.test_run_dir / "collaboration_analytics.json", 'w', encoding='utf-8') as f:
                    json.dump(analytics_data, f, ensure_ascii=False, indent=2)

            overall_success = sessions_success and analytics_success

            self.log_test_result("协作追踪API", overall_success, {
                "sessions_api": sessions_success,
                "analytics_api": analytics_success
            })
            return overall_success

        except Exception as e:
            self.log_test_result("协作追踪API", False, {"error": str(e)})
            return False

    # 删除非核心模板测试方法 - 专注核心多智能体协作功能

    async def test_course_design_session_flow(self) -> bool:
        """测试完整的课程设计会话流程"""
        try:
            # 1. 创建课程设计会话
            session_request = {
                "requirements": {
                    "topic": "月球永居人类的科技装备展",
                    "audience": "中小学生",
                    "age_group": {"min": 8, "max": 15},
                    "duration": {"days": 3, "hours_per_day": 6},
                    "goals": [
                        "激发孩子对未来科技和太空探索的想象力",
                        "掌握3D建模和3D打印的基础技能",
                        "学会使用AI动画技术制作虚实融合视频",
                        "培养创新思维和科学探索精神",
                        "完成月球装备的完整设计制作流程"
                    ],
                    "context": "国庆节3天AI科技训练营，6人小班制，未来科幻主题",
                    "constraints": {
                        "budget": "充足",
                        "equipment": "3D打印机、计算机、AI动画软件、摄影设备",
                        "time_limit": "3天内完成所有作品"
                    },
                    "preferences": {
                        "teaching_style": "项目制学习+脑洞大开",
                        "assessment_type": "作品展示+创意评价"
                    },
                    "special_requirements": {
                        "class_size": 6,
                        "final_deliverables": [
                            "月球装备说明书",
                            "3D打印装备实物",
                            "AI动画虚实融合展览视频"
                        ],
                        "theme_focus": "月球永居生存装备",
                        "creativity_level": "科幻未来向"
                    }
                },
                "mode": "full_course",
                "config": {
                    "streaming": True,
                    "max_iterations": 3,
                    "model_preference": "claude",
                    "temperature": 0.7,
                    "enable_collaboration_tracking": True  # 重要：启用协作追踪
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/sessions",
                json=session_request,
                headers={"Authorization": "Bearer mock_token"}  # 模拟认证
            )

            if response.status_code != 200:
                error_details = {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "response_headers": dict(response.headers)
                }
                try:
                    error_json = response.json()
                    error_details["response_json"] = error_json
                except:
                    pass
                self.log_test_result("创建设计会话", False, error_details)
                logger.error(f"创建设计会话失败 - 状态码: {response.status_code}, 详细错误: {response.text}")
                return False

            session_data = response.json()["data"]
            session_id = session_data["session_id"]
            self.session_data["session_id"] = session_id

            # 2. 启动设计流程（异步模式）
            response = await self.client.post(
                f"{self.base_url}/api/v1/agents/sessions/{session_id}/start",
                headers={"Authorization": "Bearer mock_token"}
            )

            if response.status_code not in [200, 202]:  # 接受异步处理
                error_details = {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "response_headers": dict(response.headers)
                }
                try:
                    error_json = response.json()
                    error_details["response_json"] = error_json
                except:
                    pass
                self.log_test_result("启动设计流程", False, error_details)
                logger.error(f"启动设计流程失败 - 状态码: {response.status_code}, 详细错误: {response.text}")
                return False

            logger.info(f"✅ 设计任务已启动，开始轮询状态...")

            # 3. 轮询会话状态直到完成（最多等待30分钟）
            max_polls = 180  # 30分钟，每10秒轮询一次
            poll_interval = 10  # 10秒间隔
            status_data = None

            for poll_count in range(max_polls):
                response = await self.client.get(
                    f"{self.base_url}/api/v1/agents/sessions/{session_id}/status",
                    headers={"Authorization": "Bearer mock_token"}
                )

                if response.status_code != 200:
                    self.log_test_result("查询会话状态", False, {"status_code": response.status_code})
                    return False

                status_data = response.json()["data"]
                status = status_data.get("status", "unknown")
                progress = status_data.get("progress", 0)
                current_agent = status_data.get("current_agent", "unknown")
                current_phase = status_data.get("current_phase", "unknown")
                estimated_remaining = status_data.get("estimated_remaining_seconds")

                logger.info(f"📊 轮询 {poll_count+1}/{max_polls}: 状态={status}, 进度={progress}%, 当前智能体={current_agent}, 阶段={current_phase}")

                if estimated_remaining:
                    logger.info(f"⏱️ 预计剩余时间: {estimated_remaining:.0f}秒")

                # 检查是否完成
                if status == "completed":
                    logger.info(f"🎉 设计任务完成！总轮询次数: {poll_count+1}")
                    break
                elif status == "failed":
                    error_msg = status_data.get("error", "未知错误")
                    logger.error(f"❌ 设计任务失败: {error_msg}")

                    # 即使失败，也尝试获取部分结果和协作数据
                    logger.info("🔄 尝试获取部分结果和协作数据...")
                    await self._handle_failed_session(session_id, error_msg)

                    self.log_test_result("课程设计会话流程", False, {"error": error_msg})
                    return False
                elif status not in ["running", "created"]:
                    logger.warning(f"⚠️ 未知状态: {status}")

                # 如果还在运行，等待下一次轮询
                if poll_count < max_polls - 1:
                    await asyncio.sleep(poll_interval)
            else:
                # 超时了
                logger.error(f"❌ 设计任务超时，已轮询 {max_polls} 次")
                self.log_test_result("课程设计会话流程", False, {"error": "任务超时"})
                return False

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

            # 保存课程设计结果
            with open(self.test_run_dir / "course_design_result.json", 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            # 导出协作追踪数据
            await self.export_collaboration_data(session_id)

            # 验证结果质量
            result_quality_check = self._validate_course_design_result(result_data)

            self.log_test_result("课程设计会话流程", True, {
                "session_id": session_id,
                "status": status_data.get("status"),
                "final_progress": status_data.get("progress"),
                "has_result": bool(result_data),
                "result_quality": result_quality_check,
                "total_polls": poll_count + 1
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
        """生成测试报告 - 增强版，包含协作追踪验证"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])

        # 检查协作追踪相关的测试结果
        collaboration_tracking_validation = {
            "tracking_api_available": self.test_results.get("协作追踪API", {}).get("success", False),
            "collaboration_data_exported": self.test_results.get("协作数据导出", {}).get("success", False),
            "evidence_found": False,
            "exported_files_count": 0
        }

        # 检查导出的协作数据文件
        collaboration_files = [
            "collaboration_flow.json",
            "ai_calls_analytics.json",
            "deliverable_traceability.json",
            "complete_collaboration_report.json"
        ]

        existing_files = []
        for filename in collaboration_files:
            filepath = self.test_run_dir / filename
            if filepath.exists():
                existing_files.append(filename)

        collaboration_tracking_validation["exported_files_count"] = len(existing_files)
        collaboration_tracking_validation["exported_files"] = existing_files

        # 检查是否存在会话失败记录
        failure_record_path = self.test_run_dir / "session_failure_record.json"
        session_failed = failure_record_path.exists()

        # 检查课程设计结果状态
        design_result = self.session_data.get("design_result", {})
        course_design_successful = False

        if session_failed:
            collaboration_tracking_validation["session_status"] = "failed"
            collaboration_tracking_validation["evidence_found"] = False
            collaboration_tracking_validation["note"] = "会话失败，协作数据仅用于问题分析"
        elif design_result and "collaboration_evidence" in design_result:
            collaboration_tracking_validation["evidence_found"] = True
            collaboration_tracking_validation["session_status"] = "completed"
            course_design_successful = True
        else:
            collaboration_tracking_validation["session_status"] = "unknown"

        report = {
            "test_metadata": {
                "test_start_time": self.test_start_time.isoformat(),
                "test_end_time": datetime.now().isoformat(),
                "export_directory": str(self.test_run_dir)
            },
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": f"{(successful_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
                "test_time": datetime.now().isoformat(),
                "course_design_successful": course_design_successful,
                "quality_assurance": "严格质量控制 - 失败时不提供低质量兜底方案"
            },
            "collaboration_tracking_validation": collaboration_tracking_validation,
            "results": self.test_results,
            "session_data": self.session_data,
            "collaboration_data": self.collaboration_data
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
            ("协作追踪API测试", self.test_collaboration_tracking_apis),
            ("课程设计会话流程", self.test_course_design_session_flow),
            ("课程迭代优化流程", self.test_course_iteration_flow),
            ("课程导出功能", self.test_course_export_flow),
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

        # 保存测试报告到exports目录
        if hasattr(tester, 'test_run_dir'):
            report_path = tester.test_run_dir / "business_flow_report.json"
        else:
            report_path = Path(__file__).parent / "test_reports" / f"business_flow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 测试报告已保存: {report_path}")

        # 生成可读的摘要文档
        if hasattr(tester, 'test_run_dir'):
            summary_path = tester.test_run_dir / "business_flow_summary.md"
            collaboration_validation = report.get("collaboration_tracking_validation", {})

            summary_text = f"""# 业务流程测试报告 - 协作追踪验证

## 测试概览
- 测试时间: {report.get('test_metadata', {}).get('test_start_time', 'N/A')}
- 导出目录: {report.get('test_metadata', {}).get('export_directory', 'N/A')}
- 总测试数: {report['summary']['total_tests']}
- 成功测试: {report['summary']['successful_tests']}
- 失败测试: {report['summary']['failed_tests']}
- 成功率: {report['summary']['success_rate']}

## 协作追踪验证结果
- 追踪API可用: {'✅' if collaboration_validation.get('tracking_api_available') else '❌'}
- 协作数据导出: {'✅' if collaboration_validation.get('collaboration_data_exported') else '❌'}
- 协作证据发现: {'✅' if collaboration_validation.get('evidence_found') else '❌'}
- 导出文件数量: {collaboration_validation.get('exported_files_count', 0)}

## 导出的协作追踪文件
{chr(10).join(f'- {filename}' for filename in collaboration_validation.get('exported_files', []))}

## 测试结论
{'🎉 协作追踪功能验证成功！完整的JSON报告已保存，可以通过导出文件验证多智能体协作过程。' if collaboration_validation.get('collaboration_data_exported') else '⚠️ 协作追踪功能验证不完整，请检查详细测试结果。'}
"""

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)

            logger.info(f"📄 测试摘要已保存: {summary_path}")

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

            # 输出协作追踪验证结果
            if "collaboration_tracking_validation" in report:
                collaboration_validation = report["collaboration_tracking_validation"]
                print("\n🎯 协作追踪功能验证结果")
                print("="*40)
                print(f"追踪API可用: {'✅' if collaboration_validation.get('tracking_api_available') else '❌'}")
                print(f"协作数据导出: {'✅' if collaboration_validation.get('collaboration_data_exported') else '❌'}")
                print(f"协作证据发现: {'✅' if collaboration_validation.get('evidence_found') else '❌'}")
                print(f"导出文件数量: {collaboration_validation.get('exported_files_count', 0)}")

                if collaboration_validation.get('exported_files'):
                    print("导出的协作文件:")
                    for filename in collaboration_validation.get('exported_files', []):
                        print(f"  - {filename}")

                if hasattr(tester, 'test_run_dir'):
                    print(f"📁 完整报告位置: {tester.test_run_dir}")

                print("="*40)

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

        # 核心业务流程测试必须100%通过
        success_rate_str = report.get("summary", {}).get("success_rate", "0%")
        success_rate = float(success_rate_str.rstrip('%'))
        failed_tests = report.get("summary", {}).get("failed_tests", 1)

        if success_rate == 100.0 and failed_tests == 0:
            print(f"🎯 成功率 {success_rate_str}，所有核心业务流程测试通过")
            return 0
        else:
            print(f"❌ 成功率 {success_rate_str}，核心业务流程测试未完全通过")
            print("核心业务接口必须100%成功才能通过测试")
            return 1

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