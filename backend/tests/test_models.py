# -*- coding: utf-8 -*-
"""
Data Model Tests
"""

import pytest
from datetime import datetime
from src.models import (
    ContentItem, SourceConfig, AppConfig,
    FilterConfig, ExtractionConfig, OutputConfig,
    LLMConfig, ProviderConfig, BotConfig, EnvironmentConfig,
    SourceType, ItemStatus, Decision,
    FeedUpdateRequest, SourceBulkRequest, SourceBulkStatusRequest,
    PromptVersionRestoreRequest, TestConnectionRequest, UserStats
)


class TestContentItem:
    """Test cases for ContentItem model."""

    def test_content_item_creation_minimal(self):
        """Test creating a ContentItem with minimal fields."""
        item = ContentItem(
            unique_id="test_id",
            title="Test Title",
            url="https://example.com"
        )
        assert item.unique_id == "test_id"
        assert item.title == "Test Title"
        assert item.url == "https://example.com"
        assert item.user_id == "local_admin"  # Default value
        assert item.is_read is False  # Default value
        assert item.is_favorited is False  # Default value
        assert item.status == ItemStatus.UNREAD  # Default value

    def test_content_item_creation_full(self):
        """Test creating a ContentItem with all fields."""
        item = ContentItem(
            user_id="test_user",
            title="Full Test Title",
            url="https://example.com/full",
            author="Test Author",
            content="Test content",
            source=SourceType.RSS,
            source_detail="Test Source",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="full_test_id",
            quality_score=8.5,
            quality_decision=Decision.PASS,
            quality_reason="High quality",
            status=ItemStatus.READ,
            is_read=True,
            is_favorited=True,
            tags=["test", "tag"],
            category="Test",
            is_annotated=True,
            annotation="Test annotation"
        )
        assert item.user_id == "test_user"
        assert item.quality_score == 8.5
        assert item.quality_decision == Decision.PASS
        assert item.status == ItemStatus.READ
        assert item.tags == ["test", "tag"]
        assert item.is_annotated is True

    def test_content_item_enum_defaults(self):
        """Test ContentItem enum default values."""
        item = ContentItem(
            unique_id="test_id",
            title="Test",
            url="https://example.com"
        )
        assert item.source == SourceType.RSS  # Default
        assert item.status == ItemStatus.UNREAD  # Default

    def test_content_item_lists_default_empty(self):
        """Test that list fields default to empty lists."""
        item = ContentItem(
            unique_id="test_id",
            title="Test",
            url="https://example.com"
        )
        assert item.tags == []
        assert item.user_notes == []

    def test_content_item_optional_fields(self):
        """Test ContentItem optional fields."""
        item = ContentItem(
            unique_id="test_id",
            title="Test",
            url="https://example.com",
            quality_score=None,
            quality_decision=None,
            quality_reason=None,
            published_at=None,
            extraction=None
        )
        assert item.quality_score is None
        assert item.quality_decision is None
        assert item.published_at is None

    def test_content_item_with_user_notes(self):
        """Test ContentItem with user notes."""
        notes = [
            {"timestamp": "2026-03-10T10:00:00", "content": "Note 1"},
            {"timestamp": "2026-03-10T11:00:00", "content": "Note 2"}
        ]
        item = ContentItem(
            unique_id="test_id",
            title="Test",
            url="https://example.com",
            user_notes=notes
        )
        assert len(item.user_notes) == 2
        assert item.user_notes[0]["content"] == "Note 1"

    def test_content_item_extraction_dict(self):
        """Test ContentItem with extraction dictionary."""
        extraction = {
            "one_line_summary": "Test summary",
            "hidden_insights": ["insight1", "insight2"],
            "golden_quotes": ["quote1"]
        }
        item = ContentItem(
            unique_id="test_id",
            title="Test",
            url="https://example.com",
            extraction=extraction
        )
        assert item.extraction == extraction
        assert item.extraction["one_line_summary"] == "Test summary"


class TestSourceConfig:
    """Test cases for SourceConfig model."""

    def test_source_config_minimal(self):
        """Test creating SourceConfig with minimal fields."""
        source = SourceConfig(
            name="Test Source",
            type=SourceType.RSS
        )
        assert source.name == "Test Source"
        assert source.type == SourceType.RSS
        assert source.user_id == "local_admin"  # Default
        assert source.enabled is True  # Default

    def test_source_config_full(self):
        """Test creating SourceConfig with all fields."""
        source = SourceConfig(
            user_id="test_user",
            name="Full Source",
            type=SourceType.TWITTER,
            enabled=False,
            url="https://twitter.com/test",
            category="Social",
            cron_interval="6h",
            default_tags=["twitter", "test"],
            extra={"api_key": "test_key"}
        )
        assert source.user_id == "test_user"
        assert source.enabled is False
        assert source.cron_interval == "6h"
        assert source.extra["api_key"] == "test_key"

    def test_source_config_all_types(self):
        """Test SourceConfig with all source types."""
        types = [SourceType.RSS, SourceType.TWITTER, SourceType.WECHAT,
                 SourceType.YOUTUBE, SourceType.BILIBILI, SourceType.IMPORT]
        for source_type in types:
            source = SourceConfig(
                name=f"Test {source_type}",
                type=source_type
            )
            assert source.type == source_type

    def test_source_config_tags_default(self):
        """Test SourceConfig default_tags defaults to empty list."""
        source = SourceConfig(
            name="Test",
            type=SourceType.RSS
        )
        assert source.default_tags == []

    def test_source_config_extra_default(self):
        """Test SourceConfig extra defaults to empty dict."""
        source = SourceConfig(
            name="Test",
            type=SourceType.RSS
        )
        assert source.extra == {}


class TestAppConfig:
    """Test cases for AppConfig model."""

    def test_app_config_default(self):
        """Test creating AppConfig with all defaults."""
        config = AppConfig()
        assert config.llm.provider == "zhipu"
        assert config.llm.model == "glm-4.7"
        assert config.sources == []
        assert config.focus_areas == ["AI Agent", "投资"]
        assert config.user_name == "user"
        assert config.timezone == "Asia/Shanghai"
        assert config.auth_enabled is False

    def test_app_config_with_llm(self):
        """Test AppConfig with custom LLM config."""
        config = AppConfig(
            llm=LLMConfig(
                provider="openai",
                model="gpt-4",
                api_key_env="OPENAI_API_KEY",
                api_base="https://api.openai.com",
                temperature=0.5
            )
        )
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4"
        assert config.llm.temperature == 0.5

    def test_app_config_with_providers(self):
        """Test AppConfig with multiple providers."""
        providers = [
            ProviderConfig(name="OpenAI", api_key="key1", api_base="https://api.openai.com"),
            ProviderConfig(name="Zhipu", api_key="key2", api_base="https://open.bigmodel.cn")
        ]
        config = AppConfig(providers=providers)
        assert len(config.providers) == 2
        assert config.providers[0].name == "OpenAI"

    def test_app_config_with_sources(self):
        """Test AppConfig with multiple sources."""
        sources = [
            SourceConfig(name="RSS1", type=SourceType.RSS, url="https://example1.com"),
            SourceConfig(name="RSS2", type=SourceType.RSS, url="https://example2.com")
        ]
        config = AppConfig(sources=sources)
        assert len(config.sources) == 2
        assert config.sources[0].name == "RSS1"

    def test_app_config_with_bots(self):
        """Test AppConfig with bot configuration."""
        bots = BotConfig(
            telegram_bot_token="test_token",
            telegram_chat_id="test_chat_id",
            feishu_webhook_url="https://feishu.webhook/test"
        )
        config = AppConfig(bots=bots)
        assert config.bots.telegram_bot_token == "test_token"

    def test_app_config_with_environment(self):
        """Test AppConfig with environment settings."""
        env = EnvironmentConfig(
            locale="zh",
            local_workspace_path="/path/to/workspace",
            system_prompt="Test prompt"
        )
        config = AppConfig(environment=env)
        assert config.environment.locale == "zh"
        assert config.environment.local_workspace_path == "/path/to/workspace"


class TestFilterConfig:
    """Test cases for FilterConfig model."""

    def test_filter_config_defaults(self):
        """Test FilterConfig default values."""
        config = FilterConfig()
        assert config.high_quality_threshold == 7.0
        assert config.edge_case_threshold == 5.0
        assert config.scoring_prompt == "config/prompts/scoring.md"
        assert config.keywords_include == []
        assert config.keywords_exclude == []

    def test_filter_config_custom(self):
        """Test FilterConfig with custom values."""
        config = FilterConfig(
            high_quality_threshold=8.0,
            edge_case_threshold=6.0,
            scoring_prompt="custom/prompts/scoring.md",
            keywords_include=["AI", "ML"],
            keywords_exclude=["spam"]
        )
        assert config.high_quality_threshold == 8.0
        assert config.keywords_include == ["AI", "ML"]


class TestExtractionConfig:
    """Test cases for ExtractionConfig model."""

    def test_extraction_config_defaults(self):
        """Test ExtractionConfig default values."""
        config = ExtractionConfig()
        assert config.prompt == "config/prompts/extraction.md"
        assert len(config.output_fields) == 4
        assert "one_line_summary" in config.output_fields

    def test_extraction_config_custom(self):
        """Test ExtractionConfig with custom values."""
        config = ExtractionConfig(
            prompt="custom/prompts/extraction.md",
            output_fields=["summary", "insights"]
        )
        assert config.prompt == "custom/prompts/extraction.md"
        assert config.output_fields == ["summary", "insights"]


class TestOutputConfig:
    """Test cases for OutputConfig model."""

    def test_output_config_defaults(self):
        """Test OutputConfig default values."""
        config = OutputConfig()
        assert config.obsidian_root == ""
        assert config.obsidian_format_prompt == "config/prompts/obsidian_format.md"
        assert config.telegram_enabled is False
        assert config.email_enabled is False

    def test_output_config_custom(self):
        """Test OutputConfig with custom values."""
        config = OutputConfig(
            obsidian_root="/path/to/vault",
            telegram_enabled=True,
            email_enabled=True
        )
        assert config.obsidian_root == "/path/to/vault"
        assert config.telegram_enabled is True


class TestLLMConfig:
    """Test cases for LLMConfig model."""

    def test_llm_config_defaults(self):
        """Test LLMConfig default values."""
        config = LLMConfig()
        assert config.provider == "zhipu"
        assert config.model == "glm-4.7"
        assert config.api_key_env == "ZHIPU_API_KEY"
        assert config.api_base == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert config.temperature == 0.1

    def test_llm_config_custom(self):
        """Test LLMConfig with custom values."""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key_env="OPENAI_API_KEY",
            api_base="https://api.openai.com",
            temperature=0.7
        )
        assert config.provider == "openai"
        assert config.temperature == 0.7


class TestProviderConfig:
    """Test cases for ProviderConfig model."""

    def test_provider_config_minimal(self):
        """Test ProviderConfig with minimal fields."""
        provider = ProviderConfig(
            name="TestProvider"
        )
        assert provider.name == "TestProvider"
        assert provider.api_key == ""
        assert provider.api_base == ""
        assert provider.enabled is True  # Default

    def test_provider_config_full(self):
        """Test ProviderConfig with all fields."""
        provider = ProviderConfig(
            name="FullProvider",
            api_key="test_key",
            api_base="https://api.test.com",
            proxy_url="socks5://127.0.0.1:1080",
            enabled=True
        )
        assert provider.proxy_url == "socks5://127.0.0.1:1080"
        assert provider.enabled is True

    def test_provider_config_optional_proxy(self):
        """Test ProviderConfig without proxy."""
        provider = ProviderConfig(
            name="NoProxy",
            api_key="key",
            api_base="https://api.test.com"
        )
        assert provider.proxy_url is None


class TestBotConfig:
    """Test cases for BotConfig model."""

    def test_bot_config_defaults(self):
        """Test BotConfig default values."""
        config = BotConfig()
        assert config.telegram_bot_token == ""
        assert config.telegram_chat_id == ""
        assert config.feishu_webhook_url == ""

    def test_bot_config_telegram(self):
        """Test BotConfig with Telegram settings."""
        config = BotConfig(
            telegram_bot_token="test_token",
            telegram_chat_id="test_chat_id"
        )
        assert config.telegram_bot_token == "test_token"
        assert config.telegram_chat_id == "test_chat_id"

    def test_bot_config_feishu(self):
        """Test BotConfig with Feishu webhook."""
        config = BotConfig(
            feishu_webhook_url="https://feishu.webhook/test"
        )
        assert config.feishu_webhook_url == "https://feishu.webhook/test"


class TestEnvironmentConfig:
    """Test cases for EnvironmentConfig model."""

    def test_environment_config_defaults(self):
        """Test EnvironmentConfig default values."""
        config = EnvironmentConfig()
        assert config.locale == "zh"
        assert config.local_workspace_path == ""
        assert config.system_prompt == ""

    def test_environment_config_custom(self):
        """Test EnvironmentConfig with custom values."""
        config = EnvironmentConfig(
            locale="en",
            local_workspace_path="/path/to/workspace",
            system_prompt="You are a helpful assistant."
        )
        assert config.locale == "en"
        assert config.system_prompt == "You are a helpful assistant."


class TestRequestModels:
    """Test cases for API request models."""

    def test_feed_update_request_minimal(self):
        """Test FeedUpdateRequest with minimal fields."""
        request = FeedUpdateRequest()
        assert request.content is None
        assert request.tags is None
        assert request.annotation is None

    def test_feed_update_request_partial(self):
        """Test FeedUpdateRequest with partial updates."""
        request = FeedUpdateRequest(
            content="Updated content"
        )
        assert request.content == "Updated content"
        assert request.tags is None

    def test_feed_update_request_full(self):
        """Test FeedUpdateRequest with all fields."""
        request = FeedUpdateRequest(
            content="Content",
            tags=["tag1", "tag2"],
            annotation="Annotation",
            category="Category"
        )
        assert request.content == "Content"
        assert len(request.tags) == 2

    def test_source_bulk_request(self):
        """Test SourceBulkRequest."""
        request = SourceBulkRequest(ids=[0, 1, 2])
        assert request.ids == [0, 1, 2]

    def test_source_bulk_status_request(self):
        """Test SourceBulkStatusRequest."""
        request = SourceBulkStatusRequest(
            ids=[0, 1],
            enabled=False
        )
        assert request.ids == [0, 1]
        assert request.enabled is False

    def test_prompt_version_restore_request(self):
        """Test PromptVersionRestoreRequest."""
        request = PromptVersionRestoreRequest(version=3)
        assert request.version == 3

    def test_test_connection_request_default(self):
        """Test TestConnectionRequest with defaults."""
        request = TestConnectionRequest()
        assert request.provider_name is None

    def test_test_connection_request_with_provider(self):
        """Test TestConnectionRequest with provider."""
        request = TestConnectionRequest(provider_name="OpenAI")
        assert request.provider_name == "OpenAI"


class TestUserStats:
    """Test cases for UserStats model."""

    def test_user_stats_defaults(self):
        """Test UserStats default values."""
        stats = UserStats()
        assert stats.total_notes == 0
        assert stats.total_tags == 0
        assert stats.days_active == 0
        assert stats.annotations_count == 0

    def test_user_stats_with_values(self):
        """Test UserStats with values."""
        stats = UserStats(
            total_notes=100,
            total_tags=25,
            days_active=30,
            annotations_count=10
        )
        assert stats.total_notes == 100
        assert stats.total_tags == 25


class TestEnums:
    """Test cases for model enums."""

    def test_source_type_values(self):
        """Test SourceType enum values."""
        assert SourceType.RSS == "rss"
        assert SourceType.TWITTER == "twitter"
        assert SourceType.WECHAT == "wechat"
        assert SourceType.YOUTUBE == "youtube"
        assert SourceType.BILIBILI == "bilibili"
        assert SourceType.IMPORT == "import"

    def test_item_status_values(self):
        """Test ItemStatus enum values."""
        assert ItemStatus.UNREAD == "未读"
        assert ItemStatus.READ == "已读"
        assert ItemStatus.DEEP_READ == "精读"

    def test_decision_values(self):
        """Test Decision enum values."""
        assert Decision.PASS == "通过"
        assert Decision.EDGE == "边缘"
        assert Decision.REJECT == "拒绝"


class TestModelValidation:
    """Test cases for model validation."""

    def test_content_item_url_validation(self):
        """Test that URL is stored as-is (Pydantic handles URL validation)."""
        item = ContentItem(
            unique_id="test",
            title="Test",
            url="https://example.com/path?query=value"
        )
        assert "query=value" in item.url

    def test_multiple_tags(self):
        """Test ContentItem with multiple tags."""
        item = ContentItem(
            unique_id="test",
            title="Test",
            url="https://example.com",
            tags=["AI", "ML", "Python", "FastAPI"]
        )
        assert len(item.tags) == 4

    def test_reread_worthy_flag(self):
        """Test reread_worthy flag."""
        item = ContentItem(
            unique_id="test",
            title="Test",
            url="https://example.com",
            reread_worthy=True
        )
        assert item.reread_worthy is True
