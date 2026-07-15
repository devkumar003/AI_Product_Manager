import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.database.session import engine
from app.middleware.exception_handler import GlobalExceptionMiddleware
from app.models import Base

# Setup structured logging before anything else
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing AI ProductOS Backend Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Production Environment Validation
    if settings.is_prod():
        if not settings.REDIS_URL and not settings.REDIS_PASSWORD:
            logger.warning("SECURITY WARNING: Redis is configured without a password in production mode.")
        if "*" in settings.BACKEND_CORS_ORIGINS:
            logger.warning("SECURITY WARNING: CORS origins contains '*' in production mode. Restrict this to authorized hosts.")
        if not any([settings.OPENAI_API_KEY, settings.GEMINI_API_KEY, settings.ANTHROPIC_API_KEY, settings.GROQ_API_KEY, settings.DEEPSEEK_API_KEY]):
            logger.error("CRITICAL CONFIGURATION: No LLM provider API keys are configured (OpenAI, Gemini, Anthropic, Groq, DeepSeek).")

    logger.info("Ensuring database tables are managed by Alembic migrations...")

    # Seed default integration plugins
    from app.database.session import SessionLocal
    from app.services.integration.plugin_manager import plugin_manager

    db = SessionLocal()
    try:
        plugin_manager.seed_default_plugins(db)
    finally:
        db.close()

    yield
    # Shutdown tasks
    logger.info("Shutting down AI ProductOS Backend Service...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

from fastapi.middleware.gzip import GZipMiddleware

from app.middleware.security import (
    RateLimitingMiddleware,
    SecurityHeadersMiddleware,
    RequestSizeLimitingMiddleware,
)

# CORS configuration
if settings.BACKEND_CORS_ORIGINS:
    allow_all = "*" in settings.BACKEND_CORS_ORIGINS
    # SECURITY: Browsers reject credentials with wildcard origins.
    # In production, never use wildcard — always list explicit origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else settings.BACKEND_CORS_ORIGINS,
        allow_origin_regex=r"https://.*\.vercel\.app" if not allow_all else None,
        allow_credentials=not allow_all,  # credentials require explicit origins
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Production Hardening Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_per_minute=300)
app.add_middleware(RequestSizeLimitingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global Exception & Logging Middleware
app.add_middleware(GlobalExceptionMiddleware)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Access API docs at /docs"
    }


# Also mount a /health directly if needed at the root level in addition to /api/v1/health
from fastapi import Response, status

@app.get("/health", tags=["health"])
async def get_root_health(response: Response):
    from app.database.session import check_db_health
    from app.core.redis import cache_manager

    health_status = {"status": "healthy", "version": "1.0.0", "details": {}}
    unhealthy = False

    # Check Database
    if check_db_health():
        health_status["details"]["database"] = "healthy"
    else:
        health_status["details"]["database"] = "unhealthy"
        unhealthy = True

    # Check Redis
    try:
        redis_ok = await cache_manager.ping()
        if redis_ok:
            health_status["details"]["redis"] = "healthy"
        else:
            if settings.ENVIRONMENT == "production":
                health_status["details"]["redis"] = "unhealthy"
                unhealthy = True
            else:
                health_status["details"]["redis"] = "warning: local memory fallback"
    except Exception as e:
        health_status["details"]["redis"] = f"unhealthy: {str(e)}"
        unhealthy = True

    if unhealthy:
        health_status["status"] = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status



# Mount AI Observability endpoints
from app.ai.telemetry.observability import health_router as ai_health_router

app.include_router(ai_health_router, prefix="/api/v1/ai", tags=["ai-observability"])
