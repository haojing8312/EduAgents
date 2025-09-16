import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';

// 智能体信息接口
export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  status: 'idle' | 'thinking' | 'collaborating' | 'completed';
  avatar: string;
  color: string;
  contribution?: string;
  lastActivity?: string;
  progress: number;
}

// 协作消息接口
export interface CollaborationMessage {
  id: string;
  agentId: string;
  agentName: string;
  content: string;
  timestamp: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

// 任务信息接口
export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'active' | 'completed';
  assignedAgents: string[];
  progress: number;
  startTime?: string;
  estimatedDuration?: number;
}

// 协作状态接口
export interface CollaborationState {
  // 智能体状态
  agents: AgentInfo[];

  // 当前任务
  currentTask: Task | null;

  // 协作状态
  collaborationStatus: 'idle' | 'active' | 'completed' | 'error';

  // 消息流
  messages: CollaborationMessage[];

  // 总体进度
  overallProgress: number;

  // UI状态
  isWorkspaceVisible: boolean;
  selectedAgentId: string | null;

  // WebSocket连接状态
  isConnected: boolean;
  connectionError: string | null;

  // Actions
  initializeAgents: (agents: AgentInfo[]) => void;
  updateAgentStatus: (agentId: string, status: AgentInfo['status'], progress?: number) => void;
  addMessage: (message: Omit<CollaborationMessage, 'id' | 'timestamp'>) => void;
  startCollaboration: (task: Task) => void;
  completeCollaboration: () => void;
  setWorkspaceVisibility: (visible: boolean) => void;
  selectAgent: (agentId: string | null) => void;
  updateConnectionStatus: (connected: boolean, error?: string) => void;
  clearMessages: () => void;
  reset: () => void;
}

// 默认智能体配置
const defaultAgents: AgentInfo[] = [
  {
    id: 'education_theorist',
    name: '教育理论专家',
    description: '深度分析教育理论，提供PBL方法论指导',
    status: 'idle',
    avatar: '🎓',
    color: '#8B5CF6', // 紫色
    progress: 0,
  },
  {
    id: 'course_architect',
    name: '课程架构师',
    description: '设计完整课程结构和学习路径',
    status: 'idle',
    avatar: '🏗️',
    color: '#F59E0B', // 橙色
    progress: 0,
  },
  {
    id: 'content_designer',
    name: '内容设计师',
    description: '创建丰富的教学内容和学习活动',
    status: 'idle',
    avatar: '✨',
    color: '#10B981', // 绿色
    progress: 0,
  },
  {
    id: 'assessment_expert',
    name: '评估专家',
    description: '制定科学的评价体系和反馈机制',
    status: 'idle',
    avatar: '📊',
    color: '#3B82F6', // 蓝色
    progress: 0,
  },
  {
    id: 'material_creator',
    name: '素材创作者',
    description: '制作精美的教学资源和工具',
    status: 'idle',
    avatar: '🎨',
    color: '#EF4444', // 红色
    progress: 0,
  },
];

export const useCollaborationStore = create<CollaborationState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // 初始状态
      agents: defaultAgents,
      currentTask: null,
      collaborationStatus: 'idle',
      messages: [],
      overallProgress: 0,
      isWorkspaceVisible: false,
      selectedAgentId: null,
      isConnected: false,
      connectionError: null,

      // Actions
      initializeAgents: (agents) => {
        set({ agents });
      },

      updateAgentStatus: (agentId, status, progress = 0) => {
        set((state) => ({
          agents: state.agents.map((agent) =>
            agent.id === agentId
              ? {
                  ...agent,
                  status,
                  progress,
                  lastActivity: new Date().toISOString(),
                }
              : agent
          ),
        }));

        // 计算整体进度
        const { agents } = get();
        const totalProgress = agents.reduce((sum, agent) => sum + agent.progress, 0);
        const overallProgress = Math.round(totalProgress / agents.length);

        set({ overallProgress });

        // 自动添加状态变更消息
        const agent = agents.find(a => a.id === agentId);
        if (agent) {
          const statusMessages = {
            idle: '准备就绪',
            thinking: '开始思考分析',
            collaborating: '正在协作处理',
            completed: '任务完成'
          };

          get().addMessage({
            agentId,
            agentName: agent.name,
            content: statusMessages[status],
            type: status === 'completed' ? 'success' : 'info'
          });
        }
      },

      addMessage: (message) => {
        const newMessage: CollaborationMessage = {
          ...message,
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
        };

        set((state) => ({
          messages: [...state.messages, newMessage].slice(-100), // 只保留最新100条消息
        }));
      },

      startCollaboration: (task) => {
        set({
          currentTask: task,
          collaborationStatus: 'active',
          overallProgress: 0,
          isWorkspaceVisible: true,
        });

        // 重置所有智能体状态
        set((state) => ({
          agents: state.agents.map(agent => ({
            ...agent,
            status: 'idle' as const,
            progress: 0,
          }))
        }));

        get().addMessage({
          agentId: 'system',
          agentName: '系统',
          content: `开始协作处理任务：${task.title}`,
          type: 'info'
        });
      },

      completeCollaboration: () => {
        set({
          collaborationStatus: 'completed',
          overallProgress: 100,
        });

        // 将所有智能体标记为完成
        set((state) => ({
          agents: state.agents.map(agent => ({
            ...agent,
            status: 'completed' as const,
            progress: 100,
          }))
        }));

        get().addMessage({
          agentId: 'system',
          agentName: '系统',
          content: '🎉 协作任务圆满完成！',
          type: 'success'
        });
      },

      setWorkspaceVisibility: (visible) => {
        set({ isWorkspaceVisible: visible });
      },

      selectAgent: (agentId) => {
        set({ selectedAgentId: agentId });
      },

      updateConnectionStatus: (connected, error) => {
        set({
          isConnected: connected,
          connectionError: error || null,
        });

        if (connected) {
          get().addMessage({
            agentId: 'system',
            agentName: '系统',
            content: '🔗 实时连接已建立',
            type: 'success'
          });
        } else if (error) {
          get().addMessage({
            agentId: 'system',
            agentName: '系统',
            content: `⚠️ 连接异常：${error}`,
            type: 'error'
          });
        }
      },

      clearMessages: () => {
        set({ messages: [] });
      },

      reset: () => {
        set({
          currentTask: null,
          collaborationStatus: 'idle',
          messages: [],
          overallProgress: 0,
          isWorkspaceVisible: false,
          selectedAgentId: null,
          agents: defaultAgents,
        });
      },
    })),
    {
      name: 'collaboration-store',
    }
  )
);

// 选择器 hooks
export const useAgents = () => useCollaborationStore(state => state.agents);
export const useCurrentTask = () => useCollaborationStore(state => state.currentTask);
export const useCollaborationStatus = () => useCollaborationStore(state => state.collaborationStatus);
export const useMessages = () => useCollaborationStore(state => state.messages);
export const useOverallProgress = () => useCollaborationStore(state => state.overallProgress);
export const useSelectedAgent = () => useCollaborationStore(state => state.selectedAgentId);
export const useConnectionStatus = () => useCollaborationStore(state => ({
  isConnected: state.isConnected,
  error: state.connectionError
}));