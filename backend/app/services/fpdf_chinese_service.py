#!/usr/bin/env python3
"""
基于fpdf2的中文PDF生成服务
使用系统Noto CJK字体确保中文字符正确显示
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from fpdf import FPDF
from fpdf.enums import XPos, YPos

logger = logging.getLogger(__name__)


class ChinesePDFGenerator:
    """中文PDF生成器，基于fpdf2库"""

    def __init__(self):
        self.pdf = None
        self.font_loaded = False
        self.system_font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

    def initialize_pdf(self) -> None:
        """初始化PDF文档"""
        self.pdf = FPDF()
        self.pdf.add_page()
        self._load_chinese_font()

    def _load_chinese_font(self) -> bool:
        """加载中文字体"""
        try:
            # 检查系统字体是否存在
            if not os.path.exists(self.system_font_path):
                logger.warning(f"系统字体不存在: {self.system_font_path}")
                # 尝试备选字体路径
                fallback_paths = [
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/System/Library/Fonts/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"
                ]

                for fallback_path in fallback_paths:
                    if os.path.exists(fallback_path):
                        self.system_font_path = fallback_path
                        logger.info(f"使用备选字体: {fallback_path}")
                        break
                else:
                    logger.error("无法找到任何可用的中文字体")
                    return False

            # 添加中文字体到fpdf2 (fpdf2不再需要uni参数)
            self.pdf.add_font("NotoSansCJK", "", self.system_font_path)
            self.pdf.set_font("NotoSansCJK", size=12)
            self.font_loaded = True
            logger.info(f"成功加载中文字体: {self.system_font_path}")
            return True

        except Exception as e:
            logger.error(f"加载中文字体失败: {e}")
            self.font_loaded = False
            return False

    def _ensure_font_loaded(self) -> None:
        """确保字体已加载"""
        if not self.font_loaded:
            if not self._load_chinese_font():
                # 降级到ASCII字体
                self.pdf.set_font("Arial", size=12)
                logger.warning("降级到ASCII字体")

    def add_title(self, title: str, font_size: int = 16) -> None:
        """添加标题"""
        self._ensure_font_loaded()

        # 如果有中文字体，使用中文字体
        if self.font_loaded:
            self.pdf.set_font("NotoSansCJK", size=font_size)
            self.pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        else:
            # 降级处理：转换为拼音或英文
            ascii_title = self._to_ascii_fallback(title)
            self.pdf.set_font("Arial", 'B', size=font_size)
            self.pdf.cell(0, 10, ascii_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.pdf.ln(5)  # 额外空行

    def add_heading(self, heading: str, font_size: int = 14) -> None:
        """添加二级标题"""
        self._ensure_font_loaded()

        if self.font_loaded:
            self.pdf.set_font("NotoSansCJK", size=font_size)
            self.pdf.cell(0, 8, heading, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            ascii_heading = self._to_ascii_fallback(heading)
            self.pdf.set_font("Arial", 'B', size=font_size)
            self.pdf.cell(0, 8, ascii_heading, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.pdf.ln(3)

    def add_paragraph(self, text: str, font_size: int = 12) -> None:
        """添加段落文本"""
        self._ensure_font_loaded()

        if self.font_loaded:
            self.pdf.set_font("NotoSansCJK", size=font_size)
            # 使用multi_cell处理长文本和自动换行
            self.pdf.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            ascii_text = self._to_ascii_fallback(text)
            self.pdf.set_font("Arial", size=font_size)
            self.pdf.multi_cell(0, 6, ascii_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.pdf.ln(2)

    def add_bullet_point(self, text: str, font_size: int = 12) -> None:
        """添加项目符号列表项"""
        self._ensure_font_loaded()

        bullet = "• " if self.font_loaded else "- "
        full_text = bullet + text

        if self.font_loaded:
            self.pdf.set_font("NotoSansCJK", size=font_size)
            self.pdf.multi_cell(0, 6, full_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            ascii_text = self._to_ascii_fallback(full_text)
            self.pdf.set_font("Arial", size=font_size)
            self.pdf.multi_cell(0, 6, ascii_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_numbered_list(self, items: list, font_size: int = 12) -> None:
        """添加编号列表"""
        for i, item in enumerate(items, 1):
            numbered_text = f"{i}. {item}"
            self.add_paragraph(numbered_text, font_size)

    def _to_ascii_fallback(self, text: str) -> str:
        """将中文转换为ASCII备选方案"""
        # 简单的中英文对照表
        translations = {
            "我的超能分身": "My Super-powered Clone",
            "课程设计": "Course Design",
            "AI原生": "AI-Native",
            "PBL": "PBL",
            "项目制学习": "Project-Based Learning",
            "ChatGPT": "ChatGPT",
            "Midjourney": "Midjourney",
            "学习目标": "Learning Objectives",
            "教学活动": "Learning Activities",
            "评估方式": "Assessment Methods",
            "课程概述": "Course Overview",
            "主题概念": "Theme Concept",
            "核心理念": "Core Concept",
            "详细活动": "Detailed Activities",
            "AI工具指导": "AI Tools Guidance",
            "教师准备": "Teacher Preparation",
            "学习材料": "Learning Materials",
            "实践项目": "Practical Projects",
            "成果展示": "Outcome Presentation"
        }

        # 尝试直接翻译
        for chinese, english in translations.items():
            text = text.replace(chinese, english)

        # 对剩余中文字符进行处理
        try:
            # 只保留ASCII字符
            ascii_text = text.encode('ascii', errors='ignore').decode('ascii')
            if not ascii_text.strip():
                return "[Chinese Content]"
            return ascii_text
        except:
            return "[Chinese Content]"

    def save_to_file(self, file_path: str) -> bool:
        """保存PDF文件"""
        try:
            if not self.pdf:
                logger.error("PDF对象未初始化")
                return False

            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path:  # 只有在目录路径非空时才创建
                os.makedirs(dir_path, exist_ok=True)

            self.pdf.output(file_path)

            # 验证文件是否成功创建
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"PDF文件保存成功: {file_path} ({file_size} bytes)")
                return True
            else:
                logger.error(f"PDF文件保存失败: {file_path}")
                return False

        except Exception as e:
            logger.error(f"保存PDF文件时发生错误: {e}")
            return False


def generate_course_pdf(course_data: Dict[str, Any], output_path: str) -> bool:
    """
    生成课程PDF文档

    Args:
        course_data: 课程数据字典
        output_path: 输出文件路径

    Returns:
        bool: 生成是否成功
    """
    try:
        generator = ChinesePDFGenerator()
        generator.initialize_pdf()

        # 添加课程标题
        title = course_data.get('title', '未命名课程')
        generator.add_title(title, 18)

        # 添加主题概念
        theme_concept = course_data.get('theme_concept', '')
        if theme_concept:
            generator.add_heading("主题概念")
            generator.add_paragraph(theme_concept)

        # 添加学习目标
        learning_objectives = course_data.get('learning_objectives', [])
        if learning_objectives:
            generator.add_heading("学习目标")
            for objective in learning_objectives:
                generator.add_bullet_point(objective)

        # 添加详细活动
        detailed_activities = course_data.get('detailed_activities', [])
        if detailed_activities:
            generator.add_heading("详细活动")
            for i, activity in enumerate(detailed_activities, 1):
                activity_title = activity.get('title', f'活动 {i}')
                generator.add_heading(f"{i}. {activity_title}", 12)

                description = activity.get('description', '')
                if description:
                    generator.add_paragraph(description)

                steps = activity.get('steps', [])
                if steps:
                    generator.add_paragraph("活动步骤:")
                    generator.add_numbered_list(steps)

        # 添加AI工具指导
        ai_tools_guidance = course_data.get('ai_tools_guidance', [])
        if ai_tools_guidance:
            generator.add_heading("AI工具指导")
            for tool in ai_tools_guidance:
                tool_name = tool.get('tool', '未知工具')
                generator.add_heading(tool_name, 12)

                purpose = tool.get('purpose', '')
                if purpose:
                    generator.add_paragraph(f"用途: {purpose}")

                guidance = tool.get('guidance', '')
                if guidance:
                    generator.add_paragraph(guidance)

        # 添加教师准备
        teacher_preparation = course_data.get('teacher_preparation', [])
        if teacher_preparation:
            generator.add_heading("教师准备")
            for item in teacher_preparation:
                generator.add_bullet_point(item)

        # 保存文件
        return generator.save_to_file(output_path)

    except Exception as e:
        logger.error(f"生成课程PDF时发生错误: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    test_course = {
        "title": "我的超能分身",
        "theme_concept": "让孩子们想象在平行宇宙中拥有超能力的自己，并使用AI工具将想象变为现实",
        "learning_objectives": [
            "培养创意思维和想象力",
            "学习使用AI绘画工具",
            "掌握基础的3D建模技能",
            "提高项目协作能力"
        ],
        "detailed_activities": [
            {
                "title": "超能力设定",
                "description": "让学生设计自己的超能力和外观",
                "steps": ["头脑风暴超能力", "描述外观特征", "绘制草图"]
            }
        ],
        "ai_tools_guidance": [
            {
                "tool": "ChatGPT",
                "purpose": "对话助手和创意启发",
                "guidance": "使用ChatGPT帮助完善角色设定"
            }
        ],
        "teacher_preparation": [
            "准备AI工具账号",
            "熟悉Midjourney基本操作",
            "准备示例作品"
        ]
    }

    success = generate_course_pdf(test_course, "test_fpdf_chinese.pdf")
    print(f"测试PDF生成: {'成功' if success else '失败'}")