# -*- coding: utf-8 -*-
"""
ItemStore — 内置 JSON 存储（供前端 Feed 读取）
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from ..models import ContentItem, AppConfig
from ..config import get_state_path


class ItemStore:
    """本地 JSON 存储"""

    def __init__(self, config: AppConfig):
        self.store_path = get_state_path("items.json")

    def save_batch(self, items: List[ContentItem]) -> None:
        """追加保存"""
        existing = self._load()
        for item in items:
            existing[item.unique_id] = item.model_dump()
        self._write(existing)

    def get_all(self) -> List[dict]:
        return list(self._load().values())

    def get_by_date(self, date_str: str) -> List[dict]:
        return [
            item for item in self._load().values()
            if item.get("published_at", "").startswith(date_str)
        ]

    def _load(self) -> dict:
        if self.store_path.exists():
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _write(self, data: dict) -> None:
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
