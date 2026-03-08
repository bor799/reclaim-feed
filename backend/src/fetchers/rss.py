# -*- coding: utf-8 -*-
"""
RSS Fetcher — 从配置的 RSS 源抓取内容

迁移自 v1 rss.py，适配新架构。
"""

from typing import List, Dict, Any
from datetime import datetime

import feedparser

from .base import BaseFetcher
from ..models import ContentItem, AppConfig, SourceConfig, SourceType


class RSSFetcher(BaseFetcher):
    """RSS / Atom 订阅源抓取器"""

    def __init__(self, config: AppConfig, source: SourceConfig):
        super().__init__(config, source)
        self.feed_url = source.url or ""
        self.source_name = source.name

    def fetch(self) -> List[Dict[str, Any]]:
        if not self.feed_url:
            return []
        try:
            feed = feedparser.parse(self.feed_url)
            return feed.entries
        except Exception as e:
            print(f"    ❌ RSS 解析失败 [{self.source_name}]: {e}")
            return []

    def parse(self, raw_data: List[Dict[str, Any]]) -> List[ContentItem]:
        items = []
        for entry in raw_data:
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                content = entry.summary or ""

            published = ""
            if hasattr(entry, "published"):
                published = entry.published

            items.append(ContentItem(
                title=entry.get("title", ""),
                url=entry.get("link", ""),
                author=entry.get("author", self.source_name),
                content=content,
                source=SourceType.RSS,
                source_detail=self.source_name,
                published_at=published,
                unique_id=entry.get("id", entry.get("link", "")),
                category=self.source.category or "",
            ))
        return items
