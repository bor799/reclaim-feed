# -*- coding: utf-8 -*-
"""
配置加载器

支持 YAML 配置文件 + 环境变量覆盖。
Prompt 从外部 Markdown 文件读取。
"""

import os
from pathlib import Path
from typing import Optional

import yaml
from .models import AppConfig


# 项目根目录（backend/）
PROJECT_ROOT = Path(__file__).parent.parent


def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """
    加载配置文件

    优先级: 环境变量 > config.yaml > 默认值
    """
    config_file = PROJECT_ROOT / config_path

    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    else:
        print(f"⚠️  配置文件不存在: {config_file}, 使用默认配置")
        raw = {}

    # 环境变量覆盖 LLM API Key
    if "ZHIPU_API_KEY" in os.environ:
        raw.setdefault("llm", {})["api_key"] = os.environ["ZHIPU_API_KEY"]

    return AppConfig(**raw)


def load_prompt(prompt_path: str) -> str:
    """
    加载外部 Prompt 文件

    Args:
        prompt_path: 相对于 PROJECT_ROOT 的路径，如 "config/prompts/scoring.md"

    Returns:
        Prompt 文本内容
    """
    full_path = PROJECT_ROOT / prompt_path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    else:
        print(f"⚠️  Prompt 文件不存在: {full_path}")
        return ""


def get_state_path(filename: str) -> Path:
    """获取状态文件路径"""
    state_dir = PROJECT_ROOT / "state"
    state_dir.mkdir(exist_ok=True)
    return state_dir / filename


def expand_path(path: str) -> Path:
    """展开 ~ 和环境变量"""
    return Path(os.path.expanduser(path)).expanduser()
