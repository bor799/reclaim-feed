# -*- coding: utf-8 -*-
"""
抽象基类 — 所有 Fetcher 必须继承

迁移自 v1，增加 Pydantic ContentItem 支持。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, date
import json

from ..models import ContentItem, AppConfig, SourceConfig
from ..config import get_state_path


class BaseFetcher(ABC):
    """数据抓取器抽象基类"""

    def __init__(self, config: AppConfig, source: SourceConfig):
        self.config = config
        self.source = source
        self.state = self._load_state()

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """抓取原始数据"""
        pass

    @abstractmethod
    def parse(self, raw_data: List[Dict[str, Any]]) -> List[ContentItem]:
        """解析为统一 ContentItem 格式"""
        pass

    def _state_key(self) -> str:
        return f"{self.__class__.__name__.lower().replace('fetcher', '')}_state.json"

    def _load_state(self) -> Dict[str, Any]:
        """加载增量状态"""
        state_file = get_state_path(self._state_key())
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"processed_ids": [], "last_fetch": None}

    def _save_state(self) -> None:
        """保存增量状态"""
        self.state["last_fetch"] = datetime.now().isoformat()
        state_file = get_state_path(self._state_key())
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def is_processed(self, unique_id: str) -> bool:
        return unique_id in self.state.get("processed_ids", [])

    def mark_processed(self, unique_id: str) -> None:
        if "processed_ids" not in self.state:
            self.state["processed_ids"] = []
        self.state["processed_ids"].append(unique_id)
        self._save_state()

    def run(self) -> List[ContentItem]:
        """执行抓取 + 解析 + 去重"""
        name = self.__class__.__name__
        print(f"  ⏳ {name}: 抓取中...")

        raw = self.fetch()
        items = self.parse(raw)

        # 去重
        new_items = []
        for item in items:
            if item.unique_id and not self.is_processed(item.unique_id):
                new_items.append(item)
                self.mark_processed(item.unique_id)

        print(f"  ✅ {name}: {len(raw)} 条原始 → {len(new_items)} 条新内容")
        return new_items
