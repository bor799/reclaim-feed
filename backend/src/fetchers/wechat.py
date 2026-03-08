# -*- coding: utf-8 -*-
"""WeChat Inbox Fetcher — 从本地文件读取微信链接"""

from typing import List, Dict, Any
from pathlib import Path

from .base import BaseFetcher
from ..models import ContentItem, AppConfig, SourceConfig, SourceType
from ..config import expand_path


class WechatFetcher(BaseFetcher):
    """微信 Inbox 文件读取"""

    def __init__(self, config: AppConfig, source: SourceConfig):
        super().__init__(config, source)
        self.inbox_path = source.extra.get("inbox_path", "~/.nanobot/workspace/wechat_inbox.txt")

    def fetch(self) -> List[Dict[str, Any]]:
        inbox = expand_path(self.inbox_path)
        if not inbox.exists():
            return []
        with open(inbox, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip().startswith("http")]
        return [{"url": url} for url in lines]

    def parse(self, raw_data: List[Dict[str, Any]]) -> List[ContentItem]:
        return [
            ContentItem(
                title="",  # 后续由 extractor 填充
                url=item["url"],
                source=SourceType.WECHAT,
                source_detail="wechat/inbox",
                unique_id=item["url"],
            )
            for item in raw_data
        ]
