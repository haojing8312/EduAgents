"""
协作相关的Pydantic模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ..services.collaboration_service import CollaboratorRole, Permission, ShareScope


class AddCollaboratorRequest(BaseModel):
    """添加协作者请求"""

    user_id: UUID = Field(..., description="用户ID")
    role: CollaboratorRole = Field(..., description="协作者角色")
    permissions: Optional[List[Permission]] = Field(None, description="自定义权限")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "editor",
                "permissions": ["view", "edit", "comment"],
            }
        }


class UpdateCollaboratorRoleRequest(BaseModel):
    """更新协作者角色请求"""

    new_role: CollaboratorRole = Field(..., description="新角色")

    class Config:
        schema_extra = {"example": {"new_role": "contributor"}}


class CollaboratorResponse(BaseModel):
    """协作者响应"""

    user_id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    profile: Optional[Dict[str, Any]] = Field(None, description="用户资料")
    role: CollaboratorRole = Field(..., description="角色")
    permissions: List[str] = Field(..., description="权限列表")
    added_at: Optional[str] = Field(None, description="添加时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "张老师",
                "email": "zhang@example.com",
                "profile": {
                    "avatar": "https://example.com/avatar.jpg",
                    "bio": "数学教师",
                },
                "role": "editor",
                "permissions": ["view", "edit", "comment"],
                "added_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
            }
        }


class ShareCourseRequest(BaseModel):
    """分享课程请求"""

    share_scope: ShareScope = Field(..., description="分享范围")
    share_settings: Dict[str, Any] = Field(default_factory=dict, description="分享设置")

    class Config:
        schema_extra = {
            "example": {
                "share_scope": "public",
                "share_settings": {
                    "allow_copy": True,
                    "allow_export": True,
                    "require_attribution": True,
                    "expiry_date": "2024-12-31T23:59:59Z",
                },
            }
        }


class ShareCourseResponse(BaseModel):
    """分享课程响应"""

    course_id: UUID = Field(..., description="课程ID")
    share_scope: str = Field(..., description="分享范围")
    share_token: Optional[str] = Field(None, description="分享令牌")
    share_url: str = Field(..., description="分享链接")
    message: str = Field(..., description="消息")

    class Config:
        schema_extra = {
            "example": {
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "share_scope": "public",
                "share_token": "abc123def456",
                "share_url": "http://localhost:3000/shared/courses/123e4567-e89b-12d3-a456-426614174000?token=abc123def456",
                "message": "课程分享成功",
            }
        }


class CopyCourseRequest(BaseModel):
    """复制课程请求"""

    source_course_id: UUID = Field(..., description="源课程ID")
    new_title: Optional[str] = Field(None, description="新课程标题")

    class Config:
        schema_extra = {
            "example": {
                "source_course_id": "123e4567-e89b-12d3-a456-426614174000",
                "new_title": "我的STEM项目 (副本)",
            }
        }


class CollaborationInviteRequest(BaseModel):
    """协作邀请请求"""

    role: CollaboratorRole = Field(..., description="邀请角色")
    email: Optional[EmailStr] = Field(None, description="邀请邮箱")
    expires_in_days: int = Field(default=7, ge=1, le=30, description="有效期（天）")

    class Config:
        schema_extra = {
            "example": {
                "role": "contributor",
                "email": "invite@example.com",
                "expires_in_days": 7,
            }
        }


class CollaborationInviteResponse(BaseModel):
    """协作邀请响应"""

    invite_token: str = Field(..., description="邀请令牌")
    invite_url: str = Field(..., description="邀请链接")
    expires_at: datetime = Field(..., description="过期时间")
    role: str = Field(..., description="邀请角色")
    message: str = Field(..., description="消息")

    class Config:
        schema_extra = {
            "example": {
                "invite_token": "inv_abc123def456",
                "invite_url": "http://localhost:3000/invites/inv_abc123def456",
                "expires_at": "2024-01-08T10:00:00Z",
                "role": "contributor",
                "message": "邀请生成成功",
            }
        }


class CourseActivityLog(BaseModel):
    """课程活动日志"""

    activity_id: str = Field(..., description="活动ID")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    action: str = Field(..., description="操作类型")
    details: str = Field(..., description="操作详情")
    timestamp: datetime = Field(..., description="时间戳")
    changes: Optional[Dict[str, Any]] = Field(None, description="变更内容")

    class Config:
        schema_extra = {
            "example": {
                "activity_id": "act_123456",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "张老师",
                "action": "编辑课程",
                "details": "更新了学习目标",
                "timestamp": "2024-01-01T10:00:00Z",
                "changes": {
                    "field": "learning_objectives",
                    "old_value": ["目标1", "目标2"],
                    "new_value": ["目标1", "目标2", "目标3"],
                },
            }
        }


class SharedCourseInfo(BaseModel):
    """共享课程信息"""

    course_id: UUID = Field(..., description="课程ID")
    title: str = Field(..., description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")
    subject: str = Field(..., description="学科")
    education_level: str = Field(..., description="教育学段")
    user_role: Optional[str] = Field(None, description="用户角色")
    share_scope: Optional[str] = Field(None, description="分享范围")
    shared_at: Optional[str] = Field(None, description="分享时间")
    quality_score: Optional[float] = Field(None, description="质量评分")

    class Config:
        schema_extra = {
            "example": {
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "环保主题STEM项目",
                "description": "基于环保问题的跨学科项目学习",
                "subject": "science",
                "education_level": "junior",
                "user_role": "viewer",
                "share_scope": "public",
                "shared_at": "2024-01-01T10:00:00Z",
                "quality_score": 85.5,
            }
        }


class CollaborationPermissions(BaseModel):
    """协作权限"""

    course_id: UUID = Field(..., description="课程ID")
    user_id: UUID = Field(..., description="用户ID")
    permissions: Dict[str, bool] = Field(..., description="权限映射")

    class Config:
        schema_extra = {
            "example": {
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "permissions": {
                    "view": True,
                    "edit": True,
                    "comment": True,
                    "manage": False,
                    "export": True,
                    "share": False,
                },
            }
        }


class CollaborationStatistics(BaseModel):
    """协作统计"""

    total_collaborations: int = Field(..., description="总协作数")
    role_distribution: Dict[str, int] = Field(..., description="角色分布")
    recent_activity_count: int = Field(..., description="最近活动数")
    most_active_role: Optional[str] = Field(None, description="最活跃角色")

    class Config:
        schema_extra = {
            "example": {
                "total_collaborations": 15,
                "role_distribution": {
                    "owner": 3,
                    "editor": 8,
                    "contributor": 2,
                    "viewer": 2,
                },
                "recent_activity_count": 5,
                "most_active_role": "editor",
            }
        }


class CollaborationSummary(BaseModel):
    """协作摘要"""

    course_id: UUID = Field(..., description="课程ID")
    title: str = Field(..., description="课程标题")
    my_role: str = Field(..., description="我的角色")
    collaborator_count: int = Field(..., description="协作者数量")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")
    quality_score: Optional[float] = Field(None, description="质量评分")

    class Config:
        schema_extra = {
            "example": {
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "环保主题STEM项目",
                "my_role": "editor",
                "collaborator_count": 3,
                "last_activity": "2024-01-01T15:30:00Z",
                "quality_score": 85.5,
            }
        }


class TeamCollaboration(BaseModel):
    """团队协作"""

    team_id: UUID = Field(..., description="团队ID")
    team_name: str = Field(..., description="团队名称")
    courses: List[CollaborationSummary] = Field(..., description="团队课程")
    members: List[CollaboratorResponse] = Field(..., description="团队成员")

    class Config:
        schema_extra = {
            "example": {
                "team_id": "123e4567-e89b-12d3-a456-426614174000",
                "team_name": "数学教研组",
                "courses": [],
                "members": [],
            }
        }


class AccessRequest(BaseModel):
    """访问请求"""

    course_id: UUID = Field(..., description="课程ID")
    requested_role: CollaboratorRole = Field(..., description="请求角色")
    message: Optional[str] = Field(None, description="请求消息")

    class Config:
        schema_extra = {
            "example": {
                "course_id": "123e4567-e89b-12d3-a456-426614174000",
                "requested_role": "viewer",
                "message": "希望参考这个优秀的课程设计",
            }
        }


class AccessRequestResponse(BaseModel):
    """访问请求响应"""

    request_id: UUID = Field(..., description="请求ID")
    course_id: UUID = Field(..., description="课程ID")
    course_title: str = Field(..., description="课程标题")
    requester_id: UUID = Field(..., description="请求者ID")
    requester_name: str = Field(..., description="请求者姓名")
    requested_role: str = Field(..., description="请求角色")
    message: Optional[str] = Field(None, description="请求消息")
    status: str = Field(..., description="状态")  # pending, approved, rejected
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "course_id": "123e4567-e89b-12d3-a456-426614174001",
                "course_title": "环保主题STEM项目",
                "requester_id": "123e4567-e89b-12d3-a456-426614174002",
                "requester_name": "李老师",
                "requested_role": "viewer",
                "message": "希望参考这个优秀的课程设计",
                "status": "pending",
                "created_at": "2024-01-01T10:00:00Z",
            }
        }


class BulkCollaboratorOperation(BaseModel):
    """批量协作者操作"""

    operation: str = Field(..., description="操作类型")  # add, remove, update_role
    collaborators: List[Dict[str, Any]] = Field(..., description="协作者列表")

    class Config:
        schema_extra = {
            "example": {
                "operation": "add",
                "collaborators": [
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "role": "editor",
                    },
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174001",
                        "role": "viewer",
                    },
                ],
            }
        }
