# 炼器房 (Reclaim your feed) - 后端开发规范与执行文档

**文档目标**：指导后端团队（或 AI Agent）全面改造原生 API 与数据链路，为全新的 3 大前端模块提供接口，同时为未来的开源云部署与 SaaS 化（多租户体系）奠定底层架构。

## 1. 核心底座改造要求：Multi-Tenant Ready (多租户防范)
考虑到项目"开源单机 Docker 为主，未来做付费 SaaS 云服务"的产品路径，后端**绝不允许在代码层面写死全局无状态变量或单一配置文件**：
- **数据隔离基石**：虽然目前不做登录注册界面，但数据库实体（源、Notes、配置）都需要留存外键列 `user_id` / `account_id`（默认可以全填为 `local_admin`）。
- **拦截器鉴权准备**：所有的 FastAPI Router 必须穿过依赖注入 (Dependency Injection) 的鉴权中间件。现阶段 (MVP) 鉴权中间件可直接提取环境配置开关：如果 `AUTH_ENABLED=False`，强制返回 `user_id='local_admin'`。

## 2. API 接口重构需求 (对应前端 3 大模块)

### 2.1 支撑 Module 1: Unified Workspace (信息流核心区)
*旧版本的接口不够立体，需要新增分析指标和特异化的快速入库接口。*

- **[新增] `GET /api/v1/user/stats` (用户数据看板 API)**
  - 返回当前用户的总处理笔记数 (`total_notes`)、总整理标签数 (`total_tags`)、加入天数 (`days_active`)、近期批注数 (`annotations_count`)。
- **[修改] `GET /api/v1/feed` (升级为 Unified Timeline API)**
  - **支持核心过滤参数**：必须支持传入 `is_annotated=boolean` (是否有批注/Markdown反馈) 按批注状态快速检索。
  - **支持混合排序展示**：为了支撑前端"抖音式"全视口滑屏流，此接口需支持将原生的信息流数据 (Feeds) 与用户保存的笔记 (Notes) 数据进行底层的 `UNION` 操作，并统一按时间线 (Timeline) 倒序分页下发，使前端能在一个列表中同构渲染两种卡片体系。
- **[新增] `POST /api/v1/extract/quick` (旁路加速萃取接口)**
  - 接受单个或一组 URL 字符串 `{"urls": ["http..."]}`。
  - 此接口绕过底层的定时计划 (CronJob)，**直接将其扔进** `Fetch -> Filter -> Analyze` 队列并立即执行解析返回。用于首页顶部快速 URL 解析条。
- **[新增] 标签解析工具函数 (Tag Parser)**
  - 拦截用户通过 GUI 保存的 Note (`Markdown` 字段)。
  - 解析出形如 `#Agent` `#AI` 的字符串，自动落入全局标签宽表 `Tags` 与该 Note 进行关联。

### 2.2 支撑 Module 2: Workflow & Sources (炼器炉配置区)
*配置需进一步从静态文件细化到可以被数据库追踪或版本化追踪的状态。*

- **[修改] Sources 数据结构升级 (`/api/v1/sources`)**
  - Schema 新增字段: `cron_interval` (String/Int：例如表示每 4 个小时抓一次此源)。
  - Schema 新增字段: `default_tags` (Array: 给这个源自动绑上特定标签如 `#Karpathy推荐`)。
  - **调度引擎更新**：后端的 RSS 爬虫和 Scheduler 不能在一锅粥里跑，必须能根据各 Source 表里的 `cron_interval` 挂载对应的 APScheduler / Celery 独立任务。
- **[新增] Prompts 管控 API (`GET/PUT /api/v1/prompts/{stage}`)**
  - 将原先写死在文件中的四大阶段 Markdown Prompt（(1)过滤 (2)萃取 (3)格式化 (4)发布）彻底转换为 API。
  - **预留 V1/V2 版本回溯功能**，数据结构上考虑储存更新时间与历史版本记录库。

### 2.3 支撑 Module 3: Settings (系统设置对接区)
*支持不同种类集成环境热更新的 API 簇。*

- **[新增] `GET/PUT /api/v1/settings/providers` (大模型服务商配置)**
  - 管理 DeepSeek, Kimi, Zhipu, Anthropic 等多厂商 API keys。入库保存注意脱敏加密/混淆存放。
- **[新增] `GET/PUT /api/v1/settings/bots` (通道配置)**
  - 管理 Telegram bot token, chat ID，或 Feishu Webhook URL。
- **[新增] `GET/PUT /api/v1/settings/environment`**
  - 设置 UI `locale` (中英文对照偏好)。
  - 设置 `local_workspace_path` (同步至本地电脑（如 Obsidian）的物理绝对路径映射)。
  - 设置系统级默认的 `system_prompt` (大模型全局身份设定映射)。

## 3. DevOps 与部署调整
- **语言/时区统一**：确保 Docker Container 强制设定 `TZ=Asia/Shanghai` 或 UTC 的规范化处理，防止前端 Timeline (根据日期归档) 出现乱序。
- **数据库技术栈**：鉴于 SaaS 未来预期支持多组 Schema 查询推荐使用 `PostgreSQL`（若保持本地开源部署可用 `SQLite` 作为默认隔离层），通过 ORM (`SQLAlchemy` / `Tortoise ORM`) 完成适配抹平差异。
- **文档化输出**：此后台规范确定后，开始改写 FastAPI 内的 Pydantic 模型作为执行第一步。
