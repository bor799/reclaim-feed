# Frontend Testing - 100X Knowledge Agent

## 概述 (Overview)

本文档描述 100X Knowledge Agent 前端的测试策略和计划。

**当前状态**: 前端暂无测试实现
**推荐框架**: Vitest + Testing Library
**技术栈**: Vue 3 + TypeScript + Vite

---

## 测试金字塔 (Testing Pyramid)

```
        ┌─────────────┐
       /   E2E Tests   \         ← Playwright/Cypress (少量)
      /─────────────────\
     /  Integration Tests \      ← Vitest + Testing Library (中等)
    /───────────────────────\
   /    Unit Tests            \    ← Vitest (大量)
  /─────────────────────────────\
```

---

## 推荐测试工具 (Recommended Tools)

### 核心框架

| 工具 | 用途 | 说明 |
|------|------|------|
| **Vitest** | 测试运行器 | Vite 原生支持，速度快 |
| **@vue/test-utils** | Vue 组件测试 | 官方组件测试工具 |
| **@testing-library/vue** | 用户行为测试 | 更接近真实用户操作 |
| **@testing-library/jest-dom** | DOM 断言 | 丰富的 DOM 匹配器 |

### E2E 测试

| 工具 | 用途 | 说明 |
|------|------|------|
| **Playwright** | E2E 测试 | 跨浏览器，支持多语言 |
| **Cypress** | E2E 测试 | 开发者友好，实时重载 |

### 覆盖率

| 工具 | 用途 | 说明 |
|------|------|------|
| **c8** / **vitest/coverage-v8** | 覆盖率报告 | V8 原生支持，速度快 |
| **istanbul** | 覆盖率报告 | 传统方案 |

---

## 测试目录结构 (Test Directory Structure)

```
frontend/
├── src/
│   ├── components/          # 组件
│   │   └── __tests__/       # 组件测试
│   ├── composables/         # Composables
│   │   └── __tests__/       # Composable 测试
│   ├── api/                 # API 客户端
│   │   └── __tests__/       # API 测试
│   ├── stores/              # Pinia Stores
│   │   └── __tests__/       # Store 测试
│   └── utils/               # 工具函数
│       └── __tests__/       # 工具函数测试
├── tests/
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── e2e/                 # E2E 测试
└── vitest.config.ts         # Vitest 配置
```

---

## 测试计划 (Test Plan)

### Phase 1: 设置基础设施 (Infrastructure Setup)

1. **安装依赖**
   ```bash
   npm install -D vitest @vue/test-utils @testing-library/vue @testing-library/jest-dom jsdom
   ```

2. **配置 Vitest**
   ```typescript
   // vitest.config.ts
   import { defineConfig } from 'vitest/config'
   import vue from '@vitejs/plugin-vue'

   export default defineConfig({
     plugins: [vue()],
     test: {
       globals: true,
       environment: 'jsdom',
       setupFiles: './tests/setup.ts',
       coverage: {
         provider: 'v8',
         reporter: ['text', 'html', 'json'],
         exclude: [...]
       }
     }
   })
   ```

3. **添加测试脚本**
   ```json
   {
     "scripts": {
       "test": "vitest",
       "test:ui": "vitest --ui",
       "test:coverage": "vitest --coverage"
     }
   }
   ```

### Phase 2: 单元测试 (Unit Tests)

#### API 客户端测试

**优先级**: 高

**测试内容**:
- API 请求构造
- 响应处理
- 错误处理
- 认证 token 处理

**示例**:
```typescript
// src/api/__tests__/client.test.ts
import { describe, it, expect, vi } from 'vitest'
import { apiClient } from '../client'

describe('apiClient', () => {
  it('should make GET request', async () => {
    const response = await apiClient.get('/api/v1/feed')
    expect(response.status).toBe(200)
  })

  it('should handle errors', async () => {
    await expect(apiClient.get('/invalid')).rejects.toThrow()
  })
})
```

#### Composables 测试

**优先级**: 高

**测试内容**:
- useFeed 状态管理
- useSources CRUD 操作
- useSettings 配置管理
- useAuth 认证状态

**示例**:
```typescript
// src/composables/__tests__/useFeed.test.ts
import { describe, it, expect, vi } from 'vitest'
import { useFeed } from '../useFeed'

describe('useFeed', () => {
  it('should fetch feed items', async () => {
    const { items, fetchFeed } = useFeed()
    await fetchFeed()
    expect(items.value.length).toBeGreaterThan(0)
  })
})
```

#### 工具函数测试

**优先级**: 中

**测试内容**:
- 日期格式化
- 文本截断
- URL 解析
- 数据验证

#### Pinia Store 测试

**优先级**: 中

**测试内容**:
- Store 初始化
- Actions 和 Getters
- 状态更新

### Phase 3: 组件测试 (Component Tests)

#### 核心组件测试

**优先级**: 高

| 组件 | 测试重点 |
|------|---------|
| FeedList | 列表渲染、分页、过滤 |
| FeedItem | 项目显示、操作按钮 |
| SourceForm | 表单验证、提交 |
| SettingsPanel | 配置更新 |
| FilterBar | 过滤器交互 |

**示例**:
```typescript
// src/components/__tests__/FeedList.test.ts
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/vue'
import FeedList from '../FeedList.vue'

describe('FeedList', () => {
  it('should render feed items', () => {
    const items = [{ id: 1, title: 'Test', url: 'https://example.com' }]
    render(FeedList, { props: { items } })
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should emit like event', async () => {
    const { emitted } = render(FeedList, { props: { items: [] } })
    // ... 测试事件发射
  })
})
```

### Phase 4: 集成测试 (Integration Tests)

**优先级**: 中

**测试内容**:
- 组件间交互
- API + Store + 组件集成
- 路由导航

### Phase 5: E2E 测试 (End-to-End Tests)

**优先级**: 低（可选）

**测试内容**:
- 用户登录流程
- 完整 CRUD 操作
- 跨页面导航

**示例 (Playwright)**:
```typescript
// tests/e2e/feed.spec.ts
import { test, expect } from '@playwright/test'

test('feed workflow', async ({ page }) => {
  await page.goto('/')
  await page.click('[data-testid="refresh-feed"]')
  await expect(page.locator('.feed-item')).toBeVisible()
})
```

---

## API 客户端测试用例规划 (API Client Test Cases)

### GET /api/v1/feed

| 测试用例 | 描述 | 预期结果 |
|---------|------|---------|
| 基础请求 | 获取 Feed 数据 | 返回 200 + items 数组 |
| 带参数请求 | 添加查询参数 | 返回过滤后的数据 |
| 空数据 | API 返回空 | 返回空数组 |
| 错误处理 | 网络错误 | 抛出异常 |

### POST /api/v1/sources

| 测试用例 | 描述 | 预期结果 |
|---------|------|---------|
| 添加源 | 提交新源配置 | 返回 200 + 成功状态 |
| 验证错误 | 提交无效数据 | 返回 422 验证错误 |
| 重复添加 | 添加重复源 | 返回适当错误 |

### PUT /api/v1/feed/{id}/like

| 测试用例 | 描述 | 预期结果 |
|---------|------|---------|
| 切换收藏 | 切换收藏状态 | 返回更新后的状态 |
| 无效 ID | 不存在项目 ID | 返回 404 |

---

## 覆盖率目标 (Coverage Goals)

| 模块 | 目标覆盖率 | 优先级 |
|------|-----------|--------|
| API 客户端 | 80%+ | 高 |
| Composables | 80%+ | 高 |
| 工具函数 | 90%+ | 中 |
| 组件 | 70%+ | 中 |
| Stores | 70%+ | 中 |
| 路由 | 50%+ | 低 |

**总体目标**: 70%+

---

## 测试最佳实践 (Testing Best Practices)

### 1. 遵循 AAA 模式

```typescript
it('should add item to cart', () => {
  // Arrange - 准备
  const cart = new ShoppingCart()
  const item = { id: 1, price: 100 }

  // Act - 执行
  cart.addItem(item)

  // Assert - 断言
  expect(cart.total).toBe(100)
})
```

### 2. 测试用户行为，而非实现细节

```typescript
// ❌ 不好
expect(wrapper.vm.items).toHaveLength(5)

// ✅ 好
expect(screen.getAllByTestId('feed-item')).toHaveLength(5)
```

### 3. 使用描述性测试名称

```typescript
// ❌ 不好
it('works')

// ✅ 好
it('should display error message when API request fails')
```

### 4. Mock 外部依赖

```typescript
vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(() => Promise.resolve({ data: [] }))
  }
}))
```

---

## 持续集成 (Continuous Integration)

### GitHub Actions 配置示例

```yaml
name: Test Frontend

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
```

---

## 执行步骤 (Implementation Steps)

### Step 1: 安装测试框架
```bash
cd frontend
npm install -D vitest @vue/test-utils @testing-library/vue @testing-library/jest-dom jsdom @vitest/ui vitest-coverage-v8
```

### Step 2: 创建 Vitest 配置
```bash
# 创建 vitest.config.ts
# 创建 tests/setup.ts
```

### Step 3: 添加测试脚本
```bash
# 在 package.json 添加测试脚本
```

### Step 4: 编写第一批测试
- API 客户端测试
- 核心 Composable 测试
- 工具函数测试

### Step 5: 设置 CI/CD
- GitHub Actions 工作流
- 覆盖率报告集成

---

## 参考资源 (References)

- [Vitest 文档](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library](https://testing-library.com/)
- [Vitest UI](https://vitest.dev/guide/ui.html)

---

## Checkout 测试文档 (Checkout Tests Documentation)

### 概述

Checkout 测试覆盖内容签出/审核功能的所有核心场景，包括单个项目签出、批量操作、签出历史记录、错误处理和边界情况。

**测试文件**: `src/services/__tests__/checkout.test.ts`
**测试用例数量**: 21 个
**代码行数**: 533 行
**状态**: ✅ 全部通过

### 测试覆盖的 API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/feed/{id}/checkout` | PUT | 签出项目 |
| `/api/v1/feed/{id}/checkout` | GET | 获取签出状态 |
| `/api/v1/feed/{id}/checkout` | DELETE | 释放签出 |
| `/api/v1/feed/batch/checkout` | POST | 批量签出 |
| `/api/v1/feed/batch/checkout` | DELETE | 批量释放签出 |
| `/api/v1/feed/{id}/checkout/history` | GET | 获取项目签出历史 |
| `/api/v1/user/checkout/history` | GET | 获取用户签出历史 |
| `/api/v1/feed/checkout` | GET | 获取所有签出项目 |
| `/api/v1/feed/{id}/checkout/notes` | PUT | 更新签出备注 |
| `/api/v1/stats/checkout` | GET | 获取签出统计 |
| `/api/v1/feed/{id}/checkout/timeout` | POST | 处理超时签出 |

### 测试用例详细说明

#### 1. Item Checkout (单项目签出) - 3 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should checkout a single item for review` | PUT `/api/v1/feed/{id}/checkout` | 签出成功，返回 `checked_out=true` |
| `should return checkout status for an item` | GET `/api/v1/feed/{id}/checkout` | 返回签出状态和签出人信息 |
| `should release checkout on an item` | DELETE `/api/v1/feed/{id}/checkout` | 释放签出成功，`checked_out=false` |

#### 2. Batch Checkout (批量签出) - 2 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should checkout multiple items at once` | POST `/api/v1/feed/batch/checkout` | 批量签出多个项目，所有项目状态更新 |
| `should release checkout on multiple items` | DELETE `/api/v1/feed/batch/checkout` | 批量释放签出，返回释放数量 |

#### 3. Checkout History (签出历史) - 2 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should get checkout history for an item` | GET `/api/v1/feed/{id}/checkout/history` | 返回项目的签出历史记录（用户、时间） |
| `should get user checkout history` | GET `/api/v1/user/checkout/history` | 返回用户的所有签出记录（包括已释放） |

#### 4. Checkout Filtering (签出过滤) - 2 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should get all checked out items` | GET `/api/v1/feed/checkout` | 返回所有已签出的项目列表 |
| `should get items checked out by current user` | GET `/api/v1/feed/checkout?user={userId}` | 按用户过滤签出项目 |

#### 5. Error Handling (错误处理) - 3 个测试

| 测试名称 | 场景 | HTTP 状态码 |
|---------|------|-------------|
| `should handle checkout of already checked out item` | 项目已被他人签出 | 409 Conflict |
| `should handle release checkout by non-owner` | 无权限释放签出 | 403 Forbidden |
| `should handle checkout of non-existent item` | 项目不存在 | 404 Not Found |

#### 6. Checkout with Notes (带备注签出) - 2 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should checkout item with review notes` | PUT `/api/v1/feed/{id}/checkout` | 签出时可以添加备注信息 |
| `should update checkout notes` | PUT `/api/v1/feed/{id}/checkout/notes` | 更新已有的签出备注 |

#### 7. Checkout Statistics (签出统计) - 1 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should get checkout statistics` | GET `/api/v1/stats/checkout` | 返回统计数据（总数、我的、超时、平均时长） |

#### 8. Coverage Edge Cases (边界情况) - 5 个测试

| 测试名称 | 场景 | 验证内容 |
|---------|------|----------|
| `should handle empty checkout list` | 空签出列表 | 正确返回空数组 |
| `should handle special characters in checkout notes` | 特殊字符（`<script>`, `&`） | 正确处理和存储 |
| `should handle concurrent checkout attempts` | 并发签出冲突 | 正确处理 409 冲突 |
| `should handle very long checkout notes` | 超长备注（10000字符） | 正确处理长文本 |
| `should handle null checkout notes` | null 值备注 | 正确处理 null |

#### 9. Checkout Timeout (超时处理) - 1 个测试

| 测试名称 | API 端点 | 验证内容 |
|---------|----------|----------|
| `should handle auto-release after timeout` | POST `/api/v1/feed/{id}/checkout/timeout` | 超时后自动释放签出 |

### 测试代码结构

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Checkout Functionality', () => {
  // Helper function
  async function makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T>

  // 9 个测试分组
  describe('Item Checkout', () => { /* 3 tests */ });
  describe('Batch Checkout', () => { /* 2 tests */ });
  describe('Checkout History', () => { /* 2 tests */ });
  describe('Checkout Filtering', () => { /* 2 tests */ });
  describe('Checkout Error Handling', () => { /* 3 tests */ });
  describe('Checkout with Notes', () => { /* 2 tests */ });
  describe('Checkout Statistics', () => { /* 1 test */ });
  describe('Checkout Coverage Edge Cases', () => { /* 5 tests */ });
  describe('Checkout Timeout Handling', () => { /* 1 test */ });
});
```

### 运行 Checkout 测试

```bash
# 运行所有 checkout 测试
cd frontend
npm test -- checkout.test.ts

# 运行并查看覆盖率
npm test:coverage -- checkout.test.ts

# 监视模式
npm test -- --watch checkout.test.ts
```

---

## 本地测试配置 (Local Testing Setup)

### 端口汇总

| 服务 | 端口 | 链接 | 说明 |
|------|------|------|------|
| 前端开发服务器 | 5173 | http://localhost:5173 | React 前端应用 |
| Vitest UI | 51204 | http://localhost:51204/__vitest__/ | 测试可视化界面 |
| 后端 API | 8000 | http://localhost:8000 | FastAPI 服务 |
| API 文档 | 8000 | http://localhost:8000/docs | Swagger 文档 |

### 启动本地测试服务

#### 前端开发服务器

```bash
cd frontend
npm run dev
```

**访问**: http://localhost:5173

#### 测试 UI（可选）

```bash
cd frontend
npm run test:ui
```

**访问**: http://localhost:51204/__vitest__/

#### 后端 API 服务

```bash
cd backend
knowledge-agent serve
# 或
python -m uvicorn src.api.main:app --reload
```

**API 文档**: http://localhost:8000/docs
**API 端点**: http://localhost:8000/api/v1/

### 多终端启动示例

```bash
# 终端 1: 启动前端
cd frontend && npm run dev

# 终端 2: 启动后端
cd backend && knowledge-agent serve

# 终端 3: 启动测试 UI（可选）
cd frontend && npm run test:ui
```

### 验证测试

```bash
# 1. 验证文档已更新
cat frontend/docs/testing/README.md | grep -A 5 "Checkout"

# 2. 运行 checkout 测试
cd frontend
npm test -- --run checkout.test.ts

# 3. 检查测试结果
npm test:coverage -- checkout.test.ts
```

---

**最后更新**: 2026-03-10
