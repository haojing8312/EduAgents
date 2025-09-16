'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Zap, CheckCircle, Clock, Activity } from 'lucide-react';
import { AgentInfo, useCollaborationStore } from '@/stores/collaborationStore';

interface AgentCardProps {
  agent: AgentInfo;
  onClick?: (agent: AgentInfo) => void;
  isSelected?: boolean;
  showDetails?: boolean;
}

export const AgentCard = ({ agent, onClick, isSelected = false, showDetails = true }: AgentCardProps) => {
  const { selectAgent } = useCollaborationStore();

  // 状态对应的图标和样式
  const getStatusConfig = (status: AgentInfo['status']) => {
    switch (status) {
      case 'thinking':
        return {
          icon: Brain,
          pulse: true,
          bgGradient: 'from-purple-500/20 to-purple-600/20',
          borderColor: 'border-purple-500/50',
          glowColor: 'shadow-purple-500/25',
          statusText: '思考中',
          statusColor: 'text-purple-600 bg-purple-100'
        };
      case 'collaborating':
        return {
          icon: Zap,
          pulse: true,
          bgGradient: 'from-yellow-500/20 to-orange-500/20',
          borderColor: 'border-yellow-500/50',
          glowColor: 'shadow-yellow-500/25',
          statusText: '协作中',
          statusColor: 'text-yellow-600 bg-yellow-100'
        };
      case 'completed':
        return {
          icon: CheckCircle,
          pulse: false,
          bgGradient: 'from-green-500/20 to-emerald-500/20',
          borderColor: 'border-green-500/50',
          glowColor: 'shadow-green-500/25',
          statusText: '已完成',
          statusColor: 'text-green-600 bg-green-100'
        };
      default:
        return {
          icon: Clock,
          pulse: false,
          bgGradient: 'from-gray-400/10 to-gray-500/10',
          borderColor: 'border-gray-300',
          glowColor: 'shadow-gray-500/10',
          statusText: '待命',
          statusColor: 'text-gray-600 bg-gray-100'
        };
    }
  };

  const statusConfig = getStatusConfig(agent.status);
  const StatusIcon = statusConfig.icon;

  const handleClick = () => {
    if (onClick) {
      onClick(agent);
    } else {
      selectAgent(isSelected ? null : agent.id);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{
        opacity: 1,
        y: 0,
        scale: isSelected ? 1.05 : 1,
        boxShadow: isSelected
          ? `0 20px 40px ${statusConfig.glowColor}`
          : `0 8px 16px ${statusConfig.glowColor}`
      }}
      exit={{ opacity: 0, y: -20, scale: 0.9 }}
      whileHover={{
        scale: isSelected ? 1.05 : 1.02,
        y: -4,
        boxShadow: `0 12px 24px ${statusConfig.glowColor}`
      }}
      whileTap={{ scale: 0.98 }}
      transition={{
        type: "spring",
        stiffness: 400,
        damping: 17,
        duration: 0.2
      }}
      className={`
        relative overflow-hidden rounded-2xl border-2 cursor-pointer
        bg-gradient-to-br ${statusConfig.bgGradient} backdrop-blur-sm
        ${statusConfig.borderColor} ${isSelected ? 'ring-2 ring-blue-500/50' : ''}
        transition-all duration-300 group
      `}
      onClick={handleClick}
      style={{
        background: `linear-gradient(135deg, ${agent.color}10, ${agent.color}20)`,
      }}
    >
      {/* 背景光效 */}
      <AnimatePresence>
        {statusConfig.pulse && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [0.8, 1.2, 0.8]
            }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{
              repeat: Infinity,
              duration: 2,
              ease: "easeInOut"
            }}
            className="absolute inset-0 rounded-2xl"
            style={{
              background: `radial-gradient(circle at center, ${agent.color}30, transparent 70%)`
            }}
          />
        )}
      </AnimatePresence>

      <div className="relative p-6 z-10">
        {/* 头部：头像和状态 */}
        <div className="flex items-start justify-between mb-4">
          <motion.div
            className="text-4xl mb-2 relative"
            animate={statusConfig.pulse ? {
              rotate: [0, 5, -5, 0],
              scale: [1, 1.1, 1]
            } : {}}
            transition={{
              repeat: statusConfig.pulse ? Infinity : 0,
              duration: 3,
              ease: "easeInOut"
            }}
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-lg"
              style={{ backgroundColor: agent.color, color: 'white' }}
            >
              {agent.avatar}
            </div>

            {/* 状态指示器 */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 border-white shadow-lg"
              style={{ backgroundColor: statusConfig.pulse ? '#10B981' : '#6B7280' }}
            >
              {statusConfig.pulse && (
                <motion.div
                  animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                  className="absolute inset-0 rounded-full bg-green-400"
                />
              )}
            </motion.div>
          </motion.div>

          <motion.div
            whileHover={{ rotate: 15 }}
            className="p-2 rounded-lg bg-white/20 backdrop-blur-sm"
          >
            <StatusIcon
              size={20}
              className={agent.status === 'completed' ? 'text-green-600' : 'text-gray-600'}
            />
          </motion.div>
        </div>

        {/* 智能体名称 */}
        <motion.h3
          className="text-lg font-bold text-gray-800 mb-2 group-hover:text-gray-900"
          layout
        >
          {agent.name}
        </motion.h3>

        {/* 状态标签 */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mb-3 ${statusConfig.statusColor}`}
        >
          <Activity size={12} className="mr-1" />
          {statusConfig.statusText}
        </motion.div>

        {showDetails && (
          <>
            {/* 描述 */}
            <motion.p
              className="text-sm text-gray-600 mb-4 leading-relaxed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              {agent.description}
            </motion.p>

            {/* 进度条 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500">进度</span>
                <span className="text-xs font-bold" style={{ color: agent.color }}>
                  {agent.progress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${agent.progress}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="h-full rounded-full shadow-sm"
                  style={{
                    backgroundColor: agent.color,
                    boxShadow: `0 0 10px ${agent.color}40`
                  }}
                />
              </div>
            </div>

            {/* 最后活动时间 */}
            {agent.lastActivity && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="flex items-center mt-4 text-xs text-gray-500"
              >
                <Clock size={12} className="mr-1" />
                <span>
                  {new Date(agent.lastActivity).toLocaleTimeString('zh-CN', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </motion.div>
            )}

            {/* 贡献内容 */}
            {agent.contribution && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-4 p-3 bg-white/30 rounded-lg backdrop-blur-sm border border-white/20"
              >
                <p className="text-xs text-gray-700 leading-relaxed">
                  <span className="font-semibold">贡献：</span>
                  {agent.contribution}
                </p>
              </motion.div>
            )}
          </>
        )}
      </div>

      {/* 选中状态的边框动画 */}
      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 rounded-2xl border-2 border-blue-500"
            style={{
              background: 'linear-gradient(45deg, transparent, rgba(59, 130, 246, 0.1), transparent)',
            }}
          />
        )}
      </AnimatePresence>

      {/* 悬浮效果光晕 */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-300"
        style={{
          background: `linear-gradient(135deg, ${agent.color}20, transparent 50%, ${agent.color}10)`
        }}
      />
    </motion.div>
  );
};