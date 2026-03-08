# ============================================
# Stage 1: Build Frontend (React + Vite)
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源码
COPY frontend/ ./

# 构建生产版本
RUN npm run build

# ============================================
# Stage 2: Runtime (Python + FastAPI)
# ============================================
FROM python:3.11-slim

WORKDIR /app

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装 uv
RUN pip install --no-cache-dir uv

# 复制后端依赖配置和 README（pyproject.toml 需要）
COPY backend/pyproject.toml .
COPY backend/uv.lock .
COPY backend/README.md .

# 安装 Python 依赖 (仅生产环境)
RUN uv sync --no-dev --frozen

# 复制后端源码和配置
COPY backend/src/ ./src/
COPY backend/config/ ./config/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /frontend/dist/ ./static/

# 暴露端口 (实际端口由 PORT 环境变量决定)
EXPOSE 8000

# 启动命令 - 使用 shell form 确保 PORT 环境变量展开
CMD sh -c "uv run knowledge-agent serve --port ${PORT:-8000}"
