"""
压力测试和性能基准测试
"""
import asyncio
import aiohttp
import time
import statistics
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import psutil
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_times: List[float]
    success_count: int
    error_count: int
    throughput: float  # requests per second
    cpu_usage: List[float]
    memory_usage: List[float]
    timestamp: datetime
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0
    
    @property
    def p95_response_time(self) -> float:
        return statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else 0
    
    @property
    def p99_response_time(self) -> float:
        return statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else 0
    
    @property
    def error_rate(self) -> float:
        total = self.success_count + self.error_count
        return self.error_count / total if total > 0 else 0
    
    @property
    def avg_cpu_usage(self) -> float:
        return statistics.mean(self.cpu_usage) if self.cpu_usage else 0
    
    @property
    def avg_memory_usage(self) -> float:
        return statistics.mean(self.memory_usage) if self.memory_usage else 0


class SystemMonitor:
    """系统资源监控器"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        
    async def start_monitoring(self, interval: float = 1.0):
        """开始监控系统资源"""
        self.monitoring = True
        while self.monitoring:
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            self.metrics.append({
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_available': memory_info.available / 1024 / 1024,  # MB
            })
            
            await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def get_metrics(self) -> List[Dict]:
        """获取监控指标"""
        return self.metrics.copy()


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.monitor = SystemMonitor()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def single_request(self, endpoint: str, method: str = 'GET', 
                           data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """单个请求测试"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000  # ms
                content = await response.text()
                
                return {
                    'success': response.status < 400,
                    'status_code': response.status,
                    'response_time': response_time,
                    'content_length': len(content),
                    'error': None
                }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'status_code': 0,
                'response_time': response_time,
                'content_length': 0,
                'error': str(e)
            }
    
    async def concurrent_requests(self, endpoint: str, num_requests: int, 
                                concurrent_users: int, method: str = 'GET',
                                data: Optional[Dict] = None) -> PerformanceMetrics:
        """并发请求测试"""
        logger.info(f"开始并发测试: {num_requests} 请求, {concurrent_users} 并发用户")
        
        # 开始系统监控
        monitor_task = asyncio.create_task(self.monitor.start_monitoring())
        
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def make_request():
            async with semaphore:
                return await self.single_request(endpoint, method, data)
        
        start_time = time.time()
        
        # 执行并发请求
        tasks = [make_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 停止监控
        self.monitor.stop_monitoring()
        monitor_task.cancel()
        
        # 分析结果
        response_times = [r['response_time'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        error_count = len(results) - success_count
        throughput = num_requests / total_time
        
        # 获取系统监控数据
        system_metrics = self.monitor.get_metrics()
        cpu_usage = [m['cpu_percent'] for m in system_metrics]
        memory_usage = [m['memory_percent'] for m in system_metrics]
        
        return PerformanceMetrics(
            response_times=response_times,
            success_count=success_count,
            error_count=error_count,
            throughput=throughput,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            timestamp=datetime.now()
        )
    
    async def stress_test(self, endpoint: str, max_users: int = 1000, 
                         step_size: int = 50, step_duration: int = 60) -> List[PerformanceMetrics]:
        """压力测试 - 逐步增加并发用户数"""
        logger.info(f"开始压力测试: 最大 {max_users} 用户, 步长 {step_size}")
        
        results = []
        
        for users in range(step_size, max_users + 1, step_size):
            logger.info(f"测试 {users} 并发用户...")
            
            metrics = await self.concurrent_requests(
                endpoint, 
                num_requests=users * 2,  # 每个用户2个请求
                concurrent_users=users
            )
            
            results.append(metrics)
            
            # 检查是否达到性能阈值
            if metrics.error_rate > 0.1 or metrics.avg_response_time > 10000:
                logger.warning(f"性能阈值已达到，停止增加负载")
                break
            
            # 等待系统恢复
            await asyncio.sleep(5)
        
        return results
    
    async def endurance_test(self, endpoint: str, duration_minutes: int = 30,
                           concurrent_users: int = 100) -> List[PerformanceMetrics]:
        """耐久性测试 - 长时间稳定负载"""
        logger.info(f"开始耐久性测试: {duration_minutes} 分钟, {concurrent_users} 并发用户")
        
        results = []
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            metrics = await self.concurrent_requests(
                endpoint,
                num_requests=concurrent_users * 5,  # 每轮每用户5个请求
                concurrent_users=concurrent_users
            )
            
            results.append(metrics)
            
            # 记录当前状态
            logger.info(f"耐久测试进行中 - 平均响应时间: {metrics.avg_response_time:.2f}ms, "
                       f"错误率: {metrics.error_rate:.2%}, CPU: {metrics.avg_cpu_usage:.1f}%")
            
            # 短暂休息
            await asyncio.sleep(10)
        
        return results


class SpecializedTests:
    """专门的性能测试"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def agent_collaboration_stress_test(self) -> Dict[str, Any]:
        """智能体协作压力测试"""
        logger.info("开始智能体协作压力测试")
        
        async with PerformanceTester(self.base_url) as tester:
            # 准备测试数据
            collaboration_data = {
                "task": "design_complete_course",
                "course_requirements": {
                    "title": "压力测试课程",
                    "subject": "计算机科学",
                    "grade_level": "高中",
                    "duration_weeks": 12
                },
                "agents": ["education_director", "learning_designer", "creative_technologist"]
            }
            
            # 测试不同并发级别的智能体协作
            results = {}
            for concurrent_collaborations in [1, 5, 10, 20]:
                logger.info(f"测试 {concurrent_collaborations} 个并发协作")
                
                metrics = await tester.concurrent_requests(
                    "/api/v1/agents/collaborate",
                    num_requests=concurrent_collaborations,
                    concurrent_users=concurrent_collaborations,
                    method='POST',
                    data=collaboration_data
                )
                
                results[f"{concurrent_collaborations}_concurrent"] = {
                    'avg_response_time': metrics.avg_response_time,
                    'p95_response_time': metrics.p95_response_time,
                    'error_rate': metrics.error_rate,
                    'throughput': metrics.throughput
                }
            
            return results
    
    async def websocket_connection_test(self) -> Dict[str, Any]:
        """WebSocket连接压力测试"""
        logger.info("开始WebSocket连接压力测试")
        
        # 模拟WebSocket连接测试
        # 实际实现需要使用websockets库
        
        connection_results = []
        max_connections = 1000
        
        for num_connections in range(100, max_connections + 1, 100):
            start_time = time.time()
            
            # 模拟连接建立
            successful_connections = 0
            failed_connections = 0
            
            try:
                # 这里应该实现实际的WebSocket连接逻辑
                # 为了演示，我们模拟连接过程
                await asyncio.sleep(0.1 * num_connections / 100)  # 模拟连接时间
                successful_connections = num_connections
            except Exception:
                failed_connections = num_connections
            
            connection_time = time.time() - start_time
            
            connection_results.append({
                'num_connections': num_connections,
                'successful_connections': successful_connections,
                'failed_connections': failed_connections,
                'connection_time': connection_time,
                'success_rate': successful_connections / num_connections
            })
            
            # 如果成功率低于80%，停止测试
            if successful_connections / num_connections < 0.8:
                logger.warning("WebSocket连接成功率过低，停止测试")
                break
        
        return {'connection_results': connection_results}
    
    async def database_performance_test(self) -> Dict[str, Any]:
        """数据库性能测试"""
        logger.info("开始数据库性能测试")
        
        async with PerformanceTester(self.base_url) as tester:
            results = {}
            
            # 测试读操作性能
            read_metrics = await tester.concurrent_requests(
                "/api/v1/courses/",
                num_requests=1000,
                concurrent_users=50
            )
            
            results['read_performance'] = {
                'avg_response_time': read_metrics.avg_response_time,
                'throughput': read_metrics.throughput,
                'error_rate': read_metrics.error_rate
            }
            
            # 测试写操作性能
            course_data = {
                "title": "性能测试课程",
                "description": "数据库性能测试",
                "subject": "测试",
                "grade_level": "测试",
                "duration_weeks": 1
            }
            
            write_metrics = await tester.concurrent_requests(
                "/api/v1/courses/",
                num_requests=200,
                concurrent_users=20,
                method='POST',
                data=course_data
            )
            
            results['write_performance'] = {
                'avg_response_time': write_metrics.avg_response_time,
                'throughput': write_metrics.throughput,
                'error_rate': write_metrics.error_rate
            }
            
            return results


class PerformanceReporter:
    """性能测试报告生成器"""
    
    @staticmethod
    def generate_report(test_results: Dict[str, Any], output_file: str = "performance_report.html"):
        """生成性能测试报告"""
        logger.info(f"生成性能测试报告: {output_file}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PBL智能助手系统性能测试报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .success {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>PBL智能助手系统性能测试报告</h1>
            <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>测试摘要</h2>
            <div class="metric">
                <h3>整体性能指标</h3>
                {PerformanceReporter._format_summary(test_results)}
            </div>
            
            <h2>详细测试结果</h2>
            {PerformanceReporter._format_detailed_results(test_results)}
            
            <h2>性能建议</h2>
            {PerformanceReporter._generate_recommendations(test_results)}
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    @staticmethod
    def _format_summary(results: Dict[str, Any]) -> str:
        """格式化摘要信息"""
        summary_html = "<ul>"
        
        for test_name, test_data in results.items():
            if isinstance(test_data, dict) and 'avg_response_time' in test_data:
                response_time = test_data['avg_response_time']
                error_rate = test_data.get('error_rate', 0)
                
                status_class = "success" if response_time < 2000 and error_rate < 0.05 else "warning"
                if response_time > 5000 or error_rate > 0.1:
                    status_class = "error"
                
                summary_html += f"""
                <li class="{status_class}">
                    <strong>{test_name}</strong>: 
                    平均响应时间 {response_time:.2f}ms, 
                    错误率 {error_rate:.2%}
                </li>
                """
        
        summary_html += "</ul>"
        return summary_html
    
    @staticmethod
    def _format_detailed_results(results: Dict[str, Any]) -> str:
        """格式化详细结果"""
        detailed_html = ""
        
        for test_name, test_data in results.items():
            detailed_html += f"<h3>{test_name}</h3>"
            
            if isinstance(test_data, dict):
                detailed_html += "<table>"
                detailed_html += "<tr><th>指标</th><th>值</th></tr>"
                
                for key, value in test_data.items():
                    if isinstance(value, float):
                        if 'time' in key.lower():
                            formatted_value = f"{value:.2f} ms"
                        elif 'rate' in key.lower():
                            formatted_value = f"{value:.2%}"
                        else:
                            formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    
                    detailed_html += f"<tr><td>{key}</td><td>{formatted_value}</td></tr>"
                
                detailed_html += "</table>"
        
        return detailed_html
    
    @staticmethod
    def _generate_recommendations(results: Dict[str, Any]) -> str:
        """生成性能优化建议"""
        recommendations = []
        
        # 分析结果并生成建议
        for test_name, test_data in results.items():
            if isinstance(test_data, dict) and 'avg_response_time' in test_data:
                response_time = test_data['avg_response_time']
                error_rate = test_data.get('error_rate', 0)
                
                if response_time > 5000:
                    recommendations.append(f"⚠️ {test_name} 响应时间过长，建议优化数据库查询或增加缓存")
                
                if error_rate > 0.1:
                    recommendations.append(f"❌ {test_name} 错误率过高，需要检查系统稳定性")
                
                if response_time > 2000:
                    recommendations.append(f"🔧 {test_name} 可以考虑实施以下优化：异步处理、连接池优化、CDN部署")
        
        if not recommendations:
            recommendations.append("✅ 系统性能表现良好，继续保持监控")
        
        recommendations_html = "<ul>"
        for rec in recommendations:
            recommendations_html += f"<li>{rec}</li>"
        recommendations_html += "</ul>"
        
        return recommendations_html


async def run_complete_performance_test(base_url: str = "http://localhost:8000"):
    """运行完整的性能测试套件"""
    logger.info("开始完整性能测试套件")
    
    all_results = {}
    
    # 1. 基础API性能测试
    logger.info("=== 基础API性能测试 ===")
    async with PerformanceTester(base_url) as tester:
        # 课程列表API
        courses_metrics = await tester.concurrent_requests(
            "/api/v1/courses/", 
            num_requests=500, 
            concurrent_users=50
        )
        all_results['courses_api'] = {
            'avg_response_time': courses_metrics.avg_response_time,
            'p95_response_time': courses_metrics.p95_response_time,
            'error_rate': courses_metrics.error_rate,
            'throughput': courses_metrics.throughput
        }
        
        # 用户认证API
        auth_data = {"username": "testuser", "password": "testpass"}
        auth_metrics = await tester.concurrent_requests(
            "/api/v1/auth/login",
            num_requests=200,
            concurrent_users=20,
            method='POST',
            data=auth_data
        )
        all_results['auth_api'] = {
            'avg_response_time': auth_metrics.avg_response_time,
            'p95_response_time': auth_metrics.p95_response_time,
            'error_rate': auth_metrics.error_rate,
            'throughput': auth_metrics.throughput
        }
    
    # 2. 专门测试
    logger.info("=== 专门性能测试 ===")
    specialized = SpecializedTests(base_url)
    
    agent_results = await specialized.agent_collaboration_stress_test()
    all_results['agent_collaboration'] = agent_results
    
    websocket_results = await specialized.websocket_connection_test()
    all_results['websocket_performance'] = websocket_results
    
    db_results = await specialized.database_performance_test()
    all_results['database_performance'] = db_results
    
    # 3. 压力测试
    logger.info("=== 压力测试 ===")
    async with PerformanceTester(base_url) as tester:
        stress_results = await tester.stress_test("/api/v1/courses/", max_users=200, step_size=25)
        
        # 找到最高性能点
        best_performance = min(stress_results, key=lambda x: x.avg_response_time)
        all_results['stress_test'] = {
            'max_stable_users': len(stress_results) * 25,
            'best_avg_response_time': best_performance.avg_response_time,
            'best_throughput': best_performance.throughput,
            'peak_cpu_usage': max(best_performance.cpu_usage) if best_performance.cpu_usage else 0
        }
    
    # 4. 生成报告
    logger.info("=== 生成性能测试报告 ===")
    PerformanceReporter.generate_report(all_results)
    
    # 输出关键指标
    logger.info("=== 测试完成 - 关键指标 ===")
    for test_name, results in all_results.items():
        if isinstance(results, dict) and 'avg_response_time' in results:
            logger.info(f"{test_name}: {results['avg_response_time']:.2f}ms 平均响应时间")
    
    return all_results


if __name__ == "__main__":
    # 运行完整性能测试
    asyncio.run(run_complete_performance_test())