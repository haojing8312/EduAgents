"""
Course Export and Material Generation Service
Provides comprehensive export capabilities for AI-generated courses in multiple formats
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import zipfile

try:
    from docx import Document
    from docx.shared import Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

try:
    import markdown
    from markdown.extensions import codehilite, tables, toc
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    markdown = None

from app.core.config import settings
from app.core.cache import smart_cache_manager
from app.models.course import Course
from app.services.course_persistence_service import get_persistence_service


logger = logging.getLogger(__name__)


class CourseExportFormat:
    """Supported export formats"""

    JSON = "json"
    MARKDOWN = "markdown"
    DOCX = "docx"
    HTML = "html"
    PDF = "pdf"
    SCORM = "scorm"


class MaterialGenerator:
    """Generates educational materials from course data"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load content templates for different material types"""
        return {
            "lesson_plan": """
# {title}

## 课程概述
{description}

## 学习目标
{objectives}

## 教学活动
{activities}

## 评估方式
{assessments}

## 所需资源
{resources}
""",
            "student_guide": """
# 学生学习指南: {title}

## 课程介绍
{introduction}

## 学习路径
{learning_path}

## 项目任务
{project_tasks}

## 自评工具
{self_assessment}
""",
            "assessment_rubric": """
# 评价量规: {title}

## 评价维度
{criteria}

## 评分标准
{scoring_guide}

## 反馈建议
{feedback_guidelines}
"""
        }

    async def generate_lesson_plans(self, course_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed lesson plans for each course module"""
        lesson_plans = []

        course_architect = course_data.get("course_architect", {})
        content_designer = course_data.get("content_designer", {})

        # Extract phases/modules
        phases = course_architect.get("course_structure", {}).get("phases", [])
        scenarios = content_designer.get("learning_scenarios", [])

        for i, phase in enumerate(phases):
            lesson_plan = {
                "id": f"lesson_{i+1}",
                "title": phase.get("title", f"第{i+1}阶段"),
                "description": phase.get("description", ""),
                "duration": phase.get("duration", "1周"),
                "objectives": phase.get("objectives", []),
                "activities": self._extract_activities_for_phase(phase, scenarios),
                "assessments": phase.get("assessments", []),
                "resources": phase.get("resources", []),
                "content": self._format_lesson_plan(phase, scenarios)
            }
            lesson_plans.append(lesson_plan)

        return lesson_plans

    def _extract_activities_for_phase(self, phase: Dict, scenarios: List[Dict]) -> List[Dict]:
        """Extract and match activities for a specific phase"""
        activities = []

        # Add phase-specific activities
        if "activities" in phase:
            for activity in phase["activities"]:
                activities.append({
                    "type": "phase_activity",
                    "title": activity.get("title", "学习活动"),
                    "description": activity.get("description", ""),
                    "duration": activity.get("duration", "45分钟")
                })

        # Match relevant scenarios
        phase_title = phase.get("title", "").lower()
        for scenario in scenarios:
            scenario_title = scenario.get("title", "").lower()
            if any(keyword in scenario_title for keyword in phase_title.split()):
                activities.append({
                    "type": "learning_scenario",
                    "title": scenario.get("title", ""),
                    "description": scenario.get("description", ""),
                    "context": scenario.get("context", ""),
                    "tasks": scenario.get("tasks", [])
                })

        return activities

    def _format_lesson_plan(self, phase: Dict, scenarios: List[Dict]) -> str:
        """Format lesson plan content using template"""
        activities_text = []
        for activity in self._extract_activities_for_phase(phase, scenarios):
            activities_text.append(f"### {activity['title']}\n{activity['description']}")

        return self.templates["lesson_plan"].format(
            title=phase.get("title", "课程阶段"),
            description=phase.get("description", ""),
            objectives="\n".join([f"- {obj}" for obj in phase.get("objectives", [])]),
            activities="\n\n".join(activities_text),
            assessments="\n".join([f"- {assess}" for assess in phase.get("assessments", [])]),
            resources="\n".join([f"- {res}" for res in phase.get("resources", [])])
        )

    async def generate_student_guide(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive student learning guide"""
        course_architect = course_data.get("course_architect", {})
        content_designer = course_data.get("content_designer", {})
        assessment_expert = course_data.get("assessment_expert", {})

        guide = {
            "title": course_architect.get("course_structure", {}).get("title", "AI时代PBL课程"),
            "introduction": course_architect.get("course_structure", {}).get("description", ""),
            "learning_path": self._create_learning_path(course_architect),
            "project_tasks": self._extract_project_tasks(content_designer),
            "self_assessment": self._create_self_assessment_tools(assessment_expert),
            "content": ""
        }

        guide["content"] = self.templates["student_guide"].format(**guide)
        return guide

    def _create_learning_path(self, course_architect: Dict) -> str:
        """Create a visual learning path from course structure"""
        phases = course_architect.get("course_structure", {}).get("phases", [])
        path_text = []

        for i, phase in enumerate(phases):
            path_text.append(f"{i+1}. **{phase.get('title', f'阶段{i+1}')}** ({phase.get('duration', '1周')})")
            if phase.get("description"):
                path_text.append(f"   - {phase['description']}")

        return "\n".join(path_text)

    def _extract_project_tasks(self, content_designer: Dict) -> str:
        """Extract project tasks from content designer output"""
        scenarios = content_designer.get("learning_scenarios", [])
        tasks_text = []

        for scenario in scenarios:
            tasks_text.append(f"## {scenario.get('title', '项目任务')}")
            if scenario.get("context"):
                tasks_text.append(f"**项目背景**: {scenario['context']}")

            if scenario.get("tasks"):
                tasks_text.append("**具体任务**:")
                for task in scenario["tasks"]:
                    tasks_text.append(f"- {task}")

        return "\n\n".join(tasks_text)

    def _create_self_assessment_tools(self, assessment_expert: Dict) -> str:
        """Create self-assessment tools from assessment expert output"""
        assessment_text = []

        if assessment_expert.get("evaluation_methods"):
            assessment_text.append("## 自我评价工具")
            for method in assessment_expert["evaluation_methods"]:
                if isinstance(method, dict):
                    assessment_text.append(f"### {method.get('name', '评价方法')}")
                    assessment_text.append(f"{method.get('description', '')}")
                else:
                    assessment_text.append(f"- {method}")

        if assessment_expert.get("rubrics"):
            assessment_text.append("\n## 评价标准")
            for rubric in assessment_expert["rubrics"]:
                if isinstance(rubric, dict):
                    assessment_text.append(f"### {rubric.get('criteria', '评价标准')}")
                    assessment_text.append(f"{rubric.get('description', '')}")

        return "\n".join(assessment_text)


class CourseExportService:
    """Main service for exporting courses in various formats"""

    def __init__(self):
        self.material_generator = MaterialGenerator()
        self.temp_dir = Path(tempfile.gettempdir()) / "pbl_exports"
        self.temp_dir.mkdir(exist_ok=True)

    async def export_course(
        self,
        course_id: str,
        export_format: str,
        include_materials: bool = True,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export a course in the specified format

        Args:
            course_id: Course ID to export
            export_format: Target format (json, markdown, docx, html, etc.)
            include_materials: Whether to include generated materials
            custom_options: Format-specific options

        Returns:
            Export result with file paths and metadata
        """
        try:
            # Get course data
            course_data = await self._get_course_data(course_id)
            if not course_data:
                return {
                    "success": False,
                    "error": "Course not found",
                    "course_id": course_id
                }

            # Check cache first
            cache_key = f"export:{course_id}:{export_format}:{include_materials}"
            if smart_cache_manager.initialized:
                cached_result = await smart_cache_manager.get(cache_key, cache_type="export")
                if cached_result:
                    logger.info(f"🎯 Export cache hit for course {course_id}")
                    return cached_result

            # Generate materials if requested
            materials = {}
            if include_materials:
                materials = await self._generate_course_materials(course_data)

            # Export in requested format
            export_result = await self._export_to_format(
                course_data, materials, export_format, custom_options or {}
            )

            # Cache result
            if smart_cache_manager.initialized and export_result.get("success"):
                await smart_cache_manager.set(
                    cache_key,
                    export_result,
                    expire=1800,  # 30 minutes
                    cache_type="export"
                )

            logger.info(f"✅ Course exported successfully: {course_id} -> {export_format}")
            return export_result

        except Exception as e:
            logger.error(f"❌ Course export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "course_id": course_id,
                "format": export_format
            }

    async def _get_course_data(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete course data including AI agent outputs"""
        try:
            async with await get_persistence_service() as persistence:
                course = await persistence.get_course_by_id(uuid.UUID(course_id))
                if course:
                    # Extract agent data from extra_data
                    agent_data = course.extra_data.get("agent_data", {})

                    # Build comprehensive course data
                    course_data = {
                        "course_id": str(course.id),
                        "title": course.title,
                        "description": course.description,
                        "subject": course.subject,
                        "education_level": course.education_level,
                        "difficulty_level": course.difficulty_level,
                        "duration_weeks": course.duration_weeks,
                        "duration_hours": course.duration_hours,
                        "learning_objectives": course.learning_objectives,
                        "core_competencies": course.core_competencies,
                        "project_context": course.project_context,
                        "driving_question": course.driving_question,
                        "created_at": course.created_at.isoformat(),
                        "ai_generated": course.extra_data.get("ai_generated", False),
                        **agent_data  # Include all agent outputs
                    }

                    return course_data

                return None

        except Exception as e:
            logger.error(f"❌ Failed to get course data: {e}")
            return None

    async def _generate_course_materials(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all course materials"""
        materials = {}

        try:
            # Generate lesson plans
            materials["lesson_plans"] = await self.material_generator.generate_lesson_plans(course_data)

            # Generate student guide
            materials["student_guide"] = await self.material_generator.generate_student_guide(course_data)

            # Generate assessment rubrics
            materials["assessment_rubrics"] = await self._generate_assessment_rubrics(course_data)

            logger.info(f"📚 Generated {len(materials)} material types")

        except Exception as e:
            logger.error(f"❌ Material generation failed: {e}")
            materials["error"] = str(e)

        return materials

    async def _generate_assessment_rubrics(self, course_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate assessment rubrics from assessment expert output"""
        rubrics = []
        assessment_expert = course_data.get("assessment_expert", {})

        if assessment_expert.get("evaluation_methods"):
            for method in assessment_expert["evaluation_methods"]:
                if isinstance(method, dict):
                    rubric = {
                        "title": method.get("name", "评价量规"),
                        "description": method.get("description", ""),
                        "criteria": method.get("criteria", []),
                        "scoring_guide": method.get("scoring", []),
                        "content": self.material_generator.templates["assessment_rubric"].format(
                            title=method.get("name", "评价量规"),
                            criteria="\n".join([f"- {c}" for c in method.get("criteria", [])]),
                            scoring_guide=method.get("description", ""),
                            feedback_guidelines="根据评价结果提供个性化反馈"
                        )
                    }
                    rubrics.append(rubric)

        return rubrics

    async def _export_to_format(
        self,
        course_data: Dict[str, Any],
        materials: Dict[str, Any],
        export_format: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export course to specific format"""

        if export_format == CourseExportFormat.JSON:
            return await self._export_to_json(course_data, materials, options)
        elif export_format == CourseExportFormat.MARKDOWN:
            return await self._export_to_markdown(course_data, materials, options)
        elif export_format == CourseExportFormat.DOCX:
            return await self._export_to_docx(course_data, materials, options)
        elif export_format == CourseExportFormat.HTML:
            return await self._export_to_html(course_data, materials, options)
        else:
            return {
                "success": False,
                "error": f"Unsupported export format: {export_format}",
                "supported_formats": [
                    CourseExportFormat.JSON,
                    CourseExportFormat.MARKDOWN,
                    CourseExportFormat.DOCX,
                    CourseExportFormat.HTML
                ]
            }

    async def _export_to_json(
        self, course_data: Dict, materials: Dict, options: Dict
    ) -> Dict[str, Any]:
        """Export course as JSON"""
        export_data = {
            "course": course_data,
            "materials": materials,
            "export_info": {
                "format": "json",
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        # Create file
        filename = f"course_{course_data['course_id']}.json"
        file_path = self.temp_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "format": "json",
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_path.stat().st_size,
            "course_id": course_data["course_id"]
        }

    async def _export_to_markdown(
        self, course_data: Dict, materials: Dict, options: Dict
    ) -> Dict[str, Any]:
        """Export course as Markdown"""

        # Build comprehensive markdown content
        md_content = []

        # Course header
        md_content.append(f"# {course_data['title']}")
        md_content.append(f"\n**课程描述**: {course_data['description']}")
        md_content.append(f"\n**学科**: {course_data['subject']}")
        md_content.append(f"**难度**: {course_data['difficulty_level']}")
        md_content.append(f"**时长**: {course_data['duration_weeks']}周 ({course_data['duration_hours']}学时)")

        # Learning objectives
        if course_data.get("learning_objectives"):
            md_content.append("\n## 学习目标")
            for obj in course_data["learning_objectives"]:
                md_content.append(f"- {obj}")

        # Project context
        if course_data.get("project_context"):
            md_content.append("\n## 项目背景")
            md_content.append(course_data["project_context"])

        # Driving question
        if course_data.get("driving_question"):
            md_content.append("\n## 核心问题")
            md_content.append(course_data["driving_question"])

        # Add materials
        if materials.get("lesson_plans"):
            md_content.append("\n## 课程计划")
            for lesson in materials["lesson_plans"]:
                md_content.append(f"\n### {lesson['title']}")
                md_content.append(lesson.get("content", lesson.get("description", "")))

        if materials.get("student_guide"):
            md_content.append("\n## 学生指南")
            md_content.append(materials["student_guide"].get("content", ""))

        # Create file
        filename = f"course_{course_data['course_id']}.md"
        file_path = self.temp_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_content))

        return {
            "success": True,
            "format": "markdown",
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_path.stat().st_size,
            "course_id": course_data["course_id"]
        }

    async def _export_to_docx(
        self, course_data: Dict, materials: Dict, options: Dict
    ) -> Dict[str, Any]:
        """Export course as Word document"""

        if not DOCX_AVAILABLE:
            return {
                "success": False,
                "error": "DOCX export requires python-docx package",
                "course_id": course_data["course_id"]
            }

        # Create Word document
        doc = Document()

        # Title
        title = doc.add_heading(course_data['title'], 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Course info
        doc.add_heading('课程信息', level=1)
        info_table = doc.add_table(rows=5, cols=2)
        info_table.style = 'Table Grid'

        info_data = [
            ('课程名称', course_data['title']),
            ('学科领域', course_data['subject']),
            ('难度等级', course_data['difficulty_level']),
            ('课程时长', f"{course_data['duration_weeks']}周 ({course_data['duration_hours']}学时)"),
            ('创建时间', course_data.get('created_at', 'N/A'))
        ]

        for i, (key, value) in enumerate(info_data):
            info_table.cell(i, 0).text = key
            info_table.cell(i, 1).text = str(value)

        # Course description
        doc.add_heading('课程描述', level=1)
        doc.add_paragraph(course_data['description'])

        # Learning objectives
        if course_data.get('learning_objectives'):
            doc.add_heading('学习目标', level=1)
            for obj in course_data['learning_objectives']:
                doc.add_paragraph(obj, style='List Bullet')

        # Add materials
        if materials.get('lesson_plans'):
            doc.add_heading('课程计划', level=1)
            for lesson in materials['lesson_plans']:
                doc.add_heading(lesson['title'], level=2)
                doc.add_paragraph(lesson.get('description', ''))

        # Create file
        filename = f"course_{course_data['course_id']}.docx"
        file_path = self.temp_dir / filename
        doc.save(str(file_path))

        return {
            "success": True,
            "format": "docx",
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_path.stat().st_size,
            "course_id": course_data["course_id"]
        }

    async def _export_to_html(
        self, course_data: Dict, materials: Dict, options: Dict
    ) -> Dict[str, Any]:
        """Export course as HTML"""

        # Build HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course_data['title']}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .course-info {{ background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .section {{ margin: 30px 0; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 10px; }}
        .objective {{ background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .lesson {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{course_data['title']}</h1>
        <p><strong>AI时代PBL课程设计</strong></p>
    </div>

    <div class="course-info">
        <h2>课程基本信息</h2>
        <p><strong>学科领域:</strong> {course_data['subject']}</p>
        <p><strong>难度等级:</strong> {course_data['difficulty_level']}</p>
        <p><strong>课程时长:</strong> {course_data['duration_weeks']}周 ({course_data['duration_hours']}学时)</p>
        <p><strong>课程描述:</strong> {course_data['description']}</p>
    </div>
"""

        # Learning objectives
        if course_data.get('learning_objectives'):
            html_content += '<div class="section"><h2>学习目标</h2>'
            for obj in course_data['learning_objectives']:
                html_content += f'<div class="objective">• {obj}</div>'
            html_content += '</div>'

        # Project context and driving question
        if course_data.get('project_context'):
            html_content += f'<div class="section"><h2>项目背景</h2><p>{course_data["project_context"]}</p></div>'

        if course_data.get('driving_question'):
            html_content += f'<div class="section"><h2>核心问题</h2><p>{course_data["driving_question"]}</p></div>'

        # Add materials
        if materials.get('lesson_plans'):
            html_content += '<div class="section"><h2>课程计划</h2>'
            for lesson in materials['lesson_plans']:
                html_content += f'''
                <div class="lesson">
                    <h3>{lesson['title']}</h3>
                    <p><strong>时长:</strong> {lesson.get('duration', 'N/A')}</p>
                    <p>{lesson.get('description', '')}</p>
                </div>
                '''
            html_content += '</div>'

        html_content += '</body></html>'

        # Create file
        filename = f"course_{course_data['course_id']}.html"
        file_path = self.temp_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return {
            "success": True,
            "format": "html",
            "file_path": str(file_path),
            "filename": filename,
            "size_bytes": file_path.stat().st_size,
            "course_id": course_data["course_id"]
        }

    async def create_course_package(
        self,
        course_id: str,
        formats: List[str],
        include_materials: bool = True
    ) -> Dict[str, Any]:
        """Create a complete course package with multiple formats"""
        try:
            package_dir = self.temp_dir / f"course_package_{course_id}"
            package_dir.mkdir(exist_ok=True)

            exported_files = []
            errors = []

            # Export in each requested format
            for fmt in formats:
                try:
                    result = await self.export_course(course_id, fmt, include_materials)
                    if result.get("success"):
                        # Copy file to package directory
                        src_path = Path(result["file_path"])
                        dst_path = package_dir / result["filename"]

                        if src_path.exists():
                            import shutil
                            shutil.copy2(src_path, dst_path)
                            exported_files.append({
                                "format": fmt,
                                "filename": result["filename"],
                                "size_bytes": result["size_bytes"]
                            })
                    else:
                        errors.append(f"{fmt}: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    errors.append(f"{fmt}: {str(e)}")

            # Create ZIP package
            zip_filename = f"course_package_{course_id}.zip"
            zip_path = self.temp_dir / zip_filename

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_info in exported_files:
                    file_path = package_dir / file_info["filename"]
                    if file_path.exists():
                        zipf.write(file_path, file_info["filename"])

                # Add package info
                package_info = {
                    "course_id": course_id,
                    "created_at": datetime.now().isoformat(),
                    "formats": [f["format"] for f in exported_files],
                    "total_files": len(exported_files),
                    "errors": errors
                }

                zipf.writestr("package_info.json", json.dumps(package_info, ensure_ascii=False, indent=2))

            return {
                "success": True,
                "package_path": str(zip_path),
                "package_filename": zip_filename,
                "package_size_bytes": zip_path.stat().st_size,
                "exported_files": exported_files,
                "errors": errors,
                "course_id": course_id
            }

        except Exception as e:
            logger.error(f"❌ Package creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "course_id": course_id
            }


# Global export service instance
export_service = CourseExportService()


async def export_course_to_format(
    course_id: str,
    export_format: str,
    include_materials: bool = True,
    custom_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Export a course in the specified format"""
    return await export_service.export_course(
        course_id, export_format, include_materials, custom_options
    )


async def create_course_package(
    course_id: str,
    formats: List[str],
    include_materials: bool = True
) -> Dict[str, Any]:
    """Create a complete course package with multiple formats"""
    return await export_service.create_course_package(course_id, formats, include_materials)


async def get_supported_formats() -> List[str]:
    """Get list of supported export formats"""
    return [
        CourseExportFormat.JSON,
        CourseExportFormat.MARKDOWN,
        CourseExportFormat.DOCX,
        CourseExportFormat.HTML
    ]