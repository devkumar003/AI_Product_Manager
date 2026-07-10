from typing import Any
from pydantic import BaseModel, Field


class ModelSettings(BaseModel):
    model: str = Field("gpt-4o", description="Target model name")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: int = Field(4096, description="Maximum completion tokens limit")
    retry_count: int = Field(3, description="Number of execution retries on failure")
    timeout: float = Field(60.0, description="Network connection request timeout in seconds")
    streaming: bool = Field(False, description="Whether to stream token responses")


class ProviderSettings(BaseModel):
    priority: list[str] = Field(
        default_factory=lambda: ["openai", "claude", "gemini", "groq", "deepseek", "ollama"],
        description="List of model providers sorted by preference priority"
    )
    fallback_priority: list[str] = Field(
        default_factory=lambda: ["groq", "ollama"],
        description="Fallback providers if high-tier services are offline"
    )


class WorkspaceAISettings(BaseModel):
    workspace_id: str
    default_model: str = "gpt-4o"
    default_provider: str = "openai"
    allowed_providers: list[str] = Field(default_factory=lambda: ["openai", "gemini", "claude"])
    max_tokens_limit: int = 8192
    custom_system_rules: str | None = None
    rate_limit_per_minute: int = 60
