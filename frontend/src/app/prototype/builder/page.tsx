'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  GripVertical,
  Clock,
  Users,
  Target,
  FileText,
  Video,
  BookOpen,
  PenTool,
  BarChart3,
  Lightbulb,
  Globe,
  Zap,
  ArrowLeft,
  ArrowRight,
  Settings,
  Download,
  Share2,
  Save,
  Eye,
  ChevronDown,
  ChevronRight,
  Move,
  Trash2,
  Copy,
  Edit,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

// Course structure interfaces
interface Activity {
  id: string;
  title: string;
  type: 'lecture' | 'workshop' | 'project' | 'discussion' | 'assessment' | 'reflection';
  duration: number;
  description: string;
  resources: string[];
  learningOutcomes: string[];
}

interface CourseSection {
  id: string;
  title: string;
  description: string;
  duration: number;
  activities: Activity[];
  collapsed: boolean;
}

interface Course {
  id: string;
  title: string;
  description: string;
  totalDuration: number;
  sections: CourseSection[];
  settings: {
    difficulty: 'beginner' | 'intermediate' | 'advanced';
    subjects: string[];
    grade: string;
    maxStudents: number;
  };
}

// Activity type definitions
const ACTIVITY_TYPES = {
  lecture: {
    icon: BookOpen,
    label: '讲座',
    color: '#3b82f6',
    bgColor: '#eff6ff'
  },
  workshop: {
    icon: PenTool,
    label: '工作坊',
    color: '#f97316',
    bgColor: '#fff7ed'
  },
  project: {
    icon: Target,
    label: '项目',
    color: '#10b981',
    bgColor: '#ecfdf5'
  },
  discussion: {
    icon: Users,
    label: '讨论',
    color: '#8b5cf6',
    bgColor: '#f3e8ff'
  },
  assessment: {
    icon: BarChart3,
    label: '评估',
    color: '#ef4444',
    bgColor: '#fef2f2'
  },
  reflection: {
    icon: Lightbulb,
    label: '反思',
    color: '#14b8a6',
    bgColor: '#f0fdfa'
  }
};

// Sample course data
const SAMPLE_COURSE: Course = {
  id: 'sustainable-city-planning',
  title: '可持续发展与城市规划',
  description: '通过真实城市规划挑战，让学生掌握可持续发展理念，整合环境科学、地理、数学等跨学科知识。',
  totalDuration: 10,
  settings: {
    difficulty: 'intermediate',
    subjects: ['环境科学', '地理', '数学', '社会学'],
    grade: '高中',
    maxStudents: 30
  },
  sections: [
    {
      id: 'exploration-phase',
      title: '探索与研究阶段',
      description: '建立问题情境，激发学生兴趣，进行基础知识学习和研究方法训练',
      duration: 5,
      collapsed: false,
      activities: [
        {
          id: 'problem-introduction',
          title: '问题情境导入',
          type: 'lecture',
          duration: 1,
          description: '通过真实城市案例引入可持续城市规划挑战',
          resources: ['城市规划视频', '案例研究材料', 'VR城市体验'],
          learningOutcomes: ['理解城市规划的复杂性', '识别可持续发展挑战']
        },
        {
          id: 'knowledge-foundation',
          title: '跨学科知识基础',
          type: 'workshop',
          duration: 2,
          description: '整合环境科学、地理、数学相关知识',
          resources: ['知识图谱', '互动练习', '概念地图工具'],
          learningOutcomes: ['掌握核心概念', '建立知识联系']
        },
        {
          id: 'research-methods',
          title: '研究方法训练',
          type: 'project',
          duration: 1.5,
          description: '学习数据收集、分析和可视化方法',
          resources: ['数据分析工具', '调研指南', '可视化软件'],
          learningOutcomes: ['掌握研究工具', '具备数据素养']
        },
        {
          id: 'mid-term-discussion',
          title: '中期讨论与反馈',
          type: 'discussion',
          duration: 0.5,
          description: '小组分享研究发现，同伴反馈',
          resources: ['讨论指南', '评估量规'],
          learningOutcomes: ['提升沟通技能', '学会批判性思维']
        }
      ]
    },
    {
      id: 'design-phase',
      title: '设计与实践阶段',
      description: '基于研究成果，协作设计可持续城市方案，制作原型并测试验证',
      duration: 5,
      collapsed: false,
      activities: [
        {
          id: 'collaborative-design',
          title: '协作方案设计',
          type: 'project',
          duration: 3,
          description: '小组协作设计可持续城市规划方案',
          resources: ['设计软件', '协作平台', '专家咨询'],
          learningOutcomes: ['应用设计思维', '发展协作技能']
        },
        {
          id: 'prototype-creation',
          title: '原型制作与测试',
          type: 'workshop',
          duration: 1,
          description: '制作3D模型或数字原型，进行可行性测试',
          resources: ['3D打印机', '建模软件', '测试工具'],
          learningOutcomes: ['将想法转化为实物', '验证设计方案']
        },
        {
          id: 'final-presentation',
          title: '最终展示与评估',
          type: 'assessment',
          duration: 0.5,
          description: '向同伴、教师和社区专家展示设计方案',
          resources: ['展示工具', '评估表', '反馈系统'],
          learningOutcomes: ['提升表达能力', '接受多方反馈']
        },
        {
          id: 'reflection-synthesis',
          title: '反思与总结',
          type: 'reflection',
          duration: 0.5,
          description: '个人和小组反思学习过程和收获',
          resources: ['反思模板', '学习档案', '成长记录'],
          learningOutcomes: ['元认知发展', '自主学习能力']
        }
      ]
    }
  ]
};

export default function BuilderPage() {
  const [course, setCourse] = useState<Course>(SAMPLE_COURSE);
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [draggedItem, setDraggedItem] = useState<any>(null);
  const [showAddActivity, setShowAddActivity] = useState(false);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  // Timeline animation
  const timelineRef = useRef<HTMLDivElement>(null);

  // Calculate total duration
  const totalDuration = course.sections.reduce((total, section) => total + section.duration, 0);

  // Handle section collapse
  const toggleSection = (sectionId: string) => {
    setCourse(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? { ...section, collapsed: !section.collapsed }
          : section
      )
    }));
  };

  // Handle activity selection
  const handleActivitySelect = (activityId: string) => {
    setSelectedActivity(selectedActivity === activityId ? null : activityId);
  };

  // Add new activity
  const addActivity = (sectionId: string, activityType: keyof typeof ACTIVITY_TYPES) => {
    const newActivity: Activity = {
      id: `activity-${Date.now()}`,
      title: `新${ACTIVITY_TYPES[activityType].label}`,
      type: activityType,
      duration: 1,
      description: '请添加活动描述...',
      resources: [],
      learningOutcomes: []
    };

    setCourse(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? {
              ...section,
              activities: [...section.activities, newActivity],
              duration: section.duration + newActivity.duration
            }
          : section
      )
    }));

    setShowAddActivity(false);
    setSelectedSection(null);
  };

  // Delete activity
  const deleteActivity = (sectionId: string, activityId: string) => {
    setCourse(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? {
              ...section,
              activities: section.activities.filter(activity => activity.id !== activityId),
              duration: section.activities
                .filter(activity => activity.id !== activityId)
                .reduce((sum, activity) => sum + activity.duration, 0)
            }
          : section
      )
    }));
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
                <h1 className="text-xl font-bold text-slate-800">可视化课程构建器</h1>
                <p className="text-sm text-slate-500">拖拽式课程设计，所见即所得</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Timeline Controls */}
              <div className="flex items-center space-x-2 bg-slate-100 rounded-lg p-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsPlaying(!isPlaying)}
                  className={`p-2 rounded-md transition-colors ${
                    isPlaying
                      ? 'bg-green-600 text-white'
                      : 'bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </motion.button>
                <button className="p-2 rounded-md text-slate-600 hover:bg-slate-50 transition-colors">
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Eye className="w-4 h-4 text-slate-600" />
                </button>
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Save className="w-4 h-4 text-slate-600" />
                </button>
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Download className="w-4 h-4 text-slate-600" />
                </button>
                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Share2 className="w-4 h-4 text-slate-600" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Course Builder */}
          <div className="lg:col-span-3">
            {/* Course Header */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60 mb-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-slate-800 mb-2">{course.title}</h2>
                  <p className="text-slate-600 mb-4">{course.description}</p>

                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4 text-slate-500" />
                      <span className="text-slate-600">{totalDuration} 天</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Users className="w-4 h-4 text-slate-500" />
                      <span className="text-slate-600">最多 {course.settings.maxStudents} 人</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Target className="w-4 h-4 text-slate-500" />
                      <span className="text-slate-600">{course.settings.difficulty}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <BookOpen className="w-4 h-4 text-slate-500" />
                      <span className="text-slate-600">{course.settings.grade}</span>
                    </div>
                  </div>
                </div>

                <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
                  <Settings className="w-5 h-5 text-slate-600" />
                </button>
              </div>

              {/* Subject Tags */}
              <div className="flex flex-wrap gap-2">
                {course.settings.subjects.map((subject) => (
                  <span
                    key={subject}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                  >
                    {subject}
                  </span>
                ))}
              </div>
            </div>

            {/* Timeline Progress */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-800">课程时间线</h3>
                <span className="text-sm text-slate-500">
                  第 {Math.ceil(currentTime)} 天 / 共 {totalDuration} 天
                </span>
              </div>

              <div className="relative">
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                    animate={{ width: `${(currentTime / totalDuration) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>

                {isPlaying && (
                  <motion.div
                    className="absolute top-0 w-1 h-2 bg-white border border-slate-300 rounded-sm"
                    animate={{
                      left: `${(currentTime / totalDuration) * 100}%`
                    }}
                    transition={{ duration: 0.5 }}
                  />
                )}
              </div>
            </div>

            {/* Course Sections */}
            <div className="space-y-6">
              {course.sections.map((section, sectionIndex) => (
                <motion.div
                  key={section.id}
                  layout
                  className="bg-white rounded-xl shadow-sm border border-slate-200/60 overflow-hidden"
                >
                  {/* Section Header */}
                  <div
                    className="p-6 border-b border-slate-200 cursor-pointer hover:bg-slate-50 transition-colors"
                    onClick={() => toggleSection(section.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                          {sectionIndex + 1}
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-slate-800">{section.title}</h3>
                          <p className="text-sm text-slate-600 mt-1">{section.description}</p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="text-sm font-medium text-slate-800">{section.duration} 天</div>
                          <div className="text-xs text-slate-500">{section.activities.length} 个活动</div>
                        </div>
                        <motion.div
                          animate={{ rotate: section.collapsed ? 0 : 90 }}
                          transition={{ duration: 0.2 }}
                        >
                          <ChevronRight className="w-5 h-5 text-slate-400" />
                        </motion.div>
                      </div>
                    </div>
                  </div>

                  {/* Activities */}
                  <AnimatePresence>
                    {!section.collapsed && (
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        <div className="p-6 space-y-4">
                          {section.activities.map((activity, activityIndex) => {
                            const ActivityIcon = ACTIVITY_TYPES[activity.type].icon;
                            const isSelected = selectedActivity === activity.id;

                            return (
                              <motion.div
                                key={activity.id}
                                layout
                                whileHover={{ y: -2 }}
                                className={`relative p-4 rounded-lg border-2 cursor-pointer transition-all ${
                                  isSelected
                                    ? 'border-blue-300 bg-blue-50/50 shadow-md'
                                    : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-white'
                                }`}
                                onClick={() => handleActivitySelect(activity.id)}
                              >
                                <div className="flex items-center space-x-4">
                                  <div className="flex items-center space-x-3">
                                    <div
                                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                                      style={{
                                        backgroundColor: ACTIVITY_TYPES[activity.type].bgColor
                                      }}
                                    >
                                      <ActivityIcon
                                        className="w-5 h-5"
                                        style={{ color: ACTIVITY_TYPES[activity.type].color }}
                                      />
                                    </div>
                                    <div className="flex-1">
                                      <h4 className="font-medium text-slate-800">{activity.title}</h4>
                                      <p className="text-sm text-slate-600">{activity.description}</p>
                                    </div>
                                  </div>

                                  <div className="flex items-center space-x-4">
                                    <span
                                      className="px-2 py-1 rounded-md text-xs font-medium"
                                      style={{
                                        backgroundColor: ACTIVITY_TYPES[activity.type].bgColor,
                                        color: ACTIVITY_TYPES[activity.type].color
                                      }}
                                    >
                                      {ACTIVITY_TYPES[activity.type].label}
                                    </span>
                                    <div className="text-sm text-slate-500">{activity.duration}天</div>

                                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                      <button className="p-1 hover:bg-slate-200 rounded transition-colors">
                                        <Move className="w-3 h-3 text-slate-600" />
                                      </button>
                                      <button className="p-1 hover:bg-slate-200 rounded transition-colors">
                                        <Copy className="w-3 h-3 text-slate-600" />
                                      </button>
                                      <button className="p-1 hover:bg-slate-200 rounded transition-colors">
                                        <Edit className="w-3 h-3 text-slate-600" />
                                      </button>
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          deleteActivity(section.id, activity.id);
                                        }}
                                        className="p-1 hover:bg-red-100 rounded transition-colors"
                                      >
                                        <Trash2 className="w-3 h-3 text-red-600" />
                                      </button>
                                    </div>
                                  </div>
                                </div>

                                {/* Expanded Activity Details */}
                                <AnimatePresence>
                                  {isSelected && (
                                    <motion.div
                                      initial={{ opacity: 0, height: 0 }}
                                      animate={{ opacity: 1, height: 'auto' }}
                                      exit={{ opacity: 0, height: 0 }}
                                      className="mt-4 pt-4 border-t border-slate-200"
                                    >
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                          <h5 className="text-sm font-medium text-slate-800 mb-2">学习成果</h5>
                                          <ul className="space-y-1">
                                            {activity.learningOutcomes.map((outcome, index) => (
                                              <li key={index} className="text-sm text-slate-600 flex items-start space-x-2">
                                                <span className="w-1 h-1 bg-slate-400 rounded-full mt-2 flex-shrink-0" />
                                                <span>{outcome}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        </div>
                                        <div>
                                          <h5 className="text-sm font-medium text-slate-800 mb-2">学习资源</h5>
                                          <div className="flex flex-wrap gap-2">
                                            {activity.resources.map((resource, index) => (
                                              <span
                                                key={index}
                                                className="px-2 py-1 bg-slate-100 text-slate-600 rounded-md text-xs"
                                              >
                                                {resource}
                                              </span>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                    </motion.div>
                                  )}
                                </AnimatePresence>
                              </motion.div>
                            );
                          })}

                          {/* Add Activity Button */}
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              setSelectedSection(section.id);
                              setShowAddActivity(true);
                            }}
                            className="w-full p-4 border-2 border-dashed border-slate-300 rounded-lg hover:border-blue-300 hover:bg-blue-50/50 transition-colors flex items-center justify-center space-x-2 text-slate-500 hover:text-blue-600"
                          >
                            <Plus className="w-5 h-5" />
                            <span className="font-medium">添加学习活动</span>
                          </motion.button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}

              {/* Add Section Button */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                className="w-full p-6 bg-white border-2 border-dashed border-slate-300 rounded-xl hover:border-blue-300 hover:bg-blue-50/50 transition-colors flex items-center justify-center space-x-3 text-slate-500 hover:text-blue-600"
              >
                <Plus className="w-6 h-6" />
                <span className="text-lg font-medium">添加课程阶段</span>
              </motion.button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Activity Types */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="font-semibold text-slate-800 mb-4">活动类型</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(ACTIVITY_TYPES).map(([type, config]) => (
                  <motion.div
                    key={type}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="p-3 rounded-lg cursor-pointer transition-colors"
                    style={{ backgroundColor: config.bgColor }}
                    draggable
                    onDragStart={() => setDraggedItem({ type: 'activity', activityType: type })}
                  >
                    <div className="flex items-center space-x-2">
                      <config.icon className="w-4 h-4" style={{ color: config.color }} />
                      <span className="text-sm font-medium" style={{ color: config.color }}>
                        {config.label}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Course Analytics */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200/60">
              <h3 className="font-semibold text-slate-800 mb-4">课程分析</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">总时长</span>
                  <span className="text-sm font-medium text-slate-800">{totalDuration} 天</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">活动数量</span>
                  <span className="text-sm font-medium text-slate-800">
                    {course.sections.reduce((total, section) => total + section.activities.length, 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">学习阶段</span>
                  <span className="text-sm font-medium text-slate-800">{course.sections.length}</span>
                </div>

                {/* Activity Distribution */}
                <div className="pt-4 border-t border-slate-200">
                  <h4 className="text-sm font-medium text-slate-800 mb-3">活动分布</h4>
                  <div className="space-y-2">
                    {Object.entries(ACTIVITY_TYPES).map(([type, config]) => {
                      const count = course.sections.reduce(
                        (total, section) =>
                          total + section.activities.filter(activity => activity.type === type).length,
                        0
                      );
                      const percentage = count > 0 ? (count / course.sections.reduce((total, section) => total + section.activities.length, 0)) * 100 : 0;

                      return (
                        <div key={type} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <config.icon className="w-3 h-3" style={{ color: config.color }} />
                            <span className="text-xs text-slate-600">{config.label}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-12 h-1 bg-slate-100 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full"
                                style={{
                                  backgroundColor: config.color,
                                  width: `${percentage}%`
                                }}
                              />
                            </div>
                            <span className="text-xs text-slate-500 w-6 text-right">{count}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* AI Suggestions */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <Zap className="w-5 h-5" />
                <h3 className="font-semibold">AI 智能建议</h3>
              </div>
              <div className="space-y-3">
                {[
                  '建议在第1阶段增加一个讨论活动',
                  '项目活动比例较高，考虑平衡',
                  '可以添加更多反思性学习环节',
                  '建议增强跨学科整合活动'
                ].map((suggestion, index) => (
                  <div key={index} className="p-3 bg-white/10 rounded-lg">
                    <p className="text-sm opacity-90">{suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Activity Modal */}
      <AnimatePresence>
        {showAddActivity && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddActivity(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-xl p-6 w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-slate-800 mb-4">选择活动类型</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(ACTIVITY_TYPES).map(([type, config]) => (
                  <motion.button
                    key={type}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => selectedSection && addActivity(selectedSection, type as keyof typeof ACTIVITY_TYPES)}
                    className="p-4 rounded-lg border-2 border-transparent hover:border-slate-300 transition-colors"
                    style={{ backgroundColor: config.bgColor }}
                  >
                    <div className="flex flex-col items-center space-y-2">
                      <config.icon className="w-6 h-6" style={{ color: config.color }} />
                      <span className="text-sm font-medium" style={{ color: config.color }}>
                        {config.label}
                      </span>
                    </div>
                  </motion.button>
                ))}
              </div>
              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setShowAddActivity(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  取消
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}