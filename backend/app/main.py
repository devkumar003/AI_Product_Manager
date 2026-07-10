import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.database.session import engine
from app.models import Base
from app.middleware.exception_handler import GlobalExceptionMiddleware

# Setup structured logging before anything else
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing AI ProductOS Backend Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Ensuring database tables are initialized...")
    Base.metadata.create_all(bind=engine)
    
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
from app.middleware.security import SecurityHeadersMiddleware, RateLimitingMiddleware

# CORS configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Production Hardening Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_per_minute=300)
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
@app.get("/health", tags=["health"])
def get_root_health():
    return {"status": "healthy", "version": "1.0.0"}


# Mount AI Observability endpoints
from app.ai.telemetry.observability import health_router as ai_health_router
app.include_router(ai_health_router, prefix="/api/v1/ai", tags=["ai-observability"])

