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

| 层次 | 配置文件 | 作用 |
|------|---------|------|
| **① 信息源** | `config/sources.yaml` | 订阅 RSS、Twitter 关注列表、B站 UP 主等 |
| **② 过滤规则**| `config/prompts/scoring.md` | 用自然语言定义你的偏好与评分阈值（替代硬编码查词） |
| **③ 深度萃取**| `config/prompts/extraction.md` | 定义你想要的结构化输出（如：水下信息、案例、金句） |
| **④ 输出格式**| `config/prompts/obsidian_format.md`| Markdown 与 Dataview Frontmatter 模板 / IM 卡片样式 |

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

## 产品演进状态与阶段性成果 (Current Progress)

本项目目前已经完成了**单机全栈重构**，并针对 SaaS/多租户形态和多端体验做了深度适配验证。以下是当前已就绪的成果：

### 1. 核心架构重做 (API + Agent Scheduler)
- **FastAPI 改造**：移除了原有的硬编码循环脚本，将 `Fetch → Filter → Analyze → Output` 链路完全 API 化。
- **APScheduler 挂载**：容器启动即运行后台守护时钟，默认 `6 小时` 拉取萃取一次，完全无人值守。
- **多租户预留 (Auth Plan A)**：所有的 Router 函数已通过 `user_id = Depends(get_current_user)` 接管，当前 MVP 阶段利用 `AUTH_ENABLED=False` 放行，可随时接入真实的 JWT 校验体系。

### 2. 前端 3 大核心模块落地 (Frontend MVP)
- **`/feed` (信息流)**：瀑布流卡片展示提炼后的 `Key Insights`，附带打分与来源标签；支持一键"收藏" (Bookmark)。
- **`/notes` (笔记区)**：创新性的"懒人收纳联动"：在 Feed 点收藏，自动携带洞察带参跳入 Notes 生成草稿；支持 Markdown 沉浸批注。
- **`/sources` (配置台)**：可视化管理知识漏斗导入层（RSS、Twitter 等订阅源）。

### 3. Apple 生态极致跨端体验 (iOS & macOS Optimization)
- **iOS 移动端优化**：适配 iPhone 刘海、灵动岛安全区 (`env(safe-area-inset)`)；屏蔽 Safari 原生橡皮筋回弹 (`overscroll-behavior-y: none`)；引入 `Bottom Action Bar` (底部触控原生导航)；支持 PWA 隐去地址栏式"安装到主屏"。
- **macOS (Chrome) 桌面级打磨**：
  - **Power-user 热键**：注入 `Cmd + K` 全局统领/搜索；Feed 页支持 `J` / `K` 上下文无鼠标穿梭并支持 `Enter` 即时查看原文；Notes 页支持 `Cmd + S` 劫持静默保存。
  - **苹果视觉**：全局开启字体锐利化平滑 (`-webkit-font-smoothing`)，改写 Chrome 默认宽大滚动条为苹果同款的细半透明毛玻璃 Overlay 滚动条。

---

## 遗留事项与未来探索想法 (Backlog & Ideas)

当前系统已经能在云端 Docker 稳定跑送，但要达到"无痛且高度自定义"的最终形态，仍有以下几个迭代重点放在了接下来的周期中：

1. **前后端接口全链路对接**
   - 当前前端数据以 Mock 和 LocalStorage 为主做概念展示，需全面接管至 FastAPI 的真实接口回传。
2. **构建 Settings (设置中心) 网页管理能力**
   - 目前 API Key 与 RSS 数据仍需深入 `backend/config/config.yaml` 手动填写。需打通 UI 界面的模型服务商 (Providers) 配置与 `Prompt` 热更新功能。
3. **引入 Markdown 所见即所得的高级解析器**
   - 当前的 `/notes` 采用简单的 `react-markdown` 纯渲染。未来计划接入 `Tailwind Typography` 和语法高亮支持，并强化 `#标签` 正则自解析自动归档等高级动作。
4. **Agent MCP 能力外放**
   - 为后续的 Agent 化工作流补充标准的协议暴露，允许其它 Agent 主动调用该系统插入某项文章的分析请求（旁路请求：`POST /api/v1/extract/quick`）。

---

## 快速部署 (Docker Ready)

如果你想自己启动这套系统体验（前提是你需要在本地或服务器配置好 `backend/.env`），详见完整的部署指令档：
👉 [部署文档 (deploy_docker.md)](./docs/deploy_docker.md)
