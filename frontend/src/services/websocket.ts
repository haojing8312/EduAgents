import { io, Socket } from 'socket.io-client';
import { useCollaborationStore } from '@/stores/collaborationStore';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;

  constructor() {
    this.connect();
  }

  private connect() {
    try {
      const serverUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'http://localhost:48280';

      this.socket = io(serverUrl, {
        transports: ['websocket'],
        upgrade: true,
        rememberUpgrade: true,
        timeout: 10000,
      });

      this.setupEventListeners();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.handleConnectionError();
    }
  }

  private setupEventListeners() {
    if (!this.socket) return;

    // 连接成功
    this.socket.on('connect', () => {
      console.log('WebSocket connected successfully');
      this.reconnectAttempts = 0;
      useCollaborationStore.getState().updateConnectionStatus(true);

      this.socket?.emit('join-collaboration-room', {
        userId: 'user_' + Date.now(),
        timestamp: new Date().toISOString()
      });
    });

    // 连接断开
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      useCollaborationStore.getState().updateConnectionStatus(false, `连接断开: ${reason}`);

      if (reason === 'io server disconnect') {
        // 服务器主动断开，需要手动重连
        this.reconnect();
      }
    });

    // 连接错误
    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.handleConnectionError();
    });

    // 智能体状态更新
    this.socket.on('agent-status-update', (data) => {
      console.log('Received agent status update:', data);
      const { agentId, status, progress, contribution } = data;

      const store = useCollaborationStore.getState();
      store.updateAgentStatus(agentId, status, progress);

      if (contribution) {
        // 更新智能体贡献内容
        const agents = store.agents.map(agent =>
          agent.id === agentId
            ? { ...agent, contribution }
            : agent
        );
        store.initializeAgents(agents);
      }
    });

    // 协作消息
    this.socket.on('collaboration-message', (message) => {
      console.log('Received collaboration message:', message);
      useCollaborationStore.getState().addMessage({
        agentId: message.agentId,
        agentName: message.agentName,
        content: message.content,
        type: message.type || 'info'
      });
    });

    // 任务进度更新
    this.socket.on('task-progress-update', (data) => {
      console.log('Received task progress update:', data);
      const { taskId, progress, status } = data;

      const store = useCollaborationStore.getState();
      if (store.currentTask?.id === taskId) {
        // 更新任务状态
        const updatedTask = {
          ...store.currentTask,
          progress,
          status
        };
        store.startCollaboration(updatedTask);
      }
    });

    // 协作完成
    this.socket.on('collaboration-completed', (data) => {
      console.log('Collaboration completed:', data);
      useCollaborationStore.getState().completeCollaboration();
    });

    // 系统通知
    this.socket.on('system-notification', (notification) => {
      console.log('System notification:', notification);
      useCollaborationStore.getState().addMessage({
        agentId: 'system',
        agentName: '系统',
        content: notification.message,
        type: notification.type || 'info'
      });
    });
  }

  private handleConnectionError() {
    useCollaborationStore.getState().updateConnectionStatus(false, '连接失败');

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnect();
    } else {
      console.error('Max reconnection attempts reached');
      useCollaborationStore.getState().addMessage({
        agentId: 'system',
        agentName: '系统',
        content: `WebSocket连接失败，已尝试重连${this.maxReconnectAttempts}次`,
        type: 'error'
      });
    }
  }

  private reconnect() {
    this.reconnectAttempts++;

    setTimeout(() => {
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      useCollaborationStore.getState().addMessage({
        agentId: 'system',
        agentName: '系统',
        content: `正在重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`,
        type: 'warning'
      });
      this.connect();
    }, this.reconnectInterval * this.reconnectAttempts);
  }

  // 发送消息到服务器
  public emit(event: string, data: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, cannot emit event:', event);
    }
  }

  // 启动课程设计协作
  public startCourseDesign(requirements: any) {
    this.emit('start-course-design', {
      requirements,
      timestamp: new Date().toISOString(),
      userId: 'user_' + Date.now()
    });
  }

  // 启动演示协作
  public startDemoCollaboration() {
    this.emit('start-demo-collaboration', {
      timestamp: new Date().toISOString(),
      userId: 'user_' + Date.now()
    });
  }

  // 模拟智能体进度更新
  public simulateAgentProgress(agentId: string, progress: number) {
    this.emit('simulate-agent-progress', {
      agentId,
      progress,
      timestamp: new Date().toISOString()
    });
  }

  // 断开连接
  public disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // 获取连接状态
  public isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

// 创建单例实例
export const webSocketService = new WebSocketService();

// React Hook for WebSocket integration
export const useWebSocket = () => {
  return {
    emit: webSocketService.emit.bind(webSocketService),
    startCourseDesign: webSocketService.startCourseDesign.bind(webSocketService),
    startDemoCollaboration: webSocketService.startDemoCollaboration.bind(webSocketService),
    simulateAgentProgress: webSocketService.simulateAgentProgress.bind(webSocketService),
    isConnected: webSocketService.isConnected.bind(webSocketService)
  };
};

export default webSocketService;