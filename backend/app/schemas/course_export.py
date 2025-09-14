"""
课程导出相关的Pydantic模型
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """导出格式枚举"""
    PDF_TEACHING_PLAN = "pdf_teaching_plan"
    PDF_HANDBOOK = "pdf_handbook"
    PDF_RUBRIC = "pdf_rubric"
    DOCX = "docx"
    PPTX = "pptx"
    JSON = "json"


class ExportStatus(str, Enum):
    """导出状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CourseExportRequest(BaseModel):
    """课程导出请求"""
    format: ExportFormat = Field(..., description="导出格式")
    options: Dict[str, Any] = Field(default_factory=dict, description="导出选项")
    async_export: bool = Field(default=False, description="是否异步导出")
    
    class Config:
        schema_extra = {
            "example": {
                "format": "pdf_teaching_plan",
                "options": {
                    "include_objectives": True,
                    "include_activities": True,
                    "include_assessments": True,
                    "detailed_lessons": True
                },
                "async_export": False
            }
        }


class BatchExportRequest(BaseModel):
    """批量导出请求"""
    formats: List[ExportFormat] = Field(..., description="导出格式列表")
    options: Dict[ExportFormat, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="每种格式的导出选项"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "formats": ["pdf_teaching_plan", "pdf_handbook", "docx"],
                "options": {
                    "pdf_teaching_plan": {
                        "include_objectives": True,
                        "detailed_lessons": True
                    },
                    "pdf_handbook": {
                        "include_schedule": True,
                        "student_friendly": True
                    },
                    "docx": {
                        "type": "complete"
                    }
                }
            }
        }


class CourseExportResponse(BaseModel):
    """课程导出响应"""
    export_id: UUID = Field(..., description="导出ID")
    status: ExportStatus = Field(..., description="导出状态")
    format: Optional[ExportFormat] = Field(None, description="导出格式")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    download_url: Optional[str] = Field(None, description="下载链接")
    error_message: Optional[str] = Field(None, description="错误信息")
    message: Optional[str] = Field(None, description="状态消息")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    class Config:
        schema_extra = {
            "example": {
                "export_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "format": "pdf_teaching_plan",
                "file_path": "/exports/123e4567-e89b-12d3-a456-426614174000.pdf",
                "file_size": 1048576,
                "download_url": "/api/v1/exports/123e4567-e89b-12d3-a456-426614174000/download",
                "created_at": "2024-01-01T10:00:00Z",
                "completed_at": "2024-01-01T10:01:30Z"
            }
        }


class ExportFormatInfo(BaseModel):
    """导出格式信息"""
    format: ExportFormat = Field(..., description="格式标识")
    name: str = Field(..., description="格式名称")
    description: str = Field(..., description="格式描述")
    file_extension: str = Field(..., description="文件扩展名")
    media_type: str = Field(..., description="媒体类型")
    options: Dict[str, Any] = Field(default_factory=dict, description="可用选项")


class SupportedFormatsResponse(BaseModel):
    """支持的格式响应"""
    formats: List[ExportFormatInfo] = Field(..., description="支持的格式列表")
    
    class Config:
        schema_extra = {
            "example": {
                "formats": [
                    {
                        "format": "pdf_teaching_plan",
                        "name": "PDF教案",
                        "description": "生成详细的PDF格式教案文档",
                        "file_extension": ".pdf",
                        "media_type": "application/pdf",
                        "options": {
                            "include_objectives": True,
                            "include_activities": True,
                            "include_assessments": True,
                            "detailed_lessons": True
                        }
                    },
                    {
                        "format": "docx",
                        "name": "Word文档",
                        "description": "生成可编辑的Word格式文档",
                        "file_extension": ".docx",
                        "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "options": {
                            "type": "complete",
                            "include_images": True
                        }
                    }
                ]
            }
        }


class ExportHistoryResponse(BaseModel):
    """导出历史响应"""
    exports: List[CourseExportResponse] = Field(..., description="导出记录列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页面大小")


class ExportStatistics(BaseModel):
    """导出统计"""
    total_exports: int = Field(..., description="总导出次数")
    format_breakdown: Dict[ExportFormat, int] = Field(..., description="格式分布")
    success_rate: float = Field(..., description="成功率")
    average_processing_time: float = Field(..., description="平均处理时间（秒）")
    most_popular_format: ExportFormat = Field(..., description="最受欢迎的格式")


# PDF特定选项
class PDFExportOptions(BaseModel):
    """PDF导出选项"""
    include_objectives: bool = Field(default=True, description="包含学习目标")
    include_activities: bool = Field(default=True, description="包含活动内容")
    include_assessments: bool = Field(default=True, description="包含评估信息")
    include_resources: bool = Field(default=True, description="包含资源列表")
    detailed_lessons: bool = Field(default=True, description="详细课时信息")
    page_size: str = Field(default="A4", description="页面尺寸")
    orientation: str = Field(default="portrait", description="页面方向")
    font_size: int = Field(default=12, description="字体大小")


# Word文档特定选项
class DocxExportOptions(BaseModel):
    """Word文档导出选项"""
    type: str = Field(default="complete", description="文档类型")
    include_images: bool = Field(default=True, description="包含图片")
    include_tables: bool = Field(default=True, description="包含表格")
    template_style: str = Field(default="modern", description="模板样式")
    page_margins: Dict[str, float] = Field(
        default_factory=lambda: {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        description="页面边距（英寸）"
    )


# PowerPoint特定选项
class PptxExportOptions(BaseModel):
    """PowerPoint导出选项"""
    slide_layout: str = Field(default="standard", description="幻灯片布局")
    include_notes: bool = Field(default=True, description="包含备注")
    animation_style: str = Field(default="none", description="动画样式")
    theme: str = Field(default="default", description="主题")
    slides_per_lesson: int = Field(default=3, description="每课时幻灯片数")


# JSON导出特定选项
class JsonExportOptions(BaseModel):
    """JSON导出选项"""
    include_metadata: bool = Field(default=True, description="包含元数据")
    include_relationships: bool = Field(default=True, description="包含关联关系")
    pretty_print: bool = Field(default=True, description="格式化输出")
    encoding: str = Field(default="utf-8", description="编码格式")