# -*- coding: utf-8 -*-
"""
Test suite for QualityFilter module (processors/quality_filter.py)

Tests LLM quality evaluation functionality including:
- Evaluation with different thresholds
- Edge cases handling
- Mock evaluation without LLM
- Decision logic
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import ContentItem, AppConfig, SourceType, ItemStatus, Decision
from src.processors.quality_filter import QualityFilter


@pytest.fixture
def filter_config():
    """Create test config for quality filter."""
    config = AppConfig()
    config.llm = Mock()
    config.llm.api_key_env = "TEST_API_KEY"
    config.llm.api_base = "https://api.test.com"
    config.llm.model = "test-model"
    config.llm.temperature = 0.5
    config.filter = Mock()
    config.filter.high_quality_threshold = 7.0
    config.filter.edge_case_threshold = 5.0
    config.filter.scoring_prompt = "scoring.md"
    config.focus_areas = ["AI", "Technology"]
    return config


@pytest.fixture
def sample_item():
    """Create sample content item."""
    return ContentItem(
        user_id="test_user",
        title="AI Development Guide",
        url="https://example.com/ai",
        content="This is a comprehensive guide about AI development with deep insights and actionable advice.",
        source=SourceType.RSS,
        source_detail="Tech Blog",
        published_at="2026-03-10T10:00:00",
        created_at="2026-03-10T10:00:00",
        unique_id="test_id_1",
        status=ItemStatus.UNREAD
    )


class TestEvaluateThresholds:
    """Test evaluation with different threshold configurations."""

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_high_quality_pass(self, mock_zhipu, filter_config, sample_item):
        """Test evaluation scores above high threshold pass."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 8.5, "reason": "Excellent content"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 8.5
        assert result.quality_decision == Decision.PASS
        assert result.quality_reason == "Excellent content"

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_edge_case(self, mock_zhipu, filter_config, sample_item):
        """Test evaluation scores between thresholds return EDGE."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 6.0, "reason": "Decent but lacks depth"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 6.0
        assert result.quality_decision == Decision.EDGE

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_low_quality_reject(self, mock_zhipu, filter_config, sample_item):
        """Test evaluation scores below edge threshold are rejected."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 3.0, "reason": "Low quality content"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 3.0
        assert result.quality_decision == Decision.REJECT

    def test_evaluate_custom_thresholds(self, sample_item):
        """Test evaluation with custom threshold values."""
        config = AppConfig()
        config.llm = Mock()
        config.llm.api_key_env = "TEST_API_KEY"
        config.filter = Mock()
        config.filter.high_quality_threshold = 8.0
        config.filter.edge_case_threshold = 6.0
        config.focus_areas = ["AI"]
        config.filter.scoring_prompt = "scoring.md"

        filter_eval = QualityFilter(config)
        assert filter_eval.threshold_high == 8.0
        assert filter_eval.threshold_edge == 6.0


class TestEvaluateEdgeCases:
    """Test edge case scenarios."""

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_exact_high_threshold(self, mock_zhipu, filter_config, sample_item):
        """Test score exactly at high threshold passes."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 7.0, "reason": "At threshold"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 7.0
        assert result.quality_decision == Decision.PASS

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_exact_edge_threshold(self, mock_zhipu, filter_config, sample_item):
        """Test score exactly at edge threshold returns EDGE."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 5.0, "reason": "At edge"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 5.0
        assert result.quality_decision == Decision.EDGE

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_zero_score(self, mock_zhipu, filter_config, sample_item):
        """Test zero score is rejected."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 0, "reason": "No value"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 0
        assert result.quality_decision == Decision.REJECT

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_perfect_score(self, mock_zhipu, filter_config, sample_item):
        """Test perfect score passes."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 10, "reason": "Perfect"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 10
        assert result.quality_decision == Decision.PASS


class TestEvaluateNoLLM:
    """Test mock evaluation without LLM."""

    def test_evaluate_no_client_rule_based(self, filter_config, sample_item):
        """Test evaluation falls back to rules without LLM client."""
        filter_eval = QualityFilter(filter_config)
        filter_eval.client = None

        result = filter_eval.evaluate(sample_item)

        assert result.quality_score is not None
        assert result.quality_decision is not None
        assert "规则评分" in result.quality_reason

    def test_mock_evaluate_content_length_scoring(self, filter_config):
        """Test mock evaluation scores based on content length."""
        filter_eval = QualityFilter(filter_config)
        filter_eval.client = None

        # Short content
        short_item = ContentItem(
            user_id="test",
            title="Short",
            url="https://test.com",
            content="Short content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="short_id",
            status=ItemStatus.UNREAD
        )

        result = filter_eval.evaluate(short_item)
        base_score = 5.0
        assert result.quality_score == base_score  # No bonus for short content

        # Long content (>2000 chars)
        long_item = ContentItem(
            user_id="test",
            title="Long",
            url="https://test.com",
            content="A" * 2500,
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="long_id",
            status=ItemStatus.UNREAD
        )

        result = filter_eval.evaluate(long_item)
        assert result.quality_score > base_score  # Bonus for long content
        assert result.quality_score <= 10  # Max score


class TestDecisionLogic:
    """Test decision making logic."""

    def test_decision_pass_when_above_high_threshold(self, filter_config):
        """Test PASS decision for scores above high threshold."""
        filter_eval = QualityFilter(filter_config)

        item = ContentItem(
            user_id="test",
            title="Test",
            url="https://test.com",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="test_id",
            quality_score=7.5,
            status=ItemStatus.UNREAD
        )

        result = filter_eval.evaluate(item)
        assert result.quality_decision == Decision.PASS

    def test_decision_edge_between_thresholds(self, filter_config):
        """Test EDGE decision for scores between thresholds."""
        filter_eval = QualityFilter(filter_config)

        item = ContentItem(
            user_id="test",
            title="Test",
            url="https://test.com",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="test_id",
            quality_score=6.0,
            status=ItemStatus.UNREAD
        )

        result = filter_eval.evaluate(item)
        assert result.quality_decision == Decision.EDGE

    def test_decision_reject_below_edge_threshold(self, filter_config):
        """Test REJECT decision for scores below edge threshold."""
        filter_eval = QualityFilter(filter_config)

        item = ContentItem(
            user_id="test",
            title="Test",
            url="https://test.com",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="test_id",
            quality_score=4.0,
            status=ItemStatus.UNREAD
        )

        result = filter_eval.evaluate(item)
        assert result.quality_decision == Decision.REJECT


class TestEvaluateBatch:
    """Test batch evaluation functionality."""

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_evaluate_batch_multiple(self, mock_zhipu, filter_config):
        """Test batch evaluating multiple items."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"score": 7.5, "reason": "Good"}'
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        items = [
            ContentItem(
                user_id="test",
                title=f"Article {i}",
                url=f"https://test.com/{i}",
                content=f"Content {i}",
                source=SourceType.RSS,
                source_detail="Test",
                published_at="2026-03-10T10:00:00",
                created_at="2026-03-10T10:00:00",
                unique_id=f"id_{i}",
                status=ItemStatus.UNREAD
            )
            for i in range(3)
        ]

        filter_eval = QualityFilter(filter_config)
        results = filter_eval.evaluate_batch(items)

        assert len(results) == 3
        assert all(item.quality_score == 7.5 for item in results)
        assert mock_client.chat.completions.create.call_count == 3


class TestParseResponse:
    """Test LLM response parsing."""

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_parse_response_with_markdown(self, mock_zhipu, filter_config, sample_item):
        """Test parsing JSON wrapped in markdown."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '''```json
{"score": 8.0, "reason": "Good content"}
```'''
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        assert result.quality_score == 8.0

    @patch('src.processors.quality_filter.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_parse_response_invalid_json(self, mock_zhipu, filter_config, sample_item):
        """Test handling invalid JSON response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "This is not JSON at all"
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        filter_eval = QualityFilter(filter_config)
        result = filter_eval.evaluate(sample_item)

        # Should still assign a score
        assert result.quality_score is not None
        assert result.quality_reason == "解析失败"


class TestDefaultPrompt:
    """Test default prompt handling."""

    def test_default_prompt_when_missing(self, filter_config):
        """Test default prompt is used when file is missing."""
        with patch('src.processors.quality_filter.load_prompt', return_value=None):
            filter_eval = QualityFilter(filter_config)
            assert filter_eval.scoring_prompt is not None
            assert "{source}" in filter_eval.scoring_prompt
            assert "{title}" in filter_eval.scoring_prompt
