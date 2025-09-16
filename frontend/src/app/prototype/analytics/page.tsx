'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Users,
  BookOpen,
  Clock,
  Target,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  Award,
  Globe,
  Brain,
  Building2,
  Palette,
  Sparkles,
  ArrowLeft,
  ArrowUp,
  ArrowDown,
  Filter,
  Download,
  RefreshCw,
  Calendar,
  Eye,
  ThumbsUp,
  MessageSquare,
  Star,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar
} from 'recharts';

// Sample data for analytics
const PERFORMANCE_DATA = [
  { month: '1月', projects: 45, completion: 89, satisfaction: 4.2, efficiency: 92 },
  { month: '2月', projects: 52, completion: 91, satisfaction: 4.3, efficiency: 94 },
  { month: '3月', projects: 61, completion: 93, satisfaction: 4.4, efficiency: 95 },
  { month: '4月', projects: 58, completion: 88, satisfaction: 4.1, efficiency: 90 },
  { month: '5月', projects: 67, completion: 94, satisfaction: 4.5, efficiency: 96 },
  { month: '6月', projects: 74, completion: 96, satisfaction: 4.6, efficiency: 97 },
  { month: '7月', projects: 82, completion: 95, satisfaction: 4.7, efficiency: 98 },
  { month: '8月', projects: 89, completion: 97, satisfaction: 4.8, efficiency: 99 },
  { month: '9月', projects: 96, completion: 98, satisfaction: 4.9, efficiency: 99 }
];

const AGENT_PERFORMANCE = [
  { name: '教育理论专家', efficiency: 96, tasks: 245, accuracy: 98, color: '#8b5cf6' },
  { name: '课程架构师', efficiency: 94, tasks: 189, accuracy: 97, color: '#f97316' },
  { name: '内容设计师', efficiency: 92, tasks: 267, accuracy: 95, color: '#10b981' },
  { name: '评估专家', efficiency: 98, tasks: 156, accuracy: 99, color: '#ef4444' },
  { name: '素材创作者', efficiency: 90, tasks: 203, accuracy: 94, color: '#14b8a6' }
];

const ACTIVITY_DISTRIBUTION = [
  { name: '讲座', value: 25, color: '#3b82f6' },
  { name: '工作坊', value: 35, color: '#f97316' },
  { name: '项目', value: 40, color: '#10b981' },
  { name: '讨论', value: 20, color: '#8b5cf6' },
  { name: '评估', value: 15, color: '#ef4444' },
  { name: '反思', value: 10, color: '#14b8a6' }
];

const USAGE_PATTERNS = [
  { hour: '00:00', users: 12, activity: 5 },
  { hour: '02:00', users: 8, activity: 3 },
  { hour: '04:00', users: 5, activity: 2 },
  { hour: '06:00', users: 15, activity: 8 },
  { hour: '08:00', users: 45, activity: 25 },
  { hour: '10:00', users: 78, activity: 45 },
  { hour: '12:00', users: 62, activity: 35 },
  { hour: '14:00', users: 89, activity: 52 },
  { hour: '16:00', users: 95, activity: 58 },
  { hour: '18:00', users: 67, activity: 38 },
  { hour: '20:00', users: 45, activity: 25 },
  { hour: '22:00', users: 28, activity: 15 }
];

const REAL_TIME_METRICS = {
  activeUsers: 1247,
  activeProjects: 156,
  completionRate: 94.2,
  avgResponseTime: 1.8,
  systemHealth: 99.7,
  aiAccuracy: 97.3
};

const RECENT_ACTIVITIES = [
  {
    id: 1,
    type: 'project_completed',
    message: 'AI智能体协作完成"可持续城市规划"项目设计',
    timestamp: new Date(Date.now() - 300000),
    impact: 'high'
  },
  {
    id: 2,
    type: 'user_feedback',
    message: '用户对课程设计质量给出5星评价',
    timestamp: new Date(Date.now() - 480000),
    impact: 'medium'
  },
  {
    id: 3,
    type: 'agent_optimization',
    message: '评估专家智能体性能提升3%',
    timestamp: new Date(Date.now() - 720000),
    impact: 'medium'
  },
  {
    id: 4,
    type: 'milestone_reached',
    message: '本月项目完成率达到98%新高',
    timestamp: new Date(Date.now() - 1200000),
    impact: 'high'
  }
];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('projects');
  const [isRealTime, setIsRealTime] = useState(true);
  const [currentData, setCurrentData] = useState(PERFORMANCE_DATA);

  // Simulate real-time data updates
  useEffect(() => {
    if (!isRealTime) return;

    const interval = setInterval(() => {
      setCurrentData(prevData => {
        const newData = [...prevData];
        const lastIndex = newData.length - 1;

        // Simulate data fluctuations
        newData[lastIndex] = {
          ...newData[lastIndex],
          projects: Math.max(80, newData[lastIndex].projects + (Math.random() - 0.5) * 5),
          completion: Math.max(85, Math.min(100, newData[lastIndex].completion + (Math.random() - 0.5) * 2)),
          satisfaction: Math.max(4.0, Math.min(5.0, newData[lastIndex].satisfaction + (Math.random() - 0.5) * 0.1)),
          efficiency: Math.max(85, Math.min(100, newData[lastIndex].efficiency + (Math.random() - 0.5) * 2))
        };

        return newData;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [isRealTime]);

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-slate-600 bg-slate-100';
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
                <h1 className="text-xl font-bold text-slate-800">智能分析中心</h1>
                <p className="text-sm text-slate-500">全方位数据洞察与性能监控</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Time Range Selector */}
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="1d">最近1天</option>
                <option value="7d">最近7天</option>
                <option value="30d">最近30天</option>
                <option value="90d">最近3个月</option>
              </select>

              {/* Real-time Toggle */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsRealTime(!isRealTime)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isRealTime
                      ? 'bg-green-100 text-green-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${isRealTime ? 'bg-green-500 animate-pulse' : 'bg-slate-400'}`} />
                    <span>实时更新</span>
                  </div>
                </button>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Filter className="w-4 h-4 text-slate-600" />
                </button>
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Download className="w-4 h-4 text-slate-600" />
                </button>
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <RefreshCw className="w-4 h-4 text-slate-600" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-6 mb-8">
          {[
            {
              label: '活跃用户',
              value: formatNumber(REAL_TIME_METRICS.activeUsers),
              change: '+12.5%',
              trend: 'up',
              icon: Users,
              color: 'blue'
            },
            {
              label: '进行中项目',
              value: REAL_TIME_METRICS.activeProjects.toString(),
              change: '+8.3%',
              trend: 'up',
              icon: BookOpen,
              color: 'green'
            },
            {
              label: '完成率',
              value: `${REAL_TIME_METRICS.completionRate}%`,
              change: '+2.1%',
              trend: 'up',
              icon: Target,
              color: 'purple'
            },
            {
              label: '响应时间',
              value: `${REAL_TIME_METRICS.avgResponseTime}s`,
              change: '-0.3s',
              trend: 'down',
              icon: Zap,
              color: 'orange'
            },
            {
              label: '系统健康度',
              value: `${REAL_TIME_METRICS.systemHealth}%`,
              change: '+0.2%',
              trend: 'up',
              icon: Activity,
              color: 'emerald'
            },
            {
              label: 'AI准确率',
              value: `${REAL_TIME_METRICS.aiAccuracy}%`,
              change: '+1.1%',
              trend: 'up',
              icon: Brain,
              color: 'indigo'
            }
          ].map((metric) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60"
            >
              <div className="flex items-center justify-between mb-3">
                <metric.icon className={`w-5 h-5 text-${metric.color}-600`} />
                <span className={`flex items-center text-sm font-medium ${
                  metric.trend === 'up' ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {metric.trend === 'up' ? <ArrowUp className="w-3 h-3 mr-1" /> : <ArrowDown className="w-3 h-3 mr-1" />}
                  {metric.change}
                </span>
              </div>
              <div className="space-y-1">
                <div className={`text-2xl font-bold text-${metric.color}-600`}>
                  {metric.value}
                </div>
                <p className="text-sm text-slate-600">{metric.label}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chart Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Performance Trends */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-slate-800">性能趋势分析</h3>
                <div className="flex items-center space-x-2">
                  {['projects', 'completion', 'satisfaction', 'efficiency'].map((metric) => (
                    <button
                      key={metric}
                      onClick={() => setSelectedMetric(metric)}
                      className={`px-3 py-1 rounded-md text-sm transition-colors ${
                        selectedMetric === metric
                          ? 'bg-blue-100 text-blue-700 font-medium'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {metric === 'projects' ? '项目数' :
                       metric === 'completion' ? '完成率' :
                       metric === 'satisfaction' ? '满意度' : '效率'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={currentData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis
                      dataKey="month"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey={selectedMetric}
                      stroke="#3b82f6"
                      strokeWidth={3}
                      dot={{ fill: '#3b82f6', strokeWidth: 0, r: 4 }}
                      activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2, fill: 'white' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Agent Performance */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="text-lg font-semibold text-slate-800 mb-6">智能体性能对比</h3>

              <div className="space-y-4">
                {AGENT_PERFORMANCE.map((agent, index) => (
                  <motion.div
                    key={agent.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: agent.color }}
                        />
                        <span className="font-medium text-slate-800">{agent.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-800">{agent.efficiency}%</div>
                        <div className="text-xs text-slate-500">{agent.tasks} 个任务</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                          <span>效率</span>
                          <span>{agent.efficiency}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div
                            className="h-full rounded-full"
                            style={{
                              backgroundColor: agent.color,
                              width: `${agent.efficiency}%`
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                          <span>准确率</span>
                          <span>{agent.accuracy}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div
                            className="h-full rounded-full opacity-75"
                            style={{
                              backgroundColor: agent.color,
                              width: `${agent.accuracy}%`
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Usage Patterns */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="text-lg font-semibold text-slate-800 mb-6">使用模式分析</h3>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={USAGE_PATTERNS}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis
                      dataKey="hour"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: '#64748b' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="users"
                      stackId="1"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="activity"
                      stackId="1"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Activity Distribution */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="text-lg font-semibold text-slate-800 mb-6">活动类型分布</h3>

              <div className="h-48 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={ACTIVITY_DISTRIBUTION}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {ACTIVITY_DISTRIBUTION.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>

              <div className="space-y-2">
                {ACTIVITY_DISTRIBUTION.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm text-slate-600">{item.name}</span>
                    </div>
                    <span className="text-sm font-medium text-slate-800">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Real-time Activity Feed */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="text-lg font-semibold text-slate-800 mb-6">实时动态</h3>

              <div className="space-y-4 max-h-64 overflow-y-auto">
                <AnimatePresence>
                  {RECENT_ACTIVITIES.map((activity) => (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="p-3 rounded-lg bg-slate-50"
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${getImpactColor(activity.impact).split(' ')[1]}`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-slate-800">{activity.message}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            {activity.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* System Status */}
            <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-6 text-white">
              <h3 className="font-semibold mb-4">系统健康状态</h3>

              <div className="space-y-4">
                {[
                  { label: 'API服务', status: '正常', value: 99.9 },
                  { label: 'AI模型', status: '正常', value: 99.7 },
                  { label: '数据库', status: '正常', value: 99.8 },
                  { label: '缓存系统', status: '正常', value: 99.5 }
                ].map((service) => (
                  <div key={service.label} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="w-4 h-4 text-green-300" />
                      <span className="text-sm opacity-90">{service.label}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">{service.value}%</div>
                      <div className="text-xs opacity-75">{service.status}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-white/10 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Info className="w-4 h-4" />
                  <span className="text-sm">所有系统运行正常</span>
                </div>
              </div>
            </div>

            {/* Performance Insights */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">性能洞察</h3>

              <div className="space-y-4">
                {[
                  {
                    title: '智能体协作效率提升',
                    value: '+15%',
                    description: '相比上月提升显著',
                    trend: 'up',
                    icon: Users
                  },
                  {
                    title: '用户满意度',
                    value: '4.8/5.0',
                    description: '连续3月保持高分',
                    trend: 'up',
                    icon: Star
                  },
                  {
                    title: '项目完成时间',
                    value: '-20%',
                    description: '平均节省1.2天',
                    trend: 'down',
                    icon: Clock
                  }
                ].map((insight, index) => (
                  <motion.div
                    key={insight.title}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-3 rounded-lg bg-slate-50"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center`}>
                        <insight.icon className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-slate-800">{insight.title}</span>
                          <span className={`text-sm font-bold ${
                            insight.trend === 'up' ? 'text-green-600' : 'text-orange-600'
                          }`}>
                            {insight.value}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">{insight.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}