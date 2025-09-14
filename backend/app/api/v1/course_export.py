"""
课程导出API接口
提供多格式导出功能
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
import zipfile
from io import BytesIO
import tempfile

from ...core.database import get_db
from ...models.course import Course, CourseExport
from ...services.document_generator import document_generator_service, DocumentGeneratorError
from ...schemas.course_export import (
    CourseExportRequest,
    CourseExportResponse,
    ExportFormat,
    ExportStatus,
    BatchExportRequest
)
from ...core.auth import get_current_user
from ...models.user import User

router = APIRouter(prefix="/courses", tags=["课程导出"])


@router.post("/{course_id}/export", response_model=CourseExportResponse)
async def export_course(
    course_id: UUID,
    export_request: CourseExportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出课程为指定格式
    
    支持的格式：
    - pdf_teaching_plan: PDF教案
    - pdf_handbook: PDF学生手册
    - pdf_rubric: PDF评估量规
    - docx: Word文档
    - pptx: PowerPoint演示文稿
    - json: JSON数据
    """
    
    # 查询课程
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources)
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查权限（简化版，实际应用中需要更详细的权限检查）
    # 这里假设用户有权限访问课程
    
    # 创建导出记录
    export_record = CourseExport(
        course_id=course_id,
        format=export_request.format,
        status=ExportStatus.PENDING,
        export_options=export_request.options,
        created_by=current_user.id
    )
    
    db.add(export_record)
    await db.commit()
    await db.refresh(export_record)
    
    # 异步处理导出
    if export_request.async_export:
        background_tasks.add_task(
            _process_export_async,
            export_record.id,
            course,
            export_request.format,
            export_request.options
        )
        
        return CourseExportResponse(
            export_id=export_record.id,
            status=ExportStatus.PENDING,
            message="导出任务已创建，请稍后查询结果"
        )
    else:
        # 同步导出
        try:
            content = await document_generator_service.generate_document(
                course,
                export_request.format,
                export_request.options
            )
            
            # 保存文件
            file_path = await _save_export_file(export_record.id, content, export_request.format)
            
            # 更新导出记录
            export_record.status = ExportStatus.COMPLETED
            export_record.file_path = file_path
            export_record.file_size = len(content)
            export_record.completed_at = datetime.utcnow()
            
            await db.commit()
            
            return CourseExportResponse(
                export_id=export_record.id,
                status=ExportStatus.COMPLETED,
                file_path=file_path,
                file_size=len(content),
                download_url=f"/api/v1/exports/{export_record.id}/download"
            )
            
        except DocumentGeneratorError as e:
            export_record.status = ExportStatus.FAILED
            export_record.error_message = str(e)
            await db.commit()
            
            raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/{course_id}/export/formats")
async def get_supported_formats():
    """获取支持的导出格式"""
    return {
        "formats": document_generator_service.get_supported_formats(),
        "descriptions": {
            "pdf_teaching_plan": "PDF格式教案",
            "pdf_handbook": "PDF格式学生手册",
            "pdf_rubric": "PDF格式评估量规",
            "docx": "Word文档",
            "pptx": "PowerPoint演示文稿",
            "json": "JSON数据格式"
        }
    }


@router.post("/{course_id}/export/batch", response_model=List[CourseExportResponse])
async def batch_export_course(
    course_id: UUID,
    batch_request: BatchExportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量导出课程为多种格式"""
    
    # 查询课程
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources)
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    export_responses = []
    
    for export_format in batch_request.formats:
        # 创建导出记录
        export_record = CourseExport(
            course_id=course_id,
            format=export_format,
            status=ExportStatus.PENDING,
            export_options=batch_request.options.get(export_format, {}),
            created_by=current_user.id
        )
        
        db.add(export_record)
        await db.commit()
        await db.refresh(export_record)
        
        # 添加后台任务
        background_tasks.add_task(
            _process_export_async,
            export_record.id,
            course,
            export_format,
            batch_request.options.get(export_format, {})
        )
        
        export_responses.append(CourseExportResponse(
            export_id=export_record.id,
            status=ExportStatus.PENDING,
            format=export_format,
            message="导出任务已创建"
        ))
    
    return export_responses


@router.get("/{course_id}/export/package")
async def export_complete_package(
    course_id: UUID,
    formats: List[str] = Query(default=["pdf_teaching_plan", "pdf_handbook", "docx", "json"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出完整教学资料包（ZIP压缩包）"""
    
    # 查询课程
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.lessons),
            selectinload(Course.assessments),
            selectinload(Course.resources)
        )
        .where(Course.id == course_id, Course.is_deleted == False)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    try:
        # 生成所有格式的文档
        documents = await document_generator_service.generate_complete_package(
            course, formats
        )
        
        # 创建ZIP文件
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for format_type, content in documents.items():
                filename = _get_filename_for_format(course.title, format_type)
                zip_file.writestr(filename, content)
            
            # 添加课程信息文件
            course_info = {
                "course_title": course.title,
                "export_date": datetime.now().isoformat(),
                "formats_included": list(documents.keys()),
                "course_summary": {
                    "subject": course.subject,
                    "education_level": course.education_level,
                    "duration_weeks": course.duration_weeks,
                    "duration_hours": course.duration_hours
                }
            }
            zip_file.writestr("课程信息.json", 
                             json.dumps(course_info, ensure_ascii=False, indent=2))
        
        zip_buffer.seek(0)
        
        # 返回ZIP文件
        return StreamingResponse(
            BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=\"{course.title}_教学资料包.zip\""
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/exports/{export_id}/status", response_model=CourseExportResponse)
async def get_export_status(
    export_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询导出状态"""
    
    result = await db.execute(
        select(CourseExport)
        .where(CourseExport.id == export_id)
    )
    export_record = result.scalar_one_or_none()
    
    if not export_record:
        raise HTTPException(status_code=404, detail="导出记录不存在")
    
    return CourseExportResponse(
        export_id=export_record.id,
        status=export_record.status,
        format=export_record.format,
        file_path=export_record.file_path,
        file_size=export_record.file_size,
        download_url=f"/api/v1/exports/{export_record.id}/download" if export_record.status == ExportStatus.COMPLETED else None,
        error_message=export_record.error_message,
        created_at=export_record.created_at,
        completed_at=export_record.completed_at
    )


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载导出文件"""
    
    result = await db.execute(
        select(CourseExport)
        .options(selectinload(CourseExport.course))
        .where(CourseExport.id == export_id)
    )
    export_record = result.scalar_one_or_none()
    
    if not export_record:
        raise HTTPException(status_code=404, detail="导出记录不存在")
    
    if export_record.status != ExportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="文件尚未生成完成")
    
    if not export_record.file_path or not os.path.exists(export_record.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 确定文件名和媒体类型
    filename = _get_filename_for_format(export_record.course.title, export_record.format)
    media_type = _get_media_type_for_format(export_record.format)
    
    return FileResponse(
        export_record.file_path,
        media_type=media_type,
        filename=filename
    )


@router.delete("/exports/{export_id}")
async def delete_export(
    export_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除导出文件"""
    
    result = await db.execute(
        select(CourseExport)
        .where(CourseExport.id == export_id)
    )
    export_record = result.scalar_one_or_none()
    
    if not export_record:
        raise HTTPException(status_code=404, detail="导出记录不存在")
    
    # 删除文件
    if export_record.file_path and os.path.exists(export_record.file_path):
        os.remove(export_record.file_path)
    
    # 删除记录
    await db.delete(export_record)
    await db.commit()
    
    return {"message": "导出记录已删除"}


@router.get("/{course_id}/exports", response_model=List[CourseExportResponse])
async def list_course_exports(
    course_id: UUID,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取课程的导出历史"""
    
    result = await db.execute(
        select(CourseExport)
        .where(CourseExport.course_id == course_id)
        .order_by(CourseExport.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    exports = result.scalars().all()
    
    return [
        CourseExportResponse(
            export_id=export.id,
            status=export.status,
            format=export.format,
            file_path=export.file_path,
            file_size=export.file_size,
            download_url=f"/api/v1/exports/{export.id}/download" if export.status == ExportStatus.COMPLETED else None,
            error_message=export.error_message,
            created_at=export.created_at,
            completed_at=export.completed_at
        )
        for export in exports
    ]


# 辅助函数

async def _process_export_async(
    export_id: UUID,
    course: Course,
    format_type: str,
    options: Dict[str, Any]
):
    """异步处理导出任务"""
    from ...core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # 获取导出记录
            result = await db.execute(
                select(CourseExport).where(CourseExport.id == export_id)
            )
            export_record = result.scalar_one()
            
            # 更新状态为处理中
            export_record.status = ExportStatus.PROCESSING
            export_record.started_at = datetime.utcnow()
            await db.commit()
            
            # 生成文档
            content = await document_generator_service.generate_document(
                course, format_type, options
            )
            
            # 保存文件
            file_path = await _save_export_file(export_id, content, format_type)
            
            # 更新记录
            export_record.status = ExportStatus.COMPLETED
            export_record.file_path = file_path
            export_record.file_size = len(content)
            export_record.completed_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            # 更新失败状态
            export_record.status = ExportStatus.FAILED
            export_record.error_message = str(e)
            await db.commit()


async def _save_export_file(export_id: UUID, content: bytes, format_type: str) -> str:
    """保存导出文件"""
    # 创建导出目录
    export_dir = os.path.join(settings.STORAGE_LOCAL_PATH, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    # 生成文件名
    extension = _get_file_extension_for_format(format_type)
    filename = f"{export_id}{extension}"
    file_path = os.path.join(export_dir, filename)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return file_path


def _get_file_extension_for_format(format_type: str) -> str:
    """根据格式获取文件扩展名"""
    extensions = {
        'pdf_teaching_plan': '.pdf',
        'pdf_handbook': '.pdf',
        'pdf_rubric': '.pdf',
        'docx': '.docx',
        'pptx': '.pptx',
        'json': '.json'
    }
    return extensions.get(format_type, '.bin')


def _get_filename_for_format(course_title: str, format_type: str) -> str:
    """根据格式生成文件名"""
    safe_title = "".join(c for c in course_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    names = {
        'pdf_teaching_plan': f"{safe_title}_教案.pdf",
        'pdf_handbook': f"{safe_title}_学生手册.pdf",
        'pdf_rubric': f"{safe_title}_评估量规.pdf",
        'docx': f"{safe_title}_完整课程.docx",
        'pptx': f"{safe_title}_课程演示.pptx",
        'json': f"{safe_title}_课程数据.json"
    }
    return names.get(format_type, f"{safe_title}.bin")


def _get_media_type_for_format(format_type: str) -> str:
    """根据格式获取媒体类型"""
    media_types = {
        'pdf_teaching_plan': 'application/pdf',
        'pdf_handbook': 'application/pdf',
        'pdf_rubric': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'json': 'application/json'
    }
    return media_types.get(format_type, 'application/octet-stream')