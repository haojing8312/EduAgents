'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Network, Zap, Users, TrendingUp, RefreshCw } from 'lucide-react';
import { AgentCard } from './AgentCard';
import {
  useAgents,
  useCollaborationStatus,
  useOverallProgress,
  useConnectionStatus,
  useCollaborationStore
} from '@/stores/collaborationStore';

interface CollaborationPanelProps {
  onAgentSelect?: (agentId: string) => void;
  className?: string;
}

export const CollaborationPanel = ({ onAgentSelect, className = '' }: CollaborationPanelProps) => {
  const agents = useAgents();
  const collaborationStatus = useCollaborationStatus();
  const overallProgress = useOverallProgress();
  const { isConnected, error: connectionError } = useConnectionStatus();
  const { selectedAgentId } = useCollaborationStore();

  // 计算统计数据
  const stats = {
    active: agents.filter(a => a.status === 'collaborating' || a.status === 'thinking').length,
    completed: agents.filter(a => a.status === 'completed').length,
    idle: agents.filter(a => a.status === 'idle').length,
  };

  // 获取协作状态配置
  const getStatusConfig = () => {
    switch (collaborationStatus) {
      case 'active':
        return {
          icon: Zap,
          text: '智能体协作进行中',
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-500'
        };
      case 'completed':
        return {
          icon: TrendingUp,
          text: '协作任务已完成',
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-500'
        };
      case 'error':
        return {
          icon: RefreshCw,
          text: '协作出现异常',
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-500'
        };
      default:
        return {
          icon: Users,
          text: '智能体准备就绪',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-300'
        };
    }
  };

  const statusConfig = getStatusConfig();
  const StatusIcon = statusConfig.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden ${className}`}
    >
      {/* 头部状态栏 */}
      <div className="relative bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 p-6">
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <motion.div
                animate={{ rotate: collaborationStatus === 'active' ? 360 : 0 }}
                transition={{ duration: 2, repeat: collaborationStatus === 'active' ? Infinity : 0, ease: 'linear' }}
                className="p-2 bg-white/20 rounded-lg backdrop-blur-sm"
              >
                <Network size={24} className="text-white" />
              </motion.div>
              <div>
                <h2 className="text-xl font-bold text-white">多智能体协作中心</h2>
                <p className="text-indigo-100 text-sm">AI原生协作・实时同步・智能编排</p>
              </div>
            </div>

            {/* 连接状态指示器 */}
            <div className="flex items-center space-x-2">
              <motion.div
                animate={{
                  scale: isConnected ? [1, 1.2, 1] : [1],
                  opacity: isConnected ? [1, 0.7, 1] : [0.5]
                }}
                transition={{
                  repeat: isConnected ? Infinity : 0,
                  duration: 2,
                  ease: 'easeInOut'
                }}
                className={`w-3 h-3 rounded-full ${
                  isConnected ? 'bg-green-400' : 'bg-red-400'
                }`}
              />
              <span className="text-white text-sm">
                {isConnected ? '实时同步' : '连接异常'}
              </span>
            </div>
          </div>

          {/* 总体进度 */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium">整体协作进度</span>
              <span className="text-white font-bold text-lg">{overallProgress}%</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-3 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${overallProgress}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-yellow-300 to-green-300 rounded-full shadow-lg"
                style={{
                  boxShadow: `0 0 20px rgba(255, 255, 255, 0.5)`
                }}
              />
            </div>
          </div>
        </div>

        {/* 背景装饰 */}
        <div className="absolute inset-0 opacity-10">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
            className="absolute top-4 right-4 w-32 h-32 border-2 border-white rounded-full"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
            className="absolute bottom-4 left-4 w-24 h-24 border border-white rounded-full"
          />
        </div>
      </div>

      {/* 协作状态信息 */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${statusConfig.bgColor} ${statusConfig.borderColor} border`}>
            <motion.div
              animate={{ scale: collaborationStatus === 'active' ? [1, 1.2, 1] : [1] }}
              transition={{ repeat: collaborationStatus === 'active' ? Infinity : 0, duration: 1.5 }}
            >
              <StatusIcon size={16} className={statusConfig.color} />
            </motion.div>
            <span className={`text-sm font-medium ${statusConfig.color}`}>
              {statusConfig.text}
            </span>
          </div>

          {/* 统计数据 */}
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>活跃 {stats.active}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>完成 {stats.completed}</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <span>待命 {stats.idle}</span>
            </div>
          </div>
        </div>

        {/* 连接错误提示 */}
        <AnimatePresence>
          {connectionError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <p className="text-red-600 text-sm">
                <span className="font-semibold">连接异常：</span>
                {connectionError}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 智能体卡片网格 */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-1 gap-4">
          <AnimatePresence mode="popLayout">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                layout
              >
                <AgentCard
                  agent={agent}
                  isSelected={selectedAgentId === agent.id}
                  onClick={(agent) => {
                    onAgentSelect?.(agent.id);
                  }}
                  showDetails={false}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* 协作连接线可视化 */}
      <AnimatePresence>
        {collaborationStatus === 'active' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 pointer-events-none overflow-hidden"
          >
            {/* SVG连接线 */}
            <svg className="absolute inset-0 w-full h-full">
              <defs>
                <motion.linearGradient
                  id="flowGradient"
                  x1="0%" y1="0%" x2="100%" y2="0%"
                >
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity={0} />
                  <stop offset="50%" stopColor="#3B82F6" stopOpacity={1} />
                  <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
                </motion.linearGradient>
              </defs>

              {/* 动态连接线 */}
              {Array.from({ length: 3 }).map((_, i) => (
                <motion.path
                  key={i}
                  d={`M ${50 + i * 100} 150 Q ${150 + i * 50} 200 ${250 + i * 100} 250`}
                  stroke="url(#flowGradient)"
                  strokeWidth="2"
                  fill="none"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.5
                  }}
                />
              ))}
            </svg>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};