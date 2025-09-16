"""
数据库基础模型
提供通用的模型基类和审计字段
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql import func
from app.core.config import get_settings


@as_declarative()
class Base:
    """数据库模型基类"""

    # 通用字段
    id: Any
    __name__: str

    # 生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名（类名的蛇形命名）"""
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    # 配置schema
    @declared_attr
    def __table_args__(cls):
        """配置表参数，包括schema"""
        settings = get_settings()
        return {"schema": settings.POSTGRES_SCHEMA}


class BaseModel(Base):
    """基础模型类，包含审计字段"""

    __abstract__ = True

    # 主键使用UUID
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="主键ID"
    )

    # 审计字段
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )

    created_by = Column(UUID(as_uuid=True), nullable=True, comment="创建人ID")

    updated_by = Column(UUID(as_uuid=True), nullable=True, comment="更新人ID")

    is_deleted = Column(
        Boolean, default=False, nullable=False, comment="是否已删除（软删除）"
    )

    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    version = Column(
        "version", Integer, default=1, nullable=False, comment="版本号（乐观锁）"
    )

    # 扩展字段（JSON）
    metadata = Column(JSON, nullable=True, comment="扩展元数据")

    def __repr__(self) -> str:
        """对象字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self, exclude: set = None) -> Dict[str, Any]:
        """转换为字典"""
        exclude = exclude or set()
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """从字典创建实例"""
        # 过滤掉不存在的字段
        valid_fields = {c.name for c in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class TimestampMixin:
    """时间戳混入类"""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class SoftDeleteMixin:
    """软删除混入类"""

    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否已删除")

    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None
