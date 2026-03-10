# -*- coding: utf-8 -*-
"""
ItemStore — 内置 JSON 存储（供前端 Feed 读取）

支持 CRUD 操作与高级搜索过滤。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

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

    def get_by_id(self, item_id: str) -> Optional[dict]:
        """根据 unique_id 获取单条记录"""
        data = self._load()
        return data.get(item_id)

    def update_item(self, item_id: str, updates: Dict[str, Any]) -> Optional[dict]:
        """
        部分更新单条记录

        Args:
            item_id: unique_id
            updates: 要更新的字段字典

        Returns:
            更新后的 item dict，如果不存在返回 None
        """
        data = self._load()
        if item_id not in data:
            return None

        item = data[item_id]

        # 如果更新了 annotation，自动解析标签
        if "annotation" in updates and updates["annotation"]:
            from ..utils import parse_tags
            parsed_tags = parse_tags(updates["annotation"])
            existing_tags = set(item.get("tags", []))
            existing_tags.update(parsed_tags)
            item["tags"] = list(existing_tags)
            item["is_annotated"] = True

        # 合并更新
        for key, value in updates.items():
            if value is not None:
                item[key] = value

        data[item_id] = item
        self._write(data)
        return item

    def search(
        self,
        user_id: str = "local_admin",
        search_query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date: Optional[str] = None,
        is_favorited: Optional[bool] = None,
        is_read: Optional[bool] = None,
        is_annotated: Optional[bool] = None,
    ) -> List[dict]:
        """
        高级搜索过滤

        所有参数可组合使用，形成 AND 逻辑。
        """
        items = self.get_all()

        # 按租户过滤
        items = [i for i in items if i.get("user_id", "local_admin") == user_id]

        # 日期精确匹配 (如 "2026-03-09")
        if date:
            items = [
                i for i in items
                if (i.get("published_at") or i.get("created_at") or "").startswith(date)
            ]

        # 日期范围
        if start_date:
            items = [
                i for i in items
                if (i.get("published_at") or i.get("created_at") or "") >= start_date
            ]
        if end_date:
            items = [
                i for i in items
                if (i.get("published_at") or i.get("created_at") or "") <= end_date + "T23:59:59"
            ]

        # 关键词搜索（标题 + 内容）
        if search_query:
            q = search_query.lower()
            items = [
                i for i in items
                if q in (i.get("title") or "").lower()
                or q in (i.get("content") or "").lower()
                or q in (i.get("annotation") or "").lower()
            ]

        # 标签过滤（任意匹配）
        if tags:
            tag_set = set(tags)
            items = [
                i for i in items
                if tag_set.intersection(set(i.get("tags", [])))
            ]

        # 布尔过滤
        if is_favorited is not None:
            items = [i for i in items if i.get("is_favorited", False) == is_favorited]

        if is_read is not None:
            items = [i for i in items if i.get("is_read", False) == is_read]

        if is_annotated is not None:
            items = [
                i for i in items
                if bool(i.get("is_annotated") or i.get("annotation")) == is_annotated
            ]

        return items

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
