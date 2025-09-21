#!/usr/bin/env python3
"""
完整的增强课程设计系统验证测试
包含课程设计 + 完整文档导出验证
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime


async def test_complete_enhanced_system():
    """完整的增强课程设计系统测试，包含文档导出验证"""

    print("🎯 完整增强课程设计系统验证测试")
    print("=" * 80)

    client = httpx.AsyncClient(timeout=120.0, trust_env=False)

    try:
        # 1. 设计增强课程
        print("📋 步骤1: 设计增强课程 - 我的超能分身")

        user_request = {
            "title": "我的超能分身",
            "theme_concept": "让孩子们想象在平行宇宙中拥有超能力的自己，并使用AI工具将想象变为现实",
            "description": "结合AI绘画、3D建模、音乐创作等工具，让孩子设计自己的超能力角色",

            "participant_count": 12,
            "age_group": "primary_upper",

            "duration_type": "one_day",
            "session_count": 1,

            "institution_type": "maker_space",
            "available_equipment": ["computer", "3d_printer", "robot_arm", "camera", "projector"],

            "target_ai_tools": ["ai_chat", "ai_drawing", "ai_3d_modeling", "ai_music"],
            "teacher_ai_experience": "beginner",

            "target_outputs": ["creative_work", "physical_product", "performance"],
            "specific_deliverables": ["身份卡", "3D模型", "演示视频"],

            "budget_level": "medium",
            "safety_requirements": ["3D打印安全", "网络使用安全"],

            "custom_requirements": "教师没有AI+PBL经验，需要详细的操作指导",
            "integration_with_existing": "可以与现有创客课程结合"
        }

        print("🚀 发起增强课程设计请求...")
        design_response = await client.post(
            "http://localhost:48284/api/v1/courses/enhanced/design",
            json=user_request
        )

        if design_response.status_code != 200:
            print(f"❌ 增强课程设计失败: {design_response.text}")
            return False

        course_data = design_response.json()
        enhanced_course = course_data["course_data"]
        course_id = course_data["course_id"]

        print(f"✅ 增强课程设计成功!")
        print(f"   课程ID: {course_id}")
        print(f"   课程标题: {enhanced_course['title']}")
        print()

        # 2. 测试所有格式的文档导出
        print("📋 步骤2: 测试完整文档导出功能")

        formats = ["html", "json", "pdf", "docx"]
        exported_files = {}
        export_success_count = 0

        for export_format in formats:
            print(f"📄 导出 {export_format.upper()} 格式...")

            export_request = {
                "course_id": course_id,
                "export_format": export_format,
                "include_resources": True,
                "include_assessments": True,
                "course_data": enhanced_course  # 直接传入课程数据
            }

            try:
                export_response = await client.post(
                    "http://localhost:48284/api/v1/courses/enhanced/export",
                    json=export_request
                )

                if export_response.status_code == 200:
                    export_data = export_response.json()
                    file_info = export_data['export_data']
                    file_name = file_info['file_name']
                    file_size = file_info['file_size']

                    print(f"✅ {export_format.upper()} 导出成功: {file_name} ({file_size})")
                    exported_files[export_format] = {
                        "filename": file_name,
                        "size": file_size,
                        "path": file_info['file_path']
                    }
                    export_success_count += 1
                else:
                    print(f"❌ {export_format.upper()} 导出失败: {export_response.text}")

            except Exception as e:
                print(f"❌ {export_format.upper()} 导出异常: {str(e)}")

        print()

        # 3. 验证导出文件内容
        print("📋 步骤3: 验证导出文件内容")

        content_validation_score = 0
        total_validations = 0

        # 验证HTML文件
        if "html" in exported_files:
            html_file = exported_files["html"]["path"]
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                html_checks = [
                    ("包含课程标题", "我的超能分身" in html_content),
                    ("包含主题概念", "超能力" in html_content),
                    ("包含Maker Space", "maker_space" in html_content),
                    ("包含AI工具", "ChatGPT" in html_content or "Midjourney" in html_content),
                    ("包含详细活动", "超能力设定工作坊" in html_content),
                    ("内容长度充足", len(html_content) > 10000)
                ]

                print("🌐 HTML文件内容验证:")
                for check_name, check_result in html_checks:
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}")
                    if check_result:
                        content_validation_score += 1
                    total_validations += 1

            except Exception as e:
                print(f"❌ HTML文件读取失败: {e}")

        # 验证JSON文件
        if "json" in exported_files:
            json_file = exported_files["json"]["path"]
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)

                json_checks = [
                    ("包含课程ID", json_content.get("course_id") == course_id),
                    ("包含课程标题", json_content.get("title") == "我的超能分身"),
                    ("包含学习目标", len(json_content.get("learning_objectives", [])) > 0),
                    ("包含详细活动", len(json_content.get("detailed_activities", [])) > 0),
                    ("包含AI工具指导", len(json_content.get("ai_tools_guidance", [])) > 0),
                    ("包含教师准备", "teacher_preparation" in json_content)
                ]

                print("\n📊 JSON文件内容验证:")
                for check_name, check_result in json_checks:
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}")
                    if check_result:
                        content_validation_score += 1
                    total_validations += 1

            except Exception as e:
                print(f"❌ JSON文件读取失败: {e}")

        # 验证PDF和DOCX文件存在性
        for format_name in ["pdf", "docx"]:
            if format_name in exported_files:
                file_path = exported_files[format_name]["path"]
                file_exists = Path(file_path).exists()
                file_size = Path(file_path).stat().st_size if file_exists else 0

                print(f"\n📄 {format_name.upper()}文件验证:")
                print(f"   {'✅' if file_exists else '❌'} 文件存在")
                print(f"   {'✅' if file_size > 1000 else '❌'} 文件大小合理 ({file_size} bytes)")

                if file_exists:
                    content_validation_score += 1
                if file_size > 1000:
                    content_validation_score += 1
                total_validations += 2

        print()

        # 4. 详细课程内容验证
        print("📋 步骤4: 详细课程内容验证")

        course_content_score = 0
        course_checks = [
            ("课程标题匹配", enhanced_course.get("title") == "我的超能分身"),
            ("主题概念完整", "超能力" in enhanced_course.get("theme_concept", "")),
            ("学习目标充足", len(enhanced_course.get("learning_objectives", [])) >= 4),
            ("详细活动充足", len(enhanced_course.get("detailed_activities", [])) >= 3),
            ("AI工具指导完整", len(enhanced_course.get("ai_tools_guidance", [])) >= 3),
            ("时间安排详细", len(enhanced_course.get("schedule", [])) >= 6),
            ("教师准备充分", len(enhanced_course.get("teacher_preparation", {}).get("pre_course_preparation", [])) >= 10),
            ("评估体系完整", len(enhanced_course.get("assessment_methods", [])) >= 2),
            ("材料清单详细", len(enhanced_course.get("required_materials", [])) >= 5),
            ("预期成果明确", len(enhanced_course.get("expected_outcomes", [])) >= 3)
        ]

        print("📚 课程内容详细检查:")
        for check_name, check_result in course_checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
            if check_result:
                course_content_score += 1

        print()

        # 5. 最终评估
        print("📋 步骤5: 最终系统评估")

        export_success_rate = (export_success_count / len(formats)) * 100
        content_validation_rate = (content_validation_score / total_validations) * 100 if total_validations > 0 else 0
        course_content_rate = (course_content_score / len(course_checks)) * 100

        print(f"📊 系统评估结果:")
        print(f"   导出成功率: {export_success_rate:.1f}% ({export_success_count}/{len(formats)})")
        print(f"   内容验证率: {content_validation_rate:.1f}% ({content_validation_score}/{total_validations})")
        print(f"   课程内容完整度: {course_content_rate:.1f}% ({course_content_score}/{len(course_checks)})")

        overall_score = (export_success_rate + content_validation_rate + course_content_rate) / 3

        print(f"\n🎯 总体系统评分: {overall_score:.1f}%")

        if overall_score >= 95:
            print("🎉 系统完美！完全满足生产要求")
            result_level = "完美"
        elif overall_score >= 85:
            print("✅ 系统优秀！基本满足生产要求")
            result_level = "优秀"
        elif overall_score >= 75:
            print("⚠️ 系统良好！需要少量优化")
            result_level = "良好"
        else:
            print("❌ 系统需要改进")
            result_level = "需改进"

        # 6. 生成详细报告
        print(f"\n📋 步骤6: 生成详细测试报告")

        detailed_report = {
            "test_time": datetime.now().isoformat(),
            "test_scenario": "完整增强课程设计系统验证",
            "course_id": course_id,
            "overall_score": overall_score,
            "result_level": result_level,
            "export_results": {
                "success_rate": export_success_rate,
                "successful_exports": export_success_count,
                "total_formats": len(formats),
                "exported_files": exported_files
            },
            "content_validation": {
                "validation_rate": content_validation_rate,
                "passed_validations": content_validation_score,
                "total_validations": total_validations
            },
            "course_content": {
                "content_rate": course_content_rate,
                "passed_checks": course_content_score,
                "total_checks": len(course_checks)
            },
            "course_summary": {
                "title": enhanced_course.get("title"),
                "theme_concept": enhanced_course.get("theme_concept"),
                "learning_objectives_count": len(enhanced_course.get("learning_objectives", [])),
                "detailed_activities_count": len(enhanced_course.get("detailed_activities", [])),
                "ai_tools_guidance_count": len(enhanced_course.get("ai_tools_guidance", [])),
                "teacher_preparation_items": len(enhanced_course.get("teacher_preparation", {}).get("pre_course_preparation", []))
            },
            "system_capabilities": {
                "enhanced_course_design": True,
                "multi_format_export": export_success_count >= 3,
                "content_validation": content_validation_rate >= 80,
                "production_ready": overall_score >= 85
            }
        }

        report_file = f"/home/easegen/EduAgents/backend/complete_enhanced_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)

        print(f"📄 详细报告已保存: {report_file}")

        # 生成客户交付文件清单
        print(f"\n📋 客户交付文件清单:")
        for format_name, file_info in exported_files.items():
            file_path = Path(file_info["path"])
            if file_path.exists():
                print(f"   ✅ {format_name.upper()}: {file_info['filename']} ({file_info['size']})")
            else:
                print(f"   ❌ {format_name.upper()}: 文件缺失")

        return overall_score >= 85

    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

    finally:
        await client.aclose()


if __name__ == "__main__":
    import sys
    success = asyncio.run(test_complete_enhanced_system())
    print(f"\n{'='*80}")
    print(f"🏁 完整系统验证结果: {'✅ 系统达到生产标准' if success else '❌ 系统需要改进'}")
    sys.exit(0 if success else 1)