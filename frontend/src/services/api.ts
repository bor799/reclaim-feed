const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

import { Source } from '../types';

// ============ API 客户端 ============

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // 兼容全路径与相对路径
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // 暴露通用的 client 用于任意 REST 操作，返回包含 {data, status} 格式兼容 axios 的习惯
  public client = {
    get: async <T = any>(url: string) => {
      const data = await this.request<T>(url);
      return { data, status: 200 };
    },
    post: async <T = any>(url: string, body?: any) => {
      const data = await this.request<T>(url, { method: 'POST', body: body ? JSON.stringify(body) : undefined });
      return { data, status: 200 };
    },
    put: async <T = any>(url: string, body?: any) => {
      const data = await this.request<T>(url, { method: 'PUT', body: body ? JSON.stringify(body) : undefined });
      return { data, status: 200 };
    },
    delete: async <T = any>(url: string) => {
      const data = await this.request<T>(url, { method: 'DELETE' });
      return { data, status: 200 };
    }
  };

  // 健康检查
  async health(): Promise<{ status: string; version: string }> {
    return this.request('/api/v1/health');
  }

  // 获取用户统计
  async getUserStats(): Promise<any> {
    return this.request('/api/v1/user/stats');
  }

  // 获取标签分类
  async getTags(): Promise<any> {
    return this.request('/api/v1/tags');
  }

  // 更新标签分类
  async updateTags(data: any): Promise<any> {
    return this.request('/api/v1/tags', { method: 'PUT', body: JSON.stringify(data) });
  }



  // 添加信息源
  async addSource(source: Omit<Source, 'id'>): Promise<any> {
    return this.request('/api/v1/sources', { method: 'POST', body: JSON.stringify(source) });
  }

  // 更新信息源
  async updateSource(id: number, source: Source): Promise<any> {
    return this.request(`/api/v1/sources/${id}`, { method: 'PUT', body: JSON.stringify(source) });
  }

  // 删除信息源
  async deleteSource(id: number): Promise<any> {
    return this.request(`/api/v1/sources/${id}`, { method: 'DELETE' });
  }

  // 获取Feed Items
  async getFeedItems(params?: any): Promise<any> {
    const q = params?.date ? `?date=${params.date}` : '';
    // 如果后端是 /api/v1/feed 就用这，我们假设兼容
    return this.request(`/api/v1/feed${q}`);
  }

  // 获取配置
  async getProviderSettings(): Promise<any> {
    return this.request('/api/v1/settings/providers');
  }
  async updateProviderSettings(data: any): Promise<any> {
    return this.request('/api/v1/settings/providers', { method: 'PUT', body: JSON.stringify(data) });
  }
  async getEnvironmentSettings(): Promise<any> {
    return this.request('/api/v1/settings/environment');
  }
  async updateEnvironmentSettings(data: any): Promise<any> {
    return this.request('/api/v1/settings/environment', { method: 'PUT', body: JSON.stringify(data) });
  }
  // Feed Methods
  async updateFeedItem(id: string, data: any): Promise<any> {
    return this.request(`/api/v1/feed/${id}`, { method: 'PUT', body: JSON.stringify(data) });
  }

  async markFeedRead(id: string): Promise<any> {
    return this.request(`/api/v1/feed/${id}/read`, { method: 'PUT' });
  }

  async toggleFeedLike(id: string): Promise<any> {
    return this.request(`/api/v1/feed/${id}/like`, { method: 'PUT' });
  }

  // Bulk Source methods
  async deleteSourcesBulk(ids: number[]): Promise<any> {
    return this.request('/api/v1/sources/bulk', { method: 'DELETE', body: JSON.stringify({ ids }) });
  }

  async updateSourcesBulkStatus(ids: number[], enabled: boolean): Promise<any> {
    return this.request('/api/v1/sources/bulk/status', { method: 'PUT', body: JSON.stringify({ ids, enabled }) });
  }

  // Get Sources with params
  async getSources(params?: any): Promise<Source[]> {
    const q = params ? `?${new URLSearchParams(params).toString()}` : '';
    return this.request(`/api/v1/sources${q}`);
  }

  // Generic Settings methods tested
  async getProviders(): Promise<any> {
    return this.getProviderSettings();
  }
  async updateProviders(data: any): Promise<any> {
    return this.updateProviderSettings(data);
  }
  async getBots(): Promise<any> {
    return this.request('/api/v1/settings/bots');
  }
  async updateBots(data: any): Promise<any> {
    return this.request('/api/v1/settings/bots', { method: 'PUT', body: JSON.stringify(data) });
  }
  async testConnection(provider: string): Promise<any> {
    return this.request(`/api/v1/system/test-connection`, { method: 'POST', body: JSON.stringify({ provider }) });
  }

  // Quick Extract
  async quickExtract(urls: string[]): Promise<any> {
    return this.request('/api/v1/extract/quick', { method: 'POST', body: JSON.stringify({ urls }) });
  }

  // 导出CSV
  async exportFeedCsv(params?: any): Promise<Blob> {
    const q = params?.tags ? `?tags=${params.tags.join(',')}` : '';
    return this.request(`/api/v1/export/feed${q}`);
  }

  // 获取Prompt
  async getPrompt(stage: string): Promise<any> {
    return this.request(`/api/v1/prompts/${stage}`);
  }

  // 更新Prompt
  async updatePrompt(stage: string, content: string, version?: string): Promise<any> {
    return this.request(`/api/v1/prompts/${stage}`, { method: 'PUT', body: JSON.stringify({ content, version }) });
  }

  // 获取Prompt历史版本
  async getPromptVersions(stage: string): Promise<any> {
    return this.request(`/api/v1/prompts/${stage}/versions`);
  }

  // 恢复Prompt往期版本
  async restorePromptVersion(stage: string, versionId: string): Promise<any> {
    return this.request(`/api/v1/prompts/${stage}/versions`, { method: 'POST', body: JSON.stringify({ version: versionId }) });
  }

  // 运行 Pipeline
  async runPipeline(dryRun: boolean = false): Promise<{ status: string; message: string }> {
    return this.request(`/api/v1/run?dry_run=${dryRun}`, { method: 'POST' });
  }
}

// ============ 导出单例 ============

export const api = new ApiClient();


