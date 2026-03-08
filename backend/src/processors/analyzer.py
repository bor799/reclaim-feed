# -*- coding: utf-8 -*-
"""
DeepAnalyzer — LLM 深度知识萃取

从外部 Prompt (config/prompts/extraction.md) 驱动萃取格式。
这是产品核心价值所在 — 做深不做宽。
"""

import json
import re
from typing import List

from zhipuai import ZhipuAI

from ..models import ContentItem, AppConfig
from ..config import load_prompt


class DeepAnalyzer:
    """LLM 深度萃取引擎"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.extraction_prompt = load_prompt(config.extraction.prompt)
        if not self.extraction_prompt:
            self.extraction_prompt = self._default_prompt()

        self.client = None
        try:
            import os
            api_key = os.environ.get(config.llm.api_key_env, "")
            if api_key:
                self.client = ZhipuAI(api_key=api_key, base_url=config.llm.api_base)
        except Exception as e:
            print(f"    ⚠️ DeepAnalyzer LLM 初始化失败: {e}")

    def analyze(self, item: ContentItem) -> ContentItem:
        """深度萃取单条内容"""
        if not self.client:
            item.extraction = {"error": "LLM 未配置"}
            return item

        try:
            prompt = self.extraction_prompt.format(
                title=item.title,
                url=item.url,
                content=item.content[:6000],
                source=item.source_detail,
                focus_areas="、".join(self.config.focus_areas),
            )

            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=[
                    {"role": "system", "content": "你是深度知识萃取专家，返回 JSON。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.llm.temperature,
            )

            result = self._parse_response(response.choices[0].message.content)
            item.extraction = result
            item.analysis_score = result.get("score", item.quality_score or 0)
            item.passed_threshold = item.analysis_score >= self.config.filter.high_quality_threshold
            item.category = result.get("category", item.category)
            item.tags = result.get("tags", item.tags)
            item.reread_worthy = result.get("reread_worthy", False)

        except Exception as e:
            print(f"    ⚠️ 萃取失败 [{item.title[:30]}]: {e}")
            item.extraction = {"error": str(e)}

        return item

    def batch_analyze(self, items: List[ContentItem]) -> List[ContentItem]:
        results = []
        for i, item in enumerate(items, 1):
            print(f"    [{i}/{len(items)}] 萃取: {item.title[:40]}...")
            results.append(self.analyze(item))
        return results

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"error": "解析失败"}

    def _default_prompt(self) -> str:
        return """你是深度知识萃取专家。

## 输入
- 标题：{title}
- 来源：{source}
- 链接：{url}
- 内容：{content}

## 用户关注：{focus_areas}

## 输出 JSON（必须包含以下字段）
{{
  "score": <0-10>,
  "category": "<分类>",
  "tags": ["标签1", "标签2"],
  "one_line_summary": "<一句话总结>",
  "hidden_insights": ["<水下信息1>", "<水下信息2>"],
  "golden_quotes": ["<金句1>"],
  "methodology": "<可复用方法论>",
  "reread_worthy": <true/false>,
  "reason": "<评分理由>"
}}
"""
