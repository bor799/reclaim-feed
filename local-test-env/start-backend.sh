#!/bin/bash
# -*- coding: utf-8 -*-
# 本地测试环境 - 后端启动脚本

set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
CONFIG_DIR="$SCRIPT_DIR/backend-config"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}100X Agent - 后端测试环境启动${NC}"
echo -e "${GREEN}================================${NC}"
echo

# 检查配置文件
if [ ! -f "$CONFIG_DIR/.env" ]; then
    echo -e "${RED}❌ 错误: .env 文件不存在${NC}"
    echo "请先创建 $CONFIG_DIR/.env 并配置 ZHIPU_API_KEY"
    echo
    echo "示例内容："
    echo "  ZHIPU_API_KEY=your_api_key_here"
    echo
    echo "获取 API Key: https://open.bigmodel.cn/usercenter/apikeys"
    exit 1
fi

# 检查 API Key 是否已配置
if grep -q "your_api_key_here" "$CONFIG_DIR/.env"; then
    echo -e "${YELLOW}⚠️  警告: ZHIPU_API_KEY 尚未配置${NC}"
    echo "请编辑 $CONFIG_DIR/.env 并设置有效的 API Key"
    echo
    echo "获取 API Key: https://open.bigmodel.cn/usercenter/apikeys"
    echo
    read -p "是否继续启动？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查虚拟环境
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    cd "$BACKEND_DIR"
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
fi

# 加载环境变量
echo -e "${GREEN}📋 加载环境变量...${NC}"
set -a
source "$CONFIG_DIR/.env"
set +a

# 设置配置目录
export AGENT_CONFIG_PATH="$CONFIG_DIR/config.yaml"

# 显示配置
echo
echo -e "${GREEN}配置信息:${NC}"
echo "  配置文件: $AGENT_CONFIG_PATH"
echo "  日志目录: $SCRIPT_DIR/logs"
echo "  状态目录: $SCRIPT_DIR/state"
echo

# 启动后端
echo -e "${GREEN}🚀 启动后端服务...${NC}"
echo -e "${YELLOW}API 地址: http://localhost:8000${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo

# 激活虚拟环境并启动
cd "$BACKEND_DIR"
source .venv/bin/activate

# 创建必要的目录
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/state"

# 启动 API 服务器
python -m src.api.main
