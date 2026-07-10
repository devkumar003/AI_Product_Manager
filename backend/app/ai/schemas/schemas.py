from typing import Any, Optional
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class AIRequest(BaseModel):
    workspace_id: str
    user_id: str
    workflow_name: Optional[str] = None
    agent_name: Optional[str] = None
    prompt_name: Optional[str] = None
    prompt_variables: dict[str, Any] = Field(default_factory=dict)
    system_prompt_override: Optional[str] = None
    user_message: str
    stream: bool = False
    model_override: Optional[str] = None
    provider_override: Optional[str] = None
    temperature_override: Optional[float] = None


class AIResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: TokenUsage
    latency_ms: float
    success: bool = True
    error_message: Optional[str] = None


class StreamingToken(BaseModel):
    token: str
    done: bool = False
    error: Optional[str] = None
    usage: Optional[TokenUsage] = None


class AgentResponse(BaseModel):
    status: str = Field(..., description="Status of the agent execution")
    summary: str = Field(..., description="High-level text summary of results")
    result: dict[str, Any] = Field(default_factory=dict, description="Structured agent-specific output map")
    confidence: float = Field(1.0, description="Estimated confidence score from 0.0 to 1.0")
    recommendations: list[str] = Field(default_factory=list, description="List of actionable recommendations")
    warnings: list[str] = Field(default_factory=list, description="Warnings or issues detected")
    next_agent: str = Field("", description="Name of the recommended next agent to invoke")

