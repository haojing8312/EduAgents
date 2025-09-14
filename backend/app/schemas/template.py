"""
模板相关的Pydantic模型
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field

from ..services.template_service import TemplateCategory


class TemplateResponse(BaseModel):
    """模板响应"""
    id: UUID = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: TemplateCategory = Field(..., description="模板分类")
    preview_image: Optional[str] = Field(None, description="预览图")
    
    # 适用范围
    subjects: Optional[List[str]] = Field(None, description="适用学科")
    education_levels: Optional[List[str]] = Field(None, description="适用学段")
    
    # 统计信息
    use_count: int = Field(default=0, description="使用次数")
    rating: float = Field(default=0.0, description="评分")
    
    # 模板数据（简化版，不包含完整的template_data）
    basic_info: Optional[Dict[str, Any]] = Field(None, description="基础信息")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, template):
        """从ORM对象创建响应"""
        # 提取基础信息
        basic_info = None
        if template.template_data and 'basic_info' in template.template_data:
            basic_info = template.template_data['basic_info']
        
        return cls(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            preview_image=template.preview_image,
            subjects=template.subjects,
            education_levels=template.education_levels,
            use_count=template.use_count,
            rating=template.rating,
            basic_info=basic_info,
            created_at=template.created_at,
            updated_at=template.updated_at
        )


class TemplateDetailResponse(TemplateResponse):
    """模板详情响应（包含完整数据）"""
    template_data: Dict[str, Any] = Field(..., description="完整模板数据")
    
    @classmethod
    def from_orm(cls, template):
        """从ORM对象创建详情响应"""
        base_data = super().from_orm(template)
        return cls(
            **base_data.dict(),
            template_data=template.template_data or {}
        )


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: List[TemplateResponse] = Field(..., description="模板列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页面大小")


class CreateTemplateRequest(BaseModel):
    """创建模板请求"""
    name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    description: str = Field(..., min_length=1, description="模板描述")
    category: TemplateCategory = Field(..., description="模板分类")
    course_id: UUID = Field(..., description="源课程ID")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "我的STEM项目模板",
                "description": "基于成功实施的环保主题STEM项目创建的模板",
                "category": "stem",
                "course_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class CreateCourseFromTemplateRequest(BaseModel):
    """从模板创建课程请求"""
    title: str = Field(..., min_length=1, max_length=200, description="课程标题")
    customizations: Dict[str, Any] = Field(
        default_factory=dict, 
        description="自定义配置"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "title": "智能交通系统设计项目",
                "customizations": {
                    "basic_info": {
                        "duration_weeks": 10,
                        "difficulty_level": "advanced"
                    },
                    "learning_design": {
                        "driving_question": "如何设计一个智能交通管理系统来缓解城市交通拥堵？"
                    }
                }
            }
        }


class TemplateCustomization(BaseModel):
    """模板自定义配置"""
    
    class BasicInfo(BaseModel):
        """基础信息自定义"""
        title: Optional[str] = Field(None, description="课程标题")
        subtitle: Optional[str] = Field(None, description="课程副标题")
        duration_weeks: Optional[int] = Field(None, ge=1, le=52, description="课程周数")
        duration_hours: Optional[int] = Field(None, ge=1, le=200, description="总学时")
        difficulty_level: Optional[str] = Field(None, description="难度等级")
        class_size_min: Optional[int] = Field(None, ge=1, description="最小班级规模")
        class_size_max: Optional[int] = Field(None, ge=1, description="最大班级规模")
    
    class LearningDesign(BaseModel):
        """学习设计自定义"""
        learning_objectives: Optional[List[str]] = Field(None, description="学习目标")
        driving_question: Optional[str] = Field(None, description="驱动性问题")
        final_products: Optional[List[str]] = Field(None, description="最终产品")
        core_competencies: Optional[List[str]] = Field(None, description="核心素养")
    
    class Structure(BaseModel):
        """结构自定义"""
        phases: Optional[List[Dict[str, Any]]] = Field(None, description="课程阶段")
        phase_duration: Optional[Dict[str, int]] = Field(None, description="阶段时长")
    
    basic_info: Optional[BasicInfo] = Field(None, description="基础信息")
    learning_design: Optional[LearningDesign] = Field(None, description="学习设计")
    structure: Optional[Structure] = Field(None, description="结构配置")


class TemplateCategory(BaseModel):
    """模板分类信息"""
    value: str = Field(..., description="分类值")
    label: str = Field(..., description="分类标签")
    description: str = Field(..., description="分类描述")


class CustomizationOption(BaseModel):
    """自定义选项"""
    type: str = Field(..., description="选项类型")
    required: bool = Field(default=False, description="是否必需")
    description: str = Field(..., description="选项描述")
    options: Optional[List[str]] = Field(None, description="可选值（对于select类型）")
    min: Optional[int] = Field(None, description="最小值（对于数值类型）")
    max: Optional[int] = Field(None, description="最大值（对于数值类型）")
    default: Optional[Any] = Field(None, description="默认值")


class CustomizationOptionsResponse(BaseModel):
    """自定义选项响应"""
    template_id: UUID = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    customization_options: Dict[str, Dict[str, CustomizationOption]] = Field(
        ..., description="自定义选项"
    )
    current_defaults: Dict[str, Any] = Field(..., description="当前默认值")


class TemplatePreviewResponse(BaseModel):
    """模板预览响应"""
    template_name: str = Field(..., description="模板名称")
    preview_data: Dict[str, Any] = Field(..., description="预览数据")
    customizations_applied: Dict[str, Any] = Field(..., description="应用的自定义配置")


class TemplateStatistics(BaseModel):
    """模板统计信息"""
    total_templates: int = Field(..., description="模板总数")
    category_distribution: Dict[str, int] = Field(..., description="分类分布")
    most_used_templates: List[TemplateResponse] = Field(..., description="最常用模板")
    highest_rated_templates: List[TemplateResponse] = Field(..., description="评分最高模板")
    recent_templates: List[TemplateResponse] = Field(..., description="最新模板")


class TemplateSearchRequest(BaseModel):
    """模板搜索请求"""
    query: Optional[str] = Field(None, description="搜索关键词")
    categories: Optional[List[TemplateCategory]] = Field(None, description="分类过滤")
    subjects: Optional[List[str]] = Field(None, description="学科过滤")
    education_levels: Optional[List[str]] = Field(None, description="学段过滤")
    difficulty_levels: Optional[List[str]] = Field(None, description="难度过滤")
    duration_range: Optional[Dict[str, int]] = Field(None, description="时长范围")
    rating_min: Optional[float] = Field(None, ge=0, le=5, description="最低评分")
    sort_by: Optional[str] = Field(default="popularity", description="排序方式")
    sort_order: Optional[str] = Field(default="desc", description="排序顺序")


class TemplateUsageReport(BaseModel):
    """模板使用报告"""
    template_id: UUID = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    total_uses: int = Field(..., description="总使用次数")
    recent_uses: int = Field(..., description="近期使用次数")
    success_rate: float = Field(..., description="成功创建率")
    average_rating: float = Field(..., description="平均评分")
    popular_customizations: Dict[str, Any] = Field(..., description="热门自定义配置")
    user_feedback: List[str] = Field(..., description="用户反馈")


class BulkTemplateOperation(BaseModel):
    """批量模板操作"""
    template_ids: List[UUID] = Field(..., description="模板ID列表")
    operation: str = Field(..., description="操作类型")
    parameters: Optional[Dict[str, Any]] = Field(None, description="操作参数")
    
    class Config:
        schema_extra = {
            "example": {
                "template_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "operation": "update_category",
                "parameters": {
                    "new_category": "stem"
                }
            }
        }