# -*- coding: utf-8 -*-
"""
Tag Parser — 解析 Markdown 中的内联标签

从用户保存的 Markdown 内容中提取 #标签 格式的字符串，
自动关联到全局标签宽表。
"""

import re
from typing import List


# 匹配 #xxx 格式的标签（支持中英文、数字、下划线、连字符）
# 排除 Markdown 标题 (## xxx) 和纯数字标签 (#123)
TAG_PATTERN = re.compile(
    r'(?<!\w)#([A-Za-z\u4e00-\u9fff][\w\u4e00-\u9fff\-]*)',
    re.UNICODE,
)


def parse_tags(markdown_content: str) -> List[str]:
    """
    从 Markdown 文本中解析出所有 #标签。

    Args:
        markdown_content: 用户编写的 Markdown 文本

    Returns:
        去重后的标签列表 (不含 # 前缀)

    Examples:
        >>> parse_tags("这是 #AI 和 #Agent 相关的笔记")
        ['AI', 'Agent']
        >>> parse_tags("## 标题不算\\n#Karpathy推荐 是标签")
        ['Karpathy推荐']
    """
    if not markdown_content:
        return []

    # 排除 Markdown 标题行 (以 # 开头的行)
    lines = markdown_content.split('\n')
    non_heading_text = '\n'.join(
        line for line in lines
        if not line.strip().startswith('# ')
        and not line.strip().startswith('## ')
        and not line.strip().startswith('### ')
        and not line.strip().startswith('#### ')
    )

    matches = TAG_PATTERN.findall(non_heading_text)

    # 去重但保持顺序
    seen = set()
    unique_tags = []
    for tag in matches:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags


def compute_tag_diff(old_tags: List[str], new_tags: List[str]) -> dict:
    """
    计算标签差异，用于增量同步

    Returns:
        {"added": [...], "removed": [...]}
    """
    old_set = set(old_tags)
    new_set = set(new_tags)
    return {
        "added": list(new_set - old_set),
        "removed": list(old_set - new_set),
    }
