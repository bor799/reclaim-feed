# -*- coding: utf-8 -*-
"""
Pipeline 核心编排 — 不可变主流程

Fetch → Filter → Analyze → Output

每个阶段只关心「输入 → 输出」，不知道其他阶段的实现细节。
所有行为由外部 Prompt 配置驱动。
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from .models import ContentItem, AppConfig, Decision


class Pipeline:
    """
    不可变知识萃取管道

    Usage:
        config = load_config("config.yaml")
        pipeline = Pipeline(config)
        results = await pipeline.run()
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self._fetchers = []
        self._setup_fetchers()

    def _setup_fetchers(self):
        """根据配置初始化 Fetchers"""
        from .fetchers.rss import RSSFetcher
        from .fetchers.twitter import TwitterFetcher
        from .fetchers.wechat import WechatFetcher

        fetcher_map = {
            "rss": RSSFetcher,
            "twitter": TwitterFetcher,
            "wechat": WechatFetcher,
        }

        for source in self.config.sources:
            if not source.enabled:
                continue
            fetcher_cls = fetcher_map.get(source.type)
            if fetcher_cls:
                self._fetchers.append(fetcher_cls(self.config, source))

    # ──────────────────────────────────────────
    # Stage 1: Fetch
    # ──────────────────────────────────────────

    async def fetch(self, source_name: Optional[str] = None) -> List[ContentItem]:
        """并发抓取所有已配置信息源，或指定单个配置源"""
        target_fetchers = self._fetchers
        # filter by source name if provided. Assuming fetchers have .source attribute or similar.
        # Actually base fetcher saves it as self.source
        if source_name:
            target_fetchers = [f for f in self._fetchers if getattr(f, 'source', None) and f.source.name == source_name]

        print(f"📡 Fetch: {len(target_fetchers)} 个源")

        tasks = [self._fetch_one(f) for f in target_fetchers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items = []
        for result in results:
            if isinstance(result, Exception):
                print(f"  ❌ 抓取失败: {result}")
            elif isinstance(result, list):
                all_items.extend(result)

        print(f"  ✅ 总计 {len(all_items)} 条内容")
        return all_items

    async def _fetch_one(self, fetcher) -> List[ContentItem]:
        """异步包装同步 Fetcher"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fetcher.run)

    # ──────────────────────────────────────────
    # Stage 2: Filter (LLM 评分)
    # ──────────────────────────────────────────

    async def filter(self, items: List[ContentItem]) -> List[ContentItem]:
        """LLM 质量评分 + 过滤"""
        from .processors.quality_filter import QualityFilter

        print(f"🔍 Filter: {len(items)} 条待评分")

        quality_filter = QualityFilter(self.config)
        scored_items = quality_filter.evaluate_batch(items)

        passed = [i for i in scored_items
                  if i.quality_decision == Decision.PASS]
        edge = [i for i in scored_items
                if i.quality_decision == Decision.EDGE]

        print(f"  ✅ 通过 {len(passed)}, 边缘 {len(edge)}, "
              f"拒绝 {len(scored_items) - len(passed) - len(edge)}")

        # 高分 + 边缘都进入下一阶段
        return passed + edge

    # ──────────────────────────────────────────
    # Stage 3: Analyze (深度萃取)
    # ──────────────────────────────────────────

    async def analyze(self, items: List[ContentItem]) -> List[ContentItem]:
        """LLM 深度知识萃取"""
        from .processors.analyzer import DeepAnalyzer

        print(f"🧠 Analyze: {len(items)} 条待萃取")

        analyzer = DeepAnalyzer(self.config)
        analyzed = analyzer.batch_analyze(items)

        passed = [i for i in analyzed if i.passed_threshold]
        print(f"  ✅ 萃取完成, {len(passed)} 条达标")
        return analyzed

    # ──────────────────────────────────────────
    # Stage 4: Output (多渠道路由)
    # ──────────────────────────────────────────

    async def output(self, items: List[ContentItem]) -> None:
        """输出到各消费渠道"""
        from .outputs.obsidian import ObsidianWriter
        from .outputs.store import ItemStore

        high_score = [i for i in items if i.passed_threshold]

        # 内置 Store（前端 Feed 用）
        store = ItemStore(self.config)
        store.save_batch(items)
        print(f"💾 Store: 保存 {len(items)} 条")

        # Obsidian（仅高分）
        if self.config.output.obsidian_root and high_score:
            obsidian = ObsidianWriter(self.config)
            paths = obsidian.batch_write(high_score)
            print(f"📝 Obsidian: 写入 {len(paths)} 条")

        # TODO: Telegram / 飞书 / 邮件（Phase 2）

    # ──────────────────────────────────────────
    # 主流程
    # ──────────────────────────────────────────

    async def run(self, dry_run: bool = False, source_name: Optional[str] = None) -> List[ContentItem]:
        """
        执行完整 Pipeline

        Fetch → Filter → Analyze → Output
        """
        print(f"🚀 100X Knowledge Agent Pipeline 启动 (Source: {source_name or 'All'})\n")

        # Stage 1
        items = await self.fetch(source_name=source_name)
        if not items:
            print("\n📭 无新内容")
            return []

        # Stage 2
        filtered = await self.filter(items)
        if not filtered:
            print("\n📭 无内容通过质量评估")
            return []

        # Stage 3
        analyzed = await self.analyze(filtered)
        if not analyzed:
            print("\n📭 无内容完成萃取")
            return []

        # Stage 4
        if not dry_run:
            await self.output(analyzed)
        else:
            print("\n🔇 干运行模式: 跳过输出")

        print(f"\n✨ 完成! {len(analyzed)} 条内容已处理")
        return analyzed
