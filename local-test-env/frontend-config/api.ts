/**
 * 本地测试环境 - API 配置
 *
 * 使用方法：
 * 1. 复制此文件到 frontend/src/services/api.ts
 * 2. 在组件中导入使用
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Source {
  id?: number;
  name: string;
  type: string;
  url: string;
  category?: string;
  enabled: boolean;
}

export interface FeedItem {
  id?: number;
  title: string;
  source: string;
  score?: number;
  summary: string;
  key_insights?: string[];
  timestamp: string;
  tags?: string[];
  url?: string;
}

// ============ API 客户端 ============

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
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

  // 健康检查
  async health(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }

  // 获取信息源
  async getSources(): Promise<Source[]> {
    return this.request('/sources');
  }

  // 获取 Feed
  async getItems(date?: string): Promise<FeedItem[]> {
    const params = date ? `?date=${date}` : '';
    return this.request(`/items${params}`);
  }

  // 获取配置
  async getSettings(): Promise<any> {
    return this.request('/settings');
  }

  // 运行 Pipeline
  async runPipeline(dryRun: boolean = false): Promise<{ status: string; message: string }> {
    return this.request(`/run?dry_run=${dryRun}`, {
      method: 'POST',
    });
  }

  // 导出 JSON
  async exportJson(): Promise<FeedItem[]> {
    return this.request('/export/json');
  }
}

// ============ 导出单例 ============

export const api = new ApiClient();

// ============ 类型导出 ============

export type { Source, FeedItem };
