# 云端部署指南

> **Reclaim Feed V2** - 智能知识萃取系统云端部署配置

## 📋 部署前准备

### 仓库信息
- **GitHub Repository**: https://github.com/bor799/reclaim-feed
- **Branch**: `main`
- **Dockerfile**: ✅ 已在根目录配置

### 部署要求
| 资源 | 要求 |
|------|------|
| RAM | ≥ 256MB |
| CPU | 单核即可 |
| 端口 | 动态（读取 `PORT` 环境变量） |
| 存储 | ≥ 100MB（用于配置文件和缓存） |

---

## 🚀 部署步骤

### 方式一：Docker 部署（推荐）

```bash
# 1. 拉取最新代码
git clone https://github.com/bor799/reclaim-feed.git
cd reclaim-feed

# 2. 构建镜像
docker build -t reclaim-feed:v2 .

# 3. 运行容器
docker run -d \
  --name reclaim-feed \
  -p 8000:8000 \
  -e PORT=8000 \
  -v reclaim-feed-config:/app/backend/config \
  reclaim-feed:v2

# 4. 查看日志
docker logs -f reclaim-feed
```

### 方式二：Docker Compose 部署

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  reclaim-feed:
    image: reclaim-feed:v2
    container_name: reclaim-feed
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    volumes:
      - reclaim-feed-config:/app/backend/config
    restart: unless-stopped

volumes:
  reclaim-feed-config:
    driver: local
```

启动服务：
```bash
docker-compose up -d
```

---

## ⚙️ 云端配置 API Keys

### 🌐 访问设置页面

部署成功后，访问：`http://your-domain:8000`

点击右上角 **⚙️ 设置** 按钮。

### 🔑 配置 LLM Provider

**支持的提供商**：
- 智谱 AI (Zhipu)
- OpenAI
- Anthropic (Claude)
- DeepSeek
- Ollama (本地)

**配置步骤**：
1. 选择 **Provider**（如：`zhipu`）
2. 输入 **API Key**（你的真实密钥）
3. 输入 **Base URL**（可选，默认使用官方端点）
4. 点击 **Test Connection** 验证
5. 点击 **Save** 保存到云端

### 🤖 配置 Telegram Bot

**获取 Bot Token**：
1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot` 创建机器人
3. 获取 Bot Token（格式：`123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`）

**获取 Chat ID**：
1. 在 Telegram 搜索 `@userinfobot`
2. 发送任意消息获取你的 Chat ID

**配置步骤**：
1. 输入 **Telegram Bot Token**
2. 输入 **Telegram Proxy URL**（可选，如：`socks5://127.0.0.1:1080`）
3. 输入 **Feishu Webhook URL**（可选）
4. 点击 **Save** 保存

### 🌐 配置网络代理（可选）

如果你的服务器需要代理访问 API：
1. 在 **Network Settings** 中输入 **Proxy URL**
   - 格式：`http://proxy-server:port`
   - 或：`socks5://proxy-server:port`
2. 点击 **Save** 保存

---

## 💾 配置存储位置

所有配置通过前端界面保存后，会自动写入到：

```
/app/backend/config/config.yaml
```

**使用 Docker Volume 持久化**：
- 配置文件存储在 Docker Volume `reclaim-feed-config` 中
- 容器重启后配置不会丢失
- 备份配置：`docker run --rm -v reclaim-feed-config:/data -v $(pwd):/backup alpine tar czf /backup/config-backup.tar.gz /data`

---

## 🧪 验证部署

### 1. 健康检查
```bash
curl http://your-domain:8000/api/v1/health
```

预期返回：
```json
{"status": "ok", "version": "2.0.0", "multi_tenant": true}
```

### 2. 测试快速提取
1. 访问前端页面
2. 输入任意文章 URL
3. 点击 **Quick Extract**
4. 检查 **Feed** 页面是否显示提取结果

### 3. 测试 Telegram 推送
1. 向你的 Bot 发送任意文章链接
2. 检查是否收到 AI 摘要回复
3. 检查 **Feed** 页面是否自动保存

---

## 🔧 常见问题

### Q1: 配置保存后丢失？
**A**: 确保使用了 Docker Volume 持久化配置：
```bash
docker volume inspect reclaim-feed-config
```

### Q2: API 连接失败？
**A**: 检查服务器网络是否需要代理：
1. 在 **Network Settings** 中配置代理
2. 或在服务器环境变量中设置：`export HTTP_PROXY=http://proxy:port`

### Q3: Telegram Bot 无响应？
**A**: 验证配置：
1. 确认 Bot Token 正确
2. 确认已向 Bot 发送过 `/start` 命令
3. 检查 Chat ID 是否正确
4. 查看后端日志：`docker logs reclaim-feed`

### Q4: 端口冲突？
**A**: 修改端口映射：
```bash
docker run -d -p 3000:8000 ...
```
然后设置环境变量：`-e PORT=3000`

---

## 📊 监控与日志

### 查看实时日志
```bash
docker logs -f reclaim-feed
```

### 查看容器状态
```bash
docker ps | grep reclaim-feed
```

### 重启服务
```bash
docker restart reclaim-feed
```

---

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker build -t reclaim-feed:v2 .

# 3. 停止旧容器
docker stop reclaim-feed && docker rm reclaim-feed

# 4. 启动新容器
docker run -d \
  --name reclaim-feed \
  -p 8000:8000 \
  -e PORT=8000 \
  -v reclaim-feed-config:/app/backend/config \
  reclaim-feed:v2
```

---

## 🌟 部署完成后

你的知识萃取系统已就绪！

1. **配置 API Keys**：访问设置页面输入你的密钥
2. **添加信息源**：在 Sources 页面管理 RSS 源
3. **开始使用**：通过前端界面或 Telegram Bot 提取文章

---

**最后更新**: 2026-03-10
**版本**: v2.0.0
