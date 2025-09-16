'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import {
  MessageCircle,
  Settings,
  Maximize2,
  Minimize2,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Sparkles
} from 'lucide-react';

import { CollaborationPanel } from './CollaborationPanel';
import { AgentCard } from './AgentCard';
import {
  useCollaborationStore,
  useCurrentTask,
  useMessages,
  useAgents,
  useCollaborationStatus,
  useOverallProgress
} from '@/stores/collaborationStore';

interface CollaborationWorkspaceProps {
  isVisible?: boolean;
  onClose?: () => void;
}

export const CollaborationWorkspace = ({
  isVisible = true,
  onClose
}: CollaborationWorkspaceProps) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedView, setSelectedView] = useState<'overview' | 'agent' | 'messages'>('overview');
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const currentTask = useCurrentTask();
  const messages = useMessages();
  const agents = useAgents();
  const collaborationStatus = useCollaborationStatus();
  const overallProgress = useOverallProgress();

  const {
    setWorkspaceVisibility,
    selectAgent,
    clearMessages,
    completeCollaboration,
    updateAgentStatus
  } = useCollaborationStore();

  // 模拟智能体协作进度
  useEffect(() => {
    if (collaborationStatus === 'active') {
      const interval = setInterval(() => {
        agents.forEach((agent, index) => {
          if (agent.status === 'idle' && Math.random() > 0.7) {
            // 随机开始思考
            updateAgentStatus(agent.id, 'thinking', 10);
          } else if (agent.status === 'thinking' && Math.random() > 0.6) {
            // 进入协作状态
            updateAgentStatus(agent.id, 'collaborating', 30 + Math.random() * 40);
          } else if (agent.status === 'collaborating' && agent.progress < 100) {
            // 更新协作进度
            const newProgress = Math.min(100, agent.progress + Math.random() * 20);
            updateAgentStatus(
              agent.id,
              newProgress >= 100 ? 'completed' : 'collaborating',
              newProgress
            );
          }
        });

        // 检查是否所有智能体都完成
        const allCompleted = agents.every(agent => agent.status === 'completed');
        if (allCompleted && collaborationStatus === 'active') {
          setTimeout(() => {
            completeCollaboration();
          }, 2000);
        }
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [collaborationStatus, agents, updateAgentStatus, completeCollaboration]);

  const selectedAgent = agents.find(a => a.id === selectedAgentId);

  const getTaskStatusIcon = () => {
    switch (collaborationStatus) {
      case 'active':
        return <RefreshCw className="animate-spin text-blue-500" size={20} />;
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      default:
        return <Clock className="text-gray-500" size={20} />;
    }
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4`}
        onClick={(e) => {
          if (e.target === e.currentTarget && !isFullscreen) {
            onClose?.();
            setWorkspaceVisibility(false);
          }
        }}
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className={`
            bg-white rounded-2xl shadow-2xl overflow-hidden
            ${isFullscreen ? 'w-full h-full' : 'w-full max-w-7xl h-5/6 max-h-[900px]'}
            flex flex-col
          `}
        >
          {/* 工作台头部 */}
          <div className="relative bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 p-6">
            <div className="flex items-center justify-between relative z-10">
              <div className="flex items-center space-x-4">
                <motion.div
                  animate={{ rotate: collaborationStatus === 'active' ? 360 : 0 }}
                  transition={{ duration: 2, repeat: collaborationStatus === 'active' ? Infinity : 0, ease: 'linear' }}
                  className="p-3 bg-white/20 rounded-xl backdrop-blur-sm"
                >
                  <Sparkles className="text-yellow-300" size={28} />
                </motion.div>
                <div>
                  <h1 className="text-2xl font-bold text-white">
                    AI原生多智能体协作工作台
                  </h1>
                  <p className="text-purple-100 text-sm mt-1">
                    {currentTask?.title || '智能体协作系统'} • 实时协同 • 世界级AI技术
                  </p>
                </div>
              </div>

              {/* 工具栏 */}
              <div className="flex items-center space-x-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg backdrop-blur-sm transition-colors"
                  title={isFullscreen ? "退出全屏" : "全屏模式"}
                >
                  {isFullscreen ? (
                    <Minimize2 className="text-white" size={20} />
                  ) : (
                    <Maximize2 className="text-white" size={20} />
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg backdrop-blur-sm transition-colors"
                  title="导出协作记录"
                >
                  <Download className="text-white" size={20} />
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-lg backdrop-blur-sm transition-colors"
                  title="设置"
                >
                  <Settings className="text-white" size={20} />
                </motion.button>

                {!isFullscreen && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      onClose?.();
                      setWorkspaceVisibility(false);
                    }}
                    className="p-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg backdrop-blur-sm transition-colors"
                    title="关闭工作台"
                  >
                    <span className="text-white text-lg">×</span>
                  </motion.button>
                )}
              </div>
            </div>

            {/* 任务信息 */}
            {currentTask && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-6 bg-white/10 backdrop-blur-sm rounded-lg p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getTaskStatusIcon()}
                    <div>
                      <h3 className="text-white font-semibold">{currentTask.title}</h3>
                      <p className="text-purple-100 text-sm">{currentTask.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-bold text-xl">{overallProgress}%</div>
                    <div className="text-purple-200 text-xs">协作进度</div>
                  </div>
                </div>

                {/* 进度条 */}
                <div className="mt-3 w-full bg-white/20 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${overallProgress}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-green-400 to-blue-400 rounded-full shadow-lg"
                  />
                </div>
              </motion.div>
            )}

            {/* 背景装饰 */}
            <div className="absolute inset-0 opacity-20">
              <motion.div
                animate={{
                  x: [0, 100, 0],
                  y: [0, 50, 0],
                  rotate: [0, 180, 360]
                }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="absolute top-10 right-20 w-20 h-20 border border-white rounded-full"
              />
              <motion.div
                animate={{
                  x: [0, -80, 0],
                  y: [0, -30, 0],
                  rotate: [0, -180, -360]
                }}
                transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
                className="absolute bottom-10 left-32 w-16 h-16 border border-white rounded-full"
              />
            </div>
          </div>

          {/* 主工作区域 */}
          <div className="flex-1 flex overflow-hidden">
            {/* 左侧智能体面板 */}
            <div className="w-80 border-r border-gray-200 flex flex-col">
              <CollaborationPanel
                onAgentSelect={setSelectedAgentId}
                className="border-none shadow-none rounded-none h-full"
              />
            </div>

            {/* 中央内容区 */}
            <div className="flex-1 flex flex-col">
              {/* 导航标签 */}
              <div className="border-b border-gray-200 px-6 py-4 bg-gray-50">
                <div className="flex space-x-6">
                  {[
                    { id: 'overview', label: '协作概览', icon: Sparkles },
                    { id: 'agent', label: '智能体详情', icon: Settings },
                    { id: 'messages', label: '协作日志', icon: MessageCircle }
                  ].map(({ id, label, icon: Icon }) => (
                    <motion.button
                      key={id}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setSelectedView(id as any)}
                      className={`
                        flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all
                        ${selectedView === id
                          ? 'bg-blue-600 text-white shadow-lg'
                          : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                        }
                      `}
                    >
                      <Icon size={18} />
                      <span>{label}</span>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* 内容区域 */}
              <div className="flex-1 p-6 overflow-auto">
                <AnimatePresence mode="wait">
                  {selectedView === 'overview' && (
                    <motion.div
                      key="overview"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                      className="h-full"
                    >
                      <div className="grid grid-cols-2 lg:grid-cols-3 gap-6 h-full">
                        {agents.map((agent, index) => (
                          <motion.div
                            key={agent.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <AgentCard
                              agent={agent}
                              isSelected={selectedAgentId === agent.id}
                              onClick={() => {
                                setSelectedAgentId(agent.id);
                                setSelectedView('agent');
                              }}
                              showDetails={true}
                            />
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {selectedView === 'agent' && selectedAgent && (
                    <motion.div
                      key="agent"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <div className="max-w-2xl mx-auto">
                        <AgentCard
                          agent={selectedAgent}
                          isSelected={true}
                          showDetails={true}
                        />

                        {/* 智能体详细信息 */}
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.2 }}
                          className="mt-6 bg-white rounded-xl border border-gray-200 p-6"
                        >
                          <h3 className="text-lg font-bold text-gray-800 mb-4">协作贡献详情</h3>
                          {selectedAgent.contribution ? (
                            <p className="text-gray-600 leading-relaxed">
                              {selectedAgent.contribution}
                            </p>
                          ) : (
                            <p className="text-gray-500 italic">该智能体暂未开始贡献内容</p>
                          )}
                        </motion.div>
                      </div>
                    </motion.div>
                  )}

                  {selectedView === 'messages' && (
                    <motion.div
                      key="messages"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                      className="h-full flex flex-col"
                    >
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold text-gray-800">协作日志</h3>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={clearMessages}
                          className="px-3 py-1 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          清空日志
                        </motion.button>
                      </div>

                      <div className="flex-1 bg-gray-50 rounded-lg p-4 overflow-auto space-y-3">
                        <AnimatePresence>
                          {messages.length === 0 ? (
                            <motion.div
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              className="text-center text-gray-500 py-12"
                            >
                              <MessageCircle size={48} className="mx-auto mb-4 text-gray-400" />
                              <p>暂无协作日志</p>
                            </motion.div>
                          ) : (
                            messages.map((message, index) => (
                              <motion.div
                                key={message.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ delay: index * 0.05 }}
                                className={`
                                  flex items-start space-x-3 p-3 rounded-lg
                                  ${message.type === 'error' ? 'bg-red-50 border border-red-200' :
                                    message.type === 'success' ? 'bg-green-50 border border-green-200' :
                                    message.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                                    'bg-white border border-gray-200'
                                  }
                                `}
                              >
                                <div
                                  className="w-2 h-2 rounded-full mt-2 flex-shrink-0"
                                  style={{
                                    backgroundColor: agents.find(a => a.id === message.agentId)?.color || '#6B7280'
                                  }}
                                />
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center space-x-2 mb-1">
                                    <span className="font-semibold text-sm text-gray-900">
                                      {message.agentName}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                      {new Date(message.timestamp).toLocaleTimeString('zh-CN')}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600">{message.content}</p>
                                </div>
                              </motion.div>
                            ))
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};