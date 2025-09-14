"""
课程协作服务
实现课程分享、协作编辑、版本管理等功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, update

from ..models.course import Course, course_collaborators
from ..models.user import User
from ..core.config import settings


class CollaboratorRole(str, Enum):
    """协作者角色"""
    OWNER = "owner"          # 拥有者
    EDITOR = "editor"        # 编辑者
    CONTRIBUTOR = "contributor"  # 贡献者
    VIEWER = "viewer"        # 查看者
    REVIEWER = "reviewer"    # 审核者


class ShareScope(str, Enum):
    """分享范围"""
    PRIVATE = "private"      # 私有
    TEAM = "team"           # 团队
    ORGANIZATION = "organization"  # 组织
    PUBLIC = "public"        # 公开


class Permission(str, Enum):
    """权限类型"""
    VIEW = "view"           # 查看
    COMMENT = "comment"     # 评论
    EDIT = "edit"          # 编辑
    MANAGE = "manage"      # 管理
    EXPORT = "export"      # 导出
    SHARE = "share"        # 分享


class CollaborationService:
    """协作服务类"""
    
    def __init__(self):
        self.role_permissions = {
            CollaboratorRole.OWNER: [Permission.VIEW, Permission.COMMENT, Permission.EDIT, 
                                   Permission.MANAGE, Permission.EXPORT, Permission.SHARE],
            CollaboratorRole.EDITOR: [Permission.VIEW, Permission.COMMENT, Permission.EDIT, 
                                    Permission.EXPORT],
            CollaboratorRole.CONTRIBUTOR: [Permission.VIEW, Permission.COMMENT, Permission.EDIT],
            CollaboratorRole.REVIEWER: [Permission.VIEW, Permission.COMMENT],
            CollaboratorRole.VIEWER: [Permission.VIEW]
        }
    
    async def add_collaborator(
        self,
        db: AsyncSession,
        course_id: UUID,
        user_id: UUID,
        role: CollaboratorRole,
        permissions: Optional[List[Permission]] = None,
        added_by: UUID = None
    ) -> Dict[str, Any]:
        """添加协作者"""
        
        # 检查课程是否存在
        result = await db.execute(
            select(Course).where(Course.id == course_id, Course.is_deleted == False)
        )
        course = result.scalar_one_or_none()
        if not course:
            raise ValueError("课程不存在")
        
        # 检查用户是否存在
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")
        
        # 检查是否已经是协作者
        existing = await db.execute(
            select(course_collaborators).where(
                and_(
                    course_collaborators.c.course_id == course_id,
                    course_collaborators.c.user_id == user_id
                )
            )
        )
        if existing.first():
            raise ValueError("用户已经是协作者")
        
        # 确定权限
        if permissions is None:
            permissions = self.role_permissions.get(role, [Permission.VIEW])
        
        # 添加协作关系
        insert_stmt = course_collaborators.insert().values(
            course_id=course_id,
            user_id=user_id,
            role=role.value,
            permissions={
                'permissions': [p.value for p in permissions],
                'added_by': str(added_by) if added_by else None,
                'added_at': datetime.utcnow().isoformat()
            }
        )
        await db.execute(insert_stmt)
        await db.commit()
        
        return {
            "course_id": course_id,
            "user_id": user_id,
            "role": role.value,
            "permissions": [p.value for p in permissions],
            "message": "协作者添加成功"
        }
    
    async def remove_collaborator(
        self,
        db: AsyncSession,
        course_id: UUID,
        user_id: UUID,
        removed_by: UUID = None
    ) -> Dict[str, Any]:
        """移除协作者"""
        
        # 检查协作关系是否存在
        result = await db.execute(
            select(course_collaborators).where(
                and_(
                    course_collaborators.c.course_id == course_id,
                    course_collaborators.c.user_id == user_id
                )
            )
        )
        collaboration = result.first()
        if not collaboration:
            raise ValueError("协作关系不存在")
        
        # 不能移除课程拥有者
        if collaboration.role == CollaboratorRole.OWNER.value:
            raise ValueError("不能移除课程拥有者")
        
        # 删除协作关系
        delete_stmt = course_collaborators.delete().where(
            and_(
                course_collaborators.c.course_id == course_id,
                course_collaborators.c.user_id == user_id
            )
        )
        await db.execute(delete_stmt)
        await db.commit()
        
        return {
            "course_id": course_id,
            "user_id": user_id,
            "message": "协作者移除成功"
        }
    
    async def update_collaborator_role(
        self,
        db: AsyncSession,
        course_id: UUID,
        user_id: UUID,
        new_role: CollaboratorRole,
        updated_by: UUID = None
    ) -> Dict[str, Any]:
        """更新协作者角色"""
        
        # 检查协作关系是否存在
        result = await db.execute(
            select(course_collaborators).where(
                and_(
                    course_collaborators.c.course_id == course_id,
                    course_collaborators.c.user_id == user_id
                )
            )
        )
        collaboration = result.first()
        if not collaboration:
            raise ValueError("协作关系不存在")
        
        # 不能修改拥有者角色
        if collaboration.role == CollaboratorRole.OWNER.value:
            raise ValueError("不能修改拥有者角色")
        
        # 更新角色和权限
        new_permissions = self.role_permissions.get(new_role, [Permission.VIEW])
        
        update_stmt = course_collaborators.update().where(
            and_(
                course_collaborators.c.course_id == course_id,
                course_collaborators.c.user_id == user_id
            )
        ).values(
            role=new_role.value,
            permissions={
                'permissions': [p.value for p in new_permissions],
                'updated_by': str(updated_by) if updated_by else None,
                'updated_at': datetime.utcnow().isoformat()
            }
        )
        await db.execute(update_stmt)
        await db.commit()
        
        return {
            "course_id": course_id,
            "user_id": user_id,
            "new_role": new_role.value,
            "new_permissions": [p.value for p in new_permissions],
            "message": "角色更新成功"
        }
    
    async def get_course_collaborators(
        self,
        db: AsyncSession,
        course_id: UUID
    ) -> List[Dict[str, Any]]:
        """获取课程协作者列表"""
        
        # 查询协作者信息
        result = await db.execute(
            select(
                course_collaborators.c.user_id,
                course_collaborators.c.role,
                course_collaborators.c.permissions,
                User.username,
                User.email,
                User.profile
            ).select_from(
                course_collaborators.join(User, course_collaborators.c.user_id == User.id)
            ).where(course_collaborators.c.course_id == course_id)
        )
        
        collaborators = []
        for row in result:
            permissions_data = row.permissions or {}
            collaborators.append({
                "user_id": row.user_id,
                "username": row.username,
                "email": row.email,
                "profile": row.profile,
                "role": row.role,
                "permissions": permissions_data.get('permissions', []),
                "added_at": permissions_data.get('added_at'),
                "updated_at": permissions_data.get('updated_at')
            })
        
        return collaborators
    
    async def check_permission(
        self,
        db: AsyncSession,
        course_id: UUID,
        user_id: UUID,
        permission: Permission
    ) -> bool:
        """检查用户权限"""
        
        # 查询协作关系
        result = await db.execute(
            select(course_collaborators).where(
                and_(
                    course_collaborators.c.course_id == course_id,
                    course_collaborators.c.user_id == user_id
                )
            )
        )
        collaboration = result.first()
        
        if not collaboration:
            return False
        
        # 检查权限
        permissions_data = collaboration.permissions or {}
        user_permissions = permissions_data.get('permissions', [])
        
        return permission.value in user_permissions
    
    async def share_course(
        self,
        db: AsyncSession,
        course_id: UUID,
        share_scope: ShareScope,
        share_settings: Dict[str, Any],
        shared_by: UUID
    ) -> Dict[str, Any]:
        """分享课程"""
        
        # 查询课程
        result = await db.execute(
            select(Course).where(Course.id == course_id, Course.is_deleted == False)
        )
        course = result.scalar_one_or_none()
        if not course:
            raise ValueError("课程不存在")
        
        # 更新分享设置
        share_config = {
            'scope': share_scope.value,
            'settings': share_settings,
            'shared_by': str(shared_by),
            'shared_at': datetime.utcnow().isoformat(),
            'share_token': str(uuid4()) if share_scope == ShareScope.PUBLIC else None
        }
        
        # 更新课程的分享状态
        if share_scope == ShareScope.PUBLIC:
            course.is_public = True
        
        # 将分享配置存储在课程的metadata中
        if not course.metadata:
            course.metadata = {}
        course.metadata['share_config'] = share_config
        
        await db.commit()
        
        return {
            "course_id": course_id,
            "share_scope": share_scope.value,
            "share_token": share_config.get('share_token'),
            "share_url": self._generate_share_url(course_id, share_config.get('share_token')),
            "message": "课程分享成功"
        }
    
    async def get_shared_courses(
        self,
        db: AsyncSession,
        user_id: UUID,
        share_scope: Optional[ShareScope] = None
    ) -> List[Dict[str, Any]]:
        """获取用户有权访问的共享课程"""
        
        # 构建查询条件
        query = select(Course).where(Course.is_deleted == False)
        
        if share_scope == ShareScope.PUBLIC:
            query = query.where(Course.is_public == True)
        else:
            # 查询用户作为协作者的课程
            subquery = select(course_collaborators.c.course_id).where(
                course_collaborators.c.user_id == user_id
            )
            query = query.where(Course.id.in_(subquery))
        
        result = await db.execute(query)
        courses = result.scalars().all()
        
        shared_courses = []
        for course in courses:
            # 获取用户在该课程中的角色
            role_result = await db.execute(
                select(course_collaborators.c.role).where(
                    and_(
                        course_collaborators.c.course_id == course.id,
                        course_collaborators.c.user_id == user_id
                    )
                )
            )
            role_row = role_result.first()
            user_role = role_row.role if role_row else None
            
            share_config = course.metadata.get('share_config', {}) if course.metadata else {}
            
            shared_courses.append({
                "course_id": course.id,
                "title": course.title,
                "description": course.description,
                "subject": course.subject,
                "education_level": course.education_level,
                "user_role": user_role,
                "share_scope": share_config.get('scope'),
                "shared_at": share_config.get('shared_at'),
                "quality_score": course.quality_score
            })
        
        return shared_courses
    
    async def copy_shared_course(
        self,
        db: AsyncSession,
        source_course_id: UUID,
        target_user_id: UUID,
        new_title: Optional[str] = None
    ) -> Course:
        """复制共享课程"""
        
        # 查询源课程
        result = await db.execute(
            select(Course)
            .options(
                selectinload(Course.lessons),
                selectinload(Course.assessments),
                selectinload(Course.resources)
            )
            .where(Course.id == source_course_id, Course.is_deleted == False)
        )
        source_course = result.scalar_one_or_none()
        if not source_course:
            raise ValueError("源课程不存在")
        
        # 检查访问权限（如果是公开课程或用户有访问权限）
        if not source_course.is_public:
            has_access = await self.check_permission(
                db, source_course_id, target_user_id, Permission.VIEW
            )
            if not has_access:
                raise ValueError("没有访问权限")
        
        # 创建课程副本
        new_course = Course(
            title=new_title or f"{source_course.title} (副本)",
            subtitle=source_course.subtitle,
            description=source_course.description,
            summary=source_course.summary,
            subject=source_course.subject,
            subjects=source_course.subjects,
            education_level=source_course.education_level,
            grade_levels=source_course.grade_levels,
            difficulty_level=source_course.difficulty_level,
            duration_weeks=source_course.duration_weeks,
            duration_hours=source_course.duration_hours,
            class_size_min=source_course.class_size_min,
            class_size_max=source_course.class_size_max,
            learning_objectives=source_course.learning_objectives,
            core_competencies=source_course.core_competencies,
            assessment_criteria=source_course.assessment_criteria,
            project_context=source_course.project_context,
            driving_question=source_course.driving_question,
            final_products=source_course.final_products,
            authentic_assessment=source_course.authentic_assessment,
            phases=source_course.phases,
            milestones=source_course.milestones,
            scaffolding_supports=source_course.scaffolding_supports,
            required_resources=source_course.required_resources,
            recommended_resources=source_course.recommended_resources,
            technology_requirements=source_course.technology_requirements,
            teacher_preparation=source_course.teacher_preparation,
            teaching_strategies=source_course.teaching_strategies,
            differentiation_strategies=source_course.differentiation_strategies,
            is_public=False,  # 副本默认为私有
            parent_course_id=source_course_id,
            created_by=target_user_id
        )
        
        db.add(new_course)
        await db.flush()  # 获取新课程ID
        
        # 复制课时
        if source_course.lessons:
            from ..models.course import Lesson
            for lesson in source_course.lessons:
                new_lesson = Lesson(
                    course_id=new_course.id,
                    title=lesson.title,
                    description=lesson.description,
                    objectives=lesson.objectives,
                    sequence_number=lesson.sequence_number,
                    duration_minutes=lesson.duration_minutes,
                    phase=lesson.phase,
                    activities=lesson.activities,
                    materials=lesson.materials,
                    homework=lesson.homework,
                    teaching_methods=lesson.teaching_methods,
                    student_grouping=lesson.student_grouping,
                    teacher_notes=lesson.teacher_notes,
                    created_by=target_user_id
                )
                db.add(new_lesson)
        
        # 复制评估
        if source_course.assessments:
            from ..models.course import Assessment
            for assessment in source_course.assessments:
                new_assessment = Assessment(
                    course_id=new_course.id,
                    title=assessment.title,
                    description=assessment.description,
                    type=assessment.type,
                    criteria=assessment.criteria,
                    rubric=assessment.rubric,
                    weight=assessment.weight,
                    due_date_offset=assessment.due_date_offset,
                    estimated_time=assessment.estimated_time,
                    created_by=target_user_id
                )
                db.add(new_assessment)
        
        # 添加拥有者协作关系
        await self.add_collaborator(
            db, new_course.id, target_user_id, CollaboratorRole.OWNER
        )
        
        await db.commit()
        await db.refresh(new_course)
        
        return new_course
    
    async def get_course_activity_log(
        self,
        db: AsyncSession,
        course_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取课程活动日志"""
        
        # 这里应该查询专门的活动日志表
        # 暂时返回模拟数据
        activities = [
            {
                "activity_id": str(uuid4()),
                "user_id": str(uuid4()),
                "username": "张老师",
                "action": "编辑课程",
                "details": "更新了学习目标",
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "changes": {
                    "field": "learning_objectives",
                    "old_value": ["目标1", "目标2"],
                    "new_value": ["目标1", "目标2", "目标3"]
                }
            },
            {
                "activity_id": str(uuid4()),
                "user_id": str(uuid4()),
                "username": "李老师",
                "action": "添加课时",
                "details": "添加了新的课时：项目展示",
                "timestamp": datetime.utcnow() - timedelta(hours=5),
                "changes": {
                    "field": "lessons",
                    "action": "add",
                    "new_item": {"title": "项目展示", "duration": 90}
                }
            }
        ]
        
        return activities[:limit]
    
    def _generate_share_url(self, course_id: UUID, share_token: Optional[str] = None) -> str:
        """生成分享链接"""
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        if share_token:
            return f"{base_url}/shared/courses/{course_id}?token={share_token}"
        else:
            return f"{base_url}/courses/{course_id}"
    
    async def generate_collaboration_invite(
        self,
        db: AsyncSession,
        course_id: UUID,
        invited_by: UUID,
        role: CollaboratorRole,
        email: Optional[str] = None,
        expires_in_days: int = 7
    ) -> Dict[str, Any]:
        """生成协作邀请"""
        
        invite_token = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        invite_data = {
            "invite_token": invite_token,
            "course_id": str(course_id),
            "invited_by": str(invited_by),
            "role": role.value,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "used": False
        }
        
        # 这里应该存储到专门的邀请表中
        # 暂时存储在Redis或临时文件中
        
        invite_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/invites/{invite_token}"
        
        return {
            "invite_token": invite_token,
            "invite_url": invite_url,
            "expires_at": expires_at,
            "role": role.value,
            "message": "邀请生成成功"
        }


# 全局服务实例
collaboration_service = CollaborationService()