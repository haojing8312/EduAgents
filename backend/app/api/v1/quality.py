"""
课程质量检查API接口
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.auth import get_current_user
from ...core.database import get_db
from ...models.course import Course
from ...models.user import User
from ...schemas.quality import (
    BatchQualityCheckRequest,
    QualityCheckRequest,
    QualityIssueResponse,
    QualityReportResponse,
    QualityStatistics,
)
from ...services.quality_checker import CheckSeverity, QualityLevel, quality_checker

router = APIRouter(prefix="/quality", tags=["课程质量"])


@router.post("/check/{course_id}", response_model=QualityReportResponse)
async def check_course_quality(
    course_id: UUID = Path(..., description="课程ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检查课程质量"""

    # 查询课程（包含关联数据）
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources),
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 检查权限（简化版）
    # 实际应用中需要更详细的权限检查

    try:
        # 执行质量检查
        quality_report = quality_checker.check_course_quality(course)

        # 更新课程质量评分
        course.quality_score = quality_report.overall_score
        await db.commit()

        # 转换为响应格式
        return QualityReportResponse.from_report(quality_report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"质量检查失败: {str(e)}")


@router.get("/report/{course_id}", response_model=QualityReportResponse)
async def get_quality_report(
    course_id: UUID = Path(..., description="课程ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取课程质量报告（如果已存在）"""

    # 这里可以从缓存或数据库中获取已生成的质量报告
    # 暂时重新生成
    return await check_course_quality(course_id, db, current_user)


@router.post("/batch-check", response_model=List[QualityReportResponse])
async def batch_quality_check(
    request: BatchQualityCheckRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量质量检查"""

    results = []

    for course_id in request.course_ids:
        try:
            result = await db.execute(
                select(Course)
                .options(
                    selectinload(Course.lessons),
                    selectinload(Course.assessments),
                    selectinload(Course.resources),
                )
                .where(Course.id == course_id, Course.is_deleted == False)
            )
            course = result.scalar_one_or_none()

            if course:
                if request.async_check:
                    # 异步处理
                    background_tasks.add_task(
                        _process_quality_check_async, course_id, course
                    )
                    results.append(
                        QualityReportResponse(
                            course_id=course_id,
                            status="pending",
                            message="质量检查任务已创建",
                        )
                    )
                else:
                    # 同步处理
                    quality_report = quality_checker.check_course_quality(course)
                    course.quality_score = quality_report.overall_score
                    await db.commit()
                    results.append(QualityReportResponse.from_report(quality_report))
            else:
                results.append(
                    QualityReportResponse(
                        course_id=course_id, status="error", message="课程不存在"
                    )
                )

        except Exception as e:
            results.append(
                QualityReportResponse(
                    course_id=course_id, status="error", message=f"检查失败: {str(e)}"
                )
            )

    return results


@router.get("/statistics")
async def get_quality_statistics(
    education_level: Optional[str] = Query(None, description="教育学段"),
    subject: Optional[str] = Query(None, description="学科"),
    limit: int = Query(default=100, description="统计课程数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取质量统计信息"""

    # 构建查询
    query = select(Course).where(Course.is_deleted == False)

    if education_level:
        query = query.where(Course.education_level == education_level)

    if subject:
        query = query.where(Course.subject == subject)

    query = query.limit(limit)

    result = await db.execute(query)
    courses = result.scalars().all()

    if not courses:
        return QualityStatistics(
            total_courses=0,
            average_score=0,
            quality_distribution={},
            common_issues=[],
            improvement_trends=[],
        )

    # 计算统计信息
    scores = [
        course.quality_score for course in courses if course.quality_score is not None
    ]

    if not scores:
        # 如果没有质量评分，返回基础统计
        return QualityStatistics(
            total_courses=len(courses),
            average_score=0,
            quality_distribution={},
            common_issues=["大部分课程尚未进行质量检查"],
            improvement_trends=[],
        )

    average_score = sum(scores) / len(scores)

    # 质量分布
    quality_distribution = {
        "excellent": len([s for s in scores if s >= 90]),
        "good": len([s for s in scores if 80 <= s < 90]),
        "acceptable": len([s for s in scores if 70 <= s < 80]),
        "needs_improvement": len([s for s in scores if 60 <= s < 70]),
        "poor": len([s for s in scores if s < 60]),
    }

    return QualityStatistics(
        total_courses=len(courses),
        average_score=average_score,
        quality_distribution=quality_distribution,
        common_issues=_get_common_issues(),
        improvement_trends=_get_improvement_trends(),
    )


@router.get("/issues/common")
async def get_common_issues(
    severity: Optional[CheckSeverity] = Query(None, description="问题严重程度"),
    category: Optional[str] = Query(None, description="问题分类"),
    limit: int = Query(default=10, description="返回数量"),
):
    """获取常见质量问题"""

    # 这里应该从实际的质量检查记录中统计
    # 暂时返回预定义的常见问题
    common_issues = [
        {
            "title": "缺少学习目标",
            "category": "学习目标",
            "severity": "critical",
            "frequency": 45,
            "description": "课程未设定明确的学习目标",
        },
        {
            "title": "缺少驱动性问题",
            "category": "PBL对齐",
            "severity": "critical",
            "frequency": 38,
            "description": "PBL课程缺少核心驱动性问题",
        },
        {
            "title": "评估方法单一",
            "category": "评估设计",
            "severity": "warning",
            "frequency": 52,
            "description": "课程评估方法缺乏多样性",
        },
        {
            "title": "缺少支架支持",
            "category": "支架支持",
            "severity": "warning",
            "frequency": 35,
            "description": "课程缺少适当的学习支架",
        },
        {
            "title": "课时安排不合理",
            "category": "课程结构",
            "severity": "warning",
            "frequency": 29,
            "description": "课时时间分配与总学时不一致",
        },
    ]

    # 应用过滤条件
    filtered_issues = common_issues

    if severity:
        filtered_issues = [i for i in filtered_issues if i["severity"] == severity]

    if category:
        filtered_issues = [i for i in filtered_issues if i["category"] == category]

    return {"issues": filtered_issues[:limit], "total": len(filtered_issues)}


@router.get("/suggestions/{course_id}")
async def get_improvement_suggestions(
    course_id: UUID = Path(..., description="课程ID"),
    category: Optional[str] = Query(None, description="问题分类"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取改进建议"""

    # 查询课程
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources),
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 执行质量检查获取建议
    quality_report = quality_checker.check_course_quality(course)

    # 过滤特定分类的问题
    issues = quality_report.issues
    if category:
        issues = [i for i in issues if i.category == category]

    # 生成针对性建议
    suggestions = []
    for issue in issues:
        suggestions.append(
            {
                "issue": issue.title,
                "category": issue.category,
                "severity": issue.severity,
                "suggestion": issue.suggestion,
                "priority": _get_priority_score(issue),
            }
        )

    # 按优先级排序
    suggestions.sort(key=lambda x: x["priority"], reverse=True)

    return {
        "course_id": course_id,
        "suggestions": suggestions,
        "overall_recommendations": quality_report.recommendations,
    }


@router.post("/auto-improve/{course_id}")
async def auto_improve_course(
    course_id: UUID = Path(..., description="课程ID"),
    categories: List[str] = Query(default=[], description="要改进的分类"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """自动改进课程（基于AI建议）"""

    # 查询课程
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources),
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 检查权限
    if course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限修改此课程")

    try:
        # 执行质量检查
        quality_report = quality_checker.check_course_quality(course)

        # 自动改进逻辑（这里是简化版，实际应该集成AI服务）
        improvements_made = []

        for issue in quality_report.issues:
            if not categories or issue.category in categories:
                if issue.severity in [CheckSeverity.CRITICAL, CheckSeverity.WARNING]:
                    improvement = _apply_auto_improvement(course, issue)
                    if improvement:
                        improvements_made.append(improvement)

        if improvements_made:
            await db.commit()

            # 重新检查质量
            new_quality_report = quality_checker.check_course_quality(course)
            course.quality_score = new_quality_report.overall_score
            await db.commit()

        return {
            "course_id": course_id,
            "improvements_made": improvements_made,
            "old_score": quality_report.overall_score,
            "new_score": (
                course.quality_score
                if improvements_made
                else quality_report.overall_score
            ),
            "message": (
                f"成功应用{len(improvements_made)}项改进"
                if improvements_made
                else "未发现可自动改进的问题"
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动改进失败: {str(e)}")


# 辅助函数


async def _process_quality_check_async(course_id: UUID, course: Course):
    """异步处理质量检查"""
    from ...core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            quality_report = quality_checker.check_course_quality(course)

            # 更新课程质量评分
            result = await db.execute(select(Course).where(Course.id == course_id))
            course_record = result.scalar_one()
            course_record.quality_score = quality_report.overall_score
            await db.commit()

        except Exception as e:
            # 记录错误日志
            print(f"异步质量检查失败: {str(e)}")


def _get_common_issues() -> List[str]:
    """获取常见问题列表"""
    return [
        "缺少明确的学习目标",
        "驱动性问题不够具体",
        "评估方法过于单一",
        "缺少学习支架设计",
        "课时安排不够合理",
    ]


def _get_improvement_trends() -> List[str]:
    """获取改进趋势"""
    return ["学习目标设计质量持续提升", "PBL特征实现度逐步改善", "评估设计多样性增加"]


def _get_priority_score(issue) -> int:
    """计算问题优先级分数"""
    severity_scores = {
        CheckSeverity.CRITICAL: 100,
        CheckSeverity.WARNING: 70,
        CheckSeverity.SUGGESTION: 40,
        CheckSeverity.INFO: 20,
    }

    base_score = severity_scores.get(issue.severity, 20)

    # 根据影响分数调整
    if hasattr(issue, "score_impact"):
        base_score += issue.score_impact

    return base_score


def _apply_auto_improvement(course: Course, issue) -> Optional[Dict[str, Any]]:
    """应用自动改进"""

    # 这里是简化的自动改进逻辑
    # 实际应该集成AI服务来生成改进内容

    if "缺少学习目标" in issue.title and not course.learning_objectives:
        # 自动生成基础学习目标
        default_objectives = [
            f"理解{course.subject}相关的核心概念",
            f"应用所学知识解决实际问题",
            f"培养{course.subject}学科的思维能力",
        ]
        course.learning_objectives = default_objectives
        return {
            "type": "学习目标补充",
            "description": "自动添加了基础学习目标",
            "details": default_objectives,
        }

    elif "缺少驱动性问题" in issue.title and not course.driving_question:
        # 自动生成基础驱动性问题
        course.driving_question = (
            f"如何运用{course.subject}知识解决我们身边的实际问题？"
        )
        return {
            "type": "驱动性问题补充",
            "description": "自动添加了基础驱动性问题",
            "details": course.driving_question,
        }

    return None
