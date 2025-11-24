###################### Build stage
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./
# Copy source code and build wheel
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev
RUN uv build

###################### Runtime stage
FROM python:3.13-slim

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy built wheel from builder stage
COPY --from=builder /app/dist/*.whl ./

# Install the wheel
RUN python -m pip install --no-cache-dir *.whl && rm *.whl

# Create non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "mcp_sl.server:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "5"]
