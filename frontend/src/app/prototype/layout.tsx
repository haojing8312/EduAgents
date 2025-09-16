'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  MessageCircle,
  Blocks,
  BarChart3,
  Settings,
  Users,
  BookOpen,
  Lightbulb,
  Zap,
  Menu,
  X,
  ChevronDown,
  Globe,
  Star,
  Award,
  TrendingUp
} from 'lucide-react';

const navigation = [
  {
    name: '协作中心',
    href: '/prototype',
    icon: LayoutDashboard,
    description: 'AI智能体实时协作监控'
  },
  {
    name: '对话设计',
    href: '/prototype/design',
    icon: MessageCircle,
    description: '自然语言课程设计对话'
  },
  {
    name: '可视构建',
    href: '/prototype/builder',
    icon: Blocks,
    description: '拖拽式课程结构构建器'
  },
  {
    name: '智能分析',
    href: '/prototype/analytics',
    icon: BarChart3,
    description: '全方位数据洞察分析'
  }
];

const quickStats = [
  { label: '活跃项目', value: '156', change: '+12%' },
  { label: '用户满意度', value: '4.8', change: '+0.2' },
  { label: '完成率', value: '94%', change: '+3%' },
  { label: 'AI效率', value: '97%', change: '+2%' }
];

export default function PrototypeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showQuickStats, setShowQuickStats] = useState(false);
  const pathname = usePathname();

  const currentPage = navigation.find(item => item.href === pathname);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{
          x: sidebarOpen ? 0 : -320,
        }}
        transition={{ type: "spring", damping: 30, stiffness: 300 }}
        className="fixed inset-y-0 left-0 z-50 w-80 bg-white/90 backdrop-blur-xl border-r border-slate-200/60 lg:translate-x-0 lg:static lg:inset-0"
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200/60">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  EduAI Revolution
                </h1>
                <p className="text-xs text-slate-500">AI原生多智能体平台</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-slate-600" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-6">
            <div className="space-y-2">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                    }`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon
                      className={`w-5 h-5 ${
                        isActive ? 'text-white' : 'text-slate-500 group-hover:text-slate-700'
                      }`}
                    />
                    <div className="flex-1">
                      <div className={`font-medium ${isActive ? 'text-white' : 'text-slate-900'}`}>
                        {item.name}
                      </div>
                      <div className={`text-xs ${isActive ? 'text-blue-100' : 'text-slate-500'}`}>
                        {item.description}
                      </div>
                    </div>
                    {isActive && (
                      <motion.div
                        layoutId="activeIndicator"
                        className="w-2 h-2 bg-white rounded-full"
                      />
                    )}
                  </Link>
                );
              })}
            </div>

            {/* Quick Actions */}
            <div className="mt-8">
              <h3 className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
                快速操作
              </h3>
              <div className="space-y-2">
                {[
                  { name: '新建项目', icon: Lightbulb, color: 'text-green-600' },
                  { name: '模板库', icon: BookOpen, color: 'text-blue-600' },
                  { name: '团队协作', icon: Users, color: 'text-purple-600' }
                ].map((action) => (
                  <button
                    key={action.name}
                    className="w-full flex items-center space-x-3 px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg transition-colors group"
                  >
                    <action.icon className={`w-4 h-4 ${action.color}`} />
                    <span className="text-sm">{action.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-8">
              <button
                onClick={() => setShowQuickStats(!showQuickStats)}
                className="w-full flex items-center justify-between px-4 py-2 text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  快速统计
                </span>
                <motion.div
                  animate={{ rotate: showQuickStats ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                </motion.div>
              </button>

              <AnimatePresence>
                {showQuickStats && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-2 space-y-2 overflow-hidden"
                  >
                    {quickStats.map((stat) => (
                      <div
                        key={stat.label}
                        className="flex items-center justify-between px-4 py-2 bg-slate-50 rounded-lg"
                      >
                        <span className="text-xs text-slate-600">{stat.label}</span>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-slate-800">{stat.value}</div>
                          <div className="text-xs text-green-600">{stat.change}</div>
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </nav>

          {/* Footer */}
          <div className="p-6 border-t border-slate-200/60">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-4 text-white">
              <div className="flex items-center space-x-3 mb-2">
                <Award className="w-5 h-5" />
                <span className="font-semibold">投资者演示版</span>
              </div>
              <p className="text-xs text-blue-100">
                世界级AI原生教育平台原型展示
              </p>
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/20">
                <div className="flex items-center space-x-1">
                  <Star className="w-3 h-3" />
                  <span className="text-xs">版本 1.0</span>
                </div>
                <div className="flex items-center space-x-1">
                  <TrendingUp className="w-3 h-3" />
                  <span className="text-xs">100M+ 估值</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="lg:pl-80">
        {/* Mobile header */}
        <div className="lg:hidden bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5 text-slate-600" />
            </button>
            <div className="text-center">
              <h1 className="font-semibold text-slate-800">{currentPage?.name}</h1>
              <p className="text-xs text-slate-500">{currentPage?.description}</p>
            </div>
            <div className="w-9" />
          </div>
        </div>

        {/* Page content */}
        <main className="min-h-screen">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white/80 backdrop-blur-md border-t border-slate-200/60 px-6 py-4">
          <div className="flex items-center justify-between text-sm text-slate-500">
            <div className="flex items-center space-x-4">
              <span>© 2024 EduAI Revolution</span>
              <span>•</span>
              <span>AI原生多智能体PBL课程设计助手</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <span>系统正常运行</span>
              </div>
              <span>•</span>
              <div className="flex items-center space-x-1">
                <Globe className="w-3 h-3" />
                <span>全球服务</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}