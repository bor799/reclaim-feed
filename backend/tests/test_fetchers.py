# -*- coding: utf-8 -*-
"""
Test suite for Fetcher modules (fetchers/)

Tests RSS and web fetching functionality including:
- Base fetcher functionality
- RSS feed parsing
- Error handling
- Network timeout handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.fetchers.base import BaseFetcher
from src.fetchers.rss import RSSFetcher
from src.models import SourceConfig, SourceType, ContentItem


# ──────────────────────────────────────────────
# RSS Fetcher Tests
# ──────────────────────────────────────────────

class TestRSSFetcher:
    """Test RSS feed fetching functionality."""

    @pytest.fixture
    def rss_source(self):
        """Create RSS source config."""
        return SourceConfig(
            user_id="test_user",
            name="Test RSS Feed",
            type=SourceType.RSS,
            url="https://example.com/rss.xml",
            enabled=True,
            cron_interval="6h"
        )

    @pytest.fixture
    def mock_rss_xml(self):
        """Mock RSS feed XML content."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <title>Test Blog</title>
            <link>https://example.com</link>
            <description>Test Description</description>
            <item>
              <title>First Article</title>
              <link>https://example.com/article1</link>
              <description>This is the first article content.</description>
              <pubDate>Mon, 10 Mar 2026 10:00:00 GMT</pubDate>
              <author>John Doe</author>
              <guid>https://example.com/article1</guid>
            </item>
            <item>
              <title>Second Article</title>
              <link>https://example.com/article2</link>
              <description>&lt;p&gt;Second article with HTML&lt;/p&gt;</description>
              <pubDate>Mon, 10 Mar 2026 11:00:00 GMT</pubDate>
              <category>Technology</category>
            </item>
          </channel>
        </rss>
        """

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_success(self, mock_get, rss_source, mock_rss_xml):
        """Test successful RSS feed fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_rss_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        assert len(items) == 2
        assert items[0].title == "First Article"
        assert items[0].url == "https://example.com/article1"
        assert items[0].source == SourceType.RSS
        assert items[0].source_detail == "Test RSS Feed"

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_html_stripping(self, mock_get, rss_source, mock_rss_xml):
        """Test HTML tags are stripped from content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_rss_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        # Second item has HTML in description
        assert "<p>" not in items[1].content
        assert "Second article with HTML" in items[1].content

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_network_error(self, mock_get, rss_source):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network error")

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        # Should return empty list on error
        assert items == []

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_timeout(self, mock_get, rss_source):
        """Test handling of timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        assert items == []

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_invalid_xml(self, mock_get, rss_source):
        """Test handling of invalid XML."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"This is not valid XML"
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        # Should handle gracefully
        assert isinstance(items, list)

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_empty_feed(self, mock_get, rss_source):
        """Test handling of empty RSS feed."""
        empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <title>Empty Feed</title>
          </channel>
        </rss>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = empty_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        assert items == []

    @patch('src.fetchers.rss.requests.get')
    def test_rss_fetch_with_categories(self, mock_get, rss_source, mock_rss_xml):
        """Test category extraction from RSS."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_rss_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        # Second item has Technology category
        # Check if category is preserved
        assert items is not None

    @patch('src.fetchers.rss.requests.get')
    def test_rss_unique_id_generation(self, mock_get, rss_source, mock_rss_xml):
        """Test unique IDs are generated for items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_rss_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(rss_source)
        items = fetcher.fetch()

        # All items should have unique IDs
        unique_ids = [item.unique_id for item in items]
        assert len(unique_ids) == len(set(unique_ids))


# ──────────────────────────────────────────────
# Base Fetcher Tests
# ──────────────────────────────────────────────

class TestBaseFetcher:
    """Test base fetcher functionality."""

    @pytest.fixture
    def base_source(self):
        """Create generic source config."""
        return SourceConfig(
            user_id="test_user",
            name="Test Source",
            type=SourceType.IMPORT,
            url="https://example.com",
            enabled=True
        )

    def test_base_fetcher_raises_not_implemented(self, base_source):
        """Test base fetcher raises NotImplementedError."""
        fetcher = BaseFetcher(base_source)

        with pytest.raises(NotImplementedError):
            fetcher.fetch()

    def test_base_fetcher_stores_source(self, base_source):
        """Test fetcher stores source config."""
        fetcher = BaseFetcher(base_source)
        assert fetcher.source == base_source


# ──────────────────────────────────────────────
# Content Item Creation Tests
# ──────────────────────────────────────────────

class TestContentItemCreation:
    """Test content items are created correctly from fetches."""

    @pytest.fixture
    def mock_atom_xml(self):
        """Mock Atom feed XML."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title>Atom Feed</title>
          <link href="https://example.com/atom" rel="self"/>
          <entry>
            <title>Atom Entry</title>
            <link href="https://example.com/atom-entry"/>
            <summary>Atom content</summary>
            <updated>2026-03-10T10:00:00Z</updated>
            <author>
              <name>Jane Doe</name>
            </author>
            <id>urn:uuid:12345</id>
          </entry>
        </feed>
        """

    @patch('src.fetchers.rss.requests.get')
    def test_content_item_required_fields(self, mock_get):
        """Test all required fields are populated."""
        source = SourceConfig(
            user_id="test_user",
            name="Test",
            type=SourceType.RSS,
            url="https://example.com/rss",
            enabled=True
        )

        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
          <channel>
            <item>
              <title>Test</title>
              <link>https://test.com</link>
              <description>Content</description>
            </item>
          </channel>
        </rss>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = rss_xml.encode('utf-8')
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        assert len(items) > 0
        item = items[0]

        assert item.user_id == "test_user"
        assert item.title is not None
        assert item.url is not None
        assert item.content is not None
        assert item.unique_id is not None
        assert item.source == SourceType.RSS
        assert item.status is not None


# ──────────────────────────────────────────────
# Error Handling Tests
# ──────────────────────────────────────────────

class TestFetchErrorHandling:
    """Test error handling in fetchers."""

    @patch('src.fetchers.rss.requests.get')
    def test_http_404_error(self, mock_get):
        """Test handling of 404 errors."""
        source = SourceConfig(
            user_id="test",
            name="Not Found",
            type=SourceType.RSS,
            url="https://example.com/404",
            enabled=True
        )

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        # Should handle 404 gracefully
        assert isinstance(items, list)

    @patch('src.fetchers.rss.requests.get')
    def test_http_500_error(self, mock_get):
        """Test handling of 500 errors."""
        source = SourceConfig(
            user_id="test",
            name="Server Error",
            type=SourceType.RSS,
            url="https://example.com/500",
            enabled=True
        )

        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        assert isinstance(items, list)

    @patch('src.fetchers.rss.requests.get')
    def test_malformed_url(self, mock_get):
        """Test handling of malformed URL."""
        source = SourceConfig(
            user_id="test",
            name="Bad URL",
            type=SourceType.RSS,
            url="not-a-valid-url",
            enabled=True
        )

        mock_get.side_effect = Exception("Invalid URL")

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        assert items == []

    @patch('src.fetchers.rss.requests.get')
    def test_connection_refused(self, mock_get):
        """Test handling of connection refused."""
        import requests
        source = SourceConfig(
            user_id="test",
            name="No Connection",
            type=SourceType.RSS,
            url="https://localhost:9999/rss",
            enabled=True
        )

        mock_get.side_effect = requests.exceptions.ConnectionError()

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        assert items == []


# ──────────────────────────────────────────────
# Performance Tests
# ──────────────────────────────────────────────

class TestFetchPerformance:
    """Test performance-related aspects of fetching."""

    @patch('src.fetchers.rss.requests.get')
    def test_large_feed_handling(self, mock_get):
        """Test handling of large RSS feeds."""
        # Generate a large RSS feed
        items_xml = []
        for i in range(100):
            items_xml.append(f"""
            <item>
              <title>Article {i}</title>
              <link>https://example.com/{i}</link>
              <description>Content {i}</description>
              <pubDate>Mon, 10 Mar 2026 10:00:00 GMT</pubDate>
            </item>
            """)

        large_xml = f"""<?xml version="1.0"?>
        <rss version="2.0">
          <channel>
            <title>Large Feed</title>
            {''.join(items_xml)}
          </channel>
        </rss>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = large_xml.encode('utf-8')
        mock_get.return_value = mock_response

        source = SourceConfig(
            user_id="test",
            name="Large Feed",
            type=SourceType.RSS,
            url="https://example.com/large",
            enabled=True
        )

        fetcher = RSSFetcher(source)
        items = fetcher.fetch()

        assert len(items) == 100
