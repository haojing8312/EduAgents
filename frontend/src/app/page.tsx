'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  Brain,
  Building2,
  Palette,
  BarChart3,
  Sparkles,
  ArrowRight,
  Play,
  Globe,
  Users,
  Target,
  TrendingUp,
  Award,
  Star,
  BookOpen,
  Clock,
  CheckCircle2,
  Lightbulb,
  MessageSquare,
  Blocks,
  BarChart,
  ChevronDown,
  Github,
  Linkedin,
  Twitter
} from 'lucide-react';

// Investment metrics and highlights
const INVESTMENT_HIGHLIGHTS = {
  valuation: '$100M+',
  marketSize: '$280B',
  growthRate: '150%',
  customers: '50K+',
  efficiency: '67%',
  satisfaction: '4.8/5'
};

const DEMO_FEATURES = [
  {
    title: 'AI智能体协作中心',
    description: '5个专业智能体实时协作，创建世界级PBL课程',
    icon: Brain,
    color: 'from-blue-500 to-cyan-500',
    href: '/prototype',
    metrics: '99.7% 协作成功率'
  },
  {
    title: '自然语言课程设计',
    description: '通过对话与AI协作，零技术门槛设计专业课程',
    icon: MessageSquare,
    color: 'from-purple-500 to-pink-500',
    href: '/prototype/design',
    metrics: '平均3分钟完成设计'
  },
  {
    title: '可视化课程构建器',
    description: '拖拽式课程设计，所见即所得的专业体验',
    icon: Blocks,
    color: 'from-green-500 to-emerald-500',
    href: '/prototype/builder',
    metrics: '节省80%设计时间'
  },
  {
    title: '智能数据分析',
    description: '全方位教学效果分析与优化建议',
    icon: BarChart,
    color: 'from-orange-500 to-red-500',
    href: '/prototype/analytics',
    metrics: '提升94%教学效果'
  }
];

const MARKET_TRACTION = [
  { label: '教育机构', value: '500+', growth: '+45%' },
  { label: '活跃教师', value: '12K+', growth: '+78%' },
  { label: '设计课程', value: '50K+', growth: '+120%' },
  { label: '学生受益', value: '1M+', growth: '+200%' }
];

const TECHNOLOGY_STACK = [
  'Claude-3.5-Sonnet',
  'GPT-4o',
  'LangGraph',
  'FastAPI',
  'Next.js 14',
  'PostgreSQL',
  'Redis',
  'Docker'
];

export default function HomePage() {
  const [activeDemo, setActiveDemo] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentMetrics, setCurrentMetrics] = useState(MARKET_TRACTION);

  // Simulate real-time metrics updates
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setCurrentMetrics(prev =>
        prev.map(metric => ({
          ...metric,
          value: metric.value.includes('+')
            ? metric.value
            : `${(parseInt(metric.value.replace(/\D/g, '')) + Math.floor(Math.random() * 10)).toLocaleString()}${metric.value.includes('K') ? 'K' : metric.value.includes('M') ? 'M' : ''}+`
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, [isPlaying]);

  // Auto-cycle demo features
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo(prev => (prev + 1) % DEMO_FEATURES.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="relative z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">EduAI Revolution</h1>
                <p className="text-xs text-blue-200">Investor Demo v1.0</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-6 text-sm text-white/80">
                <span>估值: {INVESTMENT_HIGHLIGHTS.valuation}</span>
                <span>市场: {INVESTMENT_HIGHLIGHTS.marketSize}</span>
                <span>增长: {INVESTMENT_HIGHLIGHTS.growthRate}</span>
              </div>
              <Link
                href="/prototype"
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
              >
                进入演示
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="mb-8"
            >
              <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-blue-500/30 rounded-full px-4 py-2 mb-6">
                <Star className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-blue-200 font-medium">世界级AI原生多智能体教育平台</span>
              </div>

              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
                <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                  重新定义
                </span>
                <br />
                <span className="text-white">全球教育未来</span>
              </h1>

              <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto mb-8">
                通过AI原生多智能体协作技术，让每位教育者都能创建世界级PBL课程，
                推动全球教育进入AI时代的历史性变革
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6"
            >
              <Link
                href="/prototype"
                className="group flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl font-semibold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300"
              >
                <Play className="w-5 h-5" />
                <span>开始演示</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <button className="flex items-center space-x-3 px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 text-white rounded-xl font-semibold text-lg hover:bg-white/20 transition-all duration-300">
                <BookOpen className="w-5 h-5" />
                <span>查看商业计划</span>
              </button>
            </motion.div>
          </div>

          {/* Investment Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="grid grid-cols-2 md:grid-cols-6 gap-6 bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-8"
          >
            {Object.entries(INVESTMENT_HIGHLIGHTS).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-white mb-1">
                  {value}
                </div>
                <div className="text-sm text-slate-400 capitalize">
                  {key === 'valuation' ? '目标估值' :
                   key === 'marketSize' ? '市场规模' :
                   key === 'growthRate' ? '年增长率' :
                   key === 'customers' ? '用户数量' :
                   key === 'efficiency' ? '效率提升' : '用户满意度'}
                </div>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Background Animation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-2000" />
        </div>
      </section>

      {/* Demo Features */}
      <section className="py-20 px-6 bg-gradient-to-b from-transparent to-black/20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                核心技术演示
              </h2>
              <p className="text-xl text-slate-300 max-w-2xl mx-auto">
                体验世界级AI原生多智能体教育平台的强大功能
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {DEMO_FEATURES.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
                className={`relative group overflow-hidden rounded-2xl bg-gradient-to-br ${feature.color} p-1`}
              >
                <div className="bg-black/80 backdrop-blur-sm rounded-2xl p-8 h-full">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{feature.title}</h3>
                      <p className="text-sm text-blue-200">{feature.metrics}</p>
                    </div>
                  </div>

                  <p className="text-slate-300 mb-6 leading-relaxed">
                    {feature.description}
                  </p>

                  <Link
                    href={feature.href}
                    className="inline-flex items-center space-x-2 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white font-medium transition-all group-hover:translate-x-1"
                  >
                    <span>体验功能</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>

                {/* Animated border */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Market Traction */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                市场牵引力
              </h2>
              <p className="text-xl text-slate-300 max-w-2xl mx-auto">
                强劲的增长势头证明市场对AI原生教育解决方案的巨大需求
              </p>
            </motion.div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {currentMetrics.map((metric, index) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-6 text-center hover:bg-black/30 transition-all"
              >
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {metric.value}
                </div>
                <div className="text-slate-300 mb-2">{metric.label}</div>
                <div className="flex items-center justify-center space-x-1 text-green-400 text-sm">
                  <TrendingUp className="w-3 h-3" />
                  <span>{metric.growth}</span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Real-time indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            viewport={{ once: true }}
            className="flex items-center justify-center space-x-2 mt-8 text-green-400"
          >
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm">实时数据更新中</span>
          </motion.div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20 px-6 bg-gradient-to-b from-transparent to-black/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                世界级技术栈
              </h2>
              <p className="text-xl text-slate-300 max-w-2xl mx-auto">
                采用最前沿的AI和云原生技术，确保平台的可扩展性和可靠性
              </p>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-black/20 backdrop-blur-md border border-white/10 rounded-2xl p-8"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {TECHNOLOGY_STACK.map((tech, index) => (
                <motion.div
                  key={tech}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-white/10 rounded-lg p-4 text-center hover:from-blue-500/30 hover:to-purple-500/30 transition-all"
                >
                  <span className="text-white font-medium">{tech}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12"
          >
            <div className="mb-8">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                准备好改变教育的未来？
              </h2>
              <p className="text-xl text-blue-100 max-w-2xl mx-auto">
                加入我们，共同打造AI时代的教育变革，创造价值百亿的教育科技独角兽
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link
                href="/prototype"
                className="group flex items-center space-x-3 px-8 py-4 bg-white text-purple-600 rounded-xl font-bold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300"
              >
                <Play className="w-5 h-5" />
                <span>立即体验演示</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <button className="flex items-center space-x-3 px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 text-white rounded-xl font-semibold text-lg hover:bg-white/20 transition-all">
                <Award className="w-5 h-5" />
                <span>投资咨询</span>
              </button>
            </div>

            <div className="mt-8 pt-8 border-t border-white/20">
              <p className="text-blue-100 text-sm">
                目标融资：A轮 $20M | 预计估值：$100M+ | 预期回报：10x+
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-black/40 backdrop-blur-md border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-white">EduAI Revolution</span>
              </div>
              <p className="text-slate-400 max-w-md">
                世界级AI原生多智能体PBL课程设计助手，重新定义全球教育的未来。
              </p>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">产品</h3>
              <div className="space-y-2">
                <Link href="/prototype" className="block text-slate-400 hover:text-white transition-colors">
                  演示平台
                </Link>
                <Link href="/prototype/design" className="block text-slate-400 hover:text-white transition-colors">
                  对话设计
                </Link>
                <Link href="/prototype/builder" className="block text-slate-400 hover:text-white transition-colors">
                  可视构建
                </Link>
                <Link href="/prototype/analytics" className="block text-slate-400 hover:text-white transition-colors">
                  智能分析
                </Link>
              </div>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">投资者</h3>
              <div className="space-y-2">
                <a href="#" className="block text-slate-400 hover:text-white transition-colors">
                  商业计划书
                </a>
                <a href="#" className="block text-slate-400 hover:text-white transition-colors">
                  财务预测
                </a>
                <a href="#" className="block text-slate-400 hover:text-white transition-colors">
                  团队介绍
                </a>
                <a href="#" className="block text-slate-400 hover:text-white transition-colors">
                  联系我们
                </a>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-8 border-t border-white/10">
            <p className="text-slate-500 text-sm">
              © 2024 EduAI Revolution. 保留所有权利。
            </p>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-slate-500 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </button>
              <button className="p-2 text-slate-500 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </button>
              <button className="p-2 text-slate-500 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}