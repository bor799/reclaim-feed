# -*- coding: utf-8 -*-
"""
Prompt 版本管理器

管理四大阶段 Prompt 的读取、更新、版本回溯。
每个 Prompt 文件对应一个 stage: scoring, extraction, obsidian_format, publish。
历史版本存储在 config/prompts/history/{stage}/ 目录下。
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from ..config import PROJECT_ROOT


PROMPT_DIR = PROJECT_ROOT / "config" / "prompts"
HISTORY_DIR = PROMPT_DIR / "history"

# 四大阶段映射
STAGE_FILES = {
    "scoring": "scoring.md",
    "extraction": "extraction.md",
    "obsidian_format": "obsidian_format.md",
    "publish": "publish.md",
}


def get_prompt(stage: str) -> Optional[str]:
    """
    读取指定阶段的当前 Prompt

    Args:
        stage: scoring | extraction | obsidian_format | publish
    """
    filename = STAGE_FILES.get(stage)
    if not filename:
        return None

    filepath = PROMPT_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None


def update_prompt(stage: str, content: str) -> Dict:
    """
    更新指定阶段的 Prompt，旧版本自动归档

    Args:
        stage: 阶段名
        content: 新 Prompt 内容

    Returns:
        {"stage": str, "version": int, "updated_at": str}
    """
    filename = STAGE_FILES.get(stage)
    if not filename:
        raise ValueError(f"未知阶段: {stage}")

    filepath = PROMPT_DIR / filename

    # 归档旧版本
    version = 1
    if filepath.exists():
        stage_history_dir = HISTORY_DIR / stage
        stage_history_dir.mkdir(parents=True, exist_ok=True)

        # 计算版本号
        existing_versions = sorted(stage_history_dir.glob(f"v*.md"))
        if existing_versions:
            last_version = int(existing_versions[-1].stem.replace("v", ""))
            version = last_version + 1
        else:
            version = 1

        # 备份当前版本
        archive_name = f"v{version}.md"
        shutil.copy2(filepath, stage_history_dir / archive_name)

        # 保存元数据
        meta_file = stage_history_dir / f"v{version}.meta.json"
        meta_file.write_text(json.dumps({
            "version": version,
            "archived_at": datetime.now().isoformat(),
            "stage": stage,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        version += 1  # 新版本号

    # 写入新内容
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

    return {
        "stage": stage,
        "version": version,
        "updated_at": datetime.now().isoformat(),
    }


def get_prompt_history(stage: str) -> List[Dict]:
    """
    获取指定阶段的历史版本列表

    Returns:
        [{"version": 1, "archived_at": "...", "preview": "..."}, ...]
    """
    filename = STAGE_FILES.get(stage)
    if not filename:
        return []

    stage_history_dir = HISTORY_DIR / stage
    if not stage_history_dir.exists():
        return []

    versions = []
    for meta_file in sorted(stage_history_dir.glob("v*.meta.json")):
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        # 加载前 200 字符作为预览
        prompt_file = meta_file.with_suffix("").with_suffix(".md")
        preview = ""
        if prompt_file.exists():
            full_text = prompt_file.read_text(encoding="utf-8")
            preview = full_text[:200]
        meta["preview"] = preview
        versions.append(meta)

    return versions


def get_prompt_version(stage: str, version: int) -> Optional[str]:
    """获取指定阶段的指定历史版本内容"""
    stage_history_dir = HISTORY_DIR / stage
    filepath = stage_history_dir / f"v{version}.md"
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None
