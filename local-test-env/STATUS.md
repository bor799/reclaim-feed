# 🚀 测试环境就绪 - 启动指南

## ✅ 配置状态

| 项目 | 状态 | 说明 |
|------|------|------|
| **后端 API Key** | ✅ 已配置 | 从 knowledge-extractor 同步 |
| **Telegram 配置** | ✅ 已配置 | 测试环境已关闭推送 |
| **Obsidian 路径** | ✅ 已配置 | 指向你的信息源库 |
| **信息源** | ✅ 已配置 | 5 个 RSS 源（前 5 个） |
| **用户配置** | ✅ 已配置 | murphy @ Asia/Shanghai |
| **前端 API 服务** | ✅ 已创建 | frontend/src/services/api.ts |
| **前端环境变量** | ✅ 已创建 | frontend/.env.local |

---

## 🎯 配置对比

### 已从现有项目同步

**配置来源**: `~/Documents/Obsidian Vault/职业发展/项目案例/100X_知识萃取系统/knowledge-extractor/`

```yaml
✅ ZHIPU_API_KEY: a0506743786a4e25ab8194ca7d7c9d19...
✅ TELEGRAM_BOT_TOKEN: 8076345416:AAGorcsTQayF...
✅ TELEGRAM_CHAT_ID: 7934670950
✅ Obsidian 路径: /Users/murphy/Documents/Obsidian Vault/信息源
✅ 用户偏好: 大模型 Agent 应用、美股交易策略、AI 行业动态...
```

### 测试环境调整

| 项目 | 测试环境 | 原因 |
|------|----------|------|
| 信息源数量 | 5 个 | 快速测试（原 95 个） |
| Telegram 推送 | 关闭 | 避免测试时打扰 |
| Obsidian 写入 | 开启 | 与生产环境一致 |

---

## 🚀 立即启动

### 方式一：一键启动（推荐）

```bash
cd "/Users/murphy/Documents/Obsidian Vault/职业发展/项目案例/100X_知识萃取系统/100x-knowledge-agent/local-test-env"
./start-all.sh
```

选择 `3` 启动前后端联调。

### 方式二：分步启动

**终端 1 - 启动后端：**
```bash
cd "/Users/murphy/Documents/Obsidian Vault/职业发展/项目案例/100X_知识萃取系统/100x-knowledge-agent/local-test-env"
./start-backend.sh
```

**终端 2 - 启动前端：**
```bash
cd "/Users/murphy/Documents/Obsidian Vault/职业发展/项目案例/100X_知识萃取系统/100x-knowledge-agent/local-test-env"
./start-frontend.sh
```

---

## 🌐 访问地址

启动成功后访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端界面** | http://localhost:5173 | React UI |
| **后端 API** | http://localhost:8000 | FastAPI |
| **API 文档** | http://localhost:8000/docs | Swagger UI |

---

## 🧪 快速测试

### 1. 测试后端健康检查

```bash
curl http://localhost:8000/health
```

预期返回：
```json
{"status": "healthy", "version": "0.1.0"}
```

### 2. 测试获取信息源

```bash
curl http://localhost:8000/sources
```

### 3. 测试运行 Pipeline

```bash
curl -X POST http://localhost:8000/run
```

### 4. 在浏览器中测试前端

访问 http://localhost:5173，查看：
- **Sources** 标签页：查看已配置的 5 个信息源
- **Feed** 标签页：查看萃取结果
- **Notes** 标签页：查看保存的笔记

---

## 📂 配置文件位置

```
local-test-env/
├── backend-config/
│   ├── .env              # API Keys
│   ├── config.yaml       # Agent 配置
│   └── prompts/          # 提示词模板
├── frontend-config/      # 前端配置模板
├── logs/                 # 运行日志
└── state/                # 运行时状态
```

---

## 🛑 停止服务

在启动的终端中按 `Ctrl+C`，或运行：

```bash
pkill -f "uvicorn|vite"
```

---

## 📝 下一步

1. **启动服务**：运行 `./start-all.sh`
2. **访问前端**：http://localhost:5173
3. **测试 API**：查看 http://localhost:8000/docs
4. **查看日志**：`tail -f local-test-env/logs/backend.log`

---

## ⚠️ 注意事项

1. **Obsidian 写入**：测试环境会写入到你的 Obsidian 信息源库，如果不想影响，编辑 `backend-config/config.yaml`，设置 `obsidian_root: ""`
2. **API 费用**：每次运行 Pipeline 会消耗智谱 AI 的 API 额度
3. **信息源限制**：测试环境只配置了 5 个源，如需更多，编辑 `backend-config/config.yaml`

---

**配置时间**: 2026-03-08
**配置来源**: knowledge-extractor 项目
**状态**: ✅ 就绪可启动
