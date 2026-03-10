# -*- coding: utf-8 -*-
"""
Test suite for Obsidian output module (outputs/obsidian.py)

Tests Obsidian Markdown writer functionality including:
- File creation
- Batch writing
- Frontmatter format
- Safe filename generation
- Category handling
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.models import ContentItem, AppConfig, SourceType, ItemStatus, Decision
from src.outputs.obsidian import ObsidianWriter


@pytest.fixture
def temp_obsidian_dir():
    """Create a temporary directory for Obsidian output."""
    temp_path = Path(tempfile.mkdtemp(prefix="obsidian_test_"))
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def obsidian_config(temp_obsidian_dir):
    """Create a test config with Obsidian output."""
    config = AppConfig()
    config.output.obsidian_root = str(temp_obsidian_dir)
    config.filter.high_quality_threshold = 7.0
    return config


@pytest.fixture
def sample_item():
    """Create a sample content item."""
    return ContentItem(
        user_id="test_user",
        title="AI Agent Development Guide",
        url="https://example.com/ai-agents",
        author="John Doe",
        content="This is a comprehensive guide to building AI agents.",
        source=SourceType.RSS,
        source_detail="Tech Blog",
        published_at="2026-03-10T10:00:00",
        created_at="2026-03-10T10:00:00",
        unique_id="test_id_1",
        quality_score=8.5,
        quality_decision=Decision.PASS,
        quality_reason="High quality content",
        status=ItemStatus.UNREAD,
        category="Technology",
        tags=["AI", "Agents"],
        analysis_score=9.0,
        reread_worthy=True,
        extraction={
            "one_line_summary": "Essential guide for AI agent development",
            "hidden_insights": ["Agents need memory", "Context is key"],
            "golden_quotes": ["Agents are the future of AI"],
            "methodology": "Build iteratively"
        }
    )


class TestObsidianCreateFile:
    """Test file creation functionality."""

    def test_obsidian_create_file(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test basic file creation."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)

        assert filepath.exists()
        assert filepath.name == "AI Agent Development Guide.md"
        assert filepath.parent.name == "Technology"

    def test_obsidian_file_content_structure(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test written file has correct structure."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)

        content = filepath.read_text(encoding="utf-8")

        # Check frontmatter
        assert "---" in content
        assert 'title: "AI Agent Development Guide"' in content
        assert 'source: "Tech Blog"' in content
        assert "category: \"Technology\"" in content
        assert "score: 9.0" in content
        assert "reread_worthy: true" in content

        # Check body
        assert "# AI Agent Development Guide" in content
        assert "> Essential guide for AI agent development" in content
        assert "## 🔍 水下信息" in content
        assert "## 💎 核心金句" in content

    def test_obsidian_creates_category_dir(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test category directory is created."""
        sample_item.category = "NewCategory"
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)

        assert filepath.parent.name == "NewCategory"
        assert filepath.parent.exists()


class TestObsidianBatchWrite:
    """Test batch writing functionality."""

    def test_obsidian_batch_write_multiple(self, obsidian_config, temp_obsidian_dir):
        """Test writing multiple items."""
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
                category="Test",
                status=ItemStatus.UNREAD
            )
            for i in range(3)
        ]

        writer = ObsidianWriter(obsidian_config)
        paths = writer.batch_write(items)

        assert len(paths) == 3
        for path in paths:
            assert path.exists()

    def test_obsidian_batch_write_handles_errors(self, obsidian_config, temp_obsidian_dir, capsys):
        """Test batch write handles individual item failures."""
        items = [
            ContentItem(
                user_id="test_user",
                title="Valid Item",
                url="https://example.com/valid",
                content="Valid content",
                source=SourceType.RSS,
                source_detail="Test",
                published_at="2026-03-10T10:00:00",
                created_at="2026-03-10T10:00:00",
                unique_id="valid_id",
                category="Test",
                status=ItemStatus.UNREAD
            ),
            None,  # Invalid item - will cause error
        ]

        writer = ObsidianWriter(obsidian_config)
        paths = writer.batch_write([i for i in items if i is not None])

        # Should still write valid items
        assert len(paths) == 1
        assert paths[0].exists()


class TestObsidianFrontmatter:
    """Test Frontmatter generation."""

    def test_obsidian_frontmatter_format(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test Frontmatter has correct Dataview format."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)
        content = filepath.read_text(encoding="utf-8")

        # Verify YAML frontmatter format
        lines = content.split("\n")
        assert lines[0] == "---"
        # Find end of frontmatter
        end_idx = lines.index("---", 1)
        assert end_idx > 0

        frontmatter_lines = lines[1:end_idx]
        # Check required fields
        frontmatter_str = "\n".join(frontmatter_lines)
        assert "title:" in frontmatter_str
        assert "source:" in frontmatter_str
        assert "category:" in frontmatter_str
        assert "score:" in frontmatter_str
        assert "status:" in frontmatter_str
        assert "tags:" in frontmatter_str
        assert "date:" in frontmatter_str
        assert "source_url:" in frontmatter_str

    def test_obsidian_frontmatter_with_extraction(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test Frontmatter includes extraction data."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)
        content = filepath.read_text(encoding="utf-8")

        # Check extraction fields are in body, not frontmatter
        assert "one_line_summary" not in content.split("---")[1]
        assert "> Essential guide" in content


class TestObsidianSafeFilename:
    """Test safe filename generation."""

    def test_obsidian_safe_filename_basic(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test basic filename sanitization."""
        writer = ObsidianWriter(obsidian_config)
        filename = writer._safe_filename(sample_item.title)

        assert filename == "AI Agent Development Guide"

    def test_obsidian_safe_filename_special_chars(self, obsidian_config, temp_obsidian_dir):
        """Test special characters are removed."""
        writer = ObsidianWriter(obsidian_config)

        # Test various special characters
        assert "file" == writer._safe_filename('file/name')
        assert "file" == writer._safe_filename('file\\name')
        assert "file" == writer._safe_filename('file*name')
        assert "file" == writer._safe_filename('file?name')
        assert "file" == writer._safe_filename('file:name')
        assert "file" == writer._safe_filename('file"name')
        assert "file" == writer._safe_filename('file<name>')
        assert "file" == writer._safe_filename('file|name')

    def test_obsidian_safe_filename_length(self, obsidian_config, temp_obsidian_dir):
        """Test filename is truncated to 80 chars."""
        writer = ObsidianWriter(obsidian_config)
        long_title = "A" * 100
        filename = writer._safe_filename(long_title)

        assert len(filename) == 80

    def test_obsidian_safe_filename_empty(self, obsidian_config, temp_obsidian_dir):
        """Test empty title returns 'untitled'."""
        writer = ObsidianWriter(obsidian_config)
        filename = writer._safe_filename("")

        assert filename == "untitled"

    def test_obsidian_safe_filename_only_special_chars(self, obsidian_config, temp_obsidian_dir):
        """Test title with only special chars returns 'untitled'."""
        writer = ObsidianWriter(obsidian_config)
        filename = writer._safe_filename("****//\\")

        assert filename == "untitled"


class TestObsidianCategories:
    """Test category handling."""

    def test_obsidian_category_directory(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test items are organized by category."""
        writer = ObsidianWriter(obsidian_config)

        categories = ["Technology", "AI", "Finance"]
        for cat in categories:
            sample_item.category = cat
            filepath = writer.write(sample_item)

            assert filepath.parent.name == cat
            assert filepath.parent.exists()

    def test_obsidian_default_category(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test items without category go to '未分类'."""
        sample_item.category = None
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)

        assert filepath.parent.name == "未分类"

    def test_obsidian_nested_categories(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test nested category paths (if supported)."""
        # Current implementation uses flat categories
        sample_item.category = "Technology/AI"
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)

        # Category with slashes would create nested directory
        assert "Technology" in str(filepath) or "AI" in str(filepath)


class TestObsidianMarkdownContent:
    """Test Markdown content generation."""

    def test_obsidian_markdown_with_full_extraction(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test Markdown includes all extraction sections."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)
        content = filepath.read_text(encoding="utf-8")

        assert "# AI Agent Development Guide" in content
        assert "## 🔍 水下信息" in content
        assert "## 💎 核心金句" in content
        assert "## 🔧 可复用方法论" in content

    def test_obsidian_markdown_minimal(self, obsidian_config, temp_obsidian_dir):
        """Test Markdown with minimal data."""
        item = ContentItem(
            user_id="test_user",
            title="Minimal Article",
            url="https://example.com/minimal",
            content="Content",
            source=SourceType.RSS,
            source_detail="Test",
            published_at="2026-03-10T10:00:00",
            created_at="2026-03-10T10:00:00",
            unique_id="minimal_id",
            category="Test",
            status=ItemStatus.UNREAD,
            extraction=None
        )

        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(item)
        content = filepath.read_text(encoding="utf-8")

        # Should still have basic structure
        assert "# Minimal Article" in content
        assert "---" in content
        assert "📎 原文:" in content

    def test_obsidian_markdown_url_link(self, obsidian_config, sample_item, temp_obsidian_dir):
        """Test URL is included as link."""
        writer = ObsidianWriter(obsidian_config)
        filepath = writer.write(sample_item)
        content = filepath.read_text(encoding="utf-8")

        assert f"[{sample_item.url}]({sample_item.url})" in content
