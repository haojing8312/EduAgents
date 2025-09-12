"""
用户数据模型
定义用户相关的数据库表结构
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.models.base import BaseModel


class UserRole(str, PyEnum):
    """用户角色枚举"""
    STUDENT = "student"           # 学生
    TEACHER = "teacher"           # 教师
    ADMIN = "admin"              # 管理员
    RESEARCHER = "researcher"     # 研究员
    GUEST = "guest"              # 访客


class UserStatus(str, PyEnum):
    """用户状态枚举"""
    ACTIVE = "active"            # 活跃
    INACTIVE = "inactive"        # 未激活
    SUSPENDED = "suspended"      # 暂停
    DELETED = "deleted"          # 已删除


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱地址"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    # 个人信息
    first_name = Column(
        String(50),
        nullable=True,
        comment="名"
    )
    
    last_name = Column(
        String(50),
        nullable=True,
        comment="姓"
    )
    
    display_name = Column(
        String(100),
        nullable=True,
        comment="显示名称"
    )
    
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="头像URL"
    )
    
    bio = Column(
        Text,
        nullable=True,
        comment="个人简介"
    )
    
    # 角色和权限
    role = Column(
        Enum(UserRole),
        default=UserRole.STUDENT,
        nullable=False,
        comment="用户角色"
    )
    
    status = Column(
        Enum(UserStatus),
        default=UserStatus.INACTIVE,
        nullable=False,
        comment="用户状态"
    )
    
    # 联系信息
    phone = Column(
        String(20),
        nullable=True,
        comment="电话号码"
    )
    
    organization = Column(
        String(200),
        nullable=True,
        comment="所属机构"
    )
    
    department = Column(
        String(100),
        nullable=True,
        comment="所属部门"
    )
    
    title = Column(
        String(100),
        nullable=True,
        comment="职位/头衔"
    )
    
    # 偏好设置
    preferences = Column(
        JSONB,
        nullable=True,
        comment="用户偏好设置"
    )
    
    # 激活和验证
    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="邮箱是否已验证"
    )
    
    email_verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="邮箱验证时间"
    )
    
    # 登录信息
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间"
    )
    
    last_login_ip = Column(
        String(45),
        nullable=True,
        comment="最后登录IP"
    )
    
    login_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="登录次数"
    )
    
    # 账户设置
    timezone = Column(
        String(50),
        default="UTC",
        nullable=False,
        comment="时区"
    )
    
    language = Column(
        String(10),
        default="zh-CN",
        nullable=False,
        comment="语言偏好"
    )
    
    # 安全设置
    two_factor_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否启用双因子认证"
    )
    
    two_factor_secret = Column(
        String(32),
        nullable=True,
        comment="双因子认证密钥"
    )
    
    # 密码重置
    reset_token = Column(
        String(255),
        nullable=True,
        comment="密码重置令牌"
    )
    
    reset_token_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="重置令牌过期时间"
    )
    
    @property
    def full_name(self) -> str:
        """获取全名"""
        if self.first_name and self.last_name:
            return f"{self.last_name}{self.first_name}"
        return self.display_name or self.username
    
    @property
    def is_active(self) -> bool:
        """检查用户是否活跃"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @property
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_teacher(self) -> bool:
        """检查是否为教师"""
        return self.role in [UserRole.TEACHER, UserRole.ADMIN]
    
    def can_access_agent(self, agent_name: str) -> bool:
        """检查是否可以访问指定智能体"""
        # 管理员可以访问所有智能体
        if self.is_admin:
            return True
        
        # 根据角色和智能体类型判断权限
        role_permissions = {
            UserRole.TEACHER: [
                "education_director",
                "pbl_curriculum_designer", 
                "learning_experience_designer",
                "creative_technologist",
                "makerspace_manager"
            ],
            UserRole.STUDENT: [
                "learning_experience_designer",
                "creative_technologist"
            ],
            UserRole.RESEARCHER: [
                "education_director",
                "pbl_curriculum_designer",
                "learning_experience_designer"
            ],
            UserRole.GUEST: [
                "learning_experience_designer"
            ]
        }
        
        allowed_agents = role_permissions.get(self.role, [])
        return agent_name in allowed_agents
    
    def update_login_info(self, ip_address: str = None):
        """更新登录信息"""
        from datetime import datetime
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
        self.login_count += 1
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class UserSession(BaseModel):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="会话令牌"
    )
    
    device_info = Column(
        JSONB,
        nullable=True,
        comment="设备信息"
    )
    
    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP地址"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="过期时间"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否活跃"
    )
    
    # 关系
    # user = relationship("User", backref="sessions")
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    def revoke(self):
        """撤销会话"""
        self.is_active = False


class UserPreference(BaseModel):
    """用户偏好设置模型"""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    category = Column(
        String(50),
        nullable=False,
        comment="设置分类"
    )
    
    key = Column(
        String(100),
        nullable=False,
        comment="设置键"
    )
    
    value = Column(
        JSONB,
        nullable=True,
        comment="设置值"
    )
    
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为默认值"
    )
    
    # 关系
    # user = relationship("User", backref="user_preferences")
    
    __table_args__ = (
        # 复合唯一索引
        Index('idx_user_preference', 'user_id', 'category', 'key', unique=True),
    )