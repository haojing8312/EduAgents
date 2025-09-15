"""
课程协作API接口
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import get_current_user
from ...core.database import get_db
from ...models.user import User
from ...schemas.collaboration import (
    AddCollaboratorRequest,
    CollaborationInviteRequest,
    CollaborationInviteResponse,
    CollaboratorResponse,
    CopyCourseRequest,
    CourseActivityLog,
    ShareCourseRequest,
    ShareCourseResponse,
    UpdateCollaboratorRoleRequest,
)
from ...services.collaboration_service import (
    CollaboratorRole,
    Permission,
    ShareScope,
    collaboration_service,
)

router = APIRouter(prefix="/collaboration", tags=["课程协作"])


@router.post("/{course_id}/collaborators", response_model=Dict[str, Any])
async def add_collaborator(
    course_id: UUID = Path(..., description="课程ID"),
    request: AddCollaboratorRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加协作者"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.MANAGE
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有管理权限")

    try:
        result = await collaboration_service.add_collaborator(
            db=db,
            course_id=course_id,
            user_id=request.user_id,
            role=request.role,
            permissions=request.permissions,
            added_by=current_user.id,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加协作者失败: {str(e)}")


@router.delete("/{course_id}/collaborators/{user_id}")
async def remove_collaborator(
    course_id: UUID = Path(..., description="课程ID"),
    user_id: UUID = Path(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """移除协作者"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.MANAGE
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有管理权限")

    try:
        result = await collaboration_service.remove_collaborator(
            db=db, course_id=course_id, user_id=user_id, removed_by=current_user.id
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除协作者失败: {str(e)}")


@router.put("/{course_id}/collaborators/{user_id}/role")
async def update_collaborator_role(
    course_id: UUID = Path(..., description="课程ID"),
    user_id: UUID = Path(..., description="用户ID"),
    request: UpdateCollaboratorRoleRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新协作者角色"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.MANAGE
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有管理权限")

    try:
        result = await collaboration_service.update_collaborator_role(
            db=db,
            course_id=course_id,
            user_id=user_id,
            new_role=request.new_role,
            updated_by=current_user.id,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新角色失败: {str(e)}")


@router.get("/{course_id}/collaborators", response_model=List[CollaboratorResponse])
async def get_course_collaborators(
    course_id: UUID = Path(..., description="课程ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取课程协作者列表"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.VIEW
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有查看权限")

    try:
        collaborators = await collaboration_service.get_course_collaborators(
            db, course_id
        )
        return [CollaboratorResponse(**collab) for collab in collaborators]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取协作者失败: {str(e)}")


@router.post("/{course_id}/share", response_model=ShareCourseResponse)
async def share_course(
    course_id: UUID = Path(..., description="课程ID"),
    request: ShareCourseRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分享课程"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.SHARE
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有分享权限")

    try:
        result = await collaboration_service.share_course(
            db=db,
            course_id=course_id,
            share_scope=request.share_scope,
            share_settings=request.share_settings,
            shared_by=current_user.id,
        )
        return ShareCourseResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分享课程失败: {str(e)}")


@router.get("/shared-courses", response_model=List[Dict[str, Any]])
async def get_shared_courses(
    share_scope: Optional[ShareScope] = Query(None, description="分享范围"),
    limit: int = Query(default=20, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取共享课程列表"""

    try:
        shared_courses = await collaboration_service.get_shared_courses(
            db=db, user_id=current_user.id, share_scope=share_scope
        )
        return shared_courses[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取共享课程失败: {str(e)}")


@router.post("/copy-course", response_model=Dict[str, Any])
async def copy_shared_course(
    request: CopyCourseRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """复制共享课程"""

    try:
        new_course = await collaboration_service.copy_shared_course(
            db=db,
            source_course_id=request.source_course_id,
            target_user_id=current_user.id,
            new_title=request.new_title,
        )

        return {
            "new_course_id": new_course.id,
            "title": new_course.title,
            "message": "课程复制成功",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"复制课程失败: {str(e)}")


@router.post("/{course_id}/invite", response_model=CollaborationInviteResponse)
async def generate_collaboration_invite(
    course_id: UUID = Path(..., description="课程ID"),
    request: CollaborationInviteRequest = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成协作邀请"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.MANAGE
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有管理权限")

    try:
        invite = await collaboration_service.generate_collaboration_invite(
            db=db,
            course_id=course_id,
            invited_by=current_user.id,
            role=request.role,
            email=request.email,
            expires_in_days=request.expires_in_days,
        )
        return CollaborationInviteResponse(**invite)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成邀请失败: {str(e)}")


@router.get("/{course_id}/activity-log", response_model=List[CourseActivityLog])
async def get_course_activity_log(
    course_id: UUID = Path(..., description="课程ID"),
    limit: int = Query(default=50, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取课程活动日志"""

    # 检查权限
    has_permission = await collaboration_service.check_permission(
        db, course_id, current_user.id, Permission.VIEW
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="没有查看权限")

    try:
        activities = await collaboration_service.get_course_activity_log(
            db=db, course_id=course_id, limit=limit
        )
        return [CourseActivityLog(**activity) for activity in activities]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动日志失败: {str(e)}")


@router.get("/{course_id}/permissions/{user_id}")
async def check_user_permissions(
    course_id: UUID = Path(..., description="课程ID"),
    user_id: UUID = Path(..., description="用户ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查用户权限"""

    # 只有管理员或本人可以查看权限
    if current_user.id != user_id:
        has_manage_permission = await collaboration_service.check_permission(
            db, course_id, current_user.id, Permission.MANAGE
        )
        if not has_manage_permission:
            raise HTTPException(status_code=403, detail="没有查看权限")

    try:
        permissions = {}
        for permission in Permission:
            permissions[permission.value] = (
                await collaboration_service.check_permission(
                    db, course_id, user_id, permission
                )
            )

        return {"course_id": course_id, "user_id": user_id, "permissions": permissions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查权限失败: {str(e)}")


@router.get("/my-collaborations")
async def get_my_collaborations(
    role: Optional[CollaboratorRole] = Query(None, description="角色过滤"),
    limit: int = Query(default=20, le=100, description="返回数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取我参与的协作课程"""

    try:
        # 查询用户参与的所有协作
        from sqlalchemy import select

        from ...models.course import Course, course_collaborators

        query = (
            select(
                Course.id,
                Course.title,
                Course.description,
                Course.subject,
                Course.education_level,
                Course.quality_score,
                course_collaborators.c.role,
                Course.updated_at,
            )
            .select_from(
                course_collaborators.join(
                    Course, course_collaborators.c.course_id == Course.id
                )
            )
            .where(
                course_collaborators.c.user_id == current_user.id,
                Course.is_deleted == False,
            )
        )

        if role:
            query = query.where(course_collaborators.c.role == role.value)

        query = query.order_by(Course.updated_at.desc()).limit(limit).offset(offset)

        result = await db.execute(query)

        collaborations = []
        for row in result:
            collaborations.append(
                {
                    "course_id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "subject": row.subject,
                    "education_level": row.education_level,
                    "quality_score": row.quality_score,
                    "my_role": row.role,
                    "last_updated": row.updated_at,
                }
            )

        return {
            "collaborations": collaborations,
            "total": len(collaborations),  # 实际应该是单独的count查询
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取协作信息失败: {str(e)}")


@router.get("/statistics")
async def get_collaboration_statistics(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取协作统计信息"""

    try:
        from sqlalchemy import func, select

        from ...models.course import Course, course_collaborators

        # 统计用户的协作信息
        result = await db.execute(
            select(
                func.count(course_collaborators.c.course_id).label(
                    "total_collaborations"
                ),
                course_collaborators.c.role,
            )
            .where(course_collaborators.c.user_id == current_user.id)
            .group_by(course_collaborators.c.role)
        )

        role_stats = {}
        total = 0
        for row in result:
            role_stats[row.role] = row.total_collaborations
            total += row.total_collaborations

        # 统计最近活动的课程
        recent_activity = await db.execute(
            select(func.count(Course.id))
            .select_from(
                course_collaborators.join(
                    Course, course_collaborators.c.course_id == Course.id
                )
            )
            .where(
                course_collaborators.c.user_id == current_user.id,
                Course.updated_at >= func.now() - func.interval("7 days"),
            )
        )
        recent_count = recent_activity.scalar() or 0

        return {
            "total_collaborations": total,
            "role_distribution": role_stats,
            "recent_activity_count": recent_count,
            "most_active_role": (
                max(role_stats.items(), key=lambda x: x[1])[0] if role_stats else None
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/{course_id}/leave")
async def leave_collaboration(
    course_id: UUID = Path(..., description="课程ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """退出协作"""

    try:
        result = await collaboration_service.remove_collaborator(
            db=db, course_id=course_id, user_id=current_user.id
        )

        return {"message": "已成功退出协作", "course_id": course_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"退出协作失败: {str(e)}")
