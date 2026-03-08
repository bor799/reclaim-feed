# 炼器房 (Reclaim your feed) - 前端开发规范与执行文档

**文档目标**：指导前端开发人员（或 AI Agent）完成 `100X Knowledge Agent` (现名`炼器房`) 的前端架构落地与后续演进。此规范基于 React + Vite 实际技术栈与当前已交付的 3 大基础路由模块。

## 1. 核心设计规范 (Design Guidelines)
- **视觉风格**：追求极致的现代简约、沉浸式、极客感，去除多余线条。设计系统围绕 Flat Design 与 Apple Human Interface Guidelines (HIG) 质感展开。
- **字体排版**：
  - 英文字体优先使用 `Inter` 及系统无衬线原生字体。
  - 中文字体优先使用 `PingFang SC`, `Microsoft YaHei`。
  - 核心诉求：拉大字号与字重级差（H1, H2, 正文），强化可读性与信息层级。**移动端基础字号建议 16px+**，防止 Safari 触发原生输入法自动缩放。
- **组件库与技术栈**：
  - 核心栈：`React` + `Vite`。
  - 样式驱动：`Tailwind CSS`，全局变量抽离在 `index.css`。
  - 图标库：`lucide-react`。
  - **核心禁令**：禁止使用厚重的全局组件库（如 Ant Design/Material UI），所有组件通过 Tailwind 拼装以保持性能最佳与定制化。

## 2. 移动优先与 iOS 深度优化 (Mobile-First & iOS Optimization)
考虑到核心消费场景为 iOS 设备（iPhone），前端实现必须达到**原生级 App 的沉浸体验**：
1. **安全区适配 (Safe Area)**：必须使用 `env(safe-area-inset-top)` 和 `env(safe-area-inset-bottom)` 避免被刘海屏、灵动岛、底部小白条遮挡内容。
2. **触控冗余 (Touch Targets)**：所有可交互元素（按钮、卡片、开关）响应区最小达到 `44x44 pt` (Apple HIG 建议)。
3. **PWA 与沉浸模式**：
   - 提供 `manifest.json` 支持"添加到主屏幕" (Add to Home Screen)。
   - 包含 `<meta name="apple-mobile-web-app-capable" content="yes">` 隐去 Safari 原生地址栏。
4. **弹簧滚动拦截 (Overscroll)**：全局 `body` 设置 `overscroll-behavior-y: none`，防止页面整体出现拉拽白边的廉价感；仅允许内容容器（如 `.feed-container`）内部使用原生级顺滑滚动。
5. **手势操作转化**：摒弃 Hover 依赖，核心高频操作应当支持手指点击或显性的底部动作条(Bottom Action Bar)。

## 3. 路由与整体布局 (Routing & Global Layout)
根据最新迭代，整体路由模块划分为三个核心并列视图：
- `/feed` -> Feed (信息流阅览区，处理日常输入，默认跳转首页)
- `/notes` -> Notes (笔记复盘区，沉淀高价值信息)
- `/sources` -> Sources (信息源管理，配置上游漏斗)

### 2.1 全局 Layout 容器设计
- **侧边栏 (Sidebar)**：
  - 左侧常驻导航。包含主菜单切分。状态激活时使用品牌色 (`Primary/CTA`) 予以高亮。底色保持纯净，收起时留白充足以将视觉重点让于主视区。
- **主内容区 (Main Layout)**：
  - 大量留白，最大宽度居中 (`max-w-6xl`)，实现视觉聚焦，抛开一切使人分心的边框。

## 3. 核心功能模块 (Core View Modules)

### 模块一：Feed 信息流阅览区 (`/feed`)
*系统的主阵地，用户消耗碎片时间进行快速过滤与阅读的区域。*

1. **信息卡片设计 (Feed Card)**
   - 瀑布流/列表排布 AI 萃取后的结果。
   - 卡片核心呈现：**文章标题**、**AI 核心摘要**、特殊的**关键洞察与金句层 (Key Insights)**。
   - 带有醒目的 **AI 评分** (如 ⭐ 9.5) 与 **来源信标**。
2. **阅读到沉淀的无缝闭环 (Bookmark 联动)**
   - 卡片右上角设置**收藏按钮**。
   - **联动逻辑**：点击收藏（实心标记）后，不仅该状态发生改变，并且**自动联动触发生成一条对应的 Note**，携带着所有源数据和洞察流向 `/notes` 页面，完成"浏览 -> 沉淀"的动作循环。

### 模块二：Notes 笔记复盘区 (`/notes`)
*沉浸式审阅、个人思考批注的内容管理大脑。*

1. **结构设计 (左右分屏)**
   - **左半侧列表**：结构化笔记列表。包含常规搜索。从 Feed 收藏触发生成的笔记具有特殊的"收藏"或"来源"标识，与手动创建区分。
   - **右半侧编辑器**：阅读与交互打磨区。
2. **编辑器交互**
   - **查看模式**：以格式化渲染的方式呈现信息源、原摘要、洞察。
   - **编辑模式**：无干扰白板 Markdown 输入，供用户重新排版、写下延展思考。
   - 交互操作：支持增删改查。当在 Notes 侧删除了由 Feed 衍生的记录时，联动解绑 Feed 侧的收藏状态。

### 模块三：Sources 信息源配置区 (`/sources`)
*控制知识管道第一层漏斗的配置中心。*

1. **配置表与状态检索**
   - 核心层列表展示所有 RSS、Twitter 等源的健康度与开启状态 (Active/Paused)。
   - 提供基于 Category 的分类管控。
2. **直观的增删改查面板**
   - 支持新增/修改 源地址 URL、系统源类型 (RSS/Twitter/YouTube 等)。
   - 后续需跟进后端接口变动，支持在前端修改特定源的抓取频率 (`cron_interval`) 以及自动标签关联 (`default_tags`)。

## 4. 后续模块预留 (Workflow & Settings)
基于 Agent 属性，在跑通前后端读取后，后续需在 UI 层面平铺：
1. **工作流 Prompt 编辑区 (Workflow 配置)**：图形化配置四个漏斗阶段（过滤分标准、萃取特殊模板），打通 API 使得用户的每一次更新可覆盖 `config/prompts/` Markdown 文件。
2. **System Settings**：多厂商模型 API Key 管理、Telegram/飞书 推送 Webhook 配置、本地同步物理地址指定。

## 5. 数据与状态管理落地规范
- **当前态 (Local MVP)**：目前凭借 React `Context API` (`AppContext`) 与 `localStorage` 进行全状态流转，用极低成本跑通了概念验证与 UI 定调。
- **演进态 (Integration with APIs)**：
  1. 所有状态从 localStorage 无缝剥离为 Axios 请求驱动，统一交由 `src/services/api.ts` 抽象处理。
  2. **拦截器底座 (Auth Interceptor)**：鉴于项目预留的 SaaS 化方向，请求封装层必须注入 Token 处理逻辑（如每次拦截附带 `Authorization: Bearer <token>`），保证页面无痛兼容未来可能会引入的多租户体系。

## 6. 预期交付与迭代顺序
- [x] **步骤 1**：环境与框架搭建 (Vite/React)，全局 Tailwind CSS 规范落户。
- [x] **步骤 2**：完成核心 Feed / Notes / Sources MVP 页面的渲染与极简式 Layout。
- [x] **步骤 3**：完成前端 `localStorage` 层面的复杂联动（收藏自动建笔记、上下文状态管理）。
- [ ] **步骤 4**：全面联调改造升级后的 FastAPI，接管假数据，跑通线上实际 Pipeline 的数据回流。
- [ ] **步骤 5**：升级 Notes 区域 Markdown 编辑器体验（集成如 `react-markdown`，增加语法高亮与渲染能力）。
- [ ] **步骤 6**：补齐系统级的 Settings 面板和 Prompt 修改页。
