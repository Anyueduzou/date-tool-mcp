FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000

# 托管环境通过 HTTP 访问，故默认使用 streamable-http 传输
CMD ["python", "-m", "date_tool_mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
