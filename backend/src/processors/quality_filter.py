# -*- coding: utf-8 -*-
"""
QualityFilter — LLM 质量评分

从外部 Prompt (config/prompts/scoring.md) 驱动评分逻辑。
迁移自 v1 source_quality_evaluator.py。
"""

import json
import re
from typing import List

from zhipuai import ZhipuAI

from ..models import ContentItem, AppConfig, Decision
from ..config import load_prompt


class QualityFilter:
    """LLM 驱动的内容质量评分器"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.threshold_high = config.filter.high_quality_threshold
        self.threshold_edge = config.filter.edge_case_threshold

        # 加载外部评分 Prompt
        self.scoring_prompt = load_prompt(config.filter.scoring_prompt)
        if not self.scoring_prompt:
            self.scoring_prompt = self._default_prompt()

        # 初始化 LLM
        self.client = None
        try:
            import os
            api_key = os.environ.get(config.llm.api_key_env, "")
            if api_key:
                self.client = ZhipuAI(api_key=api_key, base_url=config.llm.api_base)
        except Exception as e:
            print(f"    ⚠️ LLM 客户端初始化失败: {e}")

    def evaluate(self, item: ContentItem) -> ContentItem:
        """评估单条内容"""
        if not self.client:
            return self._mock_evaluate(item)

        try:
            prompt = self.scoring_prompt.format(
                source=item.source_detail,
                title=item.title,
                url=item.url,
                content=item.content[:3000],
                focus_areas="、".join(self.config.focus_areas),
            )

            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=[
                    {"role": "system", "content": "你是内容质量评估专家，返回纯 JSON。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.llm.temperature,
            )

            result = self._parse_response(response.choices[0].message.content)
            item.quality_score = result.get("score", 0)
            item.quality_reason = result.get("reason", "")

        except Exception as e:
            print(f"    ⚠️ 评分失败 [{item.title[:30]}]: {e}")
            item.quality_score = 5.0
            item.quality_reason = "评分异常，使用默认分"

        # 决策
        if item.quality_score >= self.threshold_high:
            item.quality_decision = Decision.PASS
        elif item.quality_score >= self.threshold_edge:
            item.quality_decision = Decision.EDGE
        else:
            item.quality_decision = Decision.REJECT

        return item

    def evaluate_batch(self, items: List[ContentItem]) -> List[ContentItem]:
        """批量评估"""
        results = []
        for i, item in enumerate(items, 1):
            print(f"    [{i}/{len(items)}] {item.title[:40]}...")
            results.append(self.evaluate(item))
        return results

    def _parse_response(self, text: str) -> dict:
        """解析 LLM JSON 响应"""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"score": 0, "reason": "解析失败"}

    def _mock_evaluate(self, item: ContentItem) -> ContentItem:
        """无 LLM 时的规则评分"""
        score = 5.0
        if len(item.content) > 1000:
            score += 1
        if len(item.content) > 2000:
            score += 1
        item.quality_score = min(10, max(0, score))
        item.quality_decision = (
            Decision.PASS if score >= self.threshold_high
            else Decision.EDGE if score >= self.threshold_edge
            else Decision.REJECT
        )
        item.quality_reason = "规则评分（无 LLM）"
        return item

    def _default_prompt(self) -> str:
        return """你是内容质量评估专家。

## 输入
- 来源：{source}
- 标题：{title}
- 链接：{url}
- 内容：{content}

## 用户关注领域
{focus_areas}

## 输出 JSON
{{"score": <0-10>, "passed": <true/false>, "decision": "<通过/边缘/拒绝>", "reason": "<理由>"}}
"""
