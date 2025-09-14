"""
系统监控和告警模块
集成Prometheus、Grafana和Sentry
"""
import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aioredis
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import sentry_sdk
from sentry_sdk import capture_exception, capture_message
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


@dataclass
class Alert:
    """告警数据类"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SystemHealth:
    """系统健康状态"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time_p95: float
    error_rate: float
    agent_status: Dict[str, bool]
    database_status: bool
    cache_status: bool
    timestamp: datetime


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_metrics()
        
    def _setup_metrics(self):
        """设置Prometheus指标"""
        # API请求指标
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # 系统资源指标
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        # 智能体指标
        self.agent_requests_total = Counter(
            'agent_requests_total',
            'Total agent requests',
            ['agent_type', 'status'],
            registry=self.registry
        )
        
        self.agent_response_time = Histogram(
            'agent_response_time_seconds',
            'Agent response time',
            ['agent_type'],
            registry=self.registry
        )
        
        self.agent_collaboration_duration = Histogram(
            'agent_collaboration_duration_seconds',
            'Agent collaboration duration',
            ['collaboration_type'],
            registry=self.registry
        )
        
        # 数据库指标
        self.db_connections_active = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            registry=self.registry
        )
        
        # WebSocket指标
        self.websocket_connections = Gauge(
            'websocket_connections_total',
            'Total WebSocket connections',
            registry=self.registry
        )
        
        self.websocket_messages = Counter(
            'websocket_messages_total',
            'Total WebSocket messages',
            ['type', 'direction'],
            registry=self.registry
        )
    
    def record_api_request(self, method: str, endpoint: str, status: str, duration: float):
        """记录API请求指标"""
        self.api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_system_resource(self, cpu: float, memory: float, disk: float):
        """记录系统资源使用情况"""
        self.cpu_usage.set(cpu)
        self.memory_usage.set(memory)
        self.disk_usage.set(disk)
    
    def record_agent_request(self, agent_type: str, status: str, duration: float):
        """记录智能体请求指标"""
        self.agent_requests_total.labels(agent_type=agent_type, status=status).inc()
        self.agent_response_time.labels(agent_type=agent_type).observe(duration)
    
    def record_collaboration(self, collaboration_type: str, duration: float):
        """记录智能体协作指标"""
        self.agent_collaboration_duration.labels(collaboration_type=collaboration_type).observe(duration)
    
    def record_database_metrics(self, active_connections: int, query_type: str, query_duration: float):
        """记录数据库指标"""
        self.db_connections_active.set(active_connections)
        self.db_query_duration.labels(query_type=query_type).observe(query_duration)
    
    def record_websocket_metrics(self, connections: int, message_type: str, direction: str):
        """记录WebSocket指标"""
        self.websocket_connections.set(connections)
        self.websocket_messages.labels(type=message_type, direction=direction).inc()
    
    def get_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        return generate_latest(self.registry).decode('utf-8')


class AlertManager:
    """告警管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_rules = self._setup_alert_rules()
        self.notification_handlers: List[Callable] = []
        
    async def initialize(self):
        """初始化Redis连接"""
        self.redis = await aioredis.from_url(self.redis_url)
        
    async def close(self):
        """关闭Redis连接"""
        if self.redis:
            await self.redis.close()
    
    def _setup_alert_rules(self) -> Dict[str, Dict]:
        """设置告警规则"""
        return {
            'high_cpu_usage': {
                'name': 'CPU使用率过高',
                'description': 'CPU使用率超过阈值',
                'threshold': 80.0,
                'severity': AlertSeverity.HIGH,
                'metric': 'cpu_usage'
            },
            'high_memory_usage': {
                'name': '内存使用率过高',
                'description': '内存使用率超过阈值',
                'threshold': 85.0,
                'severity': AlertSeverity.HIGH,
                'metric': 'memory_usage'
            },
            'high_error_rate': {
                'name': 'API错误率过高',
                'description': 'API错误率超过阈值',
                'threshold': 5.0,  # 5%
                'severity': AlertSeverity.CRITICAL,
                'metric': 'error_rate'
            },
            'slow_response_time': {
                'name': '响应时间过长',
                'description': 'API响应时间P95超过阈值',
                'threshold': 5000.0,  # 5秒
                'severity': AlertSeverity.MEDIUM,
                'metric': 'response_time_p95'
            },
            'agent_failure': {
                'name': '智能体故障',
                'description': '智能体服务不可用',
                'threshold': 1.0,
                'severity': AlertSeverity.CRITICAL,
                'metric': 'agent_status'
            },
            'database_connection_failure': {
                'name': '数据库连接故障',
                'description': '数据库连接不可用',
                'threshold': 1.0,
                'severity': AlertSeverity.CRITICAL,
                'metric': 'database_status'
            }
        }
    
    async def check_alerts(self, health_data: SystemHealth):
        """检查告警条件"""
        current_time = datetime.now()
        
        for rule_id, rule in self.alert_rules.items():
            metric_name = rule['metric']
            threshold = rule['threshold']
            
            # 获取当前指标值
            current_value = getattr(health_data, metric_name, None)
            if current_value is None:
                continue
            
            alert_triggered = False
            
            # 检查不同类型的阈值条件
            if metric_name in ['cpu_usage', 'memory_usage', 'error_rate', 'response_time_p95']:
                alert_triggered = current_value > threshold
            elif metric_name in ['agent_status', 'database_status']:
                if isinstance(current_value, bool):
                    alert_triggered = not current_value
                elif isinstance(current_value, dict):
                    alert_triggered = not all(current_value.values())
            
            if alert_triggered:
                await self._trigger_alert(rule_id, rule, current_value, current_time)
            else:
                await self._resolve_alert(rule_id, current_time)
    
    async def _trigger_alert(self, rule_id: str, rule: Dict, current_value: Any, timestamp: datetime):
        """触发告警"""
        if rule_id not in self.active_alerts:
            alert = Alert(
                id=rule_id,
                name=rule['name'],
                description=rule['description'],
                severity=rule['severity'],
                threshold=rule['threshold'],
                current_value=current_value,
                timestamp=timestamp
            )
            
            self.active_alerts[rule_id] = alert
            
            # 存储到Redis
            await self.redis.setex(
                f"alert:{rule_id}",
                3600,  # 1小时过期
                json.dumps(alert.to_dict(), default=str)
            )
            
            # 发送通知
            await self._send_notifications(alert)
            
            logger.warning(f"告警触发: {alert.name} - 当前值: {current_value}, 阈值: {rule['threshold']}")
        else:
            # 更新现有告警
            self.active_alerts[rule_id].current_value = current_value
            self.active_alerts[rule_id].timestamp = timestamp
    
    async def _resolve_alert(self, rule_id: str, timestamp: datetime):
        """解决告警"""
        if rule_id in self.active_alerts:
            alert = self.active_alerts[rule_id]
            alert.resolved = True
            alert.resolved_at = timestamp
            
            # 从Redis删除
            await self.redis.delete(f"alert:{rule_id}")
            
            # 发送解决通知
            await self._send_resolution_notification(alert)
            
            # 从活跃告警中移除
            del self.active_alerts[rule_id]
            
            logger.info(f"告警解决: {alert.name}")
    
    def add_notification_handler(self, handler: Callable):
        """添加通知处理器"""
        self.notification_handlers.append(handler)
    
    async def _send_notifications(self, alert: Alert):
        """发送告警通知"""
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"发送告警通知失败: {e}")
    
    async def _send_resolution_notification(self, alert: Alert):
        """发送告警解决通知"""
        for handler in self.notification_handlers:
            try:
                if hasattr(handler, 'send_resolution'):
                    await handler.send_resolution(alert)
            except Exception as e:
                logger.error(f"发送解决通知失败: {e}")
    
    async def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, services_config: Dict[str, str]):
        self.services_config = services_config
        
    async def check_system_health(self) -> SystemHealth:
        """检查系统健康状态"""
        import psutil
        
        # 系统资源
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 网络连接数
        connections = len(psutil.net_connections())
        
        # 检查各种服务状态
        agent_status = await self._check_agent_status()
        database_status = await self._check_database_status()
        cache_status = await self._check_cache_status()
        
        # 获取性能指标
        response_time_p95 = await self._get_response_time_p95()
        error_rate = await self._get_error_rate()
        
        return SystemHealth(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            active_connections=connections,
            response_time_p95=response_time_p95,
            error_rate=error_rate,
            agent_status=agent_status,
            database_status=database_status,
            cache_status=cache_status,
            timestamp=datetime.now()
        )
    
    async def _check_agent_status(self) -> Dict[str, bool]:
        """检查智能体状态"""
        agents = [
            'education_director', 'learning_designer', 'creative_technologist',
            'assessment_specialist', 'community_coordinator'
        ]
        
        status = {}
        for agent in agents:
            try:
                # 模拟健康检查请求
                url = f"{self.services_config.get('agent_service')}/health/{agent}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        status[agent] = response.status == 200
            except Exception:
                status[agent] = False
        
        return status
    
    async def _check_database_status(self) -> bool:
        """检查数据库状态"""
        try:
            # 这里应该实际检查数据库连接
            # 简化示例
            return True
        except Exception:
            return False
    
    async def _check_cache_status(self) -> bool:
        """检查缓存状态"""
        try:
            # 这里应该实际检查Redis连接
            # 简化示例
            return True
        except Exception:
            return False
    
    async def _get_response_time_p95(self) -> float:
        """获取API响应时间P95"""
        try:
            # 从Prometheus查询P95响应时间
            # 简化示例
            return 1500.0  # ms
        except Exception:
            return 0.0
    
    async def _get_error_rate(self) -> float:
        """获取错误率"""
        try:
            # 从Prometheus查询错误率
            # 简化示例
            return 2.5  # %
        except Exception:
            return 0.0


class NotificationHandlers:
    """通知处理器集合"""
    
    @staticmethod
    async def slack_notification(alert: Alert):
        """Slack通知"""
        webhook_url = "YOUR_SLACK_WEBHOOK_URL"
        
        severity_colors = {
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.MEDIUM: "#ff9500",
            AlertSeverity.HIGH: "#ff0000",
            AlertSeverity.CRITICAL: "#8b0000"
        }
        
        payload = {
            "attachments": [{
                "color": severity_colors.get(alert.severity, "#ff0000"),
                "title": f"🚨 {alert.name}",
                "text": alert.description,
                "fields": [
                    {"title": "严重级别", "value": alert.severity.value, "short": True},
                    {"title": "当前值", "value": str(alert.current_value), "short": True},
                    {"title": "阈值", "value": str(alert.threshold), "short": True},
                    {"title": "时间", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                ]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Slack通知发送失败: {response.status}")
        except Exception as e:
            logger.error(f"Slack通知发送异常: {e}")
    
    @staticmethod
    async def email_notification(alert: Alert):
        """邮件通知"""
        # 这里应该实现邮件发送逻辑
        # 使用SMTP或邮件服务API
        logger.info(f"邮件通知: {alert.name}")
    
    @staticmethod
    async def webhook_notification(alert: Alert):
        """Webhook通知"""
        webhook_url = "YOUR_WEBHOOK_URL"
        
        payload = alert.to_dict()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Webhook通知发送失败: {response.status}")
        except Exception as e:
            logger.error(f"Webhook通知发送异常: {e}")


class SentryIntegration:
    """Sentry错误监控集成"""
    
    @staticmethod
    def initialize(dsn: str, environment: str = "production"):
        """初始化Sentry"""
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # 捕获info及以上级别的日志
            event_level=logging.ERROR  # 发送error及以上级别的日志作为事件
        )
        
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                sentry_logging,
                AsyncioIntegration(auto_enabling_integrations=False)
            ],
            environment=environment,
            traces_sample_rate=0.1,  # 10%的性能追踪采样率
            profiles_sample_rate=0.1,  # 10%的性能分析采样率
        )
    
    @staticmethod
    def capture_agent_error(agent_type: str, error: Exception, context: Dict[str, Any] = None):
        """捕获智能体错误"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("agent_type", agent_type)
            scope.set_context("agent_context", context or {})
            capture_exception(error)
    
    @staticmethod
    def capture_performance_issue(metric_name: str, value: float, threshold: float):
        """捕获性能问题"""
        message = f"性能指标超过阈值: {metric_name} = {value}, 阈值 = {threshold}"
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("metric_type", "performance")
            scope.set_extra("metric_name", metric_name)
            scope.set_extra("current_value", value)
            scope.set_extra("threshold", threshold)
            capture_message(message, level="warning")


class MonitoringSystem:
    """监控系统主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(config.get('redis_url', 'redis://localhost:6379'))
        self.health_checker = HealthChecker(config.get('services', {}))
        self.monitoring = False
        
        # 设置Sentry
        if config.get('sentry_dsn'):
            SentryIntegration.initialize(
                config['sentry_dsn'],
                config.get('environment', 'production')
            )
        
        # 设置通知处理器
        self._setup_notification_handlers()
    
    def _setup_notification_handlers(self):
        """设置通知处理器"""
        if self.config.get('slack_webhook'):
            self.alert_manager.add_notification_handler(NotificationHandlers.slack_notification)
        
        if self.config.get('email_enabled'):
            self.alert_manager.add_notification_handler(NotificationHandlers.email_notification)
        
        if self.config.get('webhook_url'):
            self.alert_manager.add_notification_handler(NotificationHandlers.webhook_notification)
    
    async def start(self):
        """启动监控系统"""
        logger.info("启动监控系统")
        await self.alert_manager.initialize()
        self.monitoring = True
        
        # 启动监控循环
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """停止监控系统"""
        logger.info("停止监控系统")
        self.monitoring = False
        await self.alert_manager.close()
    
    async def _monitoring_loop(self):
        """监控主循环"""
        while self.monitoring:
            try:
                # 收集健康状态数据
                health_data = await self.health_checker.check_system_health()
                
                # 更新Prometheus指标
                self.metrics_collector.record_system_resource(
                    health_data.cpu_usage,
                    health_data.memory_usage,
                    health_data.disk_usage
                )
                
                # 检查告警条件
                await self.alert_manager.check_alerts(health_data)
                
                # 记录健康数据到日志
                logger.info(f"系统健康检查完成 - CPU: {health_data.cpu_usage:.1f}%, "
                           f"内存: {health_data.memory_usage:.1f}%, "
                           f"响应时间P95: {health_data.response_time_p95:.1f}ms")
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                SentryIntegration.capture_agent_error("monitoring_system", e)
            
            # 等待下一次检查
            await asyncio.sleep(self.config.get('check_interval', 60))  # 默认60秒检查一次
    
    def get_metrics_endpoint(self):
        """获取Prometheus指标端点"""
        return self.metrics_collector.get_metrics()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        health_data = await self.health_checker.check_system_health()
        active_alerts = await self.alert_manager.get_active_alerts()
        
        return {
            'health': asdict(health_data),
            'active_alerts': [alert.to_dict() for alert in active_alerts],
            'metrics_available': True,
            'monitoring_active': self.monitoring
        }


# 使用示例
async def main():
    """主函数示例"""
    config = {
        'redis_url': 'redis://localhost:6379',
        'sentry_dsn': 'YOUR_SENTRY_DSN',
        'slack_webhook': 'YOUR_SLACK_WEBHOOK_URL',
        'environment': 'production',
        'check_interval': 30,
        'services': {
            'agent_service': 'http://localhost:8000',
            'database_url': 'postgresql://localhost:5432/pbl',
            'redis_url': 'redis://localhost:6379'
        }
    }
    
    monitoring = MonitoringSystem(config)
    await monitoring.start()
    
    # 运行一段时间后停止
    await asyncio.sleep(300)  # 5分钟
    await monitoring.stop()


if __name__ == "__main__":
    asyncio.run(main())