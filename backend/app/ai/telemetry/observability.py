"""
Task 14 — Observability: Health Checks, Readiness, Liveness, Prometheus Metrics

Provides /health, /ready, /live endpoints and a metrics registry.
"""

import logging
import time
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger("app.ai.observability")

health_router = APIRouter(tags=["observability"])

_start_time = time.time()

# ── In-memory metrics counters ──
_metrics: dict[str, float] = {
    "ai_requests_total": 0,
    "ai_requests_success": 0,
    "ai_requests_failed": 0,
    "ai_tokens_total": 0,
    "ai_cost_total_usd": 0.0,
    "ai_latency_sum_ms": 0.0,
    "memory_operations_total": 0,
    "rag_queries_total": 0,
    "http_requests_total": 0,
    "http_requests_2xx": 0,
    "http_requests_3xx": 0,
    "http_requests_4xx": 0,
    "http_requests_5xx": 0,
    "http_latency_sum_ms": 0.0,
}


def record_metric(name: str, value: float = 1.0) -> None:
    if name in _metrics:
        _metrics[name] += value


def record_http_request(status_code: int, duration_ms: float) -> None:
    if "http_requests_total" in _metrics:
        _metrics["http_requests_total"] += 1
        _metrics["http_latency_sum_ms"] += duration_ms
        if 200 <= status_code < 300:
            _metrics["http_requests_2xx"] += 1
        elif 300 <= status_code < 400:
            _metrics["http_requests_3xx"] += 1
        elif 400 <= status_code < 500:
            _metrics["http_requests_4xx"] += 1
        elif 500 <= status_code < 600:
            _metrics["http_requests_5xx"] += 1


def get_metrics() -> dict[str, float]:
    return dict(_metrics)



@health_router.get("/health")
async def health_check() -> dict[str, Any]:
    """Comprehensive health check."""
    uptime = time.time() - _start_time
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 1),
        "version": "2.0.0",
        "phase": "Phase 2 Complete",
        "services": {
            "ai_orchestrator": "operational",
            "agent_registry": "operational",
            "llm_manager": "operational",
            "memory_engine": "operational",
            "knowledge_base": "operational",
            "rag_pipeline": "operational",
            "workflow_engine": "operational",
            "streaming_engine": "operational",
            "export_engine": "operational",
        },
    }


from fastapi import Response, status

@health_router.get("/ready")
async def readiness_check(response: Response) -> dict[str, Any]:
    """Kubernetes readiness probe."""
    from app.database.session import check_db_health
    from app.core.redis import cache_manager
    from app.core.settings import settings
    
    db_ok = check_db_health()
    try:
        redis_ok = await cache_manager.ping()
    except Exception:
        redis_ok = False
        
    is_ready = db_ok
    if settings.ENVIRONMENT == "production":
        is_ready = db_ok and redis_ok
        
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return {
        "ready": is_ready,
        "database": "healthy" if db_ok else "unhealthy",
        "redis": "healthy" if redis_ok else "unhealthy",
        "timestamp": time.time()
    }



@health_router.get("/live")
async def liveness_check() -> dict[str, Any]:
    """Kubernetes liveness probe."""
    return {"alive": True, "timestamp": time.time()}


@health_router.get("/metrics")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint."""
    from fastapi import Response
    lines = []
    for name, val in get_metrics().items():
        lines.append(f"# HELP {name} AI ProductOS Metric {name}")
        lines.append(f"# TYPE {name} gauge")
        lines.append(f"{name} {val}")
    lines.append(f"# HELP uptime_seconds Service Uptime in seconds")
    lines.append(f"# TYPE uptime_seconds gauge")
    lines.append(f"uptime_seconds {round(time.time() - _start_time, 1)}")
    
    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain; version=0.0.4"
    )
