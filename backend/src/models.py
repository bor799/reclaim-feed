# -*- coding: utf-8 -*-
"""
数据模型 — Pydantic 配置校验 + 统一数据结构

所有 Pipeline 阶段共享的数据结构定义在此。
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────

class SourceType(str, Enum):
    """信息源类型"""
    RSS = "rss"
    TWITTER = "twitter"
    WECHAT = "wechat"
    YOUTUBE = "youtube"
    BILIBILI = "bilibili"
    IMPORT = "import"  # 外部导入（如 Horizon 日报）


class ItemStatus(str, Enum):
    """内容状态（Dataview 看板用）"""
    UNREAD = "未读"
    READ = "已读"
    DEEP_READ = "精读"


class Decision(str, Enum):
    """评分决策"""
    PASS = "通过"
    EDGE = "边缘"
    REJECT = "拒绝"


# ──────────────────────────────────────────────
# 内容项（Pipeline 流转单元）
# ──────────────────────────────────────────────

class ContentItem(BaseModel):
    """统一内容格式 — 从 Fetch 到 Output 全程使用"""

    # 多租户隔离 (SaaS Ready)
    user_id: str = "local_admin"

    # 基础字段
    title: str = ""
    url: str = ""
    author: str = ""
    content: str = ""
    source: SourceType = SourceType.RSS
    source_detail: str = ""
    published_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    unique_id: str = ""

    # 质量评估（Filter 阶段写入）
    quality_score: Optional[float] = None
    quality_decision: Optional[Decision] = None
    quality_reason: Optional[str] = None

    # 深度萃取（Analyze 阶段写入）
    extraction: Optional[Dict[str, Any]] = None
    analysis_score: Optional[float] = None
    passed_threshold: bool = False

    # 消费状态
    status: ItemStatus = ItemStatus.UNREAD
    is_read: bool = False
    is_favorited: bool = False
    reread_worthy: bool = False
    tags: List[str] = Field(default_factory=list)
    category: str = ""
    is_annotated: bool = False

    # 用户笔记
    user_notes: List[Dict[str, Any]] = Field(default_factory=list)
    annotation: Optional[str] = None  # Markdown 批注内容

    class Config:
        use_enum_values = True


# ──────────────────────────────────────────────
# 配置模型
# ──────────────────────────────────────────────

class SourceConfig(BaseModel):
    """单个信息源配置"""
    user_id: str = "local_admin"  # 多租户隔离
    name: str
    type: SourceType
    enabled: bool = True
    url: Optional[str] = None
    category: Optional[str] = None
    cron_interval: Optional[str] = None  # e.g. "4h", "30m", "daily"
    default_tags: List[str] = Field(default_factory=list)  # 自动标签
    extra: Dict[str, Any] = Field(default_factory=dict)


class FilterConfig(BaseModel):
    """过滤配置"""
    high_quality_threshold: float = 7.0
    edge_case_threshold: float = 5.0
    scoring_prompt: str = "config/prompts/scoring.md"
    keywords_include: List[str] = Field(default_factory=list)
    keywords_exclude: List[str] = Field(default_factory=list)


class ExtractionConfig(BaseModel):
    """萃取配置"""
    prompt: str = "config/prompts/extraction.md"
    output_fields: List[str] = Field(default_factory=lambda: [
        "one_line_summary",
        "hidden_insights",
        "golden_quotes",
        "methodology",
    ])


class OutputConfig(BaseModel):
    """输出配置"""
    obsidian_root: str = ""
    obsidian_format_prompt: str = "config/prompts/obsidian_format.md"
    telegram_enabled: bool = False
    email_enabled: bool = False


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = "zhipu"
    model: str = "glm-4.7"
    api_key_env: str = "ZHIPU_API_KEY"
    api_base: str = "https://open.bigmodel.cn/api/coding/paas/v4"
    temperature: float = 0.1


class ProviderConfig(BaseModel):
    """单个 LLM 服务商配置"""
    name: str
    api_key: str = ""  # 入库时加密/混淆存放
    api_base: str = ""
    proxy_url: Optional[str] = None  # 代理服务器地址，如 socks5://127.0.0.1:1080
    enabled: bool = True


class BotConfig(BaseModel):
    """推送通道配置"""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_proxy_url: Optional[str] = None
    feishu_webhook_url: str = ""


class EnvironmentConfig(BaseModel):
    """环境设置"""
    locale: str = "zh"  # "zh" | "en"
    local_workspace_path: str = ""  # Obsidian 仓库的物理绝对路径
    system_prompt: str = ""  # 大模型全局身份设定映射


class UserStats(BaseModel):
    """用户数据看板"""
    total_notes: int = 0
    total_tags: int = 0
    days_active: int = 0
    annotations_count: int = 0


class PromptVersion(BaseModel):
    """Prompt 版本记录"""
    version: int = 1
    content: str = ""
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


# ──────────────────────────────────────────────
# API 请求模型
# ──────────────────────────────────────────────

class FeedUpdateRequest(BaseModel):
    """单条 Feed 卡片更新请求"""
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    annotation: Optional[str] = None
    category: Optional[str] = None


class SourceBulkRequest(BaseModel):
    """批量 Source 操作请求"""
    ids: List[int]  # Source 索引列表


class SourceBulkStatusRequest(BaseModel):
    """批量 Source 状态更新请求"""
    ids: List[int]
    enabled: bool


class PromptVersionRestoreRequest(BaseModel):
    """恢复指定版本 Prompt 请求"""
    version: int


class TestConnectionRequest(BaseModel):
    """连通性测试请求"""
    provider_name: Optional[str] = None  # 不传则测试当前 Active Engine


class AppConfig(BaseModel):
    """应用总配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    sources: List[SourceConfig] = Field(default_factory=list)
    filter: FilterConfig = Field(default_factory=FilterConfig)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    focus_areas: List[str] = Field(default_factory=lambda: ["AI Agent", "投资"])
    user_name: str = "user"
    timezone: str = "Asia/Shanghai"
    providers: List[ProviderConfig] = Field(default_factory=list)
    bots: BotConfig = Field(default_factory=BotConfig)
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    auth_enabled: bool = False  # MVP 阶段默认关闭
