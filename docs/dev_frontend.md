# 100X Knowledge Agent: 前端架构与 UI/UX 详细设计开发指南

## 0. 目标与背景 (Context & Goals)
本文档旨在为前端开发者及 AI 助手 (如 Cursor, Claude, Antigravity) 提供**高度结构化、像素级、体感级清晰**的开发指南。
鉴于此前系统呈现的“前后端分离基本不可用、界面跳转失效、模块职责模糊”等痛点，且基于已确定的 6 张核心原型设计，我们将通过模块化拆解与精确的 UI 布局约定，直接指导每一个界面区域的开发与联调。不要上来就写代码，务必先深刻理解下列的业务流与设计审美。

**核心体验追求 (The Vibe)**：流畅、现代、沉浸式、极客感 (Geeky but Elegant)。我们要贴合 macOS 的质感体验，深度契合高知用户的自定义工作流与国内外 AI 大模型厂商的复杂配置环境。

---

## 1. 全局体验体系设计原则与审美 (Global UX & Aesthetic Principles)

*   **玻璃拟物与 macOS 质感 (Glassmorphism)**: 抛弃死板的纯色块。大量运用背景毛玻璃 (`backdrop-blur-md/lg`)、半透明遮罩 (`bg-white/10 dark:bg-black/40`) 与极细的 1px 边框透视，营造悬浮感。
*   **抽屉与空间折叠 (Spatial Navigation)**: 坚决抵制传统呆板的整页跳转刷新。应用内大量使用滑动窗口 (Sliding Window)、侧边折叠抽屉、右侧滑出浮现面板，保持用户的“阅读上下文连贯性”。
*   **无鼠化与极客按键 (Keyboard-First Flow)**: 深入骨髓的极客体感。必须内置 `J`/`K` 上下切换卡片焦点，`Cmd+K` 全局唤出命令/搜索面板，`Enter` 展开详情，`Cmd+S` 静默保存。
*   **微排版与留白 (Micro-typography)**: 拒绝拥挤。利用大面积负空间引导视线，字重对比（Headline vs Description）必须明显，使用 Inter/SF Pro 等非系统默认衬线/无衬线高品质字体。

---

## 2. 核心四大界面模块拆解与精准布局 (Core Interfaces Detailed Layout)

请开发/AI在构建组件时，严格按照以下 4 个模块逐步推进。所有模糊的交互地带已在此彻底澄清。

### 模块一：主信息流与聚合工作区 (Feed & Notes Workspace)
这是用户每天停留最久的核心消费场。它不是简单的列表，而是极具呼吸感的信息工作台。

**【整体布局视角】**
采用经典的 **“三段式弹性布局” (Left Menu - Center Feed - Right Peek Panel)**。
1. **左侧导航滑出栏 (Left Sidebar & Folders)**:
   - **视觉**: 默认可收缩为极其细窄的图标列 (Icon strip)，悬浮或点击后展开 (Slide-out)。
   - **功能与按钮**: 顶部包含"全局检索(Search)"；中间为"系统导航"；下半部为"信息分类树 (Tag Clouds)"与"历史收藏夹 (Bookmarks)"。点击左侧任意项，只是筛选中间的中心流数据，**不导致页面跳转**。
2. **中间主视图 (Center Infinite Feed)**:
   - **顶部控制台 (Top Bar)**: 左侧为日期漏斗（时间戳筛选）；中间为极其吸睛的 **快速抽取框 (Quick Extract Input)**，形似 Mac 的 Spotlight 框，填入 URL `Enter` 即可送给后端；右侧为“数据导出/一键外呼”触发按钮。
   - **卡片核心交互 (Card Interactions)**: 卡片内部右上角有隐性触发的悬浮操作组，Hover 时展现「保存笔记 (Save)」「打标签 (Tag)」「共享 (Share)」。
   - **重心/引力场排序 (Gravity Sorting - 核心体感)**: 信息流极具动态。未读消息具有微弱辉光(Glow)与高亮色带，绝对**置顶展现**！当卡片被阅读 (滚动驻留或点击展开) 后，触发平滑的过渡动画下沉，视觉呈现略微暗化 (Opacity: 0.75)。
3. **右侧洞察抽屉 (Right Insight Peek - 解决原"按钮不清晰")**:
   - 当点击某条中心 Feed 的“深度分析”时，不要跳转！而是从屏幕最右侧丝滑地滑出一个抽屉面板。
   - **详情界面**: 展示 AI 根据 Prompt 萃取出的“水下信息”、“金句结构”与 Markdown 富文本。底部配有 `Add to Notes` 按钮，将此条数据导入个人的二创编辑器中。

---

### 模块二与三：Prompt 设定与信息矩阵管理一体化 (Integrated Prompt & Source Matrix)
**⚠️ 关键认知纠偏**：以前模块 2 (Prompt) 和模块 3 (Sources) 是割裂的。现在的核心逻辑是——“**先有规则(Prompt)，后有数据矩阵(Sources Matrix)**”。我们将两者糅合进一个高度具备审美感的工作流中。

**【布局走向：左右/上下切分的分步工作台 (Stepper/Split 工作台)】**
不再是传统的列表表单页，而是一个具有“炼丹”极客感的操作台。

1. **左半屏 / 步骤一：Pro (Prompt) 规则定义区**
   - 这里存放系统的大脑。界面采用类似 VS Code/Cursor 的沉浸式多 Tab 编辑器。
   - **Tab页签**: `[筛选标准 (Scoring)]`、`[萃取要求 (Extraction)]`、`[输出格式 (Format)]`。
   - **编辑器体感**: 纯粹的 Markdown 沉浸式编辑，支持语法高亮。底部具有 `Version Default/A/B` 控制条。
2. **右半屏 / 步骤二：信息矩阵管理底座 (Source Data Matrix)**
   - 当左侧配好任意一套 Prompt 后，右侧展现“矩阵卡片组”或“高配数据表(Data Grid)”。
   - **视觉与配置**: 这些源 (Twitter, RSS, YouTube) 就像一个个外设模块插在右边。
   - **卡片/行级按钮**: 每一条来源必须清晰包含：开关 (Toggle Switch，控制激活态)，轮询状态指示灯 (Cron Light，绿色闪烁表示监听中)，以及快速唤起的 `Add Source Modal`。
   - **协同体感**: 左侧改动规则，右侧可以针对某个源进行 Test Run (试跑)，展现极具设计感的代码态测试输出弹窗。

---

### 模块四：系统级设置与 API 开发者控制台 (Settings & API Dev Hub)
这是掌控分发网络与大模型引擎配置的核心重地。我们需要极度专业、详尽、具备开发者亲和力。

**【整体布局】**
左侧为模块导航 Tab (`引擎配置`, `分发机器人`, `API 开发者选项`)，右侧为具体的区块表单阵列，借鉴 Cloudflare / Vercel 管理后台的块状阴影 (Card Shadow) 极简风格。

1. **大模型引擎阵列 (LLM Providers Setup)**:
   - 必须涵盖并存的国内外国双轨模型卡片（OpenAI, Claude, 智谱, Moonshot Kimi, DeepSeek）。
   - **核心特定场景支持 - “科学上网 Proxy” 连通配置**: 针对通过 API 国内直连不通的痛点！在界面最显著位置或高级选项中，直接提供 `Proxy Address:Port (e.g. 127.0.0.1:7890)` 的配置输入框。加入一个极具爽感的 **"Test Connection" 闪电测速按钮**，点击后出现 ping 延迟指示，给足反馈。
2. **分发通路管控 (Bot Network Setup)**:
   - 这是产出端。配置 `Telegram Group Token/ChatID` 与 `Feishu Webhook` 的表单卡片。打通与用户的最后几公里。
3. **API 开发者中心 (API Developer Hub - 流畅体感打磨)**:
   - 对于希望利用本系统进行二次开发（如开发自有插件、跨工具调用）的人：
   - 在本配置区底端设立专属区。不仅是抛出一个 Token，必须具备**自带格式化的高亮代码块（cURL Snippets）**，直观演示如何调取系统的核心接口 `/api/v1/extract/quick` 等等。
   - **体感细节**: 代码块右上角的一键拷贝(Copy)，点击后显示绿色的 "Copied!" 提示。配备实时的调用 Log 监控滚动小窗，呈现系统如何执行用户的请求流水过程。

---

## 3. 前后端联调与接口契约 (API Contracts Reference)

- **核心信息流**: `GET /api/v1/feed`、`PUT /api/v1/feed/{id}/read` (承载界面一的已读引力下沉体感)。
- **规则矩阵保存**: `PUT /api/v1/prompts/{stage}` 与 `POST /api/v1/sources`。
- **配置与网络连通**: 涵盖模型密钥的 `PUT /api/v1/settings/providers` (必须在此接口 payload 中约定扩展 `proxy_url` 字段)。

## 4. 前端开发流水线执行步骤 (Execution Steps)

1. **统一审美基调**: 构建好 Tailwind CSS 色阶（深色背景推荐 `zinc-900` / `stone-900`，配上适当毛玻璃滤镜层）。确定好字体的 `font-sans` 全局映射。
2. **搭建立体框架 (Layout Container)**: 实现左侧的 Collapsible Sidebar，确保它能顺畅的响应拉伸。中央留出固定尺寸与滚动条隐去的区域。
3. **先攻模块二＆三一体化视图**: 结合 Markdown 编辑器组件，搭建左右/上下切分的界面。重点雕琢右侧信息矩阵卡片的启停状态动效。
4. **精细雕琢模块一 (Feed Fluid)**: 在此阶段接入真实数据。实现 `is_read` 的引力衰减排序效果（必须带有 Transition 让卡片滑出当前视区）。
5. **打磨系统控制台与开发者体验**: 最后搭建模块四，务必实现 Proxy 连通性的测速反馈动效与 API 示例区的极简排版呈现。
