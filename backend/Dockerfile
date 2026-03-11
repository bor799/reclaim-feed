FROM python:3.11-slim

WORKDIR /app

# Set timezone
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY config/ ./config/

# Install dependencies
RUN uv sync --no-dev

# Expose port
EXPOSE 8000

# Default command - shell form for PORT variable expansion
CMD sh -c "uv run knowledge-agent serve --port ${PORT:-8000}"
