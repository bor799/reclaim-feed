# -*- coding: utf-8 -*-
"""命令行入口"""

import argparse
import asyncio
import sys
from pathlib import Path

from .config import load_config
from .pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser(
        description="100X 知识 Agent — 做深不做宽",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  knowledge-agent                  # 运行完整 Pipeline
  knowledge-agent --dry-run        # 干运行（不写入）
  knowledge-agent --url URL        # 分析单个 URL
  knowledge-agent serve            # 启动 FastAPI 服务
        """,
    )
    parser.add_argument("--dry-run", action="store_true", help="干运行模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--url", type=str, help="分析单个 URL")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--port", type=int, default=None, help="服务端口 (默认使用环境变量 PORT 或 8000)")
    parser.add_argument("command", nargs="?", default="run", help="run | serve")

    args = parser.parse_args()

    config = load_config(args.config)

    if args.command == "serve":
        from .api.main import start_server
        start_server(config, port=args.port)
    else:
        asyncio.run(Pipeline(config).run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
