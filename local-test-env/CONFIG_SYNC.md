# 配置同步说明

## ✅ 已从现有项目同步的配置

测试环境配置已从 `knowledge-extractor` 项目同步完成：

### 🔑 API 密钥

| 配置项 | 值 | 来源 |
|--------|-----|------|
| `ZHIPU_API_KEY` | `a0506743786a4e25ab8194ca7d7c9d19...` | knowledge-extractor/config/credentials.yaml |
| `TELEGRAM_BOT_TOKEN` | `8076345416:AAGorcsTQayF...` | knowledge-extractor/config/credentials.yaml |
| `TELEGRAM_CHAT_ID` | `7934670950` | knowledge-extractor/config/credentials.yaml |

### 📡 信息源

从 `rss_sources.json` 的 95 个源中选择了前 5 个用于测试：

1. Simon Willison (AI进展)
2. Hacker News (AI进展)
3. Jeff Geerling (AI进展)
4. Krebs on Security (AI进展)
5. Daring Fireball (AI进展)

### 👤 用户配置

| 配置项 | 值 |
|--------|-----|
| 用户名 | murphy |
| 时区 | Asia/Shanghai |
| 关注领域 | 大模型 Agent 应用、美股交易策略、AI 行业动态、实战踩坑经验、技术复盘与故障分析 |

### 📂 路径配置

| 配置项 | 路径 |
|--------|------|
| Obsidian Vault | `/Users/murphy/Documents/Obsidian Vault/信息源` |

### 🎯 质量阈值

| 配置项 | 值 |
|--------|-----|
| 高质量阈值 | 7.0 |
| 边缘内容阈值 | 5.0 |

---

## 📊 配置对比

### 测试环境 vs 生产环境

| 项目 | 测试环境 | 生产环境 |
|------|----------|----------|
| **信息源数量** | 5 个（快速测试） | 95 个（完整覆盖） |
| **Telegram 推送** | ❌ 关闭（避免打扰） | ✅ 开启 |
| **Obsidian 写入** | ✅ 开启（与生产相同） | ✅ 开启 |
| **API 配置** | ✅ 与生产相同 | ✅ 相同 |
| **用户偏好** | ✅ 与生产相同 | ✅ 相同 |

---

## 🚀 现在可以启动了！

配置已完成，直接运行：

```bash
cd local-test-env
./start-all.sh
```

选择 `3` 启动前后端联调。

---

## ⚠️ 注意事项

1. **测试环境会写入 Obsidian**：如果不想影响生产库，可以在 `config.yaml` 中设置 `obsidian_root: ""`
2. **Telegram 已关闭**：测试环境不会发送消息到 Telegram
3. **仅使用 5 个信息源**：测试更快，完整运行请使用生产环境

---

## 📝 配置文件位置

- **环境变量**: `local-test-env/backend-config/.env`
- **Agent 配置**: `local-test-env/backend-config/config.yaml`
- **生产环境配置**: `~/Documents/Obsidian Vault/职业发展/项目案例/100X_知识萃取系统/knowledge-extractor/config/`
