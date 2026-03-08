# 炼器房 (Reclaim your feed) - Docker 云端部署指南

本指南主要面向**使用者**及**负责自动化部署的 Agent (如 Claude Code)**。本项目已完成了前后端架构的分离重构，并针对 SaaS/多租户路径进行了鉴权接管。本指南提供通过 Docker Compose 快速把该项目部署至生产服务器的最佳步骤。

## 1. 必须上传的核心物料清单
在推送到云端服务器前，必须打包上传以下目录和文件（为节省带宽，请**排除** `node_modules`, `dist`, `.venv`, `__pycache__` 等编译临时目录）：

- 📁 `backend/` (后端 FastAPI 源码及 Prompts 等环境资源)
  - 必须包含 `backend/.env` (注入你的环境凭据，比如大模型 API Keys)
  - 必须包含 `backend/config/config.yaml` (包含你的默认数据源及配置)
  - 必须包含 `backend/Dockerfile`
- 📁 `frontend/` (前端 React 源码)
  - 必须包含 `frontend/Dockerfile`
- 📄 `docker-compose.yml` (位于项目根目录，编排前后端容器)
- 📄 `README.md` 与 `docs/` 等附加文档 (可选，用于部署机器核验)

建议直接将上述结构压缩为 `.tar.gz` 进行传输，并在远程机器同级目录下解压。

## 2. API 与参数配置预检 (Pre-flight Checklist)

### 2.1 后端 `.env` 环境预制 (关键 ⚠️)
请确保 `backend/.env` 在云端已包含正确的凭据（目前 Web 端尚未接管系统配置，这些变量主导着底层引擎）：
```env
# 大模型鉴权 (目前接入智谱)
ZHIPU_API_KEY=你的_API_KEY.在这里填入

# 后期预留的鉴权开关 (目前单机测试态建议关闭)
AUTH_ENABLED=False

# 时区设定 (保障定时器与前台时间轴一致)
TZ=Asia/Shanghai
```

### 2.2 前台路由代理预备
如果你在公网环境下部署，前端 API 需要知道后端的绝对调用地址。如果是跨越机器级别，你可能需要在 Nginx 层做 Proxy Pass，或者在 `.env.production` 设定 `VITE_API_URL`。
*注：当前 `docker-compose.yml` 默认两者都在单台云服务器上，可直接测试。*

## 3. 一键编译与拉起 (Deployment)

进入云服务器解压后的 `100x-knowledge-agent` 根目录：

```bash
# 停止可能残留的旧有容器
docker-compose down

# 强制基于最新代码重新编译镜像，并在后台拉起
docker-compose up --build -d
```

**服务映射状态：**
1. **Frontend**: 暴露在云主机的 `8080` 端口 (React + Alpine Nginx)。
2. **Backend**: 暴露在云主机的 `8000` 端口 (FastAPI + 挂载着 6 小时触发一次的 APScheduler 定时爬虫任务)。

请确保你云主机的安全组 (Security Group) 或防火墙，对外放行了 `8080` (如果你挂了域名，可通过 Nginx 代理映射到 80/443)。

## 4. 数据备份与持久化说明
在 `docker-compose` 架构下，以下关键目录已做了 Volume 映射，这关乎着你的资产，请在发生服务器迁移时**重点备份这两个文件夹**：
- `backend/state/` (存储 SQLite 或 JSON 的元数据状态，以及最终抓取落地的 Notes)。
- `backend/config/` (核心的配置源文件)。
