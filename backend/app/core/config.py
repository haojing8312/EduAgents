"""
核心配置模块
统一管理应用的所有配置项，支持多环境配置和环境变量覆盖
"""

import os
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "PBL智能助手"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # API配置
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS配置
    ALLOWED_HOSTS: str = Field(default="*", env="ALLOWED_HOSTS")

    @property
    def ALLOWED_HOSTS_LIST(self) -> List[str]:
        """Convert ALLOWED_HOSTS string to list"""
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    # 数据库配置
    # PostgreSQL
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="pbl_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="pbl_assistant", env="POSTGRES_DB")

    @property
    def DATABASE_URL(self) -> str:
        """构建数据库连接URL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis配置
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_CACHE_DB: int = Field(default=1, env="REDIS_CACHE_DB")
    REDIS_SESSION_DB: int = Field(default=2, env="REDIS_SESSION_DB")

    @property
    def REDIS_URL(self) -> str:
        """构建Redis连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def REDIS_CACHE_URL(self) -> str:
        """Redis缓存连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return (
            f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_CACHE_DB}"
        )

    @property
    def REDIS_SESSION_URL(self) -> str:
        """Redis会话连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return (
            f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_SESSION_DB}"
        )

    # ChromaDB配置
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")
    CHROMA_COLLECTION_NAME: str = Field(
        default="pbl_knowledge", env="CHROMA_COLLECTION_NAME"
    )

    @property
    def CHROMA_URL(self) -> str:
        """ChromaDB连接URL"""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"

    # 大语言模型配置
    LLM_PROVIDER: str = Field(
        default="openai", env="LLM_PROVIDER"
    )  # openai, anthropic, azure

    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_API_BASE: Optional[str] = Field(default=None, env="OPENAI_API_BASE")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-large", env="OPENAI_EMBEDDING_MODEL"
    )

    # Anthropic配置
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-opus-20240229", env="ANTHROPIC_MODEL"
    )

    # Azure OpenAI配置
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_ENDPOINT"
    )
    AZURE_OPENAI_API_KEY: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_API_KEY"
    )
    AZURE_OPENAI_API_VERSION: str = Field(
        default="2024-02-15-preview", env="AZURE_OPENAI_API_VERSION"
    )

    # 智能体配置
    AGENT_MAX_TOKENS: int = Field(default=4000, env="AGENT_MAX_TOKENS")
    AGENT_TEMPERATURE: float = Field(default=0.7, env="AGENT_TEMPERATURE")
    AGENT_TIMEOUT_SECONDS: int = Field(default=60, env="AGENT_TIMEOUT_SECONDS")
    AGENT_MAX_RETRIES: int = Field(default=3, env="AGENT_MAX_RETRIES")

    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(
        default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL"
    )
    WEBSOCKET_MAX_CONNECTIONS: int = Field(
        default=1000, env="WEBSOCKET_MAX_CONNECTIONS"
    )
    WEBSOCKET_MESSAGE_MAX_SIZE: int = Field(
        default=1024 * 1024, env="WEBSOCKET_MESSAGE_MAX_SIZE"
    )  # 1MB

    # 文件上传配置
    UPLOAD_MAX_SIZE: int = Field(
        default=10 * 1024 * 1024, env="UPLOAD_MAX_SIZE"
    )  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: str = Field(
        default=".jpg,.jpeg,.png,.gif,.pdf,.docx,.txt,.md",
        env="UPLOAD_ALLOWED_EXTENSIONS",
    )

    @property
    def UPLOAD_ALLOWED_EXTENSIONS_LIST(self) -> List[str]:
        """Convert UPLOAD_ALLOWED_EXTENSIONS string to list"""
        return [ext.strip() for ext in self.UPLOAD_ALLOWED_EXTENSIONS.split(",")]

    # 对象存储配置（支持本地存储和云存储）
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, minio
    STORAGE_LOCAL_PATH: str = Field(default="./uploads", env="STORAGE_LOCAL_PATH")

    # S3/MinIO配置
    S3_ENDPOINT: Optional[str] = Field(default=None, env="S3_ENDPOINT")
    S3_ACCESS_KEY: Optional[str] = Field(default=None, env="S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = Field(default=None, env="S3_SECRET_KEY")
    S3_BUCKET_NAME: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")

    # 缓存配置
    CACHE_TTL_SHORT: int = Field(default=300, env="CACHE_TTL_SHORT")  # 5分钟
    CACHE_TTL_MEDIUM: int = Field(default=1800, env="CACHE_TTL_MEDIUM")  # 30分钟
    CACHE_TTL_LONG: int = Field(default=3600, env="CACHE_TTL_LONG")  # 1小时

    # 速率限制配置
    RATE_LIMIT_CALLS: int = Field(default=100, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # 秒

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")  # json, text
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")

    # 监控配置
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")

    # Sentry配置（错误监控）
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # 邮件配置（可选）
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")

    # 任务队列配置
    TASK_QUEUE_NAME: str = Field(default="pbl_tasks", env="TASK_QUEUE_NAME")
    TASK_MAX_WORKERS: int = Field(default=4, env="TASK_MAX_WORKERS")
    TASK_RETRY_DELAY: int = Field(default=60, env="TASK_RETRY_DELAY")  # 秒

    # 开发配置
    RELOAD_ON_CHANGE: bool = Field(default=True, env="RELOAD_ON_CHANGE")

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        if v not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be development, staging, or production")
        return v

    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        if v not in ["openai", "anthropic", "azure"]:
            raise ValueError("LLM_PROVIDER must be openai, anthropic, or azure")
        return v

    @field_validator("STORAGE_TYPE")
    @classmethod
    def validate_storage_type(cls, v: str) -> str:
        if v not in ["local", "s3", "minio"]:
            raise ValueError("STORAGE_TYPE must be local, s3, or minio")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()


# 环境特定配置
class DevelopmentSettings(Settings):
    """开发环境配置"""

    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    RELOAD_ON_CHANGE: bool = True


class ProductionSettings(Settings):
    """生产环境配置"""

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    RELOAD_ON_CHANGE: bool = False

    # 生产环境安全配置
    ALLOWED_HOSTS: str = Field(env="ALLOWED_HOSTS")

    @field_validator("ALLOWED_HOSTS")
    @classmethod
    def validate_allowed_hosts_in_production(cls, v):
        if v == "*":
            raise ValueError("ALLOWED_HOSTS cannot be * in production")
        return v


def get_environment_settings() -> Settings:
    """根据环境变量获取对应配置"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionSettings()
    elif env == "development":
        return DevelopmentSettings()
    else:
        return Settings()
