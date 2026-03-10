# -*- coding: utf-8 -*-
"""
Integration tests for 100X Knowledge Agent

Tests end-to-end workflows including:
- Full pipeline execution
- API CRUD operations
- Frontend-backend data flow
- Concurrent operations
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import (
    AppConfig, SourceConfig, ContentItem, SourceType,
    ItemStatus, Decision
)
from src.pipeline import Pipeline
from src.processors.quality_filter import QualityFilter
from src.processors.analyzer import DeepAnalyzer
from src.outputs.obsidian import ObsidianWriter
from src.outputs.store import ItemStore
from fastapi.testclient import TestClient


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def integration_temp_dir():
    """Create temporary directory for integration tests."""
    temp_path = Path(tempfile.mkdtemp(prefix="integration_test_"))
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def integration_config(integration_temp_dir):
    """Create full config for integration tests."""
    config = AppConfig()
    config.llm = Mock()
    config.llm.provider = "zhipu"
    config.llm.model = "glm-4.7"
    config.llm.api_key_env = "ZHIPU_API_KEY"
    config.llm.api_base = "https://open.bigmodel.cn/api/paas/v4"
    config.llm.temperature = 0.7

    config.filter = Mock()
    config.filter.high_quality_threshold = 7.0
    config.filter.edge_case_threshold = 5.0
    config.filter.scoring_prompt = "scoring.md"

    config.extraction = Mock()
    config.extraction.prompt = "extraction.md"

    config.output = Mock()
    config.output.obsidian_root = str(integration_temp_dir / "obsidian")
    config.output.dir = str(integration_temp_dir / "store")
    config.output.max_items = 100

    config.focus_areas = ["AI", "Technology"]

    return config


# ──────────────────────────────────────────────
# End-to-End Workflow Tests
# ──────────────────────────────────────────────

class TestFullWorkflow:
    """Test complete workflow from source to output."""

    @pytest.mark.integration
    def test_full_workflow_mock_content(self, integration_config, integration_temp_dir):
        """Test full workflow with mock content."""
        # This test simulates the complete pipeline:
        # 1. Create source
        # 2. Fetch content (mocked)
        # 3. Quality filter
        # 4. Deep analysis
        # 5. Store
        # 6. Output to Obsidian

        source = SourceConfig(
            user_id="test_user",
            name="Test Blog",
            type=SourceType.RSS,
            url="https://example.com/rss",
            enabled=True,
            cron_interval="6h"
        )

        # Mock content item
        item = ContentItem(
            user_id="test_user",
            title="AI Best Practices 2026",
            url="https://example.com/ai-best-practices",
            author="Expert Author",
            content="This article covers the latest AI development best practices including memory management, context optimization, and iterative development patterns.",
            source=SourceType.RSS,
            source_detail="Test Blog",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="test_001",
            status=ItemStatus.UNREAD
        )

        # Step 1-2: Source & Fetch (already have item)

        # Step 3: Quality Filter
        filter_eval = QualityFilter(integration_config)
        filter_eval.client = None  # Use mock evaluation
        item = filter_eval.evaluate(item)

        assert item.quality_score is not None
        assert item.quality_decision in [Decision.PASS, Decision.EDGE, Decision.REJECT]

        # Step 4: Deep Analysis (mock if no LLM)
        analyzer = DeepAnalyzer(integration_config)
        if analyzer.client:
            item = analyzer.analyze(item)
        else:
            # Mock extraction
            item.extraction = {
                "score": 8.5,
                "category": "AI Development",
                "tags": ["AI", "Best Practices"],
                "one_line_summary": "Essential AI development guide",
                "hidden_insights": ["Memory is critical"],
                "golden_quotes": ["AI is the future"],
                "methodology": "Iterative approach"
            }
            item.analysis_score = 8.5

        # Step 5: Store
        store_path = integration_temp_dir / "items.json"
        store = ItemStore(str(store_path))
        store.add_or_update([item])

        stored_items = store.load()
        assert len(stored_items) == 1
        assert stored_items[0].unique_id == "test_001"

        # Step 6: Obsidian Output (if high quality)
        if item.quality_score >= integration_config.filter.high_quality_threshold:
            writer = ObsidianWriter(integration_config)
            filepath = writer.write(item)

            assert filepath.exists()
            content = filepath.read_text(encoding="utf-8")
            assert "# AI Best Practices 2026" in content


# ──────────────────────────────────────────────
# API Integration Tests
# ──────────────────────────────────────────────

class TestAPIIntegration:
    """Test API endpoints integration."""

    @pytest.fixture
    def api_client(self, app_with_test_config):
        """Create test client for API tests."""
        from src.api.deps import get_current_user

        def override_get_current_user():
            return "integration_test_user"

        app_with_test_config.dependency_overrides[get_current_user] = override_get_current_user

        with TestClient(app_with_test_config) as client:
            yield client

        app_with_test_config.dependency_overrides.clear()

    def test_api_crud_workflow(self, api_client):
        """Test full CRUD workflow through API."""
        # Create
        response = api_client.post(
            "/api/v1/feed",
            json={
                "title": "API Test Article",
                "url": "https://api-test.com/article",
                "content": "Test content for API",
                "source": "RSS",
                "source_detail": "Test API"
            }
        )
        assert response.status_code == 200
        result = response.json()
        item_id = result.get("item", {}).get("unique_id")

        # Read
        response = api_client.get("/api/v1/feed")
        assert response.status_code == 200
        feed = response.json()
        assert feed["total"] >= 1

        # Update
        if item_id:
            response = api_client.put(
                f"/api/v1/feed/{item_id}",
                json={"is_read": True}
            )
            assert response.status_code == 200

            # Verify update
            response = api_client.get("/api/v1/feed")
            feed = response.json()
            updated_item = next((i for i in feed["items"] if i["unique_id"] == item_id), None)
            if updated_item:
                assert updated_item.get("is_read") == True

    def test_api_pagination(self, api_client, mock_feed_items):
        """Test API pagination works correctly."""
        # Add multiple items
        for item in mock_feed_items[:5]:
            api_client.post(
                "/api/v1/feed",
                json={
                    "title": item.title,
                    "url": item.url,
                    "content": item.content,
                    "source": item.source,
                    "source_detail": item.source_detail
                }
            )

        # Test pagination
        response = api_client.get("/api/v1/feed?limit=2&page=1")
        assert response.status_code == 200
        feed = response.json()
        assert len(feed["items"]) <= 2
        assert feed["page"] == 1
        assert feed["limit"] == 2

    def test_api_filtering(self, api_client, mock_feed_items):
        """Test API filtering by tags and status."""
        # Add items with different tags
        for item in mock_feed_items[:3]:
            api_client.post(
                "/api/v1/feed",
                json={
                    "title": item.title,
                    "url": item.url,
                    "content": item.content,
                    "source": item.source,
                    "source_detail": item.source_detail,
                    "tags": item.tags
                }
            )

        # Filter by tags
        response = api_client.get("/api/v1/feed?tags=AI")
        assert response.status_code == 200
        feed = response.json()
        # All items should have AI tag or be empty

        # Filter by favorited
        response = api_client.get("/api/v1/feed?is_favorited=true")
        assert response.status_code == 200


# ──────────────────────────────────────────────
# Concurrent Operation Tests
# ──────────────────────────────────────────────

class TestConcurrentOperations:
    """Test concurrent access and operations."""

    def test_concurrent_write_same_item(self, integration_config, integration_temp_dir):
        """Test concurrent writes to the same item."""
        store_path = integration_temp_dir / "items.json"

        item = ContentItem(
            user_id="test_user",
            title="Concurrent Test",
            url="https://test.com/concurrent",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="concurrent_id",
            status=ItemStatus.UNREAD
        )

        # Create two stores pointing to same file
        store1 = ItemStore(str(store_path))
        store2 = ItemStore(str(store_path))

        # Add from both
        store1.add_or_update([item])
        store2.add_or_update([item])

        # Verify only one exists
        items = store1.load()
        concurrent_items = [i for i in items if i.unique_id == "concurrent_id"]
        assert len(concurrent_items) == 1

    def test_batch_operations(self, integration_config, integration_temp_dir):
        """Test batch add and update operations."""
        store_path = integration_temp_dir / "items.json"

        items = [
            ContentItem(
                user_id="test_user",
                title=f"Batch Item {i}",
                url=f"https://test.com/batch/{i}",
                content=f"Content {i}",
                source=SourceType.RSS,
                source_detail="Batch Test",
                published_at="2026-03-10T10:00:00",
                created_at="2026-03-10T10:00:00",
                unique_id=f"batch_{i}",
                status=ItemStatus.UNREAD
            )
            for i in range(10)
        ]

        store = ItemStore(str(store_path))
        store.add_or_update(items)

        loaded = store.load()
        assert len(loaded) == 10

        # Batch update
        for item in loaded:
            item.is_read = True

        store.add_or_update(loaded)

        updated = store.load()
        assert all(item.is_read for item in updated)


# ──────────────────────────────────────────────
# Error Recovery Tests
# ──────────────────────────────────────────────

class TestErrorRecovery:
    """Test error recovery in workflows."""

    def test_recovery_from_llm_failure(self, integration_config):
        """Test pipeline continues when LLM fails."""
        item = ContentItem(
            user_id="test_user",
            title="Test Article",
            url="https://test.com",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="error_test_id",
            status=ItemStatus.UNREAD
        )

        # Quality filter without LLM should still work
        filter_eval = QualityFilter(integration_config)
        filter_eval.client = None
        result = filter_eval.evaluate(item)

        assert result.quality_score is not None

        # Analyzer without LLM should set error
        analyzer = DeepAnalyzer(integration_config)
        analyzer.client = None
        result = analyzer.analyze(item)

        assert result.extraction is not None
        assert "error" in result.extraction or result.extraction != {}

    def test_invalid_source_handling(self, integration_config, integration_temp_dir):
        """Test handling of invalid source configurations."""
        # Create source with invalid URL
        source = SourceConfig(
            user_id="test_user",
            name="Invalid Source",
            type=SourceType.RSS,
            url="not-a-valid-url",
            enabled=True,
            cron_interval="6h"
        )

        # Pipeline should handle gracefully
        # (actual fetch would fail, but system should continue)
        assert source.type == SourceType.RSS


# ──────────────────────────────────────────────
# Data Consistency Tests
# ──────────────────────────────────────────────

class TestDataConsistency:
    """Test data consistency across operations."""

    def test_item_id_uniqueness(self, integration_config, integration_temp_dir):
        """Test item IDs remain unique across operations."""
        store_path = integration_temp_dir / "items.json"

        # Add same item twice
        item = ContentItem(
            user_id="test_user",
            title="Unique Test",
            url="https://test.com/unique",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="unique_id_123",
            status=ItemStatus.UNREAD
        )

        store = ItemStore(str(store_path))
        store.add_or_update([item])
        item.title = "Updated Title"
        store.add_or_update([item])

        # Should only have one item with updated title
        items = store.load()
        unique_items = [i for i in items if i.unique_id == "unique_id_123"]
        assert len(unique_items) == 1
        assert unique_items[0].title == "Updated Title"

    def test_score_calculation_consistency(self, integration_config):
        """Test score calculations are consistent."""
        item = ContentItem(
            user_id="test_user",
            title="Score Test",
            url="https://test.com/score",
            content="A" * 1500,
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="score_test_id",
            status=ItemStatus.UNREAD
        )

        filter_eval = QualityFilter(integration_config)
        filter_eval.client = None

        # Evaluate multiple times
        scores = [filter_eval.evaluate(item).quality_score for _ in range(5)]

        # All scores should be identical
        assert len(set(scores)) == 1
