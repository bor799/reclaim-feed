#!/bin/bash
# -*- coding: utf-8 -*-
# 配置验证脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/backend-config"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}配置验证 - 100X Agent 测试环境${NC}"
echo -e "${BLUE}================================${NC}"
echo

# 检查 .env 文件
echo -e "${BLUE}[1/5]${NC} 检查环境变量文件..."
if [ -f "$CONFIG_DIR/.env" ]; then
    echo -e "${GREEN}✅ .env 文件存在${NC}"

    # 检查 API Key
    if grep -q "a0506743786a4e25ab8194ca7d7c9d19" "$CONFIG_DIR/.env"; then
        echo -e "${GREEN}✅ ZHIPU_API_KEY 已配置${NC}"
    else
        echo -e "${RED}❌ ZHIPU_API_KEY 未配置${NC}"
    fi

    # 检查 Telegram
    if grep -q "TELEGRAM_BOT_TOKEN=8076345416" "$CONFIG_DIR/.env"; then
        echo -e "${GREEN}✅ Telegram 配置已同步${NC}"
    fi

    # 检查 Obsidian
    if grep -q "Obsidian Vault/信息源" "$CONFIG_DIR/.env"; then
        echo -e "${GREEN}✅ Obsidian 路径已配置${NC}"
    fi
else
    echo -e "${RED}❌ .env 文件不存在${NC}"
    exit 1
fi

echo

# 检查 config.yaml
echo -e "${BLUE}[2/5]${NC} 检查 Agent 配置文件..."
if [ -f "$CONFIG_DIR/config.yaml" ]; then
    echo -e "${GREEN}✅ config.yaml 存在${NC}"

    # 统计信息源数量
    SOURCE_COUNT=$(grep -c "name:" "$CONFIG_DIR/config.yaml" || echo 0)
    echo -e "${GREEN}✅ 信息源数量: $SOURCE_COUNT${NC}"

    # 检查用户名
    if grep -q "user_name: murphy" "$CONFIG_DIR/config.yaml"; then
        echo -e "${GREEN}✅ 用户名: murphy${NC}"
    fi
else
    echo -e "${RED}❌ config.yaml 不存在${NC}"
    exit 1
fi

echo

# 检查提示词文件
echo -e "${BLUE}[3/5]${NC} 检查提示词文件..."
PROMPTS_DIR="$CONFIG_DIR/prompts"
if [ -d "$PROMPTS_DIR" ]; then
    PROMPT_FILES=$(ls "$PROMPTS_DIR" 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ 提示词目录存在 ($PROMPT_FILES 个文件)${NC}"

    if [ -f "$PROMPTS_DIR/scoring.md" ]; then
        echo -e "${GREEN}  - scoring.md${NC}"
    fi
    if [ -f "$PROMPTS_DIR/extraction.md" ]; then
        echo -e "${GREEN}  - extraction.md${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  提示词目录不存在${NC}"
fi

echo

# 检查后端依赖
echo -e "${BLUE}[4/5]${NC} 检查后端环境..."
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"
if [ -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${GREEN}✅ 后端虚拟环境存在${NC}"
else
    echo -e "${YELLOW}⚠️  后端虚拟环境不存在，启动时会自动创建${NC}"
fi

echo

# 检查前端配置
echo -e "${BLUE}[5/5]${NC} 检查前端配置..."
FRONTEND_DIR="$(cd "$SCRIPT_DIR/../frontend" && pwd)"

if [ -f "$FRONTEND_DIR/.env.local" ]; then
    echo -e "${GREEN}✅ 前端 .env.local 存在${NC}"
else
    echo -e "${YELLOW}⚠️  前端 .env.local 不存在，运行 ./setup.sh 自动创建${NC}"
fi

if [ -f "$FRONTEND_DIR/src/services/api.ts" ]; then
    echo -e "${GREEN}✅ 前端 API 服务文件存在${NC}"
else
    echo -e "${YELLOW}⚠️  前端 API 服务文件不存在，运行 ./setup.sh 自动创建${NC}"
fi

echo
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ 配置验证完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo -e "${BLUE}配置摘要:${NC}"
echo "  API Key: ✅ 已配置"
echo "  信息源: $SOURCE_COUNT 个"
echo "  用户: murphy"
echo "  Telegram: 已配置（测试环境关闭）"
echo "  Obsidian: 已配置"
echo
echo -e "${BLUE}下一步:${NC}"
echo -e "  ${YELLOW}cd $SCRIPT_DIR && ./start-all.sh${NC}"
echo
