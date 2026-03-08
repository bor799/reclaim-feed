#!/bin/bash
# -*- coding: utf-8 -*-
# 本地测试环境 - 快速设置脚本

set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}100X Agent - 测试环境快速设置${NC}"
echo -e "${GREEN}================================${NC}"
echo

# 检查后端 API Key
echo -e "${BLUE}[1/4]${NC} 检查后端配置..."
if [ -f "$SCRIPT_DIR/backend-config/.env" ]; then
    if grep -q "your_api_key_here" "$SCRIPT_DIR/backend-config/.env"; then
        echo -e "${YELLOW}⚠️  需要配置 ZHIPU_API_KEY${NC}"
        echo
        echo "请编辑以下文件并设置 API Key："
        echo "  $SCRIPT_DIR/backend-config/.env"
        echo
        echo "获取 API Key: https://open.bigmodel.cn/usercenter/apikeys"
        echo
        read -p "是否现在打开编辑器？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} "$SCRIPT_DIR/backend-config/.env"
        fi
    else
        echo -e "${GREEN}✅ 后端 API Key 已配置${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  后端配置文件不存在${NC}"
fi

# 复制前端 API 服务
echo
echo -e "${BLUE}[2/4]${NC} 配置前端 API 服务..."
mkdir -p "$FRONTEND_DIR/src/services" 2>/dev/null || true
if [ ! -f "$FRONTEND_DIR/src/services/api.ts" ]; then
    cp "$SCRIPT_DIR/frontend-config/api.ts" "$FRONTEND_DIR/src/services/api.ts"
    echo -e "${GREEN}✅ API 服务文件已创建${NC}"
else
    echo -e "${YELLOW}⚠️  API 服务文件已存在，跳过${NC}"
fi

# 复制前端环境变量
echo
echo -e "${BLUE}[3/4]${NC} 配置前端环境变量..."
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    cp "$SCRIPT_DIR/frontend-config/.env.test" "$FRONTEND_DIR/.env.local"
    echo -e "${GREEN}✅ .env.local 已创建${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local 已存在，跳过${NC}"
fi

# 创建必要的目录
echo
echo -e "${BLUE}[4/4]${NC} 创建必要的目录..."
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/state"
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 完成
echo
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ 设置完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo -e "${BLUE}下一步:${NC}"
echo
echo "1. 确保 ZHIPU_API_KEY 已配置："
echo "   编辑: $SCRIPT_DIR/backend-config/.env"
echo
echo "2. 启动测试环境："
echo -e "   ${YELLOW}cd $SCRIPT_DIR && ./start-all.sh${NC}"
echo
echo "3. 访问应用："
echo -e "   前端: ${YELLOW}http://localhost:5173${NC}"
echo -e "   后端: ${YELLOW}http://localhost:8000${NC}"
echo -e "   API 文档: ${YELLOW}http://localhost:8000/docs${NC}"
echo
