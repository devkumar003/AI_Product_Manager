import time
from collections import defaultdict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Inject standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


from app.core.settings import settings

class RateLimitingMiddleware(BaseHTTPMiddleware):
    MAX_TRACKED_IPS = 50_000  # Hard cap to prevent OOM under distributed attacks

    def __init__(self, app, requests_per_minute: int = 200):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_records: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Bypass rate limit during testing environment
        if getattr(settings, "ENVIRONMENT", "development") == "testing":
            return await call_next(request)

        # Prevent client IP spoofing by reading the first entry of the X-Forwarded-For header
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Bypass for health check endpoints
        if request.url.path in [
            "/health",
            "/ready",
            "/live",
            "/api/v1/health/health",
            "/api/v1/health/ready",
            "/api/v1/health/live",
        ]:
            return await call_next(request)

        # Detect auth routes and impose a strict rate limit of 10 requests/minute
        path = request.url.path.lower()
        is_auth_endpoint = any(p in path for p in ["/auth/login", "/auth/register", "/auth/signup"])
        limit = 10 if is_auth_endpoint else self.requests_per_minute

        now = time.time()
        window_start = now - 60

        # Get existing timestamps within the sliding window, plus the current request
        existing = self.client_records.get(client_ip, [])
        timestamps = [t for t in existing if t > window_start]

        # Check rate limit BEFORE recording the current request
        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Too many requests. Please try again in a minute.",
                    "error": "Rate limit exceeded",
                },
            )

        # Record current request
        timestamps.append(now)
        self.client_records[client_ip] = timestamps

        # Periodic sweep: prune stale IPs to cap memory usage
        if len(self.client_records) > self.MAX_TRACKED_IPS:
            stale_keys = [
                ip for ip, ts in self.client_records.items()
                if not ts or ts[-1] <= window_start
            ]
            for ip in stale_keys:
                del self.client_records[ip]

        return await call_next(request)


class RequestSizeLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_content_length: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_content_length = max_content_length

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_content_length:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "message": "Payload too large. Maximum size allowed is 10MB.",
                            "error": "Payload Too Large",
                        },
                    )
            except ValueError:
                pass
        return await call_next(request)
