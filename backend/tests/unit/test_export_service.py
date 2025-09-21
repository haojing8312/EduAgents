"""
测试课程导出服务
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime
import json
import io
import zipfile

from app.services.export_service import (
    CourseExportService,
    MaterialGenerator,
    export_service
)


class TestCourseExportService:
    """课程导出服务测试"""

    @pytest_asyncio.fixture
    async def mock_export_service(self):
        """模拟导出服务"""
        service = CourseExportService()

        # 模拟数据库会话
        service.db_session = AsyncMock()

        # 模拟material_generator
        service.material_generator = MagicMock()
        service.material_generator.generate_lesson_plans = AsyncMock(return_value=[
            {"title": "lesson1", "content": "lesson content"}
        ])
        service.material_generator.generate_student_guide = AsyncMock(return_value={
            "title": "student guide", "content": "guide content"
        })
        service.material_generator.generate_assessment_rubric = AsyncMock(return_value={
            "title": "assessment", "content": "rubric content"
        })

        yield service

    @pytest.mark.asyncio
    async def test_export_course_json(self, mock_export_service):
        """测试JSON格式导出"""
        service = mock_export_service
        course_id = "test-course-123"

        # 模拟课程数据
        mock_course_data = {
            "id": course_id,
            "title": "AI基础课程",
            "description": "面向高中生的AI课程",
            "agents_data": {
                "education_theorist": {"theory": "constructivism"},
                "course_architect": {"structure": "8-week program"}
            }
        }

        # 模拟获取课程数据
        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = mock_course_data

            result = await service.export_course(course_id, "json", include_materials=True)

            assert result["success"] is True
            assert result["format"] == "json"
            assert "export_data" in result
            assert "materials" in result
            assert result["size"] > 0

    @pytest.mark.asyncio
    async def test_export_course_markdown(self, mock_export_service):
        """测试Markdown格式导出"""
        service = mock_export_service
        course_id = "test-course-123"

        mock_course_data = {
            "id": course_id,
            "title": "AI基础课程",
            "description": "面向高中生的AI课程",
            "agents_data": {
                "education_theorist": {"theory": "constructivism"}
            }
        }

        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = mock_course_data

            result = await service.export_course(course_id, "markdown", include_materials=False)

            assert result["success"] is True
            assert result["format"] == "markdown"
            assert "export_data" in result
            assert result["export_data"].startswith("# AI基础课程")

    @pytest.mark.asyncio
    async def test_export_course_docx(self, mock_export_service):
        """测试DOCX格式导出"""
        service = mock_export_service
        course_id = "test-course-123"

        mock_course_data = {
            "id": course_id,
            "title": "AI基础课程",
            "description": "面向高中生的AI课程"
        }

        with patch.object(service, '_get_course_data') as mock_get_course, \
             patch('app.services.export_service.DOCX_AVAILABLE', True), \
             patch('docx.Document') as mock_doc:

            mock_get_course.return_value = mock_course_data
            mock_document = MagicMock()
            mock_doc.return_value = mock_document
            mock_document.save = MagicMock()

            result = await service.export_course(course_id, "docx")

            assert result["success"] is True
            assert result["format"] == "docx"
            assert "file_path" in result

    @pytest.mark.asyncio
    async def test_export_course_html(self, mock_export_service):
        """测试HTML格式导出"""
        service = mock_export_service
        course_id = "test-course-123"

        mock_course_data = {
            "id": course_id,
            "title": "AI基础课程",
            "description": "面向高中生的AI课程"
        }

        with patch.object(service, '_get_course_data') as mock_get_course, \
             patch('app.services.export_service.JINJA2_AVAILABLE', True):

            mock_get_course.return_value = mock_course_data

            # 模拟Jinja2模板
            with patch('jinja2.Environment') as mock_env:
                mock_template = MagicMock()
                mock_template.render.return_value = "<html><body>课程内容</body></html>"
                mock_env.return_value.get_template.return_value = mock_template

                result = await service.export_course(course_id, "html")

                assert result["success"] is True
                assert result["format"] == "html"
                assert "export_data" in result
                assert result["export_data"].startswith("<html>")

    @pytest.mark.asyncio
    async def test_create_export_package(self, mock_export_service):
        """测试创建导出包"""
        service = mock_export_service
        course_id = "test-course-123"
        formats = ["json", "markdown"]

        mock_course_data = {
            "id": course_id,
            "title": "AI基础课程"
        }

        with patch.object(service, '_get_course_data') as mock_get_course, \
             patch('zipfile.ZipFile') as mock_zip, \
             patch('tempfile.mkdtemp') as mock_temp:

            mock_get_course.return_value = mock_course_data
            mock_temp.return_value = "/tmp/test_export"

            # 模拟ZIP文件操作
            mock_zip_instance = MagicMock()
            mock_zip.return_value.__enter__.return_value = mock_zip_instance

            result = await service.create_export_package(course_id, formats, include_materials=True)

            assert result["success"] is True
            assert "package_path" in result
            assert result["formats"] == formats
            assert "materials_included" in result

    @pytest.mark.asyncio
    async def test_get_supported_formats(self, mock_export_service):
        """测试获取支持的格式"""
        service = mock_export_service

        formats = await service.get_supported_formats()
        assert isinstance(formats, list)
        assert "json" in formats
        assert "markdown" in formats
        assert "html" in formats

    @pytest.mark.asyncio
    async def test_export_course_not_found(self, mock_export_service):
        """测试导出不存在的课程"""
        service = mock_export_service
        course_id = "nonexistent-course"

        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = None

            result = await service.export_course(course_id, "json")

            assert result["success"] is False
            assert "error" in result
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_export_unsupported_format(self, mock_export_service):
        """测试不支持的导出格式"""
        service = mock_export_service
        course_id = "test-course-123"

        result = await service.export_course(course_id, "unsupported_format")

        assert result["success"] is False
        assert "error" in result
        assert "not supported" in result["error"].lower()


class TestMaterialGenerator:
    """教材生成器测试"""

    @pytest_asyncio.fixture
    async def mock_material_generator(self):
        """模拟教材生成器"""
        generator = MaterialGenerator()
        generator.llm_manager = AsyncMock()
        generator.llm_manager.chat.return_value = MagicMock(content="Generated content")
        yield generator

    @pytest.mark.asyncio
    async def test_generate_lesson_plans(self, mock_material_generator):
        """测试生成课程计划"""
        generator = mock_material_generator
        course_data = {
            "title": "AI基础课程",
            "agents_data": {
                "course_architect": {
                    "result": "8周课程结构"
                }
            }
        }

        # 模拟LLM响应
        generator.llm_manager.chat.return_value.content = json.dumps([
            {
                "lesson_number": 1,
                "title": "AI概述",
                "duration": "2小时",
                "objectives": ["理解AI基本概念"],
                "activities": ["讲座", "讨论"],
                "materials": ["PPT", "视频"],
                "assessment": "课堂提问"
            }
        ])

        lesson_plans = await generator.generate_lesson_plans(course_data)

        assert isinstance(lesson_plans, list)
        assert len(lesson_plans) > 0
        assert "title" in lesson_plans[0]
        assert "objectives" in lesson_plans[0]

    @pytest.mark.asyncio
    async def test_generate_student_guide(self, mock_material_generator):
        """测试生成学生指南"""
        generator = mock_material_generator
        course_data = {
            "title": "AI基础课程",
            "description": "面向高中生的AI入门课程"
        }

        # 模拟LLM响应
        generator.llm_manager.chat.return_value.content = json.dumps({
            "title": "AI基础课程学生指南",
            "introduction": "欢迎参加AI基础课程",
            "learning_objectives": ["掌握AI基本概念"],
            "course_structure": "8周学习计划",
            "assessment_methods": ["项目评估", "同伴评议"],
            "resources": ["推荐阅读", "在线工具"],
            "tips": ["学习建议"]
        })

        student_guide = await generator.generate_student_guide(course_data)

        assert isinstance(student_guide, dict)
        assert "title" in student_guide
        assert "learning_objectives" in student_guide
        assert "course_structure" in student_guide

    @pytest.mark.asyncio
    async def test_generate_assessment_rubric(self, mock_material_generator):
        """测试生成评估量规"""
        generator = mock_material_generator
        course_data = {
            "title": "AI基础课程",
            "agents_data": {
                "assessment_expert": {
                    "result": "多元化评估策略"
                }
            }
        }

        # 模拟LLM响应
        generator.llm_manager.chat.return_value.content = json.dumps({
            "title": "AI基础课程评估量规",
            "assessment_types": ["项目评估", "同伴评议", "反思日志"],
            "rubric_criteria": [
                {
                    "criterion": "概念理解",
                    "weight": 30,
                    "levels": {
                        "excellent": "完全掌握AI核心概念",
                        "good": "基本掌握AI核心概念",
                        "satisfactory": "部分掌握AI核心概念",
                        "needs_improvement": "需要加强概念学习"
                    }
                }
            ],
            "grading_scale": "A-F等级制",
            "feedback_guidelines": "及时、具体、建设性"
        })

        assessment_rubric = await generator.generate_assessment_rubric(course_data)

        assert isinstance(assessment_rubric, dict)
        assert "title" in assessment_rubric
        assert "assessment_types" in assessment_rubric
        assert "rubric_criteria" in assessment_rubric

    @pytest.mark.asyncio
    async def test_generate_teacher_materials(self, mock_material_generator):
        """测试生成教师材料"""
        generator = mock_material_generator
        course_data = {
            "title": "AI基础课程",
            "agents_data": {
                "content_designer": {
                    "result": "互动式教学设计"
                }
            }
        }

        # 模拟LLM响应
        generator.llm_manager.chat.return_value.content = json.dumps({
            "teaching_guide": "教学指导手册",
            "presentation_slides": "课程PPT大纲",
            "activity_instructions": "活动操作指南",
            "discussion_prompts": "讨论引导问题",
            "assessment_tools": "评估工具包",
            "troubleshooting": "常见问题解答"
        })

        teacher_materials = await generator.generate_teacher_materials(course_data)

        assert isinstance(teacher_materials, dict)
        assert "teaching_guide" in teacher_materials
        assert "activity_instructions" in teacher_materials

    @pytest.mark.asyncio
    async def test_material_generation_error_handling(self, mock_material_generator):
        """测试教材生成错误处理"""
        generator = mock_material_generator

        # 模拟LLM异常
        generator.llm_manager.chat.side_effect = Exception("LLM调用失败")

        lesson_plans = await generator.generate_lesson_plans({"title": "test"})
        assert lesson_plans == []

        student_guide = await generator.generate_student_guide({"title": "test"})
        assert student_guide == {}

        assessment_rubric = await generator.generate_assessment_rubric({"title": "test"})
        assert assessment_rubric == {}


class TestExportServiceIntegration:
    """导出服务集成测试"""

    @pytest.mark.asyncio
    async def test_global_export_service(self):
        """测试全局导出服务实例"""
        assert export_service is not None
        assert isinstance(export_service, CourseExportService)

    @pytest.mark.asyncio
    async def test_format_compatibility(self):
        """测试格式兼容性"""
        service = CourseExportService()

        # 测试可选依赖的降级处理
        with patch('app.services.export_service.DOCX_AVAILABLE', False):
            formats = await service.get_supported_formats()
            assert "docx" not in formats

        with patch('app.services.export_service.JINJA2_AVAILABLE', False):
            formats = await service.get_supported_formats()
            # HTML格式依赖Jinja2，应该被排除或有降级方案

    @pytest.mark.asyncio
    async def test_export_data_integrity(self):
        """测试导出数据完整性"""
        service = CourseExportService()

        # 测试复杂课程数据的导出
        complex_course_data = {
            "id": "complex-course",
            "title": "复杂课程",
            "description": "包含多种数据类型的课程",
            "agents_data": {
                "education_theorist": {
                    "content": "理论框架",
                    "metadata": {"timestamp": datetime.now().isoformat()}
                },
                "course_architect": {
                    "result": ["模块1", "模块2", "模块3"],
                    "structure": {"weeks": 8, "hours_per_week": 4}
                }
            },
            "learning_objectives": [
                "目标1：掌握基础概念",
                "目标2：完成实践项目"
            ],
            "resources": {
                "required": ["教材A", "软件B"],
                "optional": ["参考书C"]
            }
        }

        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = complex_course_data

            # 测试JSON导出保持数据结构
            result = await service.export_course("complex-course", "json")
            assert result["success"] is True

            exported_data = json.loads(result["export_data"])
            assert exported_data["title"] == "复杂课程"
            assert len(exported_data["learning_objectives"]) == 2
            assert "education_theorist" in exported_data["agents_data"]

    @pytest.mark.asyncio
    async def test_large_course_export(self):
        """测试大型课程导出"""
        service = CourseExportService()

        # 模拟大型课程数据
        large_course_data = {
            "id": "large-course",
            "title": "大型课程",
            "agents_data": {f"agent_{i}": {"content": "内容" * 1000} for i in range(10)}
        }

        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = large_course_data

            result = await service.export_course("large-course", "json")
            assert result["success"] is True
            assert result["size"] > 10000  # 确保大文件被正确处理

    @pytest.mark.asyncio
    async def test_concurrent_exports(self):
        """测试并发导出"""
        service = CourseExportService()
        course_data = {"id": "test", "title": "并发测试课程"}

        with patch.object(service, '_get_course_data') as mock_get_course:
            mock_get_course.return_value = course_data

            # 同时发起多个导出请求
            import asyncio
            tasks = [
                service.export_course("test", "json"),
                service.export_course("test", "markdown"),
                service.export_course("test", "html")
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 验证所有导出都成功
            for result in results:
                assert not isinstance(result, Exception)
                assert result["success"] is True


@pytest.mark.asyncio
async def test_export_file_cleanup():
    """测试导出文件清理"""
    service = CourseExportService()

    with patch('tempfile.mkdtemp') as mock_temp, \
         patch('shutil.rmtree') as mock_rmtree, \
         patch('os.path.exists') as mock_exists:

        mock_temp.return_value = "/tmp/test_export"
        mock_exists.return_value = True

        # 模拟文件清理
        await service._cleanup_temp_files("/tmp/test_export")
        mock_rmtree.assert_called_once_with("/tmp/test_export")


@pytest.mark.asyncio
async def test_export_metadata_inclusion():
    """测试导出元数据包含"""
    service = CourseExportService()
    course_data = {
        "id": "meta-test",
        "title": "元数据测试课程",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    with patch.object(service, '_get_course_data') as mock_get_course:
        mock_get_course.return_value = course_data

        result = await service.export_course("meta-test", "json")
        exported_data = json.loads(result["export_data"])

        # 验证元数据被包含
        assert "export_metadata" in exported_data
        assert "exported_at" in exported_data["export_metadata"]
        assert "format" in exported_data["export_metadata"]
        assert "version" in exported_data["export_metadata"]