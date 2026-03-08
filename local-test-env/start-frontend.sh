#!/bin/bash
# -*- coding: utf-8 -*-
# 本地测试环境 - 前端启动脚本

set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
CONFIG_DIR="$SCRIPT_DIR/frontend-config"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}100X Agent - 前端测试环境启动${NC}"
echo -e "${GREEN}================================${NC}"
echo

# 检查依赖
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules 不存在，正在安装依赖...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已存在${NC}"
fi

# 复制环境变量文件
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo -e "${YELLOW}⚠️  .env.local 不存在，正在创建...${NC}"
    cp "$CONFIG_DIR/.env.test" "$FRONTEND_DIR/.env.local"
    echo -e "${GREEN}✅ .env.local 创建完成${NC}"
else
    echo -e "${GREEN}✅ .env.local 已存在${NC}"
fi

# 检查 API 服务配置
if [ ! -f "$FRONTEND_DIR/src/services/api.ts" ]; then
    echo -e "${YELLOW}⚠️  API 服务文件不存在${NC}"
    echo "请复制 $CONFIG_DIR/api.ts 到 $FRONTEND_DIR/src/services/api.ts"
    echo
    echo "命令: mkdir -p $FRONTEND_DIR/src/services && cp $CONFIG_DIR/api.ts $FRONTEND_DIR/src/services/api.ts"
    echo
    read -p "是否自动复制？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$FRONTEND_DIR/src/services"
        cp "$CONFIG_DIR/api.ts" "$FRONTEND_DIR/src/services/api.ts"
        echo -e "${GREEN}✅ API 服务文件已复制${NC}"
    fi
else
    echo -e "${GREEN}✅ API 服务文件已存在${NC}"
fi

# 显示配置
echo
echo -e "${GREEN}配置信息:${NC}"
echo "  后端 API: http://localhost:8000"
echo "  前端地址: http://localhost:5173"
echo

# 启动前端
echo -e "${GREEN}🚀 启动前端服务...${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo

cd "$FRONTEND_DIR"
npm run dev
