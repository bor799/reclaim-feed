<div align="center">

# 🔮 炼器房 (Reclaim your feed)

**做深不做宽。专注于高知人群的 AI 深度知识萃取与消费引擎。**

---

</div>

## 产品定位：为什么我们需要另一个 News 系统？

目前市面上的新闻聚合系统（如 Horizon、RSS 阅读器）大多专注于**"做宽"**：接入无数信息源，快速打分，生成一篇简短的日报摘要。但这往往导致用户陷入**浅层信息过载**，缺乏护城河。

**炼器房 (Reclaim your feed) 的核心价值在于"做深"**：
- **深度萃取**：不仅仅是"总结大意"，而是从一篇文章中提取出别人看不到的**水下信息**、核心**金句**以及可复用的**方法论**。
- **配置即代码**：一切 Prompts（评分标准、萃取格式）全部外置为 Markdown。不改代码，只写 Prompt 即可定制你的个人 Agent。
- **消费闭环**：不仅推送到 Obsidian / IM，还提供类 Apple 备忘录的内置阅读体验与想法批注，最终无缝导出到 NotebookLM 等生产工具。

## 产品边界与信息生命周期

本系统专注于信息生命周期的 **前中段（萃取 → 消费 → 生产）**，将**分发**留给更专业的生态工具。

```
[精选源 / 宽泛源导入] 
      ↓
(1) 萃取 (Extract)：过滤噪音 → LLM 深度分析
      ↓
(2) 消费 (Consume)：Obsidian 看板 / IM 推送 / GUI 阅读与批注
      ↓
(3) 生产 (Produce)：Markdown 导出 / NotebookLM 播客生成 / 社交媒体格式
      ↓
(4) [边界外] 分发 (Distribute)：借助 baoyu-skills 等生态工具发帖
```

---

## 核心架构设计

> **原则：主流程代码不可变，配置全面外置，不重复造轮子。**

### 1. 两层信息源模型

为保证深度且不错过重要信息，我们采用两层漏斗：
- **宽泛源（导入层）**：如 Horizon 日报、HN Top、泛在推文池。（重前端轻后端，高分才入库）
- **精选源（核心层）**：如 Karpathy 推荐的 RSS、高质量 Twitter 关注列表。

### 2. Pipeline（后端引擎核心）

后端本质上是一个稳定的 `Fetch → Filter → Analyze → Output` 管道。

### 3. 四层可配置 Prompt

| 层次         | 配置文件                                | 作用                                           |
| ---------- | ----------------------------------- | -------------------------------------------- |
| **① 信息源**  | `config/sources.yaml`               | 订阅 RSS、Twitter 关注列表、YouTube等                 |
| **② 过滤规则** | `config/prompts/scoring.md`         | 用自然语言定义你的偏好与评分阈值（替代硬编码查词）                    |
| **③ 深度萃取** | `config/prompts/extraction.md`      | 定义你想要的结构化输出（如：水下信息、案例、金句）                    |
| **④ 输出格式** | `config/prompts/obsidian_format.md` | Markdown 与 Dataview Frontmatter 模板 / IM 卡片样式 |

---

## 生态工具集成

我们坚持**不造轮子**，通过标准化接口与优秀的开源生态无缝集成。

### 现阶段内置集成 (Phase 1)
*   **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)**: 强大的 CLI，赋予 Agent 抓取 Twitter、小红书、Reddit、B站的能力，零 API 费用。
*   **[yt-search-download](https://github.com/joeseesun/yt-search-download)**: Claude Code Skill，一键获取 YouTube 视频详情与双语字幕。
*   **[bilibili-watcher](https://github.com/openakita/openakita/tree/main/skills/bilibili-watcher)**: B站动态追踪与字幕提取。

### 接口预留与后续接入 (Phase 2 & 3)
*   **[Claude-to-IM](https://github.com/op7418/Claude-to-IM)**: 桥接 Node.js 库，无需从零开发即可无缝将萃取结果多模态推送到 Telegram、飞书、Discord，并支持内联操作按钮。
*   **[anything-to-notebooklm](https://github.com/joeseesun/anything-to-notebooklm)**: 内容汇聚与格式转换器，一键将本地知识库导入 NotebookLM 生成播客。
*   **[baoyu-skills](https://github.com/jimliu/baoyu-skills)**: 生成小红书图文、配图、幻灯片的 Agent 技能（未来对接写入层出口）。
*   **关注列表与书签**：预留 Import API 导入多平台（如 Twitter/小红书/Chrome）关注或收藏列表。

---

## 四种交付与使用形态

本系统不仅仅是一个 CLI 工具，它适应不同用户与 Agent 的交互需求：

1. **本地安装 (CLI)**：面向开发者，`uv sync` 快速启动，配置文件直观。
2. **Server / Docker**：面向运维/团队，`docker-compose up` 实现云端 24h 高可用抓取与推送。
3. **Agent Skill / MCP Server**：面向前沿大模型工作流，为 Claude Code 等大模型助手提供直接调用能力 (`/run_pipeline`, `/score_item`)。
4. **GUI App (后续规划)**：面向普通高知用户，前后端分离（React+Vite），提供开箱即用的 Web 配置页、阅读 Feed 与笔记批注功能。

---

## 系统设计与核心模块 (System Architecture & Modules)

本项目基于前后端分离架构，旨在提供高性能、沉浸式、极客感 (Geeky but Elegant) 的前端消费体验，以及高兼容、稳健调度的后台支撑网络。

### 1. 后端引擎 (Backend Engine: Python + FastAPI)
后端的本质是一个稳定的 `Fetch → Filter → Analyze → Output` 管道，并在此之上完全实现 API 化与模块化：
- **数据管线与分析调度**: 各信息源可根据其 `cron_interval` 独立设置抓取频次并挂载调度，并提供 `POST /api/v1/extract/quick` 旁路萃取接口应对突发手动解析需求。
- **统一时间线 API (Unified Timeline API)**: 深度聚合原生 Feeds 和用户批注 Notes，基于底层 SQL `UNION` 倒序混合排列，实现针对未读状态的强制置顶 (Pinned) 与已读状态的引力衰减下沉 (Gravity Sorting)。
- **多租户数据底座 (Multi-Tenant Ready)**: 所有资源响应依赖基于全局拦截器 API 的 `user_id` 外键隔离。
- **配置与规则全面释放**: 原僵化的 Markdown 规则与资源转换为 CRUD，包含四大阶段 `Prompts` API 控制、`Sources` 管理配置与 Cron 调度、以及可热插拔的模型服务商 (AI Providers) 与机器人分发接驳 (Bots) 设置等接口模块化升级。

### 2. 前端交互 (Frontend UI/UX: React + Vite + Tailwind CSS)
彻底摈弃传统生硬跨页刷新，采用极致的"玻璃拟物化与 macOS 质感 (Glassmorphism)"：
- **键盘极客流优先 (Keyboard-First Flow)**：全局注入 `Cmd+K` 统领命令与搜索面板，并针对重度阅读引入 `J`/`K` 辅以 `Enter` 实现上下穿梭，结合 `Cmd+S` 无缝沉浸保存笔记。
- **模块一：统一信息流 & 工作区 (Feed & Notes Workspace)**：整合左侧聚合流与右侧/全屏滑动展开窗口，内置"顶部链接一件提取"与精细化动态过滤区，卡片带有 Edit/Like/Tag 等微操作。
- **模块二：消息源矩阵与 Prompt 体系管理**：带有全屏视界 Markdown 沉浸编辑用于改写萃取 Prompt，配合带滑窗的 RSS 列表以悬浮弹窗提供精准管理。
- **模块三：原生级偏好面板 (Settings)**：提供大面积模糊虚焦质感面板设置 API Key / Base URL 与测速连通性等。

---

## 阶段性成果与已实现功能 (Current Progress & Features)

本项目目前已经完成了**单机全栈改造**，功能模块落地成果如下：

1. **后端核心 API 链路重构与测试 (Backend Engine)**
   - 彻底将系统所有功能行为升级为稳健的 FastAPI API，并打通并新增用户统计大盘、源信息参数设置、系统级环境控制以及阅读标记 (is_read / Bookmark)。
   - 后端逻辑全面通过 `pytest` 完成自动化集成测试 (Integration Tests)，在多租户底层结构与运行性能上取得了保障。

2. **前端与后端接口全链路对接 (Full-Stack API Integration)**
   - 前端数据已全面脱离 Mock 和 LocalStorage，全面接管至 FastAPI 的真实接口回传 (`/api/v1/feed`, `/api/v1/sources` 等)。
   - 实现了本地测试环境 (`local-test-env`)，支持前后端服务的一键启停。

3. **核心 UI/UX 设计模块落地 (Frontend MVP Design Modules)**
   - **沉浸式聚合信息流 (`ImmersiveLayout`)**：顶栏原生支持 URL 链接"快速提取"，支持通过卡片的动态引力排序和筛选状态无刷新重塑前端瀑布流。
   - **Prompt 管理控制台 (`PromptsView`)**：带有三段式 Tab 的全屏视界 Markdown 沉浸编辑器，用于在线改写筛选、萃取与分发的 Prompt 版本控制。
   - **信息源导控矩阵 (`SourcesView`)**：带有跟随滚动的玻璃态折叠 Header 布局与 RSS 列表，并可以在前端无缝编写和调度 Cron 配置参数。
   - **原生级系统偏好面板 (`SettingsView`)**：打通 UI 界面的模型服务商 (Providers) 配置、系统代理环境 (Proxy)、前端 API 联通性测试与分发 Bots 填报。

4. **Apple 级别生态全沉浸视觉包容 (Apple Ecosystem Optimization)**
   - **全面跨端 PWA 适配**：对于移动端提供完备 Service Worker 及 Web Manifest 方案，iOS Safari 特别修缮原生防打断(`overscroll-behavior-y`)与底部原生导航(Bottom Action Bar)并可零妥协“安装到主屏 (`Add to Home Screen`)”。
   - **macOS 机能视觉化打磨**：引入深海静蓝 (`Blue-600`) 的系统点缀色，配合 `backdrop-blur-md/lg` 毛玻璃滤镜，以及最高级的全局 macOS 全平滑字体渲染 (`-webkit-font-smoothing: antialiased`)。

---

## 遗留事项与未来探索想法 (Backlog & Ideas)

当前系统前端交互与核心引擎已经完备互通并在云端 Docker 稳定跑送。为了达到最终形态，后续迭代重点为：

1. **引入 Markdown 所见即所得的高级解析器**
   - 当前的 `/notes` 采用简单的 `react-markdown` 纯渲染。未来计划接入 `Tailwind Typography` 和语法高亮支持，并强化 `#标签` 正则自解析自动归档等高级动作。
2. **Agent MCP 能力外放与进一步适配**
   - 为后续的 Agent 化工作流补充标准的协议暴露，允许其它 Agent 主动调用该系统插入某项文章的分析请求（旁路请求：`POST /api/v1/extract/quick`）。

---

## 快速部署 (Docker Ready)

如果你想自己启动这套系统体验（前提是你需要在本地或服务器配置好 `backend/.env`），详见完整的部署指令档：
👉 [部署文档 (deploy_docker.md)](./docs/deploy_docker.md)
