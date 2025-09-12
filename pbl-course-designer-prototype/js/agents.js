// 智能体管理器
class AgentManager {
    constructor() {
        this.agents = {
            'theory-expert': {
                name: '教育理论专家',
                role: 'UBD框架设计',
                avatar: '🎯',
                status: 'pending',
                progress: 0,
                capabilities: [
                    '基于UBD理论设计课程框架',
                    '分析学习目标和评估方式',
                    '制定教学策略建议'
                ]
            },
            'course-architect': {
                name: '课程架构师',
                role: '整体结构设计',
                avatar: '🏗️',
                status: 'pending',
                progress: 0,
                capabilities: [
                    '设计课程整体结构',
                    '规划课时安排',
                    '制定学习路径'
                ]
            },
            'content-designer': {
                name: '内容设计师',
                role: '学习活动创作',
                avatar: '✍️',
                status: 'pending',
                progress: 0,
                capabilities: [
                    '创作学习活动和练习',
                    '设计互动教学内容',
                    '开发项目任务'
                ]
            },
            'assessment-expert': {
                name: '评估专家',
                role: '评价体系设计',
                avatar: '📊',
                status: 'pending',
                progress: 0,
                capabilities: [
                    '设计评价标准和量表',
                    '制定形成性评估方案',
                    '创建学习成果评价体系'
                ]
            },
            'material-creator': {
                name: '资料制作师',
                role: '教学资料生成',
                avatar: '📁',
                status: 'pending',
                progress: 0,
                capabilities: [
                    '生成详细教案',
                    '制作教学PPT',
                    '创建学生手册和练习册'
                ]
            }
        };

        this.activeAgents = [];
        this.init();
    }

    init() {
        this.renderAgents();
        this.bindEvents();
    }

    renderAgents() {
        const agentsList = document.querySelector('.agents-list');
        agentsList.innerHTML = '';

        Object.entries(this.agents).forEach(([id, agent]) => {
            const agentCard = this.createAgentCard(id, agent);
            agentsList.appendChild(agentCard);
        });
    }

    createAgentCard(id, agent) {
        const card = document.createElement('div');
        card.className = 'agent-card';
        card.dataset.agent = id;

        let statusHTML = '';
        if (agent.status === 'completed') {
            statusHTML = `
                <div class="agent-status completed">
                    <span class="status-icon">✅</span>
                    已完成任务
                </div>
            `;
        } else if (agent.status === 'working') {
            statusHTML = `
                <div class="agent-status working">
                    <span class="status-icon">⚡</span>
                    正在工作中...
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${agent.progress}%"></div>
                    </div>
                </div>
            `;
        } else {
            statusHTML = `
                <div class="agent-status pending">
                    <span class="status-icon">⏳</span>
                    等待启动
                </div>
            `;
        }

        card.innerHTML = `
            <div class="agent-avatar">${agent.avatar}</div>
            <div class="agent-info">
                <h3>${agent.name}</h3>
                <p class="agent-role">${agent.role}</p>
                ${statusHTML}
            </div>
        `;

        return card;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.agent-card')) {
                const agentId = e.target.closest('.agent-card').dataset.agent;
                this.showAgentModal(agentId);
            }
        });
    }

    activateAgent(agentId) {
        if (!this.agents[agentId]) return;

        this.agents[agentId].status = 'working';
        this.agents[agentId].progress = 0;
        this.activeAgents.push(agentId);

        this.updateAgentCard(agentId);
        this.simulateWork(agentId);
        
        // 更新团队状态
        this.updateTeamStatus();
    }

    simulateWork(agentId) {
        const agent = this.agents[agentId];
        const duration = 5000; // 5秒完成工作
        const interval = 100; // 每100ms更新一次
        const increment = (interval / duration) * 100;

        const progressTimer = setInterval(() => {
            agent.progress += increment;
            
            if (agent.progress >= 100) {
                agent.progress = 100;
                clearInterval(progressTimer);
                
                // 延迟一下再完成，让用户看到100%
                setTimeout(() => {
                    if (agent.status === 'working') { // 确保没有被手动完成
                        this.completeAgent(agentId);
                    }
                }, 500);
            }
            
            this.updateAgentProgress(agentId);
        }, interval);

        // 模拟工作状态消息
        this.sendAgentMessage(agentId);
    }

    sendAgentMessage(agentId) {
        const agent = this.agents[agentId];
        const messages = {
            'theory-expert': [
                '正在分析课程需求...',
                '基于UBD理论制定学习目标...',
                '设计逆向教学设计框架...'
            ],
            'course-architect': [
                '正在构建课程整体架构...',
                '规划课时分配和学习路径...',
                '设计课程模块和衔接关系...'
            ],
            'content-designer': [
                '正在创作学习活动...',
                '设计互动教学内容...',
                '开发项目任务和练习...'
            ],
            'assessment-expert': [
                '正在制定评价标准...',
                '设计形成性评估方案...',
                '创建学习成果量表...'
            ],
            'material-creator': [
                '正在生成教学资料...',
                '制作教案和PPT...',
                '创建学生手册...'
            ]
        };

        const agentMessages = messages[agentId] || ['正在工作中...'];
        const randomMessage = agentMessages[Math.floor(Math.random() * agentMessages.length)];

        // 有时发送消息到聊天区域
        if (Math.random() < 0.3 && window.app) {
            setTimeout(() => {
                window.app.addMessage('agent', randomMessage, agentId);
            }, Math.random() * 3000 + 1000);
        }
    }

    completeAgent(agentId) {
        if (!this.agents[agentId]) return;

        this.agents[agentId].status = 'completed';
        this.agents[agentId].progress = 100;
        
        // 从活跃列表中移除
        this.activeAgents = this.activeAgents.filter(id => id !== agentId);
        
        this.updateAgentCard(agentId);
        this.updateTeamStatus();

        // 发送完成消息
        if (window.app) {
            const completionMessages = {
                'theory-expert': '✅ 教育理论分析完成！已制定基于UBD框架的课程目标。',
                'course-architect': '✅ 课程架构设计完成！整体结构和课时安排已确定。',
                'content-designer': '✅ 学习内容创作完成！所有教学活动和项目任务已设计。',
                'assessment-expert': '✅ 评价体系设计完成！评估标准和方案已制定。',
                'material-creator': '✅ 教学资料生成完成！所有文档和材料已准备就绪。'
            };
            
            setTimeout(() => {
                window.app.addMessage('agent', completionMessages[agentId] || '任务完成！', agentId);
            }, 500);
        }
    }

    updateAgentCard(agentId) {
        const card = document.querySelector(`[data-agent="${agentId}"]`);
        if (!card) return;

        const agent = this.agents[agentId];
        const newCard = this.createAgentCard(agentId, agent);
        card.innerHTML = newCard.innerHTML;
        
        // 添加视觉效果
        if (agent.status === 'working') {
            card.classList.add('active');
        } else if (agent.status === 'completed') {
            card.classList.remove('active');
            card.style.animation = 'completePulse 0.6s ease-out';
            setTimeout(() => {
                if (card.style.animation) {
                    card.style.animation = '';
                }
            }, 600);
        }
    }

    updateAgentProgress(agentId) {
        const card = document.querySelector(`[data-agent="${agentId}"]`);
        const progressFill = card?.querySelector('.progress-fill');
        
        if (progressFill) {
            progressFill.style.width = `${this.agents[agentId].progress}%`;
        }
    }

    updateTeamStatus() {
        const statusElement = document.querySelector('.team-status span:last-child');
        const statusDot = document.querySelector('.status-dot');
        
        if (this.activeAgents.length > 0) {
            statusElement.textContent = '协作中';
            statusDot.classList.add('active');
        } else {
            const completedCount = Object.values(this.agents).filter(a => a.status === 'completed').length;
            if (completedCount === Object.keys(this.agents).length) {
                statusElement.textContent = '全部完成';
                statusDot.classList.remove('active');
                statusDot.style.background = '#10b981';
            } else {
                statusElement.textContent = '待命中';
                statusDot.classList.remove('active');
            }
        }
    }

    showAgentModal(agentId) {
        const agent = this.agents[agentId];
        if (!agent) return;

        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'agent-modal active';
        modal.innerHTML = `
            <div class="agent-modal-content">
                <button class="close-modal">×</button>
                <div class="agent-modal-header">
                    <div class="agent-modal-avatar">${agent.avatar}</div>
                    <div class="agent-modal-info">
                        <h3>${agent.name}</h3>
                        <p>${agent.role}</p>
                    </div>
                </div>
                
                <div class="agent-capabilities">
                    <h4>核心能力</h4>
                    <div class="capability-list">
                        ${agent.capabilities.map(cap => `
                            <div class="capability-item">
                                <span class="capability-icon">✓</span>
                                ${cap}
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="agent-progress">
                    <h4>工作进度</h4>
                    <div class="progress-item">
                        <span class="progress-label">当前状态</span>
                        <span class="progress-value">${this.getStatusText(agent.status)}</span>
                    </div>
                    <div class="progress-item">
                        <span class="progress-label">完成度</span>
                        <span class="progress-value">${agent.progress.toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 绑定关闭事件
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    getStatusText(status) {
        const statusMap = {
            'pending': '等待中',
            'working': '工作中',
            'completed': '已完成'
        };
        return statusMap[status] || '未知';
    }

    // 重置所有智能体状态
    reset() {
        Object.keys(this.agents).forEach(id => {
            this.agents[id].status = 'pending';
            this.agents[id].progress = 0;
        });
        this.activeAgents = [];
        this.renderAgents();
        this.updateTeamStatus();
    }

    // 获取智能体状态统计
    getStats() {
        const stats = {
            total: Object.keys(this.agents).length,
            pending: 0,
            working: 0,
            completed: 0
        };

        Object.values(this.agents).forEach(agent => {
            stats[agent.status]++;
        });

        return stats;
    }
}

// 添加完成动画的CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes completePulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);