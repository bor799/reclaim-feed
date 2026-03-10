# Frontend Tests Plan - 100X Knowledge Agent

## 前端测试计划 (Frontend Test Plan)

本文档详细描述前端测试用例规划和实施策略。

---

## 测试架构 (Test Architecture)

```
┌─────────────────────────────────────────────────────────┐
│                    E2E Tests                            │
│              (Playwright / Cypress)                     │
│  完整用户场景: 登录 → 配置 → 使用 → 验证              │
├─────────────────────────────────────────────────────────┤
│              Integration Tests                          │
│          (Vitest + Testing Library)                    │
│  组件 + API + Store 集成测试                            │
├─────────────────────────────────────────────────────────┤
│               Component Tests                           │
│         (@vue/test-utils + Testing Library)            │
│  Vue 组件渲染、交互、事件测试                           │
├─────────────────────────────────────────────────────────┤
│               Unit Tests                                │
│                   (Vitest)                              │
│  工具函数、Composables、API 客户端测试                  │
└─────────────────────────────────────────────────────────┘
```

---

## 1. 单元测试规划 (Unit Tests)

### 1.1 API 客户端测试

**文件**: `src/api/__tests__/`

#### test-client.ts

| 测试用例 | 描述 | 预期结果 |
|---------|------|---------|
| `should_create_client_with_base_url` | 客户端初始化 | baseURL 正确设置 |
| `should_set_auth_token` | 设置认证 token | 请求头包含 Authorization |
| `should_make_get_request` | GET 请求 | 返回响应数据 |
| `should_make_post_request` | POST 请求 | 返回响应数据 |
| `should_handle_401_error` | 认证失败 | 触发登录跳转 |
| `should_handle_network_error` | 网络错误 | 显示错误提示 |
| `should_retry_on_timeout` | 超时重试 | 执行重试逻辑 |

#### test-feed-api.ts

| 端点 | 测试用例 | 描述 |
|------|---------|------|
| GET /feed | `should_fetch_feed_items` | 获取 Feed 列表 |
| GET /feed | `should_fetch_with_pagination` | 分页参数正确传递 |
| GET /feed | `should_fetch_with_filters` | 过滤参数正确传递 |
| GET /feed | `should_handle_empty_response` | 空响应处理 |
| PUT /feed/:id | `should_update_feed_item` | 更新 Feed 项目 |
| PUT /feed/:id/read | `should_mark_as_read` | 标记已读 |
| PUT /feed/:id/like | `should_toggle_favorite` | 切换收藏状态 |
| GET /export/feed | `should_export_csv` | CSV 导出 |

#### test-sources-api.ts

| 端点 | 测试用例 | 描述 |
|------|---------|------|
| GET /sources | `should_fetch_sources` | 获取源列表 |
| POST /sources | `should_create_source` | 创建新源 |
| POST /sources | `should_validate_source_data` | 数据验证 |
| PUT /sources/:id | `should_update_source` | 更新源配置 |
| DELETE /sources/:id | `should_delete_source` | 删除源 |
| DELETE /sources/bulk | `should_bulk_delete` | 批量删除 |

#### test-settings-api.ts

| 端点 | 测试用例 | 描述 |
|------|---------|------|
| GET /settings | `should_fetch_settings` | 获取设置 |
| PUT /settings/providers | `should_update_providers` | 更新 LLM 提供商 |
| POST /system/test-connection | `should_test_connection` | 测试连接 |
| GET /export/json | `should_export_json` | JSON 导出 |

### 1.2 Composables 测试

**文件**: `src/composables/__tests__/`

#### test-useFeed.ts

```typescript
describe('useFeed', () => {
  it('should initialize with empty state')
  it('should fetch feed items')
  it('should handle loading state')
  it('should handle error state')
  it('should refresh feed')
  it('should mark item as read')
  it('should toggle item favorite')
  it('should filter by tags')
  it('should filter by search query')
  it('should paginate results')
  it('should prioritize unread items')
})
```

#### test-useSources.ts

```typescript
describe('useSources', () => {
  it('should initialize with empty state')
  it('should fetch sources')
  it('should create new source')
  it('should update source')
  it('should delete source')
  it('should bulk delete sources')
  it('should bulk update status')
  it('should filter by status')
  it('should filter by tag')
  it('should validate source data')
})
```

#### test-useSettings.ts

```typescript
describe('useSettings', () => {
  it('should initialize with default settings')
  it('should fetch settings')
  it('should update providers')
  it('should update bots')
  it('should update environment')
  it('should test connection')
  it('should export data')
  it('should handle save errors')
})
```

#### test-useAuth.ts

```typescript
describe('useAuth', () => {
  it('should initialize with unauthenticated state')
  it('should login with valid credentials')
  it('should reject invalid credentials')
  it('should store auth token')
  it('should logout')
  it('should refresh token')
  it('should handle token expiry')
})
```

### 1.3 工具函数测试

**文件**: `src/utils/__tests__/`

#### test-formatters.ts

```typescript
describe('formatters', () => {
  describe('formatDate', () => {
    it('should format ISO date string')
    it('should handle invalid date')
    it('should use locale')
  })

  describe('truncateText', () => {
    it('should truncate long text')
    it('should not truncate short text')
    it('should add ellipsis')
  })

  describe('formatQualityScore', () => {
    it('should return color for high score')
    it('should return color for medium score')
    it('should return color for low score')
  })
})
```

#### test-validators.ts

```typescript
describe('validators', () => {
  describe('validateUrl', () => {
    it('should accept valid URLs')
    it('should reject invalid URLs')
    it('should accept RSS URLs')
    it('should accept Twitter URLs')
  })

  describe('validateSourceConfig', () => {
    it('should validate required fields')
    it('should validate cron interval')
    it('should validate source type')
  })
})
```

---

## 2. 组件测试规划 (Component Tests)

### 2.1 核心组件

#### FeedList.vue

```typescript
describe('FeedList', () => {
  it('should render empty state when no items')
  it('should render feed items')
  it('should display item title')
  it('should display item source')
  it('should display quality score badge')
  it('should show read/unread indicator')
  it('should show favorite indicator')
  it('should emit like event on like click')
  it('should emit read event on item click')
  it('should support infinite scroll')
  it('should show loading indicator')
  it('should show error message')
})
```

#### FeedItem.vue

```typescript
describe('FeedItem', () => {
  it('should render item content')
  it('should display tags')
  it('should display category')
  it('should show annotation if exists')
  it('should emit like event')
  it('should emit read event')
  it('should emit expand event')
  it('should apply read class when is_read')
  it('should apply favorite class when is_favorited')
})
```

#### FilterBar.vue

```typescript
describe('FilterBar', () => {
  it('should render search input')
  it('should render tag filter')
  it('should render date filter')
  it('should render status filter')
  it('should emit search event')
  it('should emit filter change event')
  it('should clear all filters')
})
```

#### SourceForm.vue

```typescript
describe('SourceForm', () => {
  it('should render form fields')
  it('should validate required fields')
  it('should validate URL format')
  it('should show source type options')
  it('should show cron interval options')
  it('should emit submit event with data')
  it('should emit cancel event')
  it('should populate form for edit mode')
})
```

#### SourceList.vue

```typescript
describe('SourceList', () => {
  it('should render source items')
  it('should show source status')
  it('should show source type icon')
  it('should enable/disable source toggle')
  it('should emit edit event')
  it('should emit delete event')
  it('should support bulk selection')
  it('should show empty state')
})
```

#### SettingsPanel.vue

```typescript
describe('SettingsPanel', () => {
  it('should render settings tabs')
  it('should show providers section')
  it('should show bots section')
  it('should show environment section')
  it('should save settings')
  it('should test connection')
  it('should show save success message')
})
```

#### ProviderConfig.vue

```typescript
describe('ProviderConfig', () => {
  it('should render provider fields')
  it('should add new provider')
  it('should remove provider')
  it('should update provider fields')
  it('should test provider connection')
  it('should show connection status')
})
```

### 2.2 布局组件

#### AppLayout.vue

```typescript
describe('AppLayout', () => {
  it('should render header')
  it('should render navigation')
  it('should render main content')
  it('should render footer')
  it('should show loading overlay')
  it('should show error toast')
})
```

#### Navigation.vue

```typescript
describe('Navigation', () => {
  it('should render nav items')
  it('should highlight active route')
  it('should navigate on click')
  it('should show badge for unread count')
})
```

---

## 3. 集成测试规划 (Integration Tests)

**文件**: `tests/integration/`

### 3.1 Feed 工作流

```typescript
describe('Feed Workflow', () => {
  it('should load and display feed', async () => {
    // 1. 组件挂载
    // 2. API 调用
    // 3. 数据渲染
    // 4. 用户交互
  })

  it('should filter and refresh feed', async () => {
    // 1. 应用过滤器
    // 2. 验证过滤结果
    // 3. 刷新数据
    // 4. 验证刷新后状态
  })

  it('should mark items as read', async () => {
    // 1. 点击项目
    // 2. API 调用
    // 3. 状态更新
    // 4. UI 反馈
  })
})
```

### 3.2 Sources 工作流

```typescript
describe('Sources Workflow', () => {
  it('should create and display new source', async () => {
    // 1. 打开表单
    // 2. 填写数据
    // 3. 提交
    // 4. 验证创建
  })

  it('should update source status', async () => {
    // 1. 切换状态
    // 2. API 调用
    // 3. 验证更新
  })
})
```

---

## 4. E2E 测试规划 (End-to-End Tests)

**文件**: `tests/e2e/`
**工具**: Playwright

### 4.1 用户场景

#### 场景 1: 首次使用

```typescript
test('first time user flow', async ({ page }) => {
  // 1. 访问首页
  await page.goto('/')

  // 2. 应该看到空状态
  await expect(page.locator('[data-testid="empty-state"]')).toBeVisible()

  // 3. 点击添加源
  await page.click('[data-testid="add-source"]')

  // 4. 填写表单
  await page.fill('[name="url"]', 'https://example.com/rss')
  await page.fill('[name="name"]', 'Test RSS')

  // 5. 提交
  await page.click('[data-testid="submit"]')

  // 6. 验证添加成功
  await expect(page.locator('[data-testid="source-item"]')).toContainText('Test RSS')
})
```

#### 场景 2: 浏览和操作 Feed

```typescript
test('browse and interact with feed', async ({ page }) => {
  // 1. 访问 Feed 页面
  await page.goto('/feed')

  // 2. 等待加载
  await page.waitForSelector('[data-testid="feed-item"]')

  // 3. 点击第一个项目
  await page.click('[data-testid="feed-item"]:first-child')

  // 4. 验证详情展开
  await expect(page.locator('[data-testid="feed-detail"]')).toBeVisible()

  // 5. 点击收藏
  await page.click('[data-testid="like-button"]')

  // 6. 验证收藏状态
  await expect(page.locator('[data-testid="like-button"]')).toHaveClass(/favorited/)
})
```

#### 场景 3: 配置和设置

```typescript
test('configure llm provider', async ({ page }) => {
  // 1. 进入设置页面
  await page.goto('/settings')

  // 2. 选择 Providers 标签
  await page.click('[data-testid="tab-providers"]')

  // 3. 点击添加提供商
  await page.click('[data-testid="add-provider"]')

  // 4. 填写配置
  await page.fill('[name="name"]', 'OpenAI')
  await page.fill('[name="api_key"]', 'sk-test')
  await page.fill('[name="api_base"]', 'https://api.openai.com')

  // 5. 测试连接
  await page.click('[data-testid="test-connection"]')

  // 6. 验证连接状态
  await expect(page.locator('[data-testid="connection-status"]')).toContainText('成功')
})
```

---

## 5. 测试配置文件

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/__tests__/**/*.{test,spec}.{ts,tsx}', 'tests/unit/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/dist/**',
        '.vite/',
      ],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

### tests/setup.ts

```typescript
import { vi } from 'vitest'
import '@testing-library/jest-dom'

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
} as any

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
```

---

## 6. 测试实施优先级

### Phase 1: 基础设施 + 核心 API (Week 1-2)

- [ ] 配置 Vitest
- [ ] API 客户端测试
- [ ] 核心 Composables 测试
- [ ] 工具函数测试

**目标**: 50% 覆盖率

### Phase 2: 核心组件测试 (Week 3-4)

- [ ] FeedList 组件
- [ ] FeedItem 组件
- [ ] FilterBar 组件
- [ ] SourceForm 组件

**目标**: 65% 覆盖率

### Phase 3: 集成测试 (Week 5-6)

- [ ] Feed 工作流测试
- [ ] Sources 工作流测试
- [ ] Settings 工作流测试

**目标**: 70% 覆盖率

### Phase 4: E2E 测试 (可选)

- [ ] Playwright 配置
- [ ] 核心用户场景

---

## 7. 测试命令 (Test Commands)

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run",
    "test:coverage": "vitest --coverage",
    "test:watch": "vitest --watch"
  }
}
```

---

**最后更新**: 2026-03-10
