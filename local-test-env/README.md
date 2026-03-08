# 100X Knowledge Agent - 本地测试环境

独立的测试环境，不影响现有代码。

## 📁 目录结构

```
local-test-env/
├── backend-config/          # 后端配置
│   ├── .env                 # 环境变量（需配置 API Key）
│   ├── config.yaml          # Agent 配置
│   └── prompts/             # 提示词模板
├── frontend-config/         # 前端配置
│   ├── .env.test            # 环境变量示例
│   ├── api.ts               # API 客户端
│   └── SourcesView.example.tsx  # 组件示例
├── logs/                    # 日志文件
├── state/                   # 运行时状态
├── start-all.sh             # 一键启动
├── start-backend.sh         # 后端启动
└── start-frontend.sh        # 前端启动
```

## 🚀 快速开始

### 1. 配置后端 API Key

编辑 `backend-config/.env` 文件：

```bash
# 获取 API Key: https://open.bigmodel.cn/usercenter/apikeys
ZHIPU_API_KEY=your_actual_api_key_here
```

### 2. 一键启动

```bash
cd local-test-env
./start-all.sh
```

选择 `3` 启动前后端联调。

### 3. 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 📝 详细步骤

### 方案 A: 使用真实后端 API

#### 1. 配置后端

```bash
cd local-test-env/backend-config
# 编辑 .env 文件，设置 ZHIPU_API_KEY
```

#### 2. 复制前端 API 服务

```bash
mkdir -p ../frontend/src/services
cp frontend-config/api.ts ../frontend/src/services/api.ts
```

#### 3. 复制环境变量

```bash
cp frontend-config/.env.test ../frontend/.env.local
```

#### 4. 启动服务

```bash
cd local-test-env
./start-all.sh  # 选择 3
```

### 方案 B: 仅测试前端（使用 Mock 数据）

如果暂时不想配置后端，可以直接启动前端：

```bash
cd frontend
npm run dev
```

前端会使用 `mockData.ts` 中的模拟数据。

## 🔧 手动启动（调试用）

### 仅启动后端

```bash
cd local-test-env
./start-backend.sh
```

后端启动后，可以测试 API：

```bash
# 健康检查
curl http://localhost:8000/health

# 获取信息源
curl http://localhost:8000/sources

# 获取配置
curl http://localhost:8000/settings

# 运行 Pipeline（需要配置 API Key）
curl -X POST http://localhost:8000/run
```

### 仅启动前端

```bash
cd local-test-env
./start-frontend.sh
```

## 📊 前端集成真实 API

### 1. 复制 API 服务文件

```bash
cp local-test-env/frontend-config/api.ts frontend/src/services/api.ts
```

### 2. 创建环境变量

```bash
cp local-test-env/frontend-config/.env.test frontend/.env.local
```

### 3. 更新组件（可选）

参考 `frontend-config/SourcesView.example.tsx` 修改组件：

- 导入 `api` 客户端
- 使用 `useEffect` 加载真实数据
- 移除 `mockData` 依赖

示例：

```tsx
import { api } from '../services/api';

useEffect(() => {
  const fetchData = async () => {
    const data = await api.getSources();
    setSources(data);
  };
  fetchData();
}, []);
```

## 🐛 调试

### 查看后端日志

```bash
tail -f local-test-env/logs/backend.log
```

### 检查后端健康状态

```bash
curl http://localhost:8000/health
```

### 常见问题

**1. 后端启动失败**
- 检查 `backend-config/.env` 中的 API Key 是否正确
- 确认已安装 Python 依赖：`cd backend && source .venv/bin/activate && pip install -e .`

**2. 前端无法连接后端**
- 检查后端是否运行：`curl http://localhost:8000/health`
- 检查 `frontend/.env.local` 中的 `VITE_API_BASE_URL`

**3. CORS 错误**
- 后端已配置 CORS，允许所有来源访问

## 📦 测试环境配置

### 后端配置 (`backend-config/config.yaml`)

- 使用 2 个测试 RSS 源
- 关闭 Obsidian 写入
- 关闭 Telegram 通知
- 质量阈值：7.0

### 前端配置 (`frontend/.env.local`)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🛑 停止服务

- 在终端中按 `Ctrl+C`
- 或运行：`pkill -f "uvicorn|vite"`

## 🔄 重置测试环境

```bash
cd local-test-env
rm -rf logs/* state/*
```

## 📚 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/sources` | GET | 获取信息源 |
| `/items` | GET | 获取萃取结果 |
| `/settings` | GET | 获取配置 |
| `/run` | POST | 运行 Pipeline |
| `/export/json` | GET | 导出 JSON |

详细文档: http://localhost:8000/docs

## 💡 提示

- 后端使用虚拟环境：`backend/.venv`
- 日志保存在 `local-test-env/logs/`
- 运行时状态保存在 `local-test-env/state/`
- 测试环境不影响 `backend/config/` 中的正式配置
