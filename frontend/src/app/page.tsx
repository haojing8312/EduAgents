'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useWebSocket } from '@/hooks/useWebSocket'

export default function Home() {
  const [courseRequirement, setCourseRequirement] = useState('')

  // 使用WebSocket进行实时通信
  const {
    isConnected,
    agents,
    overallProgress,
    courseData,
    isDesigning,
    error: websocketError,
    startDesign
  } = useWebSocket('main-session')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working': return 'bg-blue-500'
      case 'completed': return 'bg-green-500'
      case 'waiting': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-300'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'working': return '工作中'
      case 'completed': return '已完成'
      case 'waiting': return '等待中'
      case 'error': return '错误'
      default: return '待命'
    }
  }

  const handleStartDesign = () => {
    if (!courseRequirement.trim()) return
    if (!isConnected) {
      alert('WebSocket未连接，请刷新页面重试')
      return
    }
    startDesign(courseRequirement)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🚀 AI辅助PBL课程设计平台
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            推动教育公平，让优质课程设计能力人人可及
          </p>
          <p className="text-lg text-gray-500">
            技术参考 Manus AI • 影响力对标 Scratch & 可汗学院
          </p>
        </div>

        <Tabs defaultValue="design" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="design">课程设计</TabsTrigger>
            <TabsTrigger value="agents">智能体协作</TabsTrigger>
            <TabsTrigger value="results">设计成果</TabsTrigger>
          </TabsList>

          <TabsContent value="design" className="space-y-6">
            {/* Course Design Input */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  📝 课程需求输入
                </CardTitle>
                <CardDescription>
                  描述您希望设计的PBL课程，我们的AI智能体团队将为您量身定制
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="requirement">课程描述</Label>
                  <Textarea
                    id="requirement"
                    placeholder="例如：为高中生设计一个关于可持续发展的跨学科PBL课程，融合科学、技术、社会研究等多个领域，培养学生的创新思维和问题解决能力..."
                    value={courseRequirement}
                    onChange={(e) => setCourseRequirement(e.target.value)}
                    className="mt-2 min-h-[120px]"
                  />
                </div>
                <div className="space-y-2">
                  {websocketError && (
                    <div className="text-red-600 text-sm p-2 bg-red-50 rounded">
                      ❌ {websocketError}
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-sm">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-gray-600">
                      {isConnected ? '已连接到后端服务' : '未连接到后端服务'}
                    </span>
                  </div>
                  <Button
                    onClick={handleStartDesign}
                    disabled={isDesigning || !courseRequirement.trim() || !isConnected}
                    size="lg"
                    className="w-full"
                  >
                    {isDesigning ? '🔄 智能体协作中...' : '🚀 启动智能体协作设计'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Overall Progress */}
            {isDesigning && (
              <Card>
                <CardHeader>
                  <CardTitle>设计进度</CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress value={overallProgress} className="w-full" />
                  <p className="text-sm text-gray-600 mt-2">
                    {Math.round(overallProgress)}% 完成
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="agents" className="space-y-6">
            {/* AI Agents Collaboration */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent) => (
                <Card key={agent.id} className="relative overflow-hidden">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{agent.name}</CardTitle>
                      <Badge
                        variant="secondary"
                        className={`${getStatusColor(agent.status)} text-white`}
                      >
                        {getStatusText(agent.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <Progress value={agent.progress} className="w-full" />
                      <p className="text-sm text-gray-600">
                        进度: {agent.progress}%
                      </p>
                      <div className="text-sm text-gray-500">
                        {agent.task || (
                          <>
                            {agent.id === 'education_theorist' && '🎯 构建AI时代教育理论框架'}
                            {agent.id === 'course_architect' && '🏗️ 设计跨学科课程架构'}
                            {agent.id === 'content_designer' && '🎨 创作场景化学习内容'}
                            {agent.id === 'assessment_expert' && '📊 设计核心能力评价体系'}
                            {agent.id === 'material_creator' && '📦 生成数字化学习资源'}
                          </>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* AI Era Core Capabilities */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  🌟 AI时代6大核心能力
                </CardTitle>
                <CardDescription>
                  我们的智能体专注培养学生在AI时代的核心竞争力
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">🤖 人机协作能力</h4>
                    <p className="text-sm text-blue-700">与AI有效协作的理论基础</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-900 mb-2">🧠 元认知与学习力</h4>
                    <p className="text-sm text-green-700">自主学习和认知管理</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-semibold text-purple-900 mb-2">💡 创造性问题解决</h4>
                    <p className="text-sm text-purple-700">批判性和创新思维</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-semibold text-orange-900 mb-2">💻 数字素养与计算思维</h4>
                    <p className="text-sm text-orange-700">数字时代生存技能</p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg">
                    <h4 className="font-semibold text-red-900 mb-2">❤️ 情感智能与人文素养</h4>
                    <p className="text-sm text-red-700">人类独特价值保持</p>
                  </div>
                  <div className="p-4 bg-yellow-50 rounded-lg">
                    <h4 className="font-semibold text-yellow-900 mb-2">🎯 自主学习与项目管理</h4>
                    <p className="text-sm text-yellow-700">终身学习能力</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>设计成果展示</CardTitle>
                <CardDescription>
                  AI智能体协作完成的完整PBL课程设计
                </CardDescription>
              </CardHeader>
              <CardContent>
                {courseData ? (
                  <div className="space-y-6">
                    {Object.entries(courseData).map(([agentId, result]: [string, any]) => {
                      const agent = agents.find(a => a.id === agentId)
                      return (
                        <Card key={agentId} className="border-l-4 border-l-blue-500">
                          <CardHeader>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {agent?.name || agentId}
                              <Badge variant="secondary" className="bg-green-100 text-green-800">
                                已完成
                              </Badge>
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <pre className="text-sm bg-gray-50 p-4 rounded overflow-x-auto whitespace-pre-wrap">
                              {JSON.stringify(result, null, 2)}
                            </pre>
                          </CardContent>
                        </Card>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <p className="text-lg mb-2">📋 设计成果将在此展示</p>
                    <p>请先完成课程设计流程</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p className="mb-2">🌟 让创新教育不再是少数人的特权，而是每个孩子都能享受的权利！</p>
          <p className="text-sm">EduAgents - 推动教育公平的AI助手 • 版本 1.0</p>
        </div>
      </div>
    </div>
  )
}
