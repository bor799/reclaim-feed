/**
 * API Client Tests
 *
 * Tests for the frontend API client including:
 * - Client initialization
 * - CRUD operations
 * - Error handling
 * - Pagination and filtering
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch before importing the module
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import after mocking fetch
import { ApiClient } from '../api';

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:8000');
    mockFetch.mockClear();
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with default base URL', () => {
      const client = new ApiClient();
      expect(client).toBeInstanceOf(ApiClient);
    });

    it('should initialize with custom base URL', () => {
      const client = new ApiClient('http://custom:3000');
      expect(client).toBeInstanceOf(ApiClient);
    });
  });

  describe('Health Check', () => {
    it('should return health status', async () => {
      const mockResponse = {
        status: 'ok',
        version: '1.0.0',
        multi_tenant: true,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.health();

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/health', {
        headers: { 'Content-Type': 'application/json' },
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('User Stats', () => {
    it('should return user statistics', async () => {
      const mockStats = {
        user_id: 'test_user',
        total_notes: 150,
        total_tags: 45,
        days_active: 30,
        annotations_count: 20,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      } as Response);

      const result = await apiClient.getUserStats();

      expect(result).toEqual(mockStats);
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/user/stats', expect.any(Object));
    });
  });

  describe('Feed Items - CRUD', () => {
    it('should get feed items without parameters', async () => {
      const mockFeed = {
        items: [
          {
            id: '1',
            title: 'Test Article',
            url: 'https://test.com',
            source: 'RSS',
            summary: 'Test summary',
            created_at: '2026-03-10T10:00:00',
          },
        ],
        total: 1,
        page: 1,
        limit: 20,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockFeed,
      } as Response);

      const result = await apiClient.getFeedItems();

      expect(result.items).toHaveLength(1);
      expect(result.total).toBe(1);
    });

    it('should get feed items with pagination', async () => {
      const mockFeed = {
        items: [],
        total: 0,
        page: 2,
        limit: 10,
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockFeed,
      } as Response);

      const result = await apiClient.getFeedItems({ page: 2, limit: 10 });

      expect(result.page).toBe(2);
      expect(result.limit).toBe(10);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/feed?page=2&limit=10',
        expect.any(Object)
      );
    });

    it('should get feed items with tag filter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, limit: 20, has_more: false }),
      } as Response);

      await apiClient.getFeedItems({ tags: ['AI', 'Technology'] });

      const callArgs = mockFetch.mock.calls[0];
      expect(callArgs[0]).toContain('tags=AI');
      expect(callArgs[0]).toContain('tags=Technology');
    });

    it('should update feed item', async () => {
      const mockResponse = {
        status: 'ok',
        item: { id: '1', title: 'Updated', is_read: true },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.updateFeedItem('1', { is_read: true });

      expect(result.item.is_read).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/feed/1', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_read: true }),
      });
    });

    it('should mark feed as read', async () => {
      const mockResponse = { status: 'ok', is_read: true };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.markFeedRead('1');

      expect(result.is_read).toBe(true);
    });

    it('should toggle feed like', async () => {
      const mockResponse = { status: 'ok', is_favorited: true };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.toggleFeedLike('1');

      expect(result.is_favorited).toBe(true);
    });
  });

  describe('Sources - CRUD', () => {
    const mockSource = {
      id: 1,
      name: 'Test RSS',
      type: 'RSS',
      url: 'https://example.com/rss',
      enabled: true,
      cron_interval: '6h',
    };

    it('should get all sources', async () => {
      const mockSources = [mockSource];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSources,
      } as Response);

      const result = await apiClient.getSources();

      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Test RSS');
    });

    it('should get sources with filters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      } as Response);

      await apiClient.getSources({ status: 'enabled', tag: 'AI' });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/sources?status=enabled&tag=AI',
        expect.any(Object)
      );
    });

    it('should add new source', async () => {
      const newSource = { ...mockSource, id: 2 };
      const mockResponse = { status: 'ok', source: newSource };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const { id, ...sourceData } = mockSource;
      const result = await apiClient.addSource(sourceData as any);

      expect(result.source.id).toBe(2);
    });

    it('should update source', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.updateSource(1, mockSource as any);

      expect(result.status).toBe('ok');
    });

    it('should delete source', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.deleteSource(1);

      expect(result.status).toBe('ok');
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/sources/1', {
        method: 'DELETE',
      });
    });

    it('should bulk delete sources', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.deleteSourcesBulk([1, 2, 3]);

      expect(result.status).toBe('ok');
    });

    it('should bulk update source status', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.updateSourcesBulkStatus([1, 2], false);

      expect(result.status).toBe('ok');
    });
  });

  describe('Tags Management', () => {
    it('should get all tags', async () => {
      const mockTags = {
        categories: {
          Technology: ['AI', 'Web', 'Mobile'],
          Science: ['Physics', 'Biology'],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTags,
      } as Response);

      const result = await apiClient.getTags();

      expect(result.categories.Technology).toContain('AI');
    });

    it('should update tags', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const tagsData = {
        categories: {
          AI: ['Machine Learning', 'Deep Learning'],
        },
      };

      const result = await apiClient.updateTags(tagsData);

      expect(result.status).toBe('ok');
    });
  });

  describe('Error Handling', () => {
    it('should throw error on 401 unauthorized', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      } as Response);

      await expect(apiClient.getUserStats()).rejects.toThrow('API Error: 401 Unauthorized');
    });

    it('should throw error on 500 server error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response);

      await expect(apiClient.getFeedItems()).rejects.toThrow('API Error: 500 Internal Server Error');
    });

    it('should throw error on network failure', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiClient.health()).rejects.toThrow('Network error');
    });

    it('should throw error with custom message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      } as Response);

      await expect(apiClient.getSources()).rejects.toThrow('API Error: 404 Not Found');
    });
  });

  describe('Settings', () => {
    it('should get providers', async () => {
      const mockProviders = [
        { name: 'OpenAI', api_key: '***', api_base: 'https://api.openai.com' },
        { name: 'Zhipu', api_key: '***', api_base: 'https://open.bigmodel.cn' },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockProviders,
      } as Response);

      const result = await apiClient.getProviders();

      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('OpenAI');
    });

    it('should update providers', async () => {
      const mockResponse = { status: 'ok' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const providers = [
        { name: 'OpenAI', api_key: 'new-key', api_base: 'https://api.openai.com' },
      ];

      const result = await apiClient.updateProviders(providers as any);

      expect(result.status).toBe('ok');
    });

    it('should get bot configuration', async () => {
      const mockBots = {
        telegram_token: '***',
        telegram_chat_id: '123456',
        feishu_webhook: 'https://feishu.webhook',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockBots,
      } as Response);

      const result = await apiClient.getBots();

      expect(result.telegram_chat_id).toBe('123456');
    });

    it('should test connection', async () => {
      const mockResponse = {
        success: true,
        latency_ms: 150,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.testConnection('OpenAI');

      expect(result.success).toBe(true);
      expect(result.latency_ms).toBe(150);
    });
  });

  describe('Pipeline Control', () => {
    it('should run pipeline', async () => {
      const mockResponse = {
        status: 'ok',
        message: 'Pipeline started',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.runPipeline(false);

      expect(result.status).toBe('ok');
    });

    it('should run pipeline in dry-run mode', async () => {
      const mockResponse = {
        status: 'ok',
        message: 'Dry run completed',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.runPipeline(true);

      expect(result.message).toContain('Dry run');
    });
  });

  describe('Quick Extract', () => {
    it('should extract from URLs', async () => {
      const mockResponse = {
        status: 'ok',
        message: 'Extraction queued',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const urls = [
        'https://example.com/article1',
        'https://example.com/article2',
      ];

      const result = await apiClient.quickExtract(urls);

      expect(result.status).toBe('ok');
    });
  });

  describe('Export', () => {
    it('should export feed as CSV', async () => {
      const mockCSV = 'title,url,created_at\nTest1,https://test1.com,2026-03-10\n';

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: async () => mockCSV,
      } as Response);

      const result = await apiClient.exportFeedCsv();

      expect(result).toContain('title,url,created_at');
    });

    it('should export with filters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: async () => 'title,url\nFiltered,https://test.com\n',
      } as Response);

      await apiClient.exportFeedCsv({ tags: ['AI'] });

      const callArgs = mockFetch.mock.calls[0];
      expect(callArgs[0]).toContain('tags=AI');
    });
  });

  describe('Prompt Management', () => {
    it('should get prompt', async () => {
      const mockPrompt = {
        content: 'Test prompt content',
        history: [
          { version: 'v1', created_at: '2026-03-01', preview: 'Old version' },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPrompt,
      } as Response);

      const result = await apiClient.getPrompt('extraction');

      expect(result.content).toBe('Test prompt content');
    });

    it('should update prompt', async () => {
      const mockResponse = { status: 'ok', data: 'Updated' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.updatePrompt('extraction', 'New content');

      expect(result.status).toBe('ok');
    });

    it('should get prompt versions', async () => {
      const mockResponse = {
        status: 'ok',
        versions: [
          { version: 'v1', created_at: '2026-03-01', preview: 'Version 1' },
          { version: 'v2', created_at: '2026-03-05', preview: 'Version 2' },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.getPromptVersions('extraction');

      expect(result.versions).toHaveLength(2);
    });

    it('should restore prompt version', async () => {
      const mockResponse = {
        status: 'ok',
        content: 'Restored content',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.restorePromptVersion('extraction', 'v1');

      expect(result.content).toBe('Restored content');
    });
  });
});
