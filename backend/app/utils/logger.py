"""
日志配置模块
提供结构化日志配置
"""

import logging
import sys
from typing import Any, Dict

from ..core.config import settings


def setup_logging():
    """设置日志配置"""

    # 设置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 创建格式器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # 设置特定日志器的级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # 在开发环境中显示更多信息
    if settings.ENVIRONMENT == "development":
        logging.getLogger("app").setLevel(logging.DEBUG)


class StructuredLogger:
    """结构化日志器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        """信息日志"""
        extra = self._format_extra(kwargs)
        self.logger.info(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        extra = self._format_extra(kwargs)
        self.logger.debug(message, extra=extra)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        extra = self._format_extra(kwargs)
        self.logger.warning(message, extra=extra)

    def error(self, message: str, **kwargs):
        """错误日志"""
        extra = self._format_extra(kwargs)
        self.logger.error(message, extra=extra)

    def _format_extra(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """格式化额外信息"""
        return {f"extra_{k}": v for k, v in kwargs.items()}


def get_logger(name: str) -> StructuredLogger:
    """获取结构化日志器"""
    return StructuredLogger(name)