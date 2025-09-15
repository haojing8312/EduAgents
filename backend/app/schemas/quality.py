"""
质量检查相关的Pydantic模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..services.quality_checker import CheckSeverity, QualityLevel


class QualityIssueResponse(BaseModel):
    """质量问题响应"""

    category: str = Field(..., description="问题分类")
    severity: CheckSeverity = Field(..., description="严重程度")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="问题描述")
    suggestion: str = Field(..., description="改进建议")
    location: Optional[str] = Field(None, description="问题位置")
    score_impact: int = Field(default=0, description="对评分的影响")


class QualityReportResponse(BaseModel):
    """质量报告响应"""

    course_id: Optional[UUID] = Field(None, description="课程ID")
    overall_score: Optional[float] = Field(None, description="总体评分")
    quality_level: Optional[QualityLevel] = Field(None, description="质量等级")
    issues: List[QualityIssueResponse] = Field(
        default_factory=list, description="问题列表"
    )
    strengths: List[str] = Field(default_factory=list, description="优势点")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    category_scores: Dict[str, float] = Field(
        default_factory=dict, description="各类别得分"
    )
    generated_at: Optional[datetime] = Field(None, description="生成时间")
    status: Optional[str] = Field(None, description="状态")
    message: Optional[str] = Field(None, description="消息")

    @classmethod
    def from_report(cls, report):
        """从质量报告创建响应"""
        return cls(
            overall_score=report.overall_score,
            quality_level=report.quality_level,
            issues=[
                QualityIssueResponse(
                    category=issue.category,
                    severity=issue.severity,
                    title=issue.title,
                    description=issue.description,
                    suggestion=issue.suggestion,
                    location=issue.location,
                    score_impact=issue.score_impact,
                )
                for issue in report.issues
            ],
            strengths=report.strengths,
            recommendations=report.recommendations,
            category_scores=report.category_scores,
            generated_at=report.generated_at,
            status="completed",
        )


class QualityCheckRequest(BaseModel):
    """质量检查请求"""

    check_categories: Optional[List[str]] = Field(None, description="要检查的分类")
    detailed_report: bool = Field(default=True, description="是否生成详细报告")
    auto_save: bool = Field(default=True, description="是否自动保存结果")

    class Config:
        schema_extra = {
            "example": {
                "check_categories": ["基础完整性", "学习目标", "PBL对齐"],
                "detailed_report": True,
                "auto_save": True,
            }
        }


class BatchQualityCheckRequest(BaseModel):
    """批量质量检查请求"""

    course_ids: List[UUID] = Field(..., description="课程ID列表")
    async_check: bool = Field(default=False, description="是否异步检查")
    check_options: Optional[QualityCheckRequest] = Field(None, description="检查选项")

    class Config:
        schema_extra = {
            "example": {
                "course_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                ],
                "async_check": True,
                "check_options": {"detailed_report": True, "auto_save": True},
            }
        }


class QualityStatistics(BaseModel):
    """质量统计"""

    total_courses: int = Field(..., description="总课程数")
    average_score: float = Field(..., description="平均分")
    quality_distribution: Dict[str, int] = Field(..., description="质量分布")
    common_issues: List[str] = Field(..., description="常见问题")
    improvement_trends: List[str] = Field(..., description="改进趋势")

    class Config:
        schema_extra = {
            "example": {
                "total_courses": 150,
                "average_score": 82.5,
                "quality_distribution": {
                    "excellent": 25,
                    "good": 45,
                    "acceptable": 50,
                    "needs_improvement": 20,
                    "poor": 10,
                },
                "common_issues": [
                    "缺少明确的学习目标",
                    "驱动性问题不够具体",
                    "评估方法过于单一",
                ],
                "improvement_trends": [
                    "学习目标设计质量持续提升",
                    "PBL特征实现度逐步改善",
                ],
            }
        }


class QualityTrendData(BaseModel):
    """质量趋势数据"""

    date: datetime = Field(..., description="日期")
    average_score: float = Field(..., description="平均分")
    course_count: int = Field(..., description="课程数量")
    quality_distribution: Dict[str, int] = Field(..., description="质量分布")


class QualityTrendResponse(BaseModel):
    """质量趋势响应"""

    period: str = Field(..., description="时间周期")
    data_points: List[QualityTrendData] = Field(..., description="数据点")
    overall_trend: str = Field(..., description="总体趋势")
    insights: List[str] = Field(..., description="洞察")


class QualityComparisonRequest(BaseModel):
    """质量对比请求"""

    course_ids: List[UUID] = Field(
        ..., min_items=2, max_items=5, description="要对比的课程ID"
    )
    comparison_categories: Optional[List[str]] = Field(None, description="对比类别")

    class Config:
        schema_extra = {
            "example": {
                "course_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001",
                ],
                "comparison_categories": ["学习目标", "PBL对齐", "评估设计"],
            }
        }


class QualityComparisonResponse(BaseModel):
    """质量对比响应"""

    courses: List[Dict[str, Any]] = Field(..., description="课程信息")
    comparison_matrix: Dict[str, Dict[UUID, float]] = Field(..., description="对比矩阵")
    best_practices: List[str] = Field(..., description="最佳实践")
    improvement_suggestions: Dict[UUID, List[str]] = Field(..., description="改进建议")


class QualityBenchmarkData(BaseModel):
    """质量基准数据"""

    education_level: str = Field(..., description="教育学段")
    subject: str = Field(..., description="学科")
    average_score: float = Field(..., description="平均分")
    score_range: Dict[str, float] = Field(..., description="分数范围")
    sample_size: int = Field(..., description="样本大小")


class QualityBenchmarkResponse(BaseModel):
    """质量基准响应"""

    benchmarks: List[QualityBenchmarkData] = Field(..., description="基准数据")
    your_position: Dict[str, Any] = Field(..., description="您的位置")
    recommendations: List[str] = Field(..., description="建议")


class AutoImprovementRequest(BaseModel):
    """自动改进请求"""

    improvement_categories: Optional[List[str]] = Field(None, description="改进类别")
    max_changes: int = Field(default=5, description="最大更改数")
    preserve_original: bool = Field(default=True, description="保留原始版本")

    class Config:
        schema_extra = {
            "example": {
                "improvement_categories": ["学习目标", "评估设计"],
                "max_changes": 3,
                "preserve_original": True,
            }
        }


class AutoImprovementResponse(BaseModel):
    """自动改进响应"""

    course_id: UUID = Field(..., description="课程ID")
    improvements_made: List[Dict[str, Any]] = Field(..., description="已应用的改进")
    old_score: float = Field(..., description="原始分数")
    new_score: float = Field(..., description="新分数")
    message: str = Field(..., description="消息")
    backup_version: Optional[UUID] = Field(None, description="备份版本ID")


class QualityAlert(BaseModel):
    """质量警报"""

    course_id: UUID = Field(..., description="课程ID")
    course_title: str = Field(..., description="课程标题")
    alert_type: str = Field(..., description="警报类型")
    severity: CheckSeverity = Field(..., description="严重程度")
    message: str = Field(..., description="警报消息")
    created_at: datetime = Field(..., description="创建时间")
    resolved: bool = Field(default=False, description="是否已解决")


class QualityAlertListResponse(BaseModel):
    """质量警报列表响应"""

    alerts: List[QualityAlert] = Field(..., description="警报列表")
    total: int = Field(..., description="总数")
    unresolved_count: int = Field(..., description="未解决数量")


class QualityDashboardData(BaseModel):
    """质量仪表板数据"""

    overview: Dict[str, Any] = Field(..., description="概览数据")
    recent_checks: List[QualityReportResponse] = Field(..., description="最近检查")
    quality_trends: QualityTrendResponse = Field(..., description="质量趋势")
    alerts: QualityAlertListResponse = Field(..., description="警报信息")
    recommendations: List[str] = Field(..., description="推荐建议")


class QualityMetrics(BaseModel):
    """质量指标"""

    completeness_score: float = Field(..., description="完整性评分")
    alignment_score: float = Field(..., description="对齐性评分")
    innovation_score: float = Field(..., description="创新性评分")
    practicality_score: float = Field(..., description="实用性评分")
    sustainability_score: float = Field(..., description="可持续性评分")


class DetailedQualityReport(QualityReportResponse):
    """详细质量报告"""

    metrics: QualityMetrics = Field(..., description="详细指标")
    issue_distribution: Dict[str, int] = Field(..., description="问题分布")
    improvement_priority: List[str] = Field(..., description="改进优先级")
    benchmark_comparison: Optional[Dict[str, Any]] = Field(None, description="基准对比")
    historical_data: Optional[List[Dict[str, Any]]] = Field(
        None, description="历史数据"
    )


class QualityCheckSchedule(BaseModel):
    """质量检查计划"""

    course_id: UUID = Field(..., description="课程ID")
    schedule_type: str = Field(
        ..., description="计划类型"
    )  # weekly, monthly, on_update
    next_check_date: datetime = Field(..., description="下次检查日期")
    auto_improve: bool = Field(default=False, description="自动改进")
    notification_enabled: bool = Field(default=True, description="启用通知")


class QualityCheckScheduleResponse(BaseModel):
    """质量检查计划响应"""

    schedules: List[QualityCheckSchedule] = Field(..., description="计划列表")
    total: int = Field(..., description="总数")
    active_count: int = Field(..., description="活跃数量")
