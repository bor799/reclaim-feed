# -*- coding: utf-8 -*-
"""
Twitter Fetcher — 通过 Agent-Reach CLI 抓取推文

依赖: Agent-Reach (pip install agent-reach)
"""

from typing import List, Dict, Any

from .base import BaseFetcher
from ..models import ContentItem, AppConfig, SourceConfig, SourceType


class TwitterFetcher(BaseFetcher):
    """Twitter 推文抓取器（通过 Agent-Reach）"""

    def __init__(self, config: AppConfig, source: SourceConfig):
        super().__init__(config, source)

    def fetch(self) -> List[Dict[str, Any]]:
        # TODO: 集成 Agent-Reach xreach CLI
        # xreach search "query" --json
        # xreach timeline "username" --json
        print("    ⚠️  TwitterFetcher: 待集成 Agent-Reach")
        return []

    def parse(self, raw_data: List[Dict[str, Any]]) -> List[ContentItem]:
        items = []
        for tweet in raw_data:
            items.append(ContentItem(
                title=tweet.get("text", "")[:100],
                url=tweet.get("url", ""),
                author=tweet.get("author", ""),
                content=tweet.get("text", ""),
                source=SourceType.TWITTER,
                source_detail=f"twitter/{tweet.get('author', '')}",
                published_at=tweet.get("created_at", ""),
                unique_id=tweet.get("id", ""),
            ))
        return items
