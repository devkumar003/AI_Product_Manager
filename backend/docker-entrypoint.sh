#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "    Starting AI ProductOS Enterprise Backend Container    "
echo "=========================================================="

# 1. Run database migrations if PostgreSQL is reachable
echo "[Entrypoint] Checking and applying Alembic migrations..."
if alembic upgrade head; then
    echo "[Entrypoint] Database schema migrations applied successfully."
else
    echo "[Entrypoint] WARNING: Alembic upgrade encountered an issue. Proceeding with application startup check..."
fi

# 2. Launch FastAPI with Uvicorn server
echo "[Entrypoint] Launching FastAPI uvicorn server..."
if [ "${ENVIRONMENT:-development}" = "production" ]; then
    WORKERS="${WEB_CONCURRENCY:-4}"
    echo "[Entrypoint] Starting production server with ${WORKERS} worker processes..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --workers "${WORKERS}" "$@"
else
    echo "[Entrypoint] Starting development/testing server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' "$@"
fi

