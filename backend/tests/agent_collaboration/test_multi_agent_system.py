"""
多智能体协作系统测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta

from app.agents.orchestrator import AgentOrchestrator
from app.agents.education_director import EducationDirector
from app.agents.learning_designer import LearningExperienceDesigner
from app.agents.creative_technologist import CreativeTechnologist
from app.agents.assessment_specialist import AssessmentFeedbackSpecialist
from app.agents.community_coordinator import CommunityCoordinator
from tests.factories import CourseFactory, ProjectFactory, AgentMessageFactory


class TestMultiAgentOrchestrator:
    """多智能体编排器测试"""
    
    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator()
    
    @pytest.fixture
    def mock_agents(self):
        """模拟智能体"""
        return {
            'education_director': AsyncMock(spec=EducationDirector),
            'learning_designer': AsyncMock(spec=LearningExperienceDesigner),
            'creative_technologist': AsyncMock(spec=CreativeTechnologist),
            'assessment_specialist': AsyncMock(spec=AssessmentFeedbackSpecialist),
            'community_coordinator': AsyncMock(spec=CommunityCoordinator),
        }
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, orchestrator):
        """测试智能体注册"""
        agent = EducationDirector()
        
        orchestrator.register_agent('education_director', agent)
        
        assert 'education_director' in orchestrator.agents
        assert orchestrator.agents['education_director'] == agent
    
    @pytest.mark.asyncio
    async def test_task_distribution(self, orchestrator, mock_agents):
        """测试任务分发"""
        # 注册模拟智能体
        for name, agent in mock_agents.items():
            orchestrator.register_agent(name, agent)
        
        task = {
            'type': 'design_course',
            'data': CourseFactory.build_dict(),
            'required_agents': ['education_director', 'learning_designer']
        }
        
        # 设置模拟返回值
        mock_agents['education_director'].process_task.return_value = {
            'status': 'completed',
            'result': {'curriculum_structure': 'PBL framework'}
        }
        mock_agents['learning_designer'].process_task.return_value = {
            'status': 'completed',
            'result': {'learning_activities': []}
        }
        
        result = await orchestrator.distribute_task(task)
        
        assert result['status'] == 'completed'
        assert 'results' in result
        assert len(result['results']) == 2
        
        # 验证任务被分发给正确的智能体
        mock_agents['education_director'].process_task.assert_called_once()
        mock_agents['learning_designer'].process_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_consensus_mechanism(self, orchestrator, mock_agents):
        """测试共识机制"""
        # 注册智能体
        for name, agent in mock_agents.items():
            orchestrator.register_agent(name, agent)
        
        decision_scenario = {
            'question': '这个项目的复杂度应该设置为什么级别？',
            'options': ['简单', '中等', '复杂'],
            'context': {'grade_level': '高中', 'duration': '12周'}
        }
        
        # 设置智能体投票结果
        votes = {
            'education_director': {'choice': '中等', 'confidence': 0.8, 'reasoning': '适合高中生'},
            'learning_designer': {'choice': '中等', 'confidence': 0.9, 'reasoning': '12周时间合适'},
            'creative_technologist': {'choice': '复杂', 'confidence': 0.7, 'reasoning': '可以挑战学生'},
        }
        
        for agent_name, vote in votes.items():
            mock_agents[agent_name].vote_on_decision.return_value = vote
        
        consensus = await orchestrator.reach_consensus(
            decision_scenario, ['education_director', 'learning_designer', 'creative_technologist']
        )
        
        assert consensus['final_decision'] == '中等'  # 多数决
        assert 0 <= consensus['confidence'] <= 1
        assert 'reasoning' in consensus
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, orchestrator, mock_agents):
        """测试工作流执行"""
        # 注册智能体
        for name, agent in mock_agents.items():
            orchestrator.register_agent(name, agent)
        
        workflow = {
            'name': 'complete_course_design',
            'steps': [
                {
                    'step': 1,
                    'agent': 'education_director',
                    'task': 'analyze_requirements',
                    'dependencies': []
                },
                {
                    'step': 2,
                    'agent': 'learning_designer',
                    'task': 'design_activities',
                    'dependencies': [1]
                },
                {
                    'step': 3,
                    'agent': 'creative_technologist',
                    'task': 'suggest_tools',
                    'dependencies': [1, 2]
                },
                {
                    'step': 4,
                    'agent': 'assessment_specialist',
                    'task': 'design_assessment',
                    'dependencies': [2]
                }
            ]
        }
        
        # 设置模拟返回值
        for agent in mock_agents.values():
            agent.execute_step.return_value = {
                'status': 'completed',
                'result': {'step_output': 'mock_result'},
                'metadata': {'execution_time': 1.5}
            }
        
        result = await orchestrator.execute_workflow(workflow, {'course_data': CourseFactory.build_dict()})
        
        assert result['status'] == 'completed'
        assert 'execution_log' in result
        assert len(result['execution_log']) == 4
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, orchestrator, mock_agents):
        """测试错误处理和恢复"""
        # 注册智能体
        for name, agent in mock_agents.items():
            orchestrator.register_agent(name, agent)
        
        # 模拟智能体执行失败
        mock_agents['education_director'].process_task.side_effect = Exception("智能体执行失败")
        mock_agents['learning_designer'].process_task.return_value = {
            'status': 'completed',
            'result': {'activities': []}
        }
        
        task = {
            'type': 'design_course',
            'data': CourseFactory.build_dict(),
            'required_agents': ['education_director', 'learning_designer']
        }
        
        result = await orchestrator.distribute_task(task)
        
        # 验证错误处理
        assert result['status'] == 'partial_failure'
        assert 'errors' in result
        assert 'education_director' in result['errors']
        
        # 验证成功的智能体仍然执行
        assert 'results' in result
        assert 'learning_designer' in result['results']


class TestAgentCommunication:
    """智能体通信测试"""
    
    @pytest.mark.asyncio
    async def test_message_passing(self):
        """测试消息传递"""
        education_director = EducationDirector()
        learning_designer = LearningExperienceDesigner()
        
        # 模拟消息传递
        with patch.object(education_director, '_call_llm') as mock_ed_llm, \
             patch.object(learning_designer, '_call_llm') as mock_ld_llm:
            
            # 教育主管发送建议
            mock_ed_llm.return_value = {
                'message': '建议采用项目驱动的学习方式',
                'type': 'suggestion',
                'target_agent': 'learning_designer'
            }
            
            message = await education_director.send_message_to_agent(
                'learning_designer',
                '请设计符合PBL理念的学习活动'
            )
            
            # 学习设计师接收并处理消息
            mock_ld_llm.return_value = {
                'response': '收到建议，将设计基于项目的学习活动',
                'action_plan': ['分析项目需求', '设计活动框架', '制定评估标准']
            }
            
            response = await learning_designer.receive_message(message)
            
            assert message['type'] == 'suggestion'
            assert response['action_plan'] is not None
    
    @pytest.mark.asyncio
    async def test_collaborative_decision_making(self):
        """测试协作决策"""
        agents = {
            'education_director': EducationDirector(),
            'learning_designer': LearningExperienceDesigner(),
            'creative_technologist': CreativeTechnologist(),
        }
        
        decision_context = {
            'topic': '选择合适的编程语言',
            'options': ['Python', 'JavaScript', 'Scratch'],
            'criteria': ['易学性', '实用性', '趣味性'],
            'target_audience': '高中生初学者'
        }
        
        votes = {}
        
        # 每个智能体独立投票
        for agent_name, agent in agents.items():
            with patch.object(agent, '_call_llm') as mock_llm:
                if agent_name == 'education_director':
                    mock_llm.return_value = {
                        'vote': 'Python',
                        'reasoning': '语法简洁，学习曲线平缓，实用性强',
                        'confidence': 0.9
                    }
                elif agent_name == 'learning_designer':
                    mock_llm.return_value = {
                        'vote': 'Python',
                        'reasoning': '适合初学者，有丰富的教学资源',
                        'confidence': 0.8
                    }
                else:  # creative_technologist
                    mock_llm.return_value = {
                        'vote': 'JavaScript',
                        'reasoning': '可以做出可视化效果，增加趣味性',
                        'confidence': 0.7
                    }
                
                vote = await agent.make_decision(decision_context)
                votes[agent_name] = vote
        
        # 计算共识
        consensus = self._calculate_consensus(votes)
        
        assert consensus['decision'] == 'Python'  # 多数票
        assert 0.7 <= consensus['average_confidence'] <= 0.9
    
    def _calculate_consensus(self, votes: Dict[str, Dict]) -> Dict[str, Any]:
        """计算共识"""
        from collections import Counter
        
        decisions = [vote['vote'] for vote in votes.values()]
        confidences = [vote['confidence'] for vote in votes.values()]
        
        decision_counts = Counter(decisions)
        majority_decision = decision_counts.most_common(1)[0][0]
        
        return {
            'decision': majority_decision,
            'vote_distribution': dict(decision_counts),
            'average_confidence': sum(confidences) / len(confidences),
            'unanimity': len(set(decisions)) == 1
        }


class TestAgentWorkflowIntegration:
    """智能体工作流集成测试"""
    
    @pytest.mark.asyncio
    async def test_complete_course_design_workflow(self):
        """测试完整课程设计工作流"""
        course_requirements = CourseFactory.build_dict()
        
        # 步骤1：教育主管分析需求
        education_director = EducationDirector()
        with patch.object(education_director, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                'curriculum_framework': 'PBL',
                'learning_objectives': course_requirements['learning_objectives'],
                'assessment_strategy': 'authentic_assessment',
                'feasibility': 'high'
            }
            
            ed_result = await education_director.analyze_curriculum_requirements(course_requirements)
        
        # 步骤2：学习设计师设计活动
        learning_designer = LearningExperienceDesigner()
        with patch.object(learning_designer, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                'learning_activities': [
                    {
                        'name': '项目启动会',
                        'type': 'workshop',
                        'duration': '2小时',
                        'objectives': ['团队组建', '项目理解']
                    },
                    {
                        'name': '技能学习模块',
                        'type': 'tutorial',
                        'duration': '4周',
                        'objectives': ['掌握基础技能']
                    }
                ],
                'learning_path': 'adaptive'
            }
            
            ld_result = await learning_designer.design_learning_activities(
                ed_result['learning_objectives']
            )
        
        # 步骤3：创意技术专家推荐工具
        creative_tech = CreativeTechnologist()
        with patch.object(creative_tech, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                'recommended_tools': [
                    {'name': 'VS Code', 'type': 'IDE', 'learning_curve': 'medium'},
                    {'name': 'GitHub', 'type': 'version_control', 'learning_curve': 'medium'},
                    {'name': 'Figma', 'type': 'design', 'learning_curve': 'low'}
                ],
                'technology_stack': 'web_development',
                'maker_activities': []
            }
            
            ct_result = await creative_tech.suggest_technology_tools({
                'project_type': 'web_application',
                'skill_level': 'beginner',
                'duration': course_requirements['duration_weeks']
            })
        
        # 步骤4：评估专家设计评估
        assessment_specialist = AssessmentFeedbackSpecialist()
        with patch.object(assessment_specialist, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                'assessment_framework': {
                    'formative': ['周反思', '同伴评议'],
                    'summative': ['项目展示', '作品集评估']
                },
                'rubric': {
                    'criteria': ['技术实现', '创新性', '团队协作', '沟通表达'],
                    'levels': 4
                }
            }
            
            as_result = await assessment_specialist.design_assessment_framework(
                ld_result['learning_activities']
            )
        
        # 步骤5：社区协调员组织活动
        community_coordinator = CommunityCoordinator()
        with patch.object(community_coordinator, '_call_llm') as mock_llm:
            mock_llm.return_value = {
                'community_events': [
                    {'name': 'kickoff_event', 'type': 'orientation'},
                    {'name': 'mid_term_showcase', 'type': 'presentation'},
                    {'name': 'final_exhibition', 'type': 'celebration'}
                ],
                'mentorship_plan': 'industry_experts',
                'collaboration_structure': 'cross_functional_teams'
            }
            
            cc_result = await community_coordinator.plan_community_engagement({
                'course': course_requirements,
                'activities': ld_result['learning_activities']
            })
        
        # 验证工作流结果
        assert ed_result['feasibility'] == 'high'
        assert len(ld_result['learning_activities']) >= 2
        assert len(ct_result['recommended_tools']) >= 3
        assert 'rubric' in as_result
        assert len(cc_result['community_events']) >= 3
        
        # 验证智能体间的一致性
        assert ed_result['curriculum_framework'] == 'PBL'
        assert ld_result['learning_path'] == 'adaptive'
        assert as_result['assessment_framework']['summative'] is not None


class TestPerformanceAndScaling:
    """性能和扩展性测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """测试并发智能体执行"""
        agents = [
            EducationDirector(),
            LearningExperienceDesigner(),
            CreativeTechnologist(),
            AssessmentFeedbackSpecialist(),
            CommunityCoordinator(),
        ]
        
        # 并发执行任务
        tasks = []
        for i, agent in enumerate(agents):
            with patch.object(agent, '_call_llm') as mock_llm:
                mock_llm.return_value = {'result': f'agent_{i}_result'}
                task = agent.process_task({'task_id': f'task_{i}'})
                tasks.append(task)
        
        # 等待所有任务完成
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 验证并发执行效果
        assert len(results) == 5
        assert execution_time < 10  # 应该在10秒内完成
        assert all(not isinstance(r, Exception) for r in results)
    
    @pytest.mark.asyncio
    async def test_agent_load_handling(self):
        """测试智能体负载处理"""
        education_director = EducationDirector()
        
        # 模拟高负载场景
        concurrent_requests = 20
        tasks = []
        
        for i in range(concurrent_requests):
            with patch.object(education_director, '_call_llm') as mock_llm:
                mock_llm.return_value = {'response': f'response_{i}'}
                task = education_director.analyze_curriculum_requirements({
                    'course_id': i,
                    'requirements': f'requirement_{i}'
                })
                tasks.append(task)
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 验证负载处理能力
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= concurrent_requests * 0.8  # 至少80%成功
        assert execution_time < 30  # 30秒内完成
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self):
        """测试内存使用优化"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量智能体实例
        agents = []
        for _ in range(100):
            agent = EducationDirector()
            agents.append(agent)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 清理智能体
        del agents
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 验证内存使用
        memory_increase = peak_memory - initial_memory
        memory_cleaned = peak_memory - final_memory
        
        assert memory_increase < 500  # 内存增长不超过500MB
        assert memory_cleaned > memory_increase * 0.7  # 至少清理70%的内存
    
    @pytest.mark.asyncio 
    async def test_response_time_requirements(self):
        """测试响应时间要求"""
        education_director = EducationDirector()
        
        # 测试不同复杂度任务的响应时间
        test_cases = [
            {'complexity': 'simple', 'max_time': 2.0},
            {'complexity': 'medium', 'max_time': 5.0},
            {'complexity': 'complex', 'max_time': 10.0},
        ]
        
        for case in test_cases:
            with patch.object(education_director, '_call_llm') as mock_llm:
                # 模拟不同复杂度的处理时间
                async def mock_delay(*args, **kwargs):
                    await asyncio.sleep(0.1)  # 模拟处理时间
                    return {'result': f"{case['complexity']}_result"}
                
                mock_llm.side_effect = mock_delay
                
                start_time = datetime.now()
                result = await education_director.analyze_curriculum_requirements({
                    'complexity': case['complexity']
                })
                execution_time = (datetime.now() - start_time).total_seconds()
                
                assert execution_time < case['max_time']
                assert result['result'] == f"{case['complexity']}_result"


class TestErrorRecoveryAndFaultTolerance:
    """错误恢复和容错测试"""
    
    @pytest.mark.asyncio
    async def test_single_agent_failure_recovery(self):
        """测试单个智能体失败恢复"""
        orchestrator = AgentOrchestrator()
        
        # 注册智能体
        primary_agent = EducationDirector()
        backup_agent = EducationDirector()  # 备份智能体
        
        orchestrator.register_agent('education_director', primary_agent)
        orchestrator.register_backup_agent('education_director', backup_agent)
        
        # 模拟主智能体失败
        with patch.object(primary_agent, 'process_task') as mock_primary:
            mock_primary.side_effect = Exception("主智能体故障")
            
            with patch.object(backup_agent, 'process_task') as mock_backup:
                mock_backup.return_value = {'status': 'completed', 'result': 'backup_result'}
                
                result = await orchestrator.execute_with_fallback(
                    'education_director',
                    {'task': 'analyze_requirements'}
                )
                
                # 验证自动切换到备份智能体
                assert result['status'] == 'completed'
                assert result['result'] == 'backup_result'
                assert result['executed_by'] == 'backup_agent'
    
    @pytest.mark.asyncio
    async def test_cascade_failure_handling(self):
        """测试级联失败处理"""
        orchestrator = AgentOrchestrator()
        
        # 创建依赖链：A -> B -> C
        agent_a = EducationDirector()
        agent_b = LearningExperienceDesigner()
        agent_c = CreativeTechnologist()
        
        orchestrator.register_agent('agent_a', agent_a)
        orchestrator.register_agent('agent_b', agent_b)
        orchestrator.register_agent('agent_c', agent_c)
        
        workflow = {
            'steps': [
                {'agent': 'agent_a', 'dependencies': []},
                {'agent': 'agent_b', 'dependencies': ['agent_a']},
                {'agent': 'agent_c', 'dependencies': ['agent_b']},
            ]
        }
        
        # 模拟中间智能体失败
        with patch.object(agent_a, 'execute_step') as mock_a:
            mock_a.return_value = {'status': 'completed', 'result': 'a_result'}
            
            with patch.object(agent_b, 'execute_step') as mock_b:
                mock_b.side_effect = Exception("智能体B失败")
                
                with patch.object(agent_c, 'execute_step') as mock_c:
                    mock_c.return_value = {'status': 'completed', 'result': 'c_result'}
                    
                    result = await orchestrator.execute_workflow_with_recovery(workflow)
                    
                    # 验证级联失败处理
                    assert result['status'] == 'partial_failure'
                    assert 'agent_a' in result['completed_steps']
                    assert 'agent_b' in result['failed_steps']
                    assert 'agent_c' in result['skipped_steps']  # 由于依赖失败而跳过
    
    @pytest.mark.asyncio
    async def test_network_partition_handling(self):
        """测试网络分区处理"""
        orchestrator = AgentOrchestrator()
        
        # 模拟分布式智能体
        local_agents = ['education_director', 'learning_designer']
        remote_agents = ['creative_technologist', 'assessment_specialist']
        
        for agent_name in local_agents + remote_agents:
            agent = MagicMock()
            orchestrator.register_agent(agent_name, agent)
        
        # 模拟网络分区
        def simulate_network_partition(agent_name):
            if agent_name in remote_agents:
                raise ConnectionError(f"无法连接到远程智能体: {agent_name}")
            return {'status': 'completed', 'result': f'{agent_name}_result'}
        
        with patch.object(orchestrator, '_execute_agent_task', side_effect=simulate_network_partition):
            task = {
                'required_agents': local_agents + remote_agents,
                'fallback_strategy': 'local_only'
            }
            
            result = await orchestrator.execute_with_partition_tolerance(task)
            
            # 验证分区容错
            assert result['status'] == 'degraded_success'
            assert len(result['successful_agents']) == len(local_agents)
            assert len(result['failed_agents']) == len(remote_agents)
            assert result['fallback_applied'] is True


class TestAgentLearningAndAdaptation:
    """智能体学习和适应性测试"""
    
    @pytest.mark.asyncio
    async def test_performance_feedback_loop(self):
        """测试性能反馈循环"""
        education_director = EducationDirector()
        
        # 模拟历史任务执行数据
        historical_data = [
            {'task_complexity': 'simple', 'execution_time': 1.2, 'success_rate': 0.95},
            {'task_complexity': 'medium', 'execution_time': 3.5, 'success_rate': 0.88},
            {'task_complexity': 'complex', 'execution_time': 8.2, 'success_rate': 0.76},
        ]
        
        # 更新智能体性能模型
        await education_director.update_performance_model(historical_data)
        
        # 测试性能预测
        predicted_time = education_director.predict_execution_time('medium')
        assert 2.0 <= predicted_time <= 5.0
        
        predicted_success = education_director.predict_success_rate('complex')
        assert 0.7 <= predicted_success <= 0.9
    
    @pytest.mark.asyncio
    async def test_adaptive_strategy_selection(self):
        """测试自适应策略选择"""
        learning_designer = LearningExperienceDesigner()
        
        # 记录不同策略的效果
        strategy_performance = {
            'project_based': {'satisfaction': 0.85, 'learning_outcome': 0.82},
            'inquiry_based': {'satisfaction': 0.78, 'learning_outcome': 0.88},
            'collaborative': {'satisfaction': 0.92, 'learning_outcome': 0.79},
        }
        
        await learning_designer.update_strategy_performance(strategy_performance)
        
        # 测试策略选择
        context = {
            'learning_objectives': ['critical_thinking', 'collaboration'],
            'student_profile': {'learning_style': 'social', 'motivation': 'high'}
        }
        
        selected_strategy = await learning_designer.select_optimal_strategy(context)
        
        # 验证选择了最适合的策略
        assert selected_strategy in strategy_performance.keys()
        # 应该偏向协作学习（基于学生的社交学习风格）
        assert selected_strategy == 'collaborative'
    
    @pytest.mark.asyncio
    async def test_knowledge_base_updates(self):
        """测试知识库更新"""
        creative_tech = CreativeTechnologist()
        
        # 新技术信息
        new_technologies = [
            {
                'name': 'Next.js 14',
                'category': 'web_framework',
                'learning_curve': 'medium',
                'popularity': 0.88,
                'release_date': '2023-10-01'
            },
            {
                'name': 'Svelte 5',
                'category': 'web_framework',
                'learning_curve': 'low',
                'popularity': 0.72,
                'release_date': '2023-12-01'
            }
        ]
        
        # 更新知识库
        await creative_tech.update_technology_knowledge(new_technologies)
        
        # 测试推荐能力更新
        recommendations = await creative_tech.recommend_technologies({
            'project_type': 'web_application',
            'team_experience': 'intermediate',
            'timeline': 'short'
        })
        
        # 验证新技术被考虑
        tech_names = [tech['name'] for tech in recommendations]
        assert any('Next.js' in name or 'Svelte' in name for name in tech_names)
    
    @pytest.mark.asyncio
    async def test_collaborative_learning_between_agents(self):
        """测试智能体间协作学习"""
        education_director = EducationDirector()
        learning_designer = LearningExperienceDesigner()
        
        # 智能体A分享经验
        experience_data = {
            'context': 'STEM课程设计',
            'successful_approaches': ['hands_on_projects', 'peer_collaboration'],
            'challenges_faced': ['time_management', 'resource_constraints'],
            'effectiveness_metrics': {'engagement': 0.89, 'completion': 0.84}
        }
        
        await education_director.share_experience(experience_data)
        
        # 智能体B学习经验
        learned_insights = await learning_designer.learn_from_peer_experience(
            'education_director', 'STEM课程设计'
        )
        
        # 验证知识传递
        assert 'hands_on_projects' in learned_insights['recommended_approaches']
        assert 'time_management' in learned_insights['potential_challenges']
        assert learned_insights['confidence_score'] > 0.7