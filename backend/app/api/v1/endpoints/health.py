import asyncio
from fastapi import APIRouter, Depends, Response, status, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.v1.deps import get_db
from app.core.redis import cache_manager
from app.core.settings import settings

router = APIRouter()

# Global metrics trackers
REQUEST_COUNTER = 0
request_counter_lock = asyncio.Lock()


@router.get("/health")
async def get_health():
    global REQUEST_COUNTER
    async with request_counter_lock:
        REQUEST_COUNTER += 1
    return {"status": "healthy", "version": "1.0.0"}


@router.get("/ready")
async def get_readiness(db: Session = Depends(get_db)):
    global REQUEST_COUNTER
    async with request_counter_lock:
        REQUEST_COUNTER += 1

    # Check Database connection
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Redis cache
    redis_ok = await cache_manager.ping()

    if not db_ok or not redis_ok:
        return Response(
            content=f'{{"status": "unready", "database": {str(db_ok).lower()}, "redis": {str(redis_ok).lower()}}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )

    return {"status": "ready", "database": "connected", "redis": "connected"}


@router.get("/live")
async def get_liveness():
    global REQUEST_COUNTER
    async with request_counter_lock:
        REQUEST_COUNTER += 1
    return {"status": "alive"}


@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    x_metrics_token: str | None = Header(None),
):
    """
    Exposes Prometheus-formatted metrics about application requests and databases.
    """
    is_testing = getattr(settings, "ENVIRONMENT", "development") == "testing"
    if not is_testing:
        expected_token = getattr(settings, "METRICS_API_KEY", "dev_metrics_secret_token")
        if not x_metrics_token or x_metrics_token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized metrics access",
            )
    
    global REQUEST_COUNTER

    # 1. DB ping
    db_ok = 1
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = 0

    # 2. Redis ping
    redis_ok = 1 if await cache_manager.ping() else 0

    prometheus_lines = [
        "# HELP api_requests_total Total number of API requests handled",
        "# TYPE api_requests_total counter",
        f"api_requests_total {REQUEST_COUNTER}",
        "# HELP db_connected Status of the database connection (1 = OK, 0 = ERR)",
        "# TYPE db_connected gauge",
        f"db_connected {db_ok}",
        "# HELP redis_connected Status of the Redis connection (1 = OK, 0 = ERR)",
        "# TYPE redis_connected gauge",
        f"redis_connected {redis_ok}",
    ]

    return Response(
        content="\n".join(prometheus_lines) + "\n",
        media_type="text/plain",
    )


@router.get("/test-error")
async def test_error():
    raise ValueError(
        "This is a simulated validation error to test global exception handling middleware."
    )
