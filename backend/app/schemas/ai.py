from pydantic import BaseModel, Field
from typing import Any


class AIGenerateRequest(BaseModel):
    idea: str = Field(..., min_length=5, description="Raw product idea")
    industry: str = Field("General Tech", description="Target industry vertical")
    model: str = Field("gpt-4o", description="Model identifier override")
    provider: str | None = Field(None, description="Explicit provider name override")


class AIGenerateResponse(BaseModel):
    refined_idea: dict[str, Any] = Field(..., description="PM Refined Idea output properties")
    prd: dict[str, Any] = Field(..., description="PRD Document output properties")
    architecture: dict[str, Any] = Field(..., description="Architect design specification properties")


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message string sent to the conversation agent")
    model: str = Field("gpt-4o", description="Model identifier override")
    provider: str | None = Field(None, description="Explicit provider name override")


class AIChatResponse(BaseModel):
    response: str = Field(..., description="Response content string from the agent")
