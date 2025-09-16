/**
 * API客户端服务
 * 处理与后端API的所有通信
 */

interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status?: string;
  error?: string;
}

interface AgentInfo {
  id: string;
  name: string;
  description: string;
}

interface AgentsResponse {
  agents: AgentInfo[];
  collaboration_modes: string[];
  status: string;
}

interface HealthStatus {
  status: string;
  timestamp: string;
  services: Record<string, string>;
  config: Record<string, string>;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:48280/api/v1';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // 健康检查
  async healthCheck(): Promise<HealthStatus> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:48280';
    return this.request<HealthStatus>(`${apiUrl}/health`);
  }

  // 获取系统信息
  async getSystemInfo(): Promise<ApiResponse> {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:48280';
    return this.request<ApiResponse>(`${apiUrl}/`);
  }

  // 获取智能体列表
  async getAgents(): Promise<AgentsResponse> {
    return this.request<AgentsResponse>('/agents');
  }

  // 创建课程设计会话
  async createCourseDesignSession(requirements: any): Promise<ApiResponse> {
    return this.request<ApiResponse>('/course/design', {
      method: 'POST',
      body: JSON.stringify(requirements),
    });
  }
}

// 创建API客户端实例
export const apiClient = new ApiClient();

// 导出类型
export type { ApiResponse, AgentInfo, AgentsResponse, HealthStatus };