#!/bin/bash
# -*- coding: utf-8 -*-
# 本地测试环境 - 一键启动前后端

set -e

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 清理函数
cleanup() {
    echo
    echo -e "${YELLOW}🛑 正在停止所有服务...${NC}"

    # 杀掉后台进程
    jobs -p | xargs -r kill 2>/dev/null || true

    # 清理日志
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true

    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}100X Agent - 本地测试环境${NC}"
echo -e "${GREEN}================================${NC}"
echo
echo -e "${BLUE}启动模式:${NC}"
echo "  [1] 仅后端"
echo "  [2] 仅前端"
echo "  [3] 前后端 (推荐)"
echo
read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}📦 启动后端服务...${NC}"
        exec "$SCRIPT_DIR/start-backend.sh"
        ;;
    2)
        echo -e "${GREEN}🎨 启动前端服务...${NC}"
        exec "$SCRIPT_DIR/start-frontend.sh"
        ;;
    3)
        echo -e "${GREEN}🚀 启动前后端服务...${NC}"
        echo

        # 启动后端（后台）
        echo -e "${BLUE}[1/2]${NC} 启动后端..."
        "$SCRIPT_DIR/start-backend.sh" > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
        BACKEND_PID=$!

        # 等待后端启动
        echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
        sleep 5

        # 检查后端是否启动成功
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
        else
            echo -e "${YELLOW}⚠️  后端服务可能未启动，查看日志: $SCRIPT_DIR/logs/backend.log${NC}"
        fi

        echo

        # 启动前端（前台）
        echo -e "${BLUE}[2/2]${NC} 启动前端..."
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅ 测试环境已就绪！${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        echo -e "${BLUE}访问地址:${NC}"
        echo -e "  前端: ${YELLOW}http://localhost:5173${NC}"
        echo -e "  后端: ${YELLOW}http://localhost:8000${NC}"
        echo -e "  API文档: ${YELLOW}http://localhost:8000/docs${NC}"
        echo
        echo -e "${BLUE}日志位置:${NC}"
        echo -e "  后端: $SCRIPT_DIR/logs/backend.log"
        echo
        echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
        echo

        exec "$SCRIPT_DIR/start-frontend.sh"
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac
