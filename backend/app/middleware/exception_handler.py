import logging
import time
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.middleware")


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start_time = time.time()

        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "traceId": trace_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)

            duration = time.time() - start_time
            # Record HTTP metric
            try:
                from app.ai.telemetry.observability import record_http_request
                record_http_request(response.status_code, duration * 1000)
            except Exception:
                pass

            # Log outgoing response
            logger.info(
                f"Outgoing response: {request.method} {request.url.path} - Status: {response.status_code}",
                extra={
                    "traceId": trace_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
            response.headers["X-Trace-ID"] = trace_id
            return response

        except Exception as exc:
            duration = time.time() - start_time
            # Standardize status code and messaging
            status_code = 500
            error_message = "Internal Server Error"
            raw_error_detail = str(exc)

            from app.core.settings import settings
            is_testing = getattr(settings, "ENVIRONMENT", "development") == "testing"

            if isinstance(exc, StarletteHTTPException):
                status_code = exc.status_code
                error_detail = str(exc.detail)
                error_message = "HTTP Exception"
            elif is_testing:
                error_detail = raw_error_detail
            else:
                error_detail = "An unexpected error occurred. Please contact support."

            # Record HTTP metric for failures
            try:
                from app.ai.telemetry.observability import record_http_request
                record_http_request(status_code, duration * 1000)
            except Exception:
                pass

            # Log error details
            logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {raw_error_detail}",
                exc_info=True,
                extra={
                    "traceId": trace_id,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "error_detail": raw_error_detail,
                },
            )

            # Standard response format
            response_content = {
                "success": False,
                "message": error_message,
                "error": error_detail,
                "traceId": trace_id,
            }

            return JSONResponse(
                status_code=status_code,
                content=response_content,
                headers={"X-Trace-ID": trace_id},
            )
