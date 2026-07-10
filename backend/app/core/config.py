from typing import Annotated, Any

from pydantic import BeforeValidator, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    PROJECT_NAME: str = "AI ProductOS"
    ENVIRONMENT: str = "development"  # development, testing, production
    API_V1_STR: str = "/api/v1"

    # CORS settings
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = [
        "http://localhost:3000"
    ]

    ENVIRONMENT: str = "development"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_product_os"
    DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URI: str | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        import os

        values = info.data
        if not v:
            v = values.get("DATABASE_URL") or os.getenv("DATABASE_URL")
        if isinstance(v, str) and v:
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+psycopg2://", 1)
            elif (
                v.startswith("postgresql://")
                and "+psycopg" not in v
                and "+asyncpg" not in v
            ):
                v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v
        if values.get("ENVIRONMENT") == "testing":
            return "sqlite:///./test.db"

        host = values.get("POSTGRES_SERVER", "localhost")
        port = int(values.get("POSTGRES_PORT", 5432))
        postgres_uri = f"postgresql+psycopg2://{values.get('POSTGRES_USER', 'postgres')}:{values.get('POSTGRES_PASSWORD', 'postgres')}@{host}:{port}/{values.get('POSTGRES_DB', 'ai_product_os')}"

        env = values.get("ENVIRONMENT", "development")
        if env in ("production", "staging"):
            return postgres_uri

        import socket

        try:
            with socket.create_connection((host, port), timeout=0.5):
                pass
            return postgres_uri
        except Exception:
            print(
                f"PostgreSQL server at {host}:{port} is unreachable. Falling back to local SQLite: sqlite:///./development.db"
            )
            return "sqlite:///./development.db"

    # Redis Config
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str | None = None
    REDIS_PASSWORD: str | None = None

    # Security Config
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days

    # AI Provider API Keys
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    DEEPSEEK_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        values = info.data
        if not v or v.strip() == "":
            raise ValueError("JWT_SECRET must not be empty.")
        if values.get("ENVIRONMENT") == "production":
            if (
                v == "generate_a_secure_random_hex_string_with_32_bytes_or_more"
                or len(v) < 32
            ):
                raise ValueError("JWT_SECRET is insecure for production environment.")
        return v

    def is_dev(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_prod(self) -> bool:
        return self.ENVIRONMENT == "production"

    def is_test(self) -> bool:
        return self.ENVIRONMENT == "testing"
