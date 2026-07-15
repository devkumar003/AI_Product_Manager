FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies if any are needed (curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create system group and user
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and migrations
COPY --chown=appuser:appgroup app/ app/
COPY --chown=appuser:appgroup alembic/ alembic/
COPY --chown=appuser:appgroup alembic.ini ./
COPY --chown=appuser:appgroup .env* ./
COPY --chown=appuser:appgroup docker-entrypoint.sh ./

RUN chmod +x /app/docker-entrypoint.sh && \
    chown appuser:appgroup /app/docker-entrypoint.sh && \
    mkdir -p /app/uploads && \
    chown -R appuser:appgroup /app/uploads

# Switch to non-root user
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
