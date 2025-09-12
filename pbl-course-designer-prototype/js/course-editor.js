// 课程编辑器类
class CourseEditor {
    constructor() {
        this.courseData = {
            theme: '',
            targetGrade: '',
            duration: '',
            objectives: '',
            lessons: []
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSampleCourse();
    }

    bindEvents() {
        // 课时项点击事件
        document.querySelectorAll('.lesson-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.selectLesson(e.currentTarget);
            });
        });

        // 编辑按钮事件
        document.querySelectorAll('.info-item span').forEach(span => {
            span.addEventListener('click', (e) => {
                this.editField(e.target);
            });
        });
    }

    loadSampleCourse() {
        this.courseData = {
            theme: 'AI伦理与社会责任',
            targetGrade: '高中一年级',
            duration: '6课时',
            objectives: '理解AI伦理基本原则，培养批判思维',
            lessons: [
                {
                    id: 1,
                    title: 'AI技术现状认知',
                    description: '了解当前AI技术发展现状和应用场景',
                    activities: ['小组讨论', '案例分析'],
                    duration: '45分钟',
                    materials: ['PPT演示文稿', '案例视频', '讨论工作表'],
                    objectives: [
                        '了解AI技术的基本概念和发展历程',
                        '识别生活中的AI应用实例',
                        '分析AI技术对社会的影响'
                    ]
                },
                {
                    id: 2,
                    title: 'AI伦理问题探索',
                    description: '探讨AI技术带来的伦理挑战和争议',
                    activities: ['辩论赛', '角色扮演'],
                    duration: '45分钟',
                    materials: ['辩论题目卡片', '角色情境卡', '评价标准'],
                    objectives: [
                        '识别AI技术中的伦理问题',
                        '分析不同立场的观点',
                        '培养批判性思维能力'
                    ]
                },
                {
                    id: 3,
                    title: '伦理框架构建',
                    description: '学习和构建AI伦理评判框架',
                    activities: ['框架设计', '同伴评议'],
                    duration: '45分钟',
                    materials: ['框架模板', '评议表格', '参考资料'],
                    objectives: [
                        '学习经典的伦理理论框架',
                        '构建AI伦理评判标准',
                        '应用框架分析具体案例'
                    ]
                }
            ]
        };

        this.updateDisplay();
    }

    updateDisplay() {
        // 更新课程基本信息
        document.getElementById('course-theme').textContent = this.courseData.theme;
        document.getElementById('target-grade').textContent = this.courseData.targetGrade;
        document.getElementById('course-duration').textContent = this.courseData.duration;
        document.getElementById('learning-objectives').textContent = this.courseData.objectives;

        // 更新课时列表
        this.updateLessonsDisplay();
    }

    updateLessonsDisplay() {
        const lessonsContainer = document.querySelector('.lessons-timeline');
        lessonsContainer.innerHTML = '';

        this.courseData.lessons.forEach((lesson, index) => {
            const lessonElement = this.createLessonElement(lesson, index + 1);
            lessonsContainer.appendChild(lessonElement);
        });
    }

    createLessonElement(lesson, number) {
        const lessonDiv = document.createElement('div');
        lessonDiv.className = 'lesson-item';
        lessonDiv.dataset.lesson = lesson.id;

        lessonDiv.innerHTML = `
            <div class="lesson-number">${number}</div>
            <div class="lesson-content">
                <h4>${lesson.title}</h4>
                <p>${lesson.description}</p>
                <div class="lesson-activities">
                    ${lesson.activities.map(activity => 
                        `<span class="activity-tag">${activity}</span>`
                    ).join('')}
                </div>
            </div>
        `;

        lessonDiv.addEventListener('click', () => {
            this.showLessonDetails(lesson);
        });

        return lessonDiv;
    }

    selectLesson(lessonElement) {
        // 移除之前的选中状态
        document.querySelectorAll('.lesson-item').forEach(item => {
            item.classList.remove('active');
        });

        // 添加选中状态
        lessonElement.classList.add('active');

        // 显示详细信息
        const lessonId = parseInt(lessonElement.dataset.lesson);
        const lesson = this.courseData.lessons.find(l => l.id === lessonId);
        
        if (lesson) {
            this.showLessonDetails(lesson);
        }
    }

    showLessonDetails(lesson) {
        // 创建课时详情模态框
        const modal = document.createElement('div');
        modal.className = 'lesson-modal';
        modal.innerHTML = `
            <div class="lesson-modal-content">
                <div class="lesson-modal-header">
                    <h2>${lesson.title}</h2>
                    <button class="close-lesson-modal">×</button>
                </div>
                
                <div class="lesson-modal-body">
                    <div class="lesson-info-grid">
                        <div class="lesson-info-section">
                            <h3>课时描述</h3>
                            <p>${lesson.description}</p>
                        </div>
                        
                        <div class="lesson-info-section">
                            <h3>学习目标</h3>
                            <ul>
                                ${lesson.objectives.map(obj => `<li>${obj}</li>`).join('')}
                            </ul>
                        </div>
                        
                        <div class="lesson-info-section">
                            <h3>学习活动</h3>
                            <div class="activities-list">
                                ${lesson.activities.map(activity => 
                                    `<div class="activity-item">${activity}</div>`
                                ).join('')}
                            </div>
                        </div>
                        
                        <div class="lesson-info-section">
                            <h3>教学材料</h3>
                            <ul>
                                ${lesson.materials.map(material => `<li>${material}</li>`).join('')}
                            </ul>
                        </div>
                        
                        <div class="lesson-info-section">
                            <h3>课时安排</h3>
                            <p>${lesson.duration}</p>
                        </div>
                    </div>
                    
                    <div class="lesson-actions">
                        <button class="btn-secondary" onclick="this.closest('.lesson-modal').remove()">关闭</button>
                        <button class="btn-primary" onclick="window.app.courseEditor.editLesson(${lesson.id})">编辑课时</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 绑定关闭事件
        modal.querySelector('.close-lesson-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });

        // 添加模态框样式
        this.addModalStyles();
    }

    editLesson(lessonId) {
        const lesson = this.courseData.lessons.find(l => l.id === lessonId);
        if (!lesson) return;

        // 创建编辑表单
        const editModal = document.createElement('div');
        editModal.className = 'edit-lesson-modal';
        editModal.innerHTML = `
            <div class="edit-lesson-content">
                <div class="edit-lesson-header">
                    <h2>编辑课时</h2>
                    <button class="close-edit-modal">×</button>
                </div>
                
                <form class="lesson-edit-form">
                    <div class="form-group">
                        <label>课时标题</label>
                        <input type="text" value="${lesson.title}" name="title">
                    </div>
                    
                    <div class="form-group">
                        <label>课时描述</label>
                        <textarea name="description" rows="3">${lesson.description}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>学习活动（用逗号分隔）</label>
                        <input type="text" value="${lesson.activities.join(', ')}" name="activities">
                    </div>
                    
                    <div class="form-group">
                        <label>课时时长</label>
                        <input type="text" value="${lesson.duration}" name="duration">
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn-secondary" onclick="this.closest('.edit-lesson-modal').remove()">取消</button>
                        <button type="submit" class="btn-primary">保存修改</button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(editModal);

        // 绑定表单提交事件
        editModal.querySelector('.lesson-edit-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveLesson(lessonId, editModal);
        });

        // 绑定关闭事件
        editModal.querySelector('.close-edit-modal').addEventListener('click', () => {
            document.body.removeChild(editModal);
        });
    }

    saveLesson(lessonId, modal) {
        const form = modal.querySelector('.lesson-edit-form');
        const formData = new FormData(form);
        
        const lesson = this.courseData.lessons.find(l => l.id === lessonId);
        if (!lesson) return;

        // 更新课时数据
        lesson.title = formData.get('title');
        lesson.description = formData.get('description');
        lesson.activities = formData.get('activities').split(',').map(s => s.trim());
        lesson.duration = formData.get('duration');

        // 更新显示
        this.updateLessonsDisplay();
        
        // 关闭模态框
        document.body.removeChild(modal);
        
        // 显示保存成功提示
        this.showNotification('课时已保存');
    }

    editField(element) {
        const currentValue = element.textContent;
        const fieldType = element.id;

        // 创建编辑输入框
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentValue;
        input.className = 'inline-edit';

        // 替换元素
        element.parentNode.replaceChild(input, element);
        input.focus();

        // 绑定保存事件
        const saveEdit = () => {
            const newValue = input.value.trim() || currentValue;
            
            // 更新数据
            this.updateCourseData(fieldType, newValue);
            
            // 恢复显示
            const newSpan = document.createElement('span');
            newSpan.id = fieldType;
            newSpan.textContent = newValue;
            newSpan.addEventListener('click', (e) => this.editField(e.target));
            
            input.parentNode.replaceChild(newSpan, input);
        };

        input.addEventListener('blur', saveEdit);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                saveEdit();
            }
        });
    }

    updateCourseData(field, value) {
        const fieldMap = {
            'course-theme': 'theme',
            'target-grade': 'targetGrade',
            'course-duration': 'duration',
            'learning-objectives': 'objectives'
        };

        const dataField = fieldMap[field];
        if (dataField) {
            this.courseData[dataField] = value;
            this.showNotification('已保存修改');
        }
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }

    addModalStyles() {
        if (document.getElementById('modal-styles')) return;

        const style = document.createElement('style');
        style.id = 'modal-styles';
        style.textContent = `
            .lesson-modal, .edit-lesson-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }

            .lesson-modal-content, .edit-lesson-content {
                background: white;
                border-radius: 12px;
                padding: 0;
                max-width: 800px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }

            .lesson-modal-header, .edit-lesson-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1.5rem;
                border-bottom: 1px solid #e2e8f0;
            }

            .lesson-modal-header h2, .edit-lesson-header h2 {
                margin: 0;
                color: #1a202c;
            }

            .close-lesson-modal, .close-edit-modal {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0.5rem;
                border-radius: 50%;
            }

            .close-lesson-modal:hover, .close-edit-modal:hover {
                background: #f1f5f9;
            }

            .lesson-modal-body {
                padding: 1.5rem;
            }

            .lesson-info-grid {
                display: grid;
                gap: 1.5rem;
                margin-bottom: 2rem;
            }

            .lesson-info-section h3 {
                color: #4c51bf;
                margin-bottom: 0.75rem;
                font-size: 1.125rem;
            }

            .activities-list {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .activity-item {
                padding: 0.5rem 1rem;
                background: #e0e7ff;
                color: #4c51bf;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 500;
            }

            .lesson-actions {
                display: flex;
                justify-content: flex-end;
                gap: 0.75rem;
                padding-top: 1rem;
                border-top: 1px solid #e2e8f0;
            }

            .lesson-edit-form {
                padding: 1.5rem;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #374151;
            }

            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 0.875rem;
            }

            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #4c51bf;
                box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
            }

            .form-actions {
                display: flex;
                justify-content: flex-end;
                gap: 0.75rem;
                padding-top: 1rem;
                border-top: 1px solid #e2e8f0;
            }

            .inline-edit {
                padding: 0.5rem;
                border: 1px solid #4c51bf;
                border-radius: 4px;
                background: white;
                font-size: inherit;
            }

            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                z-index: 1001;
            }

            .notification.show {
                transform: translateX(0);
            }
        `;

        document.head.appendChild(style);
    }

    // 导出课程数据
    exportCourse() {
        const dataStr = JSON.stringify(this.courseData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.courseData.theme || 'course'}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('课程数据已导出');
    }

    // 导入课程数据
    importCourse(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const courseData = JSON.parse(e.target.result);
                this.courseData = courseData;
                this.updateDisplay();
                this.showNotification('课程数据已导入');
            } catch (error) {
                this.showNotification('导入失败：文件格式错误');
            }
        };
        reader.readAsText(file);
    }
}