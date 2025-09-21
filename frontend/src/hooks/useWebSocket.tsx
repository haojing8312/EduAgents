'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

export interface AgentStatus {
  id: string
  name: string
  status: 'idle' | 'waiting' | 'working' | 'completed' | 'error'
  progress: number
  task?: string
  result?: any
}

export interface WebSocketMessage {
  type: 'design_started' | 'agent_started' | 'agent_progress' | 'agent_completed' | 'design_completed' | 'error' | 'status'
  message?: string
  agent_id?: string
  agent_name?: string
  task?: string
  progress?: number
  overall_progress?: number
  result?: any
  course_data?: any
  agents?: AgentStatus[]
  error?: string
}

interface UseWebSocketReturn {
  isConnected: boolean
  agents: AgentStatus[]
  overallProgress: number
  courseData: any
  isDesigning: boolean
  error: string | null
  startDesign: (courseRequirement: string) => void
  disconnect: () => void
}

export function useWebSocket(sessionId: string = 'default'): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [agents, setAgents] = useState<AgentStatus[]>([
    { id: 'education_theorist', name: 'AI时代教育理论专家', status: 'idle', progress: 0 },
    { id: 'course_architect', name: 'AI时代课程架构师', status: 'idle', progress: 0 },
    { id: 'content_designer', name: 'AI时代内容设计师', status: 'idle', progress: 0 },
    { id: 'assessment_expert', name: 'AI时代评估专家', status: 'idle', progress: 0 },
    { id: 'material_creator', name: 'AI时代素材创作者', status: 'idle', progress: 0 },
  ])
  const [overallProgress, setOverallProgress] = useState(0)
  const [courseData, setCourseData] = useState<any>(null)
  const [isDesigning, setIsDesigning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    try {
      // 使用当前域名和端口，但可能需要调整端口
      const wsUrl = `ws://localhost:48284/api/v1/ws/course-design/${sessionId}`
      console.log('Connecting to WebSocket:', wsUrl)

      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setError(null)
      }

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          setError('消息解析错误')
        }
      }

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)

        // 自动重连（除非是手动关闭）
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, 3000)
        }
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setError('连接错误，请检查后端服务')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setError('无法建立WebSocket连接')
    }
  }, [sessionId])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'design_started':
        setIsDesigning(true)
        setOverallProgress(0)
        setCourseData(null)
        setError(null)
        if (message.agents) {
          setAgents(message.agents.map(agent => ({
            ...agent,
            status: agent.status as any
          })))
        }
        break

      case 'agent_started':
        if (message.agent_id) {
          setAgents(prev => prev.map(agent =>
            agent.id === message.agent_id
              ? { ...agent, status: 'working', progress: 0, task: message.task }
              : agent.status === 'working'
                ? { ...agent, status: 'completed' }
                : agent
          ))
        }
        break

      case 'agent_progress':
        if (message.agent_id) {
          setAgents(prev => prev.map(agent =>
            agent.id === message.agent_id
              ? { ...agent, progress: message.progress || 0 }
              : agent
          ))
          if (message.overall_progress !== undefined) {
            setOverallProgress(message.overall_progress)
          }
        }
        break

      case 'agent_completed':
        if (message.agent_id) {
          setAgents(prev => prev.map(agent =>
            agent.id === message.agent_id
              ? { ...agent, status: 'completed', progress: 100, result: message.result }
              : agent
          ))
        }
        break

      case 'design_completed':
        setIsDesigning(false)
        setOverallProgress(100)
        setCourseData(message.course_data)
        setAgents(prev => prev.map(agent => ({ ...agent, status: 'completed' })))
        break

      case 'error':
        setError(message.message || '未知错误')
        if (message.agent_id) {
          setAgents(prev => prev.map(agent =>
            agent.id === message.agent_id
              ? { ...agent, status: 'error' }
              : agent
          ))
        }
        break

      default:
        console.log('Unhandled message type:', message.type)
    }
  }, [])

  const startDesign = useCallback((courseRequirement: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = {
        action: 'start_design',
        course_requirement: courseRequirement
      }
      wsRef.current.send(JSON.stringify(message))
    } else {
      setError('WebSocket未连接，请刷新页面重试')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    agents,
    overallProgress,
    courseData,
    isDesigning,
    error,
    startDesign,
    disconnect
  }
}