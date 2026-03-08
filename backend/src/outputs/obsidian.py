# -*- coding: utf-8 -*-
"""
ObsidianWriter — 写入 Markdown + Dataview 兼容 Frontmatter

迁移自 v1 obsidian.py。
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List

from ..models import ContentItem, AppConfig
from ..config import expand_path


class ObsidianWriter:
    """Obsidian Markdown 写入器"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.output_root = expand_path(config.output.obsidian_root)

    def write(self, item: ContentItem) -> Path:
        """写入单条内容到 Obsidian"""
        # 确定输出目录
        category_dir = self.output_root / (item.category or "未分类")
        category_dir.mkdir(parents=True, exist_ok=True)

        # 文件名
        safe_title = self._safe_filename(item.title)
        filepath = category_dir / f"{safe_title}.md"

        # 构建 Markdown
        content = self._build_markdown(item)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def batch_write(self, items: List[ContentItem]) -> List[Path]:
        paths = []
        for item in items:
            try:
                path = self.write(item)
                paths.append(path)
            except Exception as e:
                print(f"    ⚠️ 写入失败 [{item.title[:30]}]: {e}")
        return paths

    def _build_markdown(self, item: ContentItem) -> str:
        """构建 Markdown 内容（含 Dataview Frontmatter）"""
        extraction = item.extraction or {}

        # Frontmatter
        frontmatter = f"""---
title: "{item.title}"
source: "{item.source_detail}"
category: "{item.category}"
score: {item.analysis_score or item.quality_score or 0}
status: "{item.status}"
reread_worthy: {str(item.reread_worthy).lower()}
tags: {item.tags}
date: {datetime.now().strftime('%Y-%m-%d')}
source_url: "{item.url}"
---
"""

        # 正文
        body_parts = [f"# {item.title}\n"]

        if extraction.get("one_line_summary"):
            body_parts.append(f"> {extraction['one_line_summary']}\n")

        if extraction.get("hidden_insights"):
            body_parts.append("## 🔍 水下信息\n")
            for insight in extraction["hidden_insights"]:
                body_parts.append(f"- {insight}")
            body_parts.append("")

        if extraction.get("golden_quotes"):
            body_parts.append("## 💎 核心金句\n")
            for quote in extraction["golden_quotes"]:
                body_parts.append(f"> {quote}\n")

        if extraction.get("methodology"):
            body_parts.append(f"## 🔧 可复用方法论\n\n{extraction['methodology']}\n")

        body_parts.append(f"\n---\n📎 原文: [{item.url}]({item.url})")

        return frontmatter + "\n".join(body_parts)

    def _safe_filename(self, title: str) -> str:
        """生成安全文件名"""
        safe = re.sub(r'[\\/*?:"<>|]', "", title)
        return safe[:80].strip() or "untitled"
