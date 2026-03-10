# -*- coding: utf-8 -*-
"""
Test configuration and fixtures for 100X Knowledge Agent tests.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock

# Ensure backend source is in the path
backend_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_dir))

from src.models import (
    AppConfig, LLMConfig, ProviderConfig, FilterConfig,
    ExtractionConfig, OutputConfig, BotConfig, EnvironmentConfig,
    SourceConfig, SourceType, ContentItem, ItemStatus, Decision
)

# Import after setting path
from fastapi.testclient import TestClient


# ──────────────────────────────────────────────
# Test Config
# ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test data."""
    temp_path = Path(tempfile.mkdtemp(prefix="knowledge_agent_test_"))
    yield temp_path
    # Cleanup after all tests
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="session")
def test_config(temp_dir):
    """Create a test config."""
    return AppConfig(
        llm=LLMConfig(
            provider="zhipu",
            model="glm-4.7",
            api_key_env="ZHIPU_API_KEY",
            api_base="https://open.bigmodel.cn/api/coding/paas/v4"
        ),
        providers=[
            ProviderConfig(
                name="OpenAI",
                api_key="dummy",
                api_base="https://api.openai.com"
            ),
            ProviderConfig(
                name="Zhipu",
                api_key="dummy",
                api_base="https://open.bigmodel.cn/api/paas/v4",
                proxy_url="socks5://127.0.0.1:1080"
            )
        ],
        sources=[
            SourceConfig(
                user_id="test_user",
                name="Test RSS",
                type=SourceType.RSS,
                url="https://example.com/rss",
                enabled=True,
                cron_interval="12h",
                default_tags=["test", "rss"]
            ),
            SourceConfig(
                user_id="test_user",
                name="Test Twitter",
                type=SourceType.TWITTER,
                url="https://twitter.com/test",
                enabled=False,
                cron_interval="6h",
                default_tags=["social"]
            )
        ],
        filter=FilterConfig(
            high_quality_threshold=7.0,
            edge_case_threshold=5.0,
            keywords_include=["AI", "Machine Learning"],
            keywords_exclude=["spam"]
        ),
        extraction=ExtractionConfig(
            output_fields=["one_line_summary", "hidden_insights", "golden_quotes"]
        ),
        output=OutputConfig(
            obsidian_root=str(temp_dir / "obsidian"),
            dir=str(temp_dir / "test_store"),
            max_items=100
        ),
        bots=BotConfig(
            telegram_bot_token="test_token",
            telegram_chat_id="test_chat_id",
            feishu_webhook_url="https://feishu.webhook/test"
        ),
        environment=EnvironmentConfig(
            locale="en",
            local_workspace_path=str(temp_dir / "workspace"),
            system_prompt="You are a helpful AI assistant."
        )
    )


@pytest.fixture(scope="function")
def app_with_test_config(test_config, temp_dir, monkeypatch):
    """
    Create a FastAPI app with test config.
    This fixture is used to create a fresh app instance for each test.
    """
    # Create test store file
    test_store_path = temp_dir / "items.json"
    test_store_path.parent.mkdir(parents=True, exist_ok=True)
    test_store_path.write_text("{}", encoding="utf-8")

    # Mock get_state_path to return our test path
    def mock_get_state_path(filename):
        return temp_dir / filename

    # Mock load_config to return test_config
    def mock_load_config(*args, **kwargs):
        return test_config

    # Apply mocks
    monkeypatch.setattr("src.config.get_state_path", mock_get_state_path)
    monkeypatch.setattr("src.outputs.store.get_state_path", mock_get_state_path)
    monkeypatch.setattr("src.config.load_config", mock_load_config)

    # Import app fresh with mocks in place
    import importlib
    import src.api.main as main_api
    importlib.reload(main_api)

    # Set config directly
    main_api._config = test_config
    main_api._pipeline = None
    main_api._scheduler = None

    # Mock the startup to avoid issues
    async def mock_startup():
        main_api._config = test_config
        main_api._pipeline = Mock()
        main_api._scheduler = Mock()

    # Override startup
    main_api.app.router.startup = mock_startup

    # Override get_current_user
    from src.api.deps import get_current_user
    def override_get_current_user():
        return "test_user"

    main_api.app.dependency_overrides[get_current_user] = override_get_current_user

    yield main_api.app

    # Clean up
    main_api.app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app_with_test_config, temp_dir, monkeypatch):
    """
    Create a test client with overridden dependencies.
    """
    # Ensure test store is empty
    test_store_path = temp_dir / "items.json"
    test_store_path.parent.mkdir(parents=True, exist_ok=True)
    test_store_path.write_text("{}", encoding="utf-8")

    # Mock get_state_path again for this test
    def mock_get_state_path(filename):
        return temp_dir / filename

    monkeypatch.setattr("src.config.get_state_path", mock_get_state_path)
    monkeypatch.setattr("src.outputs.store.get_state_path", mock_get_state_path)

    with TestClient(app_with_test_config, raise_server_exceptions=False) as c:
        yield c


# ──────────────────────────────────────────────
# Mock Data Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def mock_feed_items() -> List[ContentItem]:
    """Generate mock Feed items for testing."""
    return [
        ContentItem(
            user_id="test_user",
            title="AI Agent Development Guide",
            url="https://example.com/ai-agents",
            author="John Doe",
            content="This is a comprehensive guide to building AI agents with advanced features.",
            source=SourceType.RSS,
            source_detail="Tech Blog",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="test_id_1",
            quality_score=8.5,
            quality_decision=Decision.PASS,
            quality_reason="High quality content with actionable insights",
            status=ItemStatus.UNREAD,
            is_read=False,
            is_favorited=True,
            tags=["AI", "Agents", "Development"],
            category="Technology",
            is_annotated=False
        ),
        ContentItem(
            user_id="test_user",
            title="Machine Learning Basics",
            url="https://example.com/ml-basics",
            author="Jane Smith",
            content="Introduction to machine learning concepts and algorithms.",
            source=SourceType.IMPORT,
            source_detail="Horizon Daily",
            published_at="2026-03-09T15:30:00",
            created_at="2026-03-09T15:30:00",
            unique_id="test_id_2",
            quality_score=6.5,
            quality_decision=Decision.EDGE,
            quality_reason="Good content but lacks depth",
            status=ItemStatus.READ,
            is_read=True,
            is_favorited=False,
            tags=["ML", "Tutorial"],
            category="Education",
            is_annotated=True,
            annotation="Good intro, need more examples"
        ),
        ContentItem(
            user_id="test_user",
            title="Investment Strategies for 2026",
            url="https://example.com/investment",
            author="Investment Pro",
            content="Top investment strategies for the coming year.",
            source=SourceType.TWITTER,
            source_detail="@investment_pro",
            published_at="2026-03-08T08:00:00",
            created_at="2026-03-08T08:00:00",
            unique_id="test_id_3",
            quality_score=4.0,
            quality_decision=Decision.REJECT,
            quality_reason="Generic content with no unique insights",
            status=ItemStatus.UNREAD,
            is_read=False,
            is_favorited=False,
            tags=["Investment", "Finance"],
            category="Finance",
            is_annotated=False
        ),
        ContentItem(
            user_id="test_user",
            title="Python Best Practices",
            url="https://example.com/python",
            author="Code Master",
            content="Python programming best practices and patterns.",
            source=SourceType.RSS,
            source_detail="Python Weekly",
            published_at="2026-03-10T14:00:00",
            created_at="2026-03-10T14:00:00",
            unique_id="test_id_4",
            quality_score=7.5,
            quality_decision=Decision.PASS,
            status=ItemStatus.UNREAD,
            is_read=False,
            is_favorited=False,
            tags=["Python", "Programming"],
            category="Technology"
        )
    ]


@pytest.fixture
def mock_sources() -> List[SourceConfig]:
    """Generate mock Sources for testing."""
    return [
        SourceConfig(
            user_id="test_user",
            name="Tech Blog RSS",
            type=SourceType.RSS,
            url="https://techblog.com/rss",
            enabled=True,
            cron_interval="6h",
            default_tags=["technology", "programming"],
            category="Tech"
        ),
        SourceConfig(
            user_id="test_user",
            name="AI News Feed",
            type=SourceType.RSS,
            url="https://ainews.com/feed",
            enabled=True,
            cron_interval="4h",
            default_tags=["AI", "News"],
            category="AI"
        ),
        SourceConfig(
            user_id="test_user",
            name="LinkedIn Posts",
            type=SourceType.IMPORT,
            url="https://linkedin.com/imports",
            enabled=False,
            cron_interval="daily",
            default_tags=["professional"],
            category="Career"
        )
    ]


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────

def assert_valid_feed_response(response_data: Dict[str, Any]) -> None:
    """Assert that feed response has valid structure."""
    assert "items" in response_data
    assert "total" in response_data
    assert "page" in response_data
    assert "limit" in response_data
    assert "has_more" in response_data
    assert isinstance(response_data["items"], list)
    assert isinstance(response_data["total"], int)
    assert isinstance(response_data["page"], int)
    assert isinstance(response_data["limit"], int)
    assert isinstance(response_data["has_more"], bool)


def assert_valid_item(item: Dict[str, Any]) -> None:
    """Assert that an item has valid structure."""
    required_fields = ["unique_id", "title", "url", "created_at"]
    for field in required_fields:
        assert field in item, f"Missing required field: {field}"


# ──────────────────────────────────────────────
# Test Data Isolation
# ──────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolate_test_data(temp_dir):
    """Reset data state before each test."""
    # Clear test store
    test_store_path = temp_dir / "items.json"
    test_store_path.parent.mkdir(parents=True, exist_ok=True)
    test_store_path.write_text("{}", encoding="utf-8")
    yield
    # Clean up after test
    pass
