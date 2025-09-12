// 主应用逻辑
class PBLCourseDesigner {
    constructor() {
        this.currentWorkspace = 'design';
        this.currentStep = 'input';
        this.courseData = {};
        this.agents = new AgentManager();
        this.courseEditor = new CourseEditor();
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeWorkspaces();
        this.loadSampleData();
    }

    bindEvents() {
        // 导航切换
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchWorkspace(e.target.dataset.tab);
            });
        });

        // 发送消息
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // 快速操作按钮
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.dataset.action);
            });
        });

        // 生成教学资料
        document.getElementById('generate-materials')?.addEventListener('click', () => {
            this.generateMaterials();
        });

        // 预览按钮
        document.getElementById('preview-btn')?.addEventListener('click', () => {
            this.previewCourse();
        });

        // 智能体卡片点击
        document.querySelectorAll('.agent-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.showAgentDetails(e.currentTarget.dataset.agent);
            });
        });
    }

    initializeWorkspaces() {
        // 初始化所有工作台
        this.switchWorkspace('design');
    }

    switchWorkspace(workspaceName) {
        // 切换导航按钮状态
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${workspaceName}"]`).classList.add('active');

        // 切换工作台显示
        document.querySelectorAll('.workspace').forEach(workspace => {
            workspace.classList.remove('active');
        });
        document.getElementById(`${workspaceName}-workspace`).classList.add('active');

        this.currentWorkspace = workspaceName;
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;

        this.addMessage('user', message);
        input.value = '';

        // 模拟AI响应
        setTimeout(() => {
            this.handleUserInput(message);
        }, 1000);
    }

    addMessage(type, content, agentName = null) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        let avatar = '👤';
        if (type === 'system') avatar = '🎓';
        if (type === 'agent') {
            const agentAvatars = {
                'theory-expert': '🎯',
                'course-architect': '🏗️',
                'content-designer': '✍️',
                'assessment-expert': '📊',
                'material-creator': '📁'
            };
            avatar = agentAvatars[agentName] || '🤖';
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleUserInput(message) {
        // 分析用户输入，决定下一步流程
        if (this.isNewCourseRequest(message)) {
            this.startCourseDesign(message);
        } else if (this.currentStep === 'collecting-requirements') {
            this.collectRequirements(message);
        } else {
            this.addMessage('system', '我正在理解您的需求，请稍等...');
            setTimeout(() => {
                this.provideFeedback(message);
            }, 1500);
        }
    }

    isNewCourseRequest(message) {
        const keywords = ['课程', '设计', 'AI', '伦理', '编程', '数据科学'];
        return keywords.some(keyword => message.includes(keyword));
    }

    startCourseDesign(message) {
        this.currentStep = 'collecting-requirements';
        
        // 启动教育理论专家
        this.agents.activateAgent('theory-expert');
        
        setTimeout(() => {
            this.addMessage('agent', 
                '很好！我是教育理论专家，我将帮助您基于UBD框架设计这个课程。让我了解更多详细信息：\n\n1. 这门课程的目标学生是什么年级？\n2. 预计课程需要多长时间？\n3. 您希望学生在课程结束后具备什么能力？', 
                'theory-expert'
            );
        }, 1000);
    }

    collectRequirements(message) {
        // 模拟收集需求的过程
        this.addMessage('agent', 
            '非常好！基于您提供的信息，我建议采用项目式学习（PBL）方法。现在让我请课程架构师来设计整体框架...', 
            'theory-expert'
        );

        // 激活课程架构师
        setTimeout(() => {
            this.agents.completeAgent('theory-expert');
            this.agents.activateAgent('course-architect');
            this.showCourseEditor();
        }, 2000);
    }

    handleQuickAction(action) {
        const quickActions = {
            'ai-ethics': '我想设计一个关于AI伦理的高中课程，让学生了解人工智能技术的社会影响和道德责任。',
            'programming': '我想设计一个编程基础课程，适合初学者，让学生掌握基本的编程思维和技能。',
            'data-science': '我想设计一个数据科学入门课程，教学生如何分析和可视化数据。'
        };

        const message = quickActions[action];
        if (message) {
            document.getElementById('chat-input').value = message;
            this.sendMessage();
        }
    }

    showCourseEditor() {
        // 隐藏聊天界面，显示课程编辑器
        document.querySelector('.chat-container').style.display = 'none';
        document.getElementById('course-editor').style.display = 'block';

        // 更新项目时间线
        this.updateTimeline();
    }

    updateTimeline() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        
        // 更新到结构设计阶段
        timelineItems[1].classList.remove('pending');
        timelineItems[1].classList.add('active');
        
        // 模拟进度更新
        setTimeout(() => {
            timelineItems[1].classList.remove('active');
            timelineItems[1].classList.add('completed');
            timelineItems[2].classList.remove('pending');
            timelineItems[2].classList.add('active');
            
            // 激活内容设计师
            this.agents.completeAgent('course-architect');
            this.agents.activateAgent('content-designer');
        }, 5000);
    }

    generateMaterials() {
        this.showLoading('正在生成教学资料...');
        
        // 激活资料制作师
        this.agents.activateAgent('material-creator');
        this.agents.activateAgent('assessment-expert');

        // 更新输出状态
        setTimeout(() => {
            this.updateOutputStatus();
            this.hideLoading();
            this.showGenerationComplete();
        }, 8000);
    }

    updateOutputStatus() {
        const outputItems = document.querySelectorAll('.output-status');
        outputItems.forEach(status => {
            status.textContent = '已生成';
            status.className = 'output-status ready';
        });
    }

    showGenerationComplete() {
        this.addMessage('system', 
            '🎉 太棒了！课程设计已完成！您的教学资料包已生成，包括详细教案、教学PPT、学生手册和评估标准。您可以在右侧面板查看和下载。'
        );
        
        // 显示聊天界面以展示完成消息
        document.querySelector('.chat-container').style.display = 'flex';
    }

    previewCourse() {
        // 创建预览模态框
        const modal = document.createElement('div');
        modal.className = 'preview-modal';
        modal.innerHTML = `
            <div class="preview-content">
                <div class="preview-header">
                    <h2>课程预览</h2>
                    <button class="close-preview">×</button>
                </div>
                <div class="preview-body">
                    <h3>AI伦理与社会责任</h3>
                    <p><strong>目标学段：</strong>高中一年级</p>
                    <p><strong>课程时长：</strong>6课时</p>
                    <p><strong>学习目标：</strong>理解AI伦理基本原则，培养批判思维</p>
                    
                    <h4>课程安排：</h4>
                    <ol>
                        <li>AI技术现状认知 - 了解当前AI技术发展现状和应用场景</li>
                        <li>AI伦理问题探索 - 探讨AI技术带来的伦理挑战和争议</li>
                        <li>伦理框架构建 - 学习和构建AI伦理评判框架</li>
                    </ol>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        modal.querySelector('.close-preview').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
    }

    showAgentDetails(agentId) {
        // 显示智能体详细信息的模态框
        console.log('显示智能体详情:', agentId);
    }

    provideFeedback(message) {
        const responses = [
            '我理解了您的想法，让我为您提供一些建议...',
            '基于教育理论最佳实践，我建议您考虑以下几点...',
            '这是一个很好的思路！让我们进一步完善细节...'
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        this.addMessage('system', randomResponse);
    }

    showLoading(text = '处理中...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.querySelector('.loading-text');
        loadingText.textContent = text;
        overlay.classList.add('active');
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.remove('active');
    }

    loadSampleData() {
        // 加载示例数据以便演示
        this.courseData = {
            theme: 'AI伦理与社会责任',
            targetGrade: '高中一年级',
            duration: '6课时',
            objectives: '理解AI伦理基本原则，培养批判思维'
        };
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PBLCourseDesigner();
});