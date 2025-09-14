"""
课程模板API接口
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models.user import User
from ...models.course import Course
from ...core.auth import get_current_user
from ...services.template_service import template_service, TemplateCategory
from ...schemas.template import (
    TemplateResponse,
    TemplateListResponse,
    CreateTemplateRequest,
    CreateCourseFromTemplateRequest,
    TemplateCustomization
)

router = APIRouter(prefix="/templates", tags=["课程模板"])


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[TemplateCategory] = Query(None, description="模板分类"),
    subject: Optional[str] = Query(None, description="学科"),
    education_level: Optional[str] = Query(None, description="教育学段"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(default=20, le=100, description="返回数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    db: AsyncSession = Depends(get_db)
):
    """获取模板列表"""
    
    templates = await template_service.get_templates(
        db=db,
        category=category,
        subject=subject,
        education_level=education_level,
        search_query=search,
        limit=limit,
        offset=offset
    )
    
    # 获取总数（简化版，实际应用中需要单独查询）
    total = len(templates)  # 这里应该是单独的count查询
    
    return TemplateListResponse(
        templates=[TemplateResponse.from_orm(template) for template in templates],
        total=total,
        page=offset // limit + 1,
        page_size=limit
    )


@router.get("/popular", response_model=List[TemplateResponse])
async def get_popular_templates(
    limit: int = Query(default=10, le=20, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门模板"""
    
    templates = await template_service.get_popular_templates(db, limit)
    return [TemplateResponse.from_orm(template) for template in templates]


@router.get("/recommended", response_model=List[TemplateResponse])
async def get_recommended_templates(
    limit: int = Query(default=10, le=20, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取推荐模板"""
    
    templates = await template_service.get_recommended_templates(db, current_user, limit)
    return [TemplateResponse.from_orm(template) for template in templates]


@router.get("/predefined")
async def get_predefined_templates():
    """获取预定义模板"""
    
    return {
        "templates": template_service.get_predefined_templates(),
        "message": "预定义模板列表"
    }


@router.get("/categories")
async def get_template_categories():
    """获取模板分类"""
    
    return {
        "categories": [
            {
                "value": category.value,
                "label": _get_category_label(category),
                "description": _get_category_description(category)
            }
            for category in TemplateCategory
        ]
    }


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_detail(
    template_id: UUID = Path(..., description="模板ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取模板详情"""
    
    template = await template_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return TemplateResponse.from_orm(template)


@router.post("", response_model=TemplateResponse)
async def create_template(
    request: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从现有课程创建模板"""
    
    # 查询源课程
    from sqlalchemy import select
    from ...models.course import Course
    
    result = await db.execute(
        select(Course).where(Course.id == request.course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="源课程不存在")
    
    # 检查权限（简化版）
    if course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限访问该课程")
    
    # 创建模板
    template = await template_service.create_template_from_course(
        db=db,
        course=course,
        template_name=request.name,
        template_description=request.description,
        category=request.category,
        user=current_user
    )
    
    return TemplateResponse.from_orm(template)


@router.post("/{template_id}/create-course")
async def create_course_from_template(
    template_id: UUID = Path(..., description="模板ID"),
    request: CreateCourseFromTemplateRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从模板创建新课程"""
    
    if not request:
        request = CreateCourseFromTemplateRequest(
            title="基于模板的新课程",
            customizations={}
        )
    
    try:
        course = await template_service.create_course_from_template(
            db=db,
            template_id=template_id,
            course_title=request.title,
            customizations=request.customizations,
            user=current_user
        )
        
        return {
            "course_id": course.id,
            "title": course.title,
            "message": "课程创建成功"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建课程失败: {str(e)}")


@router.get("/{template_id}/preview")
async def preview_template_course(
    template_id: UUID = Path(..., description="模板ID"),
    customizations: Dict[str, Any] = Query(default={}, description="自定义配置"),
    db: AsyncSession = Depends(get_db)
):
    """预览基于模板的课程结构"""
    
    template = await template_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 应用自定义配置
    preview_data = template_service._apply_customizations(
        template.template_data, 
        customizations
    )
    
    return {
        "template_name": template.name,
        "preview_data": preview_data,
        "customizations_applied": customizations
    }


@router.post("/initialize-defaults")
async def initialize_default_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """初始化默认模板（管理员功能）"""
    
    # 这里应该检查管理员权限
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        await template_service.initialize_default_templates(db)
        return {"message": "默认模板初始化成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化失败: {str(e)}")


@router.get("/{template_id}/customization-options")
async def get_customization_options(
    template_id: UUID = Path(..., description="模板ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取模板的自定义选项"""
    
    template = await template_service.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 分析模板数据，提供可自定义的选项
    customization_options = {
        "basic_info": {
            "title": {"type": "string", "required": True, "description": "课程标题"},
            "subtitle": {"type": "string", "required": False, "description": "课程副标题"},
            "duration_weeks": {"type": "integer", "min": 1, "max": 52, "description": "课程周数"},
            "duration_hours": {"type": "integer", "min": 1, "max": 200, "description": "总学时"},
            "difficulty_level": {
                "type": "select",
                "options": ["beginner", "intermediate", "advanced"],
                "description": "难度等级"
            }
        },
        "learning_design": {
            "learning_objectives": {"type": "array", "description": "学习目标"},
            "driving_question": {"type": "text", "description": "驱动性问题"},
            "final_products": {"type": "array", "description": "最终产品"}
        },
        "structure": {
            "phases": {"type": "array", "description": "课程阶段"},
            "phase_duration": {"type": "object", "description": "各阶段时长"}
        }
    }
    
    return {
        "template_id": template_id,
        "template_name": template.name,
        "customization_options": customization_options,
        "current_defaults": template.template_data
    }


# 辅助函数

def _get_category_label(category: TemplateCategory) -> str:
    """获取分类标签"""
    labels = {
        TemplateCategory.STEM: "STEM教育",
        TemplateCategory.HUMANITIES: "人文学科",
        TemplateCategory.ARTS: "艺术类",
        TemplateCategory.SOCIAL_STUDIES: "社会研究",
        TemplateCategory.LANGUAGE: "语言类",
        TemplateCategory.INTERDISCIPLINARY: "跨学科",
        TemplateCategory.PROJECT_BASED: "项目式学习",
        TemplateCategory.INQUIRY_BASED: "探究式学习",
        TemplateCategory.DESIGN_THINKING: "设计思维",
        TemplateCategory.COMMUNITY_SERVICE: "社区服务"
    }
    return labels.get(category, category.value)


def _get_category_description(category: TemplateCategory) -> str:
    """获取分类描述"""
    descriptions = {
        TemplateCategory.STEM: "科学、技术、工程、数学跨学科项目",
        TemplateCategory.HUMANITIES: "语言、文学、历史、哲学等人文学科",
        TemplateCategory.ARTS: "美术、音乐、舞蹈等艺术创作项目",
        TemplateCategory.SOCIAL_STUDIES: "社会议题调研和公民教育项目",
        TemplateCategory.LANGUAGE: "语言学习和文学创作项目",
        TemplateCategory.INTERDISCIPLINARY: "整合多个学科的综合性项目",
        TemplateCategory.PROJECT_BASED: "以项目为中心的学习模式",
        TemplateCategory.INQUIRY_BASED: "以探究为导向的学习方式",
        TemplateCategory.DESIGN_THINKING: "运用设计思维解决问题",
        TemplateCategory.COMMUNITY_SERVICE: "服务学习和社会实践项目"
    }
    return descriptions.get(category, "")