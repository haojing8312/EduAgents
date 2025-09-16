'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Mic,
  MicOff,
  Brain,
  Building2,
  Palette,
  BarChart3,
  Sparkles,
  User,
  Bot,
  Lightbulb,
  BookOpen,
  Target,
  Clock,
  Users,
  FileText,
  Download,
  Share2,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RefreshCw,
  Zap,
  ArrowLeft,
  ChevronRight,
  Star
} from 'lucide-react';

// Message types for the conversation
interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  agentId?: string;
  timestamp: Date;
  suggestions?: string[];
  attachments?: any[];
  metadata?: {
    confidence?: number;
    sources?: string[];
    relatedConcepts?: string[];
  };
}

// Course outline structure
interface CourseSection {
  id: string;
  title: string;
  description: string;
  duration: string;
  activities: string[];
  learningOutcomes: string[];
  assessments: string[];
}

const AGENTS = {
  education_theorist: {
    id: 'education_theorist',
    name: '教育理论专家',
    icon: Brain,
    color: '#8b5cf6',
    avatar: '🧠'
  },
  course_architect: {
    id: 'course_architect',
    name: '课程架构师',
    icon: Building2,
    color: '#f97316',
    avatar: '🏗️'
  },
  content_designer: {
    id: 'content_designer',
    name: '内容设计师',
    icon: Palette,
    color: '#10b981',
    avatar: '🎨'
  },
  assessment_expert: {
    id: 'assessment_expert',
    name: '评估专家',
    icon: BarChart3,
    color: '#ef4444',
    avatar: '📊'
  },
  material_creator: {
    id: 'material_creator',
    name: '素材创作者',
    icon: Sparkles,
    color: '#14b8a6',
    avatar: '🎭'
  }
};

const SAMPLE_MESSAGES: Message[] = [
  {
    id: '1',
    type: 'user',
    content: '我想为高中生设计一个关于"可持续发展与城市规划"的PBL项目，学制2周，需要涵盖环境科学、地理、数学等跨学科内容。',
    timestamp: new Date(Date.now() - 300000)
  },
  {
    id: '2',
    type: 'agent',
    agentId: 'education_theorist',
    content: '这是一个很好的跨学科PBL项目主题！从教育理论角度，我建议采用建构主义学习理论框架，让学生通过真实问题探究建构知识。可持续城市规划正好符合PBL的核心特征：真实性、复杂性、协作性。我推荐以下理论支撑：\n\n• **问题导向学习**：以真实城市规划挑战为驱动\n• **社会建构主义**：通过小组协作共建知识\n• **体验学习理论**：从具体体验到抽象概化\n• **多元智能理论**：照顾不同学习风格',
    timestamp: new Date(Date.now() - 280000),
    metadata: {
      confidence: 92,
      sources: ['建构主义学习理论', 'PBL教学法研究', '跨学科教育实践'],
      relatedConcepts: ['深度学习', '21世纪技能', '批判性思维']
    }
  },
  {
    id: '3',
    type: 'agent',
    agentId: 'course_architect',
    content: '基于理论专家的建议，我为这个2周的PBL项目设计了系统化的学习架构：\n\n**项目结构设计：**\n\n**第1周：探索与研究阶段**\n• Day 1-2: 问题情境导入，城市规划基础认知\n• Day 3-4: 跨学科知识整合（环境科学+地理+数学）\n• Day 5: 中期汇报与同伴反馈\n\n**第2周：设计与实践阶段**\n• Day 6-8: 小组协作设计可持续城市方案\n• Day 9: 原型制作与测试\n• Day 10: 最终展示与评估反思\n\n每个阶段都有明确的学习目标、关键问题和评估节点。',
    timestamp: new Date(Date.now() - 240000),
    suggestions: ['调整项目时长', '修改学习阶段', '添加实地调研', '增强技术整合']
  },
  {
    id: '4',
    type: 'system',
    content: '🎯 智能体协作提示：内容设计师正在基于已确定的架构创建具体的学习活动和材料...',
    timestamp: new Date(Date.now() - 200000)
  }
];

export default function DesignPage() {
  const [messages, setMessages] = useState<Message[]>(SAMPLE_MESSAGES);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [activeAgents, setActiveAgents] = useState<string[]>(['education_theorist', 'course_architect']);
  const [isGenerating, setIsGenerating] = useState(false);
  const [courseOutline, setCourseOutline] = useState<CourseSection[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate agent responses
  const simulateAgentResponse = async (userMessage: string) => {
    setIsGenerating(true);

    // Simulate thinking time
    await new Promise(resolve => setTimeout(resolve, 2000));

    const responses = [
      {
        agentId: 'content_designer',
        content: '基于前面的架构设计，我来为每个阶段创建具体的学习活动：\n\n**探索阶段活动设计：**\n• 虚拟城市规划游戏体验\n• "我理想的社区"思维导图\n• 数据收集工作单（人口、环境、交通）\n• 跨学科知识整合工作坊\n\n**设计阶段活动：**\n• 协作式概念图绘制\n• 3D城市模型制作\n• 可持续发展指标计算\n• 原型测试与迭代\n\n每个活动都配有详细的指导手册和评估量规。',
        suggestions: ['个性化学习路径', '增加互动元素', '技术工具整合', '社区合作机会']
      },
      {
        agentId: 'assessment_expert',
        content: '我设计了全方位的评估体系，确保学习效果的科学测量：\n\n**形成性评估（70%）：**\n• 每日学习日志 (15%)\n• 同伴互评量规 (20%)\n• 原型迭代记录 (20%)\n• 反思性写作 (15%)\n\n**总结性评估（30%）：**\n• 最终设计方案展示 (20%)\n• 跨学科知识应用测试 (10%)\n\n**评估创新点：**\n✨ AI驱动的个性化反馈\n✨ 实时数据分析与预测\n✨ 多维度能力模型测评',
        metadata: {
          confidence: 88,
          sources: ['多元评估理论', '真实性评估方法', '项目评估最佳实践']
        }
      }
    ];

    for (const response of responses) {
      await new Promise(resolve => setTimeout(resolve, 1500));

      const newMessage: Message = {
        id: Date.now().toString() + response.agentId,
        type: 'agent',
        agentId: response.agentId,
        content: response.content,
        timestamp: new Date(),
        suggestions: response.suggestions,
        metadata: response.metadata
      };

      setMessages(prev => [...prev, newMessage]);
      setActiveAgents(prev => [...prev, response.agentId]);
    }

    setIsGenerating(false);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    await simulateAgentResponse(inputValue);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                <ArrowLeft className="w-5 h-5 text-slate-600" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-slate-800">智能对话式课程设计</h1>
                <p className="text-sm text-slate-500">与AI智能体协作创建世界级PBL课程</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {Object.values(AGENTS).map((agent) => (
                  <div
                    key={agent.id}
                    className={`relative w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all ${
                      activeAgents.includes(agent.id)
                        ? 'bg-white border-2 shadow-sm scale-110'
                        : 'bg-slate-100 border border-slate-200 scale-90 opacity-50'
                    }`}
                    style={{
                      borderColor: activeAgents.includes(agent.id) ? agent.color : undefined
                    }}
                  >
                    {agent.avatar}
                    {activeAgents.includes(agent.id) && (
                      <motion.div
                        className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border border-white"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                      />
                    )}
                  </div>
                ))}
              </div>

              <div className="flex items-center space-x-2 bg-green-50 rounded-lg px-3 py-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-green-700">
                  {activeAgents.length} 个智能体协作中
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Conversation Panel */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 flex flex-col h-[calc(100vh-200px)]">
              {/* Conversation Header */}
              <div className="p-6 border-b border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-800">课程设计对话</h2>
                    <p className="text-sm text-slate-500 mt-1">
                      通过自然对话与AI智能体协作设计PBL课程
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                      <Download className="w-4 h-4 text-slate-600" />
                    </button>
                    <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                      <Share2 className="w-4 h-4 text-slate-600" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 p-6 overflow-y-auto space-y-6">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`flex space-x-4 ${
                        message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      {/* Avatar */}
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        message.type === 'user'
                          ? 'bg-blue-600'
                          : message.type === 'system'
                          ? 'bg-slate-500'
                          : 'bg-white border-2'
                      }`}
                      style={{
                        borderColor: message.agentId ? AGENTS[message.agentId as keyof typeof AGENTS]?.color : undefined,
                        backgroundColor: message.type === 'agent' ?
                          AGENTS[message.agentId as keyof typeof AGENTS]?.color + '20' : undefined
                      }}>
                        {message.type === 'user' ? (
                          <User className="w-5 h-5 text-white" />
                        ) : message.type === 'system' ? (
                          <Zap className="w-5 h-5 text-white" />
                        ) : message.agentId ? (
                          React.createElement(AGENTS[message.agentId as keyof typeof AGENTS].icon, {
                            className: "w-5 h-5",
                            style: { color: AGENTS[message.agentId as keyof typeof AGENTS].color }
                          })
                        ) : (
                          <Bot className="w-5 h-5 text-slate-600" />
                        )}
                      </div>

                      {/* Message Content */}
                      <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                        {/* Sender Name */}
                        <div className="flex items-center space-x-2 mb-2">
                          {message.type === 'user' ? (
                            <span className="text-sm font-medium text-blue-600">你</span>
                          ) : message.type === 'system' ? (
                            <span className="text-sm font-medium text-slate-500">系统提示</span>
                          ) : (
                            <>
                              <span className="text-sm font-medium" style={{
                                color: AGENTS[message.agentId as keyof typeof AGENTS]?.color
                              }}>
                                {AGENTS[message.agentId as keyof typeof AGENTS]?.name}
                              </span>
                              {message.metadata?.confidence && (
                                <div className="flex items-center space-x-1">
                                  <Star className="w-3 h-3 text-yellow-500" />
                                  <span className="text-xs text-slate-500">
                                    {message.metadata.confidence}%
                                  </span>
                                </div>
                              )}
                            </>
                          )}
                          <span className="text-xs text-slate-400">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>

                        {/* Message Bubble */}
                        <div className={`inline-block max-w-4xl p-4 rounded-2xl ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : message.type === 'system'
                            ? 'bg-slate-100 text-slate-700'
                            : 'bg-slate-50 text-slate-800 border border-slate-200'
                        }`}>
                          <div className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </div>

                          {/* Metadata */}
                          {message.metadata?.sources && (
                            <div className="mt-3 pt-3 border-t border-slate-200/50">
                              <div className="flex flex-wrap gap-2">
                                {message.metadata.sources.map((source, index) => (
                                  <span
                                    key={index}
                                    className="px-2 py-1 bg-slate-200/50 rounded-md text-xs text-slate-600"
                                  >
                                    {source}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Suggestions */}
                        {message.suggestions && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {message.suggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                onClick={() => setInputValue(suggestion)}
                                className="px-3 py-1 bg-white border border-slate-200 rounded-full text-xs text-slate-600 hover:bg-slate-50 transition-colors"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Action Buttons */}
                        {message.type === 'agent' && (
                          <div className="mt-3 flex items-center space-x-2">
                            <button className="p-1 hover:bg-slate-100 rounded-md transition-colors">
                              <ThumbsUp className="w-3 h-3 text-slate-400" />
                            </button>
                            <button className="p-1 hover:bg-slate-100 rounded-md transition-colors">
                              <ThumbsDown className="w-3 h-3 text-slate-400" />
                            </button>
                            <button className="p-1 hover:bg-slate-100 rounded-md transition-colors">
                              <Copy className="w-3 h-3 text-slate-400" />
                            </button>
                            <button className="p-1 hover:bg-slate-100 rounded-md transition-colors">
                              <RefreshCw className="w-3 h-3 text-slate-400" />
                            </button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Generating Indicator */}
                <AnimatePresence>
                  {isGenerating && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="flex items-center space-x-4"
                    >
                      <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                          <Zap className="w-5 h-5 text-slate-600" />
                        </motion.div>
                      </div>
                      <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200">
                        <div className="flex items-center space-x-2">
                          <div className="flex space-x-1">
                            {[0, 1, 2].map((i) => (
                              <motion.div
                                key={i}
                                className="w-2 h-2 bg-slate-400 rounded-full"
                                animate={{
                                  opacity: [0.5, 1, 0.5],
                                  scale: [1, 1.2, 1]
                                }}
                                transition={{
                                  duration: 1.5,
                                  repeat: Infinity,
                                  delay: i * 0.2
                                }}
                              />
                            ))}
                          </div>
                          <span className="text-sm text-slate-600">AI智能体正在思考和协作中...</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-6 border-t border-slate-200">
                <div className="flex items-end space-x-4">
                  <div className="flex-1">
                    <div className="relative">
                      <textarea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="描述你想要设计的PBL课程，智能体会协作为你创建完整方案..."
                        rows={3}
                        className="w-full px-4 py-3 pr-12 border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                      <button
                        onClick={() => setIsRecording(!isRecording)}
                        className={`absolute bottom-3 right-3 p-2 rounded-lg transition-colors ${
                          isRecording
                            ? 'bg-red-100 text-red-600 hover:bg-red-200'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isGenerating}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </motion.button>
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center space-x-2">
                    <Lightbulb className="w-3 h-3" />
                    <span>按 Enter 发送，Shift+Enter 换行</span>
                  </div>
                  <div>
                    {inputValue.length} / 2000 字符
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Quick Suggestions */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="font-semibold text-slate-800 mb-4">智能建议</h3>
              <div className="space-y-3">
                {[
                  '我想设计一个STEAM项目',
                  '如何评估学生的批判性思维',
                  '添加技术整合元素',
                  '创建跨学科学习体验',
                  '设计真实世界问题情境',
                  '优化小组协作策略'
                ].map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setInputValue(suggestion)}
                    className="w-full text-left p-3 bg-slate-50 hover:bg-slate-100 rounded-lg text-sm text-slate-700 transition-colors flex items-center justify-between group"
                  >
                    <span>{suggestion}</span>
                    <ChevronRight className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>

            {/* Course Progress */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="font-semibold text-slate-800 mb-4">课程构建进度</h3>
              <div className="space-y-4">
                {[
                  { stage: '需求分析', progress: 100, status: 'completed' },
                  { stage: '理论框架', progress: 85, status: 'active' },
                  { stage: '课程架构', progress: 70, status: 'active' },
                  { stage: '内容设计', progress: 30, status: 'active' },
                  { stage: '评估体系', progress: 45, status: 'active' },
                  { stage: '素材制作', progress: 0, status: 'pending' },
                  { stage: '整合优化', progress: 0, status: 'pending' }
                ].map((stage, index) => (
                  <div key={stage.stage} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm font-medium ${
                        stage.status === 'completed' ? 'text-green-600' :
                        stage.status === 'active' ? 'text-blue-600' :
                        'text-slate-400'
                      }`}>
                        {stage.stage}
                      </span>
                      <span className="text-xs text-slate-500">{stage.progress}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          stage.status === 'completed' ? 'bg-green-500' :
                          stage.status === 'active' ? 'bg-blue-500' :
                          'bg-slate-300'
                        }`}
                        style={{ width: `${stage.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <h3 className="font-semibold mb-4">导出选项</h3>
              <div className="space-y-3">
                {[
                  { icon: FileText, label: 'PDF课程方案' },
                  { icon: BookOpen, label: '教师指导手册' },
                  { icon: Target, label: '学生活动包' },
                  { icon: BarChart3, label: '评估工具集' }
                ].map((option, index) => (
                  <button
                    key={option.label}
                    className="w-full flex items-center space-x-3 p-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <option.icon className="w-4 h-4" />
                    <span className="text-sm">{option.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}