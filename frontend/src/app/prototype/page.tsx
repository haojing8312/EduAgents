'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Building2,
  Palette,
  BarChart3,
  Sparkles,
  Play,
  Pause,
  RotateCcw,
  MessageSquare,
  Users,
  BookOpen,
  TrendingUp,
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  Lightbulb,
  Target,
  Layers,
  FileText,
  Settings
} from 'lucide-react';

// Agent definitions with world-class design
const AGENTS = [
  {
    id: 'education_theorist',
    name: '教育理论专家',
    nameEn: 'Education Theorist',
    icon: Brain,
    color: {
      primary: '#8b5cf6',
      light: '#f3e8ff',
      dark: '#6d28d9'
    },
    description: '分析PBL教育理论框架',
    capabilities: ['教育心理学', 'PBL方法论', '学习理论', '认知科学'],
    status: 'active',
    progress: 85,
    currentTask: '正在分析建构主义学习理论应用场景...'
  },
  {
    id: 'course_architect',
    name: '课程架构师',
    nameEn: 'Course Architect',
    icon: Building2,
    color: {
      primary: '#f97316',
      light: '#fff7ed',
      dark: '#ea580c'
    },
    description: '设计课程结构和学习路径',
    capabilities: ['课程设计', '学习路径', '知识图谱', '教学序列'],
    status: 'thinking',
    progress: 62,
    currentTask: '构建项目制学习的核心知识架构...'
  },
  {
    id: 'content_designer',
    name: '内容设计师',
    nameEn: 'Content Designer',
    icon: Palette,
    color: {
      primary: '#10b981',
      light: '#ecfdf5',
      dark: '#047857'
    },
    description: '创建教学内容和学习活动',
    capabilities: ['内容创作', '活动设计', '互动体验', '多媒体整合'],
    status: 'waiting',
    progress: 25,
    currentTask: '等待架构确认后开始内容创作...'
  },
  {
    id: 'assessment_expert',
    name: '评估专家',
    nameEn: 'Assessment Expert',
    icon: BarChart3,
    color: {
      primary: '#ef4444',
      light: '#fef2f2',
      dark: '#dc2626'
    },
    description: '构建评价体系和反馈机制',
    capabilities: ['评估设计', '反馈机制', '数据分析', '学习测量'],
    status: 'active',
    progress: 78,
    currentTask: '设计多维度项目评估矩阵...'
  },
  {
    id: 'material_creator',
    name: '素材创作者',
    nameEn: 'Material Creator',
    icon: Sparkles,
    color: {
      primary: '#14b8a6',
      light: '#f0fdfa',
      dark: '#0d9488'
    },
    description: '制作教学资源和工具',
    capabilities: ['素材制作', '工具开发', '资源整合', '技术实现'],
    status: 'active',
    progress: 45,
    currentTask: '生成交互式学习工具原型...'
  }
];

const COLLABORATION_PHASES = [
  { name: '需求分析', progress: 100, status: 'completed' },
  { name: '理论建构', progress: 85, status: 'active' },
  { name: '架构设计', progress: 62, status: 'active' },
  { name: '内容创作', progress: 25, status: 'pending' },
  { name: '评估设计', progress: 78, status: 'active' },
  { name: '资源制作', progress: 45, status: 'active' },
  { name: '整合优化', progress: 0, status: 'pending' },
  { name: '质量验证', progress: 0, status: 'pending' }
];

const DEMO_METRICS = {
  totalProjects: 1247,
  activeAgents: 5,
  completionRate: 94.2,
  avgTimeToComplete: '3.2天',
  userSatisfaction: 4.8,
  costSaving: '67%'
};

export default function PrototypePage() {
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentPhase, setCurrentPhase] = useState(1);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [collaborationMessages, setCollaborationMessages] = useState<any[]>([]);

  // Simulate real-time collaboration updates
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      // Simulate agent progress updates
      const randomAgent = AGENTS[Math.floor(Math.random() * AGENTS.length)];
      const messages = [
        `${randomAgent.name} 已完成任务阶段`,
        `正在与其他智能体同步数据...`,
        `发现新的优化方案`,
        `协作流程顺利进行中`
      ];

      setCollaborationMessages(prev => [
        ...prev.slice(-4),
        {
          id: Date.now(),
          agent: randomAgent,
          message: messages[Math.floor(Math.random() * messages.length)],
          timestamp: new Date()
        }
      ]);
    }, 3000);

    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    EduAI Revolution
                  </h1>
                  <p className="text-sm text-slate-500">AI原生多智能体PBL课程设计助手</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-slate-100 rounded-lg p-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsPlaying(!isPlaying)}
                  className={`p-2 rounded-md transition-colors ${
                    isPlaying
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 rounded-md text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                </motion.button>
              </div>

              <div className="flex items-center space-x-2 text-sm">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="font-medium text-slate-700">实时协作中</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Metrics Dashboard */}
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          {[
            { label: '项目总数', value: DEMO_METRICS.totalProjects.toLocaleString(), icon: BookOpen, color: 'blue' },
            { label: '活跃智能体', value: DEMO_METRICS.activeAgents.toString(), icon: Users, color: 'purple' },
            { label: '完成率', value: `${DEMO_METRICS.completionRate}%`, icon: CheckCircle2, color: 'green' },
            { label: '平均完成时间', value: DEMO_METRICS.avgTimeToComplete, icon: Clock, color: 'orange' },
            { label: '用户满意度', value: DEMO_METRICS.userSatisfaction.toString(), icon: TrendingUp, color: 'pink' },
            { label: '成本节省', value: DEMO_METRICS.costSaving, icon: Target, color: 'teal' }
          ].map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60"
            >
              <div className="flex items-center justify-between mb-3">
                <metric.icon className={`w-5 h-5 text-${metric.color}-600`} />
                <span className={`text-2xl font-bold text-${metric.color}-600`}>
                  {metric.value}
                </span>
              </div>
              <p className="text-sm text-slate-600">{metric.label}</p>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Collaboration Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60 mb-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-800">AI智能体协作中心</h2>
                <div className="flex items-center space-x-2 text-sm text-slate-500">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span>5个智能体协作中</span>
                </div>
              </div>

              {/* Agent Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {AGENTS.map((agent) => (
                  <motion.div
                    key={agent.id}
                    layoutId={agent.id}
                    whileHover={{ y: -2 }}
                    onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                    className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 ${
                      selectedAgent === agent.id
                        ? 'border-blue-300 bg-blue-50/50'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    } ${
                      agent.status === 'active' ? 'shadow-lg' : 'shadow-sm'
                    }`}
                    style={{
                      boxShadow: agent.status === 'active'
                        ? `0 4px 20px ${agent.color.primary}20`
                        : undefined
                    }}
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: agent.color.light }}
                      >
                        <agent.icon
                          className="w-5 h-5"
                          style={{ color: agent.color.primary }}
                        />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-slate-800">{agent.name}</h3>
                        <p className="text-xs text-slate-500">{agent.nameEn}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {agent.status === 'active' && (
                          <motion.div
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                            className="w-3 h-3 bg-green-400 rounded-full"
                          />
                        )}
                        {agent.status === 'thinking' && (
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                            className="w-3 h-3 border-2 border-orange-400 border-t-transparent rounded-full"
                          />
                        )}
                        {agent.status === 'waiting' && (
                          <div className="w-3 h-3 bg-slate-300 rounded-full" />
                        )}
                      </div>
                    </div>

                    <p className="text-sm text-slate-600 mb-3">{agent.currentTask}</p>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span>进度</span>
                        <span>{agent.progress}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <motion.div
                          className="h-full rounded-full"
                          style={{ backgroundColor: agent.color.primary }}
                          initial={{ width: 0 }}
                          animate={{ width: `${agent.progress}%` }}
                          transition={{ duration: 1, ease: "easeOut" }}
                        />
                      </div>
                    </div>

                    <AnimatePresence>
                      {selectedAgent === agent.id && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-4 pt-4 border-t border-slate-200"
                        >
                          <div className="grid grid-cols-2 gap-2">
                            {agent.capabilities.map((capability) => (
                              <div
                                key={capability}
                                className="px-2 py-1 bg-slate-100 rounded-md text-xs text-slate-600 text-center"
                              >
                                {capability}
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>

              {/* Collaboration Flow */}
              <div className="border-t border-slate-200 pt-6">
                <h3 className="font-semibold text-slate-800 mb-4">协作流程</h3>
                <div className="space-y-3">
                  {COLLABORATION_PHASES.map((phase, index) => (
                    <div key={phase.name} className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                        phase.status === 'completed' ? 'bg-green-600' :
                        phase.status === 'active' ? 'bg-blue-600' :
                        'bg-slate-300'
                      }`}>
                        {phase.status === 'completed' && (
                          <CheckCircle2 className="w-3 h-3 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className={`text-sm font-medium ${
                            phase.status === 'pending' ? 'text-slate-400' : 'text-slate-800'
                          }`}>
                            {phase.name}
                          </span>
                          <span className="text-xs text-slate-500">{phase.progress}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1 mt-1">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              phase.status === 'completed' ? 'bg-green-600' :
                              phase.status === 'active' ? 'bg-blue-600' :
                              'bg-slate-300'
                            }`}
                            style={{ width: `${phase.progress}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Real-time Activity Feed */}
          <div className="space-y-6">
            {/* Live Messages */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <div className="flex items-center space-x-2 mb-4">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-slate-800">实时协作消息</h3>
              </div>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                <AnimatePresence>
                  {collaborationMessages.slice(-5).map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="flex items-start space-x-3 p-3 rounded-lg bg-slate-50"
                    >
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: msg.agent.color.light }}
                      >
                        <msg.agent.icon
                          className="w-4 h-4"
                          style={{ color: msg.agent.color.primary }}
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-800">{msg.message}</p>
                        <p className="text-xs text-slate-500 mt-1">
                          {msg.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="font-semibold text-slate-800 mb-4">快速操作</h3>
              <div className="space-y-3">
                {[
                  { icon: Lightbulb, label: '新建PBL项目', color: 'blue' },
                  { icon: FileText, label: '查看生成报告', color: 'green' },
                  { icon: Settings, label: '智能体配置', color: 'purple' },
                  { icon: BarChart3, label: '性能分析', color: 'orange' }
                ].map((action) => (
                  <motion.button
                    key={action.label}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full p-3 rounded-lg bg-${action.color}-50 hover:bg-${action.color}-100 transition-colors flex items-center space-x-3 group`}
                  >
                    <action.icon className={`w-5 h-5 text-${action.color}-600`} />
                    <span className={`text-sm font-medium text-${action.color}-700`}>
                      {action.label}
                    </span>
                    <ArrowRight className={`w-4 h-4 text-${action.color}-400 ml-auto opacity-0 group-hover:opacity-100 transition-opacity`} />
                  </motion.button>
                ))}
              </div>
            </div>

            {/* System Status */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <Zap className="w-6 h-6" />
                <h3 className="font-semibold">系统状态</h3>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm opacity-90">AI推理引擎</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-sm">正常</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm opacity-90">协作网络</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-sm">高速</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm opacity-90">数据同步</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-sm">实时</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}