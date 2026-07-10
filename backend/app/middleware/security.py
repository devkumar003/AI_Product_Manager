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


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 200):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Simple client request history tracking
        self.client_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
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

        now = time.time()
        # Clean older records
        self.client_records[client_ip] = [
            t for t in self.client_records[client_ip] if now - t < 60
        ]

        if len(self.client_records[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Too many requests. Please try again in a minute.",
                    "error": "Rate limit exceeded",
                },
            )

        self.client_records[client_ip].append(now)
        return await call_next(request)
