"""
智能体单元测试
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.assessment_specialist import AssessmentFeedbackSpecialist
from app.agents.community_coordinator import CommunityCoordinator
from app.agents.creative_technologist import CreativeTechnologist
from app.agents.education_director import EducationDirector
from app.agents.learning_designer import LearningExperienceDesigner
from tests.factories import (
    AgentMessageFactory,
    CourseFactory,
    ProjectFactory,
    UserFactory,
)


class TestEducationDirector:
    """教育主管智能体测试"""

    @pytest.fixture
    def education_director(self):
        return EducationDirector()

    @pytest.mark.asyncio
    async def test_analyze_curriculum_requirements(self, education_director):
        """测试课程需求分析"""
        requirements = {
            "subject": "计算机科学",
            "grade_level": "高中",
            "duration": "12周",
            "learning_goals": ["编程基础", "算法思维", "项目管理"],
        }

        with patch.object(education_director, "_call_llm") as mock_llm:
            mock_llm.return_value = {
                "analysis": "课程设计合理",
                "recommendations": ["增加实践项目", "加强团队协作"],
                "feasibility": "high",
            }

            result = await education_director.analyze_curriculum_requirements(
                requirements
            )

            assert result["feasibility"] == "high"
            assert "recommendations" in result
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_learning_objectives(self, education_director):
        """测试学习目标验证"""
        objectives = ["掌握Python基础语法", "理解面向对象编程", "能够独立完成小型项目"]

        result = await education_director.validate_learning_objectives(objectives)

        assert isinstance(result, dict)
        assert "valid_objectives" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_generate_curriculum_outline(self, education_director):
        """测试课程大纲生成"""
        course_data = CourseFactory.build_dict()

        with patch.object(education_director, "_call_llm") as mock_llm:
            mock_llm.return_value = {
                "weeks": [
                    {"week": 1, "topic": "Python基础", "objectives": ["变量", "函数"]},
                    {"week": 2, "topic": "数据结构", "objectives": ["列表", "字典"]},
                ],
                "assessment_points": ["期中项目", "期末展示"],
            }

            result = await education_director.generate_curriculum_outline(course_data)

            assert "weeks" in result
            assert len(result["weeks"]) >= 1
            assert "assessment_points" in result


class TestLearningExperienceDesigner:
    """学习体验设计师测试"""

    @pytest.fixture
    def learning_designer(self):
        return LearningExperienceDesigner()

    @pytest.mark.asyncio
    async def test_design_learning_activities(self, learning_designer):
        """测试学习活动设计"""
        learning_objectives = ["理解算法复杂度", "实现基础排序算法", "分析算法性能"]

        with patch.object(learning_designer, "_call_llm") as mock_llm:
            mock_llm.return_value = {
                "activities": [
                    {
                        "type": "实验",
                        "title": "排序算法对比",
                        "duration": "2小时",
                        "materials": ["代码模板", "测试数据"],
                    }
                ],
                "sequence": ["理论讲解", "动手实验", "成果分享"],
            }

            result = await learning_designer.design_learning_activities(
                learning_objectives
            )

            assert "activities" in result
            assert "sequence" in result
            assert len(result["activities"]) >= 1

    @pytest.mark.asyncio
    async def test_create_project_scaffolds(self, learning_designer):
        """测试项目脚手架创建"""
        project_data = ProjectFactory.build_dict()

        result = await learning_designer.create_project_scaffolds(project_data)

        assert isinstance(result, dict)
        assert "scaffolds" in result
        assert "milestones" in result

    @pytest.mark.asyncio
    async def test_personalize_learning_path(self, learning_designer):
        """测试个性化学习路径"""
        student_profile = {
            "learning_style": "visual",
            "prior_knowledge": "basic",
            "interests": ["游戏开发", "人工智能"],
            "pace": "moderate",
        }

        course_content = CourseFactory.build_dict()

        result = await learning_designer.personalize_learning_path(
            student_profile, course_content
        )

        assert "customized_path" in result
        assert "recommended_resources" in result
        assert "adaptive_activities" in result


class TestCreativeTechnologist:
    """创意技术专家测试"""

    @pytest.fixture
    def creative_tech(self):
        return CreativeTechnologist()

    @pytest.mark.asyncio
    async def test_suggest_technology_tools(self, creative_tech):
        """测试技术工具推荐"""
        project_requirements = {
            "type": "web_development",
            "complexity": "intermediate",
            "team_size": 4,
            "duration": "8周",
        }

        with patch.object(creative_tech, "_call_llm") as mock_llm:
            mock_llm.return_value = {
                "tools": [
                    {
                        "name": "React",
                        "purpose": "前端框架",
                        "learning_curve": "medium",
                    },
                    {"name": "Node.js", "purpose": "后端开发", "learning_curve": "low"},
                ],
                "workflow": ["设计原型", "开发MVP", "迭代优化"],
            }

            result = await creative_tech.suggest_technology_tools(project_requirements)

            assert "tools" in result
            assert "workflow" in result
            assert len(result["tools"]) >= 1

    @pytest.mark.asyncio
    async def test_design_maker_activities(self, creative_tech):
        """测试创客活动设计"""
        theme = "智能家居"
        age_group = "15-18岁"
        available_tools = ["Arduino", "传感器", "3D打印机"]

        result = await creative_tech.design_maker_activities(
            theme, age_group, available_tools
        )

        assert "activities" in result
        assert "required_materials" in result
        assert "safety_guidelines" in result

    @pytest.mark.asyncio
    async def test_prototype_validation(self, creative_tech):
        """测试原型验证"""
        prototype_data = {
            "name": "智能温控器",
            "description": "基于Arduino的温度控制系统",
            "features": ["温度感应", "自动调节", "远程控制"],
            "target_users": "家庭用户",
        }

        result = await creative_tech.validate_prototype(prototype_data)

        assert "feasibility_score" in result
        assert "improvement_suggestions" in result
        assert "technical_challenges" in result


class TestAssessmentSpecialist:
    """评估反馈专家测试"""

    @pytest.fixture
    def assessment_specialist(self):
        return AssessmentFeedbackSpecialist()

    @pytest.mark.asyncio
    async def test_design_rubric(self, assessment_specialist):
        """测试评分标准设计"""
        learning_objectives = ["代码质量", "创新思维", "团队协作", "问题解决"]

        with patch.object(assessment_specialist, "_call_llm") as mock_llm:
            mock_llm.return_value = {
                "rubric": {
                    "criteria": [
                        {
                            "name": "代码质量",
                            "levels": [
                                {"score": 4, "description": "代码清晰、高效"},
                                {"score": 3, "description": "代码基本规范"},
                                {"score": 2, "description": "代码可运行但有问题"},
                                {"score": 1, "description": "代码有严重问题"},
                            ],
                        }
                    ]
                },
                "total_points": 100,
            }

            result = await assessment_specialist.design_rubric(learning_objectives)

            assert "rubric" in result
            assert "total_points" in result
            assert "criteria" in result["rubric"]

    @pytest.mark.asyncio
    async def test_provide_feedback(self, assessment_specialist):
        """测试反馈生成"""
        submission = {
            "student_id": 123,
            "project_title": "个人博客系统",
            "code_quality": 85,
            "creativity": 90,
            "collaboration": 75,
            "documentation": 80,
        }

        result = await assessment_specialist.provide_feedback(submission)

        assert "overall_score" in result
        assert "strengths" in result
        assert "areas_for_improvement" in result
        assert "specific_recommendations" in result

    @pytest.mark.asyncio
    async def test_peer_assessment_design(self, assessment_specialist):
        """测试同伴评估设计"""
        project_type = "团队项目"
        assessment_focus = ["团队协作", "贡献度", "沟通能力"]

        result = await assessment_specialist.design_peer_assessment(
            project_type, assessment_focus
        )

        assert "assessment_form" in result
        assert "guidelines" in result
        assert "scoring_method" in result


class TestCommunityCoordinator:
    """社区协调员测试"""

    @pytest.fixture
    def community_coordinator(self):
        return CommunityCoordinator()

    @pytest.mark.asyncio
    async def test_facilitate_collaboration(self, community_coordinator):
        """测试协作促进"""
        team_data = {
            "members": [
                {"id": 1, "name": "张三", "skills": ["Python", "设计"]},
                {"id": 2, "name": "李四", "skills": ["JavaScript", "测试"]},
                {"id": 3, "name": "王五", "skills": ["数据分析", "文档"]},
            ],
            "project_requirements": ["前端开发", "后端开发", "数据处理", "文档编写"],
        }

        result = await community_coordinator.facilitate_collaboration(team_data)

        assert "role_assignments" in result
        assert "collaboration_plan" in result
        assert "communication_guidelines" in result

    @pytest.mark.asyncio
    async def test_organize_showcase_event(self, community_coordinator):
        """测试成果展示活动组织"""
        event_requirements = {
            "participant_count": 50,
            "project_count": 12,
            "duration": "2小时",
            "audience": ["学生", "老师", "家长"],
        }

        result = await community_coordinator.organize_showcase_event(event_requirements)

        assert "event_schedule" in result
        assert "venue_requirements" in result
        assert "presentation_format" in result

    @pytest.mark.asyncio
    async def test_mentorship_matching(self, community_coordinator):
        """测试导师匹配"""
        students = [
            {"id": 1, "interests": ["AI", "机器学习"], "level": "beginner"},
            {"id": 2, "interests": ["web开发", "UI设计"], "level": "intermediate"},
        ]

        mentors = [
            {"id": 101, "expertise": ["AI", "数据科学"], "capacity": 3},
            {"id": 102, "expertise": ["前端开发", "用户体验"], "capacity": 2},
        ]

        result = await community_coordinator.match_mentors(students, mentors)

        assert "matches" in result
        assert "unmatched_students" in result
        assert "mentor_utilization" in result


# 智能体协作测试
class TestAgentCollaboration:
    """智能体协作测试"""

    @pytest.mark.asyncio
    async def test_multi_agent_course_design(self):
        """测试多智能体课程设计协作"""
        # 模拟多个智能体协作设计课程
        education_director = EducationDirector()
        learning_designer = LearningExperienceDesigner()
        creative_tech = CreativeTechnologist()

        course_requirements = CourseFactory.build_dict()

        # 教育主管分析需求
        with patch.object(
            education_director, "analyze_curriculum_requirements"
        ) as mock_analyze:
            mock_analyze.return_value = {"feasibility": "high", "framework": "PBL"}

            curriculum_analysis = (
                await education_director.analyze_curriculum_requirements(
                    course_requirements
                )
            )

        # 学习设计师设计活动
        with patch.object(
            learning_designer, "design_learning_activities"
        ) as mock_design:
            mock_design.return_value = {"activities": [], "sequence": []}

            learning_activities = await learning_designer.design_learning_activities(
                course_requirements["learning_objectives"]
            )

        # 创意技术专家推荐工具
        with patch.object(creative_tech, "suggest_technology_tools") as mock_suggest:
            mock_suggest.return_value = {"tools": [], "workflow": []}

            tech_recommendations = await creative_tech.suggest_technology_tools(
                {
                    "type": course_requirements.get("subject", "general"),
                    "complexity": "intermediate",
                }
            )

        # 验证协作结果
        assert curriculum_analysis["feasibility"] == "high"
        assert "activities" in learning_activities
        assert "tools" in tech_recommendations

    @pytest.mark.asyncio
    async def test_agent_consensus_mechanism(self):
        """测试智能体共识机制"""
        agents = [
            EducationDirector(),
            LearningExperienceDesigner(),
            CreativeTechnologist(),
        ]

        # 模拟决策场景
        decision_point = {
            "topic": "项目复杂度评估",
            "options": ["简单", "中等", "复杂"],
            "context": "高中生12周PBL项目",
        }

        votes = []
        for agent in agents:
            with patch.object(agent, "_call_llm") as mock_llm:
                mock_llm.return_value = {"recommendation": "中等", "confidence": 0.8}
                vote = await agent.make_decision(decision_point)
                votes.append(vote)

        # 计算共识
        consensus = self._calculate_consensus(votes)
        assert consensus["decision"] in ["简单", "中等", "复杂"]
        assert 0 <= consensus["confidence"] <= 1

    def _calculate_consensus(self, votes):
        """计算智能体共识"""
        # 简化的共识算法
        decisions = [vote["recommendation"] for vote in votes]
        confidences = [vote["confidence"] for vote in votes]

        # 多数决
        from collections import Counter

        decision_counts = Counter(decisions)
        majority_decision = decision_counts.most_common(1)[0][0]

        # 平均置信度
        avg_confidence = sum(confidences) / len(confidences)

        return {
            "decision": majority_decision,
            "confidence": avg_confidence,
            "unanimity": len(set(decisions)) == 1,
        }
