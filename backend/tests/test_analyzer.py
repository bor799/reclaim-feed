# -*- coding: utf-8 -*-
"""
Test suite for DeepAnalyzer module (processors/analyzer.py)

Tests LLM deep extraction functionality including:
- Successful analysis with LLM
- LLM error handling
- Response parsing
- Batch analysis
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models import ContentItem, AppConfig, SourceType, ItemStatus, Decision
from src.processors.analyzer import DeepAnalyzer


@pytest.fixture
def analyzer_config():
    """Create test config for analyzer."""
    config = AppConfig()
    config.llm = Mock()
    config.llm.api_key_env = "TEST_API_KEY"
    config.llm.api_base = "https://api.test.com"
    config.llm.model = "test-model"
    config.llm.temperature = 0.7
    config.filter = Mock()
    config.filter.high_quality_threshold = 7.0
    config.focus_areas = ["AI", "Technology"]
    config.extraction = Mock()
    config.extraction.prompt = "extraction.md"
    return config


@pytest.fixture
def sample_item():
    """Create sample content item."""
    return ContentItem(
        user_id="test_user",
        title="AI Development Guide",
        url="https://example.com/ai",
        content="This is a comprehensive guide about AI development with deep insights.",
        source=SourceType.RSS,
        source_detail="Tech Blog",
        published_at="2026-03-10T10:00:00",
        created_at="2026-03-10T10:00:00",
        unique_id="test_id_1",
        quality_score=8.0,
        category="Technology",
        tags=["AI"],
        status=ItemStatus.UNREAD
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response JSON."""
    return {
        "score": 9.0,
        "category": "AI Development",
        "tags": ["AI", "Deep Learning", "Best Practices"],
        "one_line_summary": "Comprehensive guide covering AI development patterns",
        "hidden_insights": [
            "Memory management is critical for agents",
            "Context windows determine agent capabilities"
        ],
        "golden_quotes": [
            "The future of AI is agentic"
        ],
        "methodology": "Build iteratively with clear milestones",
        "reread_worthy": True,
        "reason": "High quality with actionable insights"
    }


class TestAnalyzeSuccess:
    """Test successful analysis scenarios."""

    @patch('src.processors.analyzer.ZhipuAI')
    def test_analyze_success(self, mock_zhipu, analyzer_config, sample_item, mock_llm_response):
        """Test successful analysis with valid LLM response."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = str(mock_llm_response)
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        assert result.extraction is not None
        assert result.extraction.get("score") == 9.0
        assert result.analysis_score == 9.0
        assert result.passed_threshold == True
        assert result.category == "AI Development"
        assert result.tags == ["AI", "Deep Learning", "Best Practices"]
        assert result.reread_worthy == True

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_with_real_extraction(self, mock_zhipu, analyzer_config, sample_item, mock_llm_response):
        """Test analysis populates all extraction fields."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = str(mock_llm_response)
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        assert "one_line_summary" in result.extraction
        assert "hidden_insights" in result.extraction
        assert "golden_quotes" in result.extraction
        assert "methodology" in result.extraction


class TestAnalyzeError:
    """Test error handling in analysis."""

    def test_analyze_no_client(self, analyzer_config, sample_item):
        """Test analysis when LLM client is not initialized."""
        analyzer = DeepAnalyzer(analyzer_config)
        analyzer.client = None

        result = analyzer.analyze(sample_item)

        assert result.extraction == {"error": "LLM 未配置"}

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_llm_api_error(self, mock_zhipu, analyzer_config, sample_item):
        """Test analysis when LLM API raises exception."""
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(side_effect=Exception("API Error"))
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        assert "error" in result.extraction

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_invalid_json(self, mock_zhipu, analyzer_config, sample_item):
        """Test analysis with invalid JSON response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        # Should handle gracefully with default values
        assert result.extraction is not None


class TestAnalyzeParseResponse:
    """Test response parsing functionality."""

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_parse_response_markdown_wrapped(self, mock_zhipu, analyzer_config, sample_item):
        """Test parsing JSON wrapped in markdown code blocks."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '''```json
{"score": 8.5, "category": "AI"}
```'''
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        assert result.extraction.get("score") == 8.5

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_parse_response_with_text_before(self, mock_zhipu, analyzer_config, sample_item):
        """Test parsing JSON with text before it."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '''Here's the analysis:
{"score": 7.5, "reason": "Good content"}
That's my assessment.'''
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        analyzer = DeepAnalyzer(analyzer_config)
        result = analyzer.analyze(sample_item)

        assert result.extraction.get("score") == 7.5


class TestAnalyzeBatch:
    """Test batch analysis functionality."""

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_batch_multiple(self, mock_zhipu, analyzer_config, mock_llm_response):
        """Test batch analyzing multiple items."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = str(mock_llm_response)
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        items = [
            ContentItem(
                user_id="test_user",
                title=f"Article {i}",
                url=f"https://example.com/{i}",
                content=f"Content {i}",
                source=SourceType.RSS,
                source_detail="Test",
                published_at="2026-03-10T10:00:00",
                created_at="2026-03-10T10:00:00",
                unique_id=f"id_{i}",
                quality_score=7.0,
                status=ItemStatus.UNREAD
            )
            for i in range(3)
        ]

        analyzer = DeepAnalyzer(analyzer_config)
        results = analyzer.batch_analyze(items)

        assert len(results) == 3
        assert all(item.extraction is not None for item in results)
        assert mock_client.chat.completions.create.call_count == 3

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_batch_handles_errors(self, mock_zhipu, analyzer_config, mock_llm_response):
        """Test batch handles individual item failures."""
        mock_client = Mock()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("API Error")
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = str(mock_llm_response)
            return mock_response

        mock_client.chat.completions.create = Mock(side_effect=side_effect)
        mock_zhipu.return_value = mock_client

        items = [
            ContentItem(
                user_id="test_user",
                title=f"Article {i}",
                url=f"https://example.com/{i}",
                content=f"Content {i}",
                source=SourceType.RSS,
                source_detail="Test",
                published_at="2026-03-10T10:00:00",
                created_at="2026-03-10T10:00:00",
                unique_id=f"id_{i}",
                quality_score=7.0,
                status=ItemStatus.UNREAD
            )
            for i in range(3)
        ]

        analyzer = DeepAnalyzer(analyzer_config)
        results = analyzer.batch_analyze(items)

        assert len(results) == 3
        # First and third should succeed, second should have error
        assert results[0].extraction is not None
        assert "error" in results[1].extraction
        assert results[2].extraction is not None


class TestAnalyzeContentTruncation:
    """Test content handling in analysis."""

    @patch('src.processors.analyzer.ZhipuAI')
    @patch.dict('os.environ', {'TEST_API_KEY': 'test-key-123'})
    def test_analyze_truncates_long_content(self, mock_zhipu, analyzer_config, mock_llm_response):
        """Test long content is truncated for LLM."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = str(mock_llm_response)
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        mock_zhipu.return_value = mock_client

        # Create item with very long content
        long_content = "A" * 10000
        sample_item = ContentItem(
            user_id="test_user",
            title="Long Article",
            url="https://example.com/long",
            content=long_content,
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="long_id",
            quality_score=7.0,
            status=ItemStatus.UNREAD
        )

        analyzer = DeepAnalyzer(analyzer_config)
        analyzer.analyze(sample_item)

        # Verify content was truncated (first 6000 chars)
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][1]['content']
        assert len(prompt) < 10000  # Should be truncated


class TestAnalyzeDefaultPrompt:
    """Test default prompt generation."""

    def test_default_prompt_when_missing(self, analyzer_config):
        """Test default prompt is used when file is missing."""
        with patch('src.processors.analyzer.load_prompt', return_value=None):
            analyzer = DeepAnalyzer(analyzer_config)
            assert analyzer.extraction_prompt is not None
            assert "{title}" in analyzer.extraction_prompt
            assert "{content}" in analyzer.extraction_prompt
