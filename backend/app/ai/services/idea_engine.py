"""
Task 1 — Idea Analysis Engine
Task 2 — Idea Validation Engine
Task 3 — Product Discovery Engine

Converts a raw natural-language product idea into structured intelligence:
industry classification, validation scores, and product discovery artifacts.
"""

from typing import Any
from pydantic import BaseModel, Field


# ── Task 1: Idea Analysis ──

class IdeaAnalysisInput(BaseModel):
    idea: str = Field(..., description="Natural language product idea")
    additional_context: str = Field(default="", description="Optional context or constraints")


class IdeaAnalysisOutput(BaseModel):
    industry: str = Field(..., description="Industry vertical")
    domain: str = Field(..., description="Business domain")
    target_audience: str = Field(..., description="Primary target audience")
    business_model: str = Field(..., description="Revenue model type")
    complexity: str = Field(..., description="low / medium / high / very_high")
    project_category: str = Field(..., description="e.g. SaaS, Mobile, Platform")
    technology_category: str = Field(..., description="e.g. Web, AI/ML, IoT")
    business_summary: str = Field(..., description="Concise business summary")
    pain_points: list[str] = Field(default_factory=list)
    business_opportunities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    expected_deliverables: list[str] = Field(default_factory=list)


IDEA_ANALYSIS_PROMPT = (
    "You are the Idea Analysis Engine of AI ProductOS.\n"
    "Analyze the given product idea and classify it into structured categories.\n"
    "Return a JSON object matching the IdeaAnalysisOutput schema with fields:\n"
    "industry, domain, target_audience, business_model, complexity, project_category,\n"
    "technology_category, business_summary, pain_points, business_opportunities,\n"
    "constraints, expected_deliverables.\n"
    "Be thorough and specific. Never use generic placeholders."
)


# ── Task 2: Idea Validation ──

class IdeaValidationInput(BaseModel):
    idea: str = Field(..., description="Product idea to validate")
    analysis_summary: str = Field(default="", description="Prior analysis context if available")


class IdeaValidationOutput(BaseModel):
    market_demand: str = Field(..., description="Assessment of market demand")
    innovation_score: float = Field(..., ge=0.0, le=10.0)
    feasibility_score: float = Field(..., ge=0.0, le=10.0)
    technical_complexity: str = Field(..., description="low / medium / high / very_high")
    business_complexity: str = Field(..., description="low / medium / high / very_high")
    competition_score: float = Field(..., ge=0.0, le=10.0)
    estimated_development_cost_usd: str = Field(..., description="Range estimate e.g. $50k-$150k")
    estimated_timeline: str = Field(..., description="e.g. 3-6 months")
    risk_score: float = Field(..., ge=0.0, le=10.0)
    success_probability: float = Field(..., ge=0.0, le=1.0)
    recommendation: str = Field(..., description="Go / No-Go / Pivot recommendation with rationale")


IDEA_VALIDATION_PROMPT = (
    "You are the Idea Validation Engine of AI ProductOS.\n"
    "Score and validate the product idea across multiple dimensions.\n"
    "Return a JSON object matching IdeaValidationOutput with all numeric scores\n"
    "and a clear Go / No-Go / Pivot recommendation with detailed rationale."
)


# ── Task 3: Product Discovery ──

class ProductDiscoveryInput(BaseModel):
    idea: str = Field(..., description="Product idea")
    validation_summary: str = Field(default="", description="Validation results if available")


class UserPersona(BaseModel):
    name: str
    role: str
    goals: list[str]
    frustrations: list[str]
    tech_savviness: str


class ProductDiscoveryOutput(BaseModel):
    product_vision: str = Field(...)
    mission: str = Field(...)
    objectives: list[str] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)
    user_personas: list[UserPersona] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    business_goals: list[str] = Field(default_factory=list)
    product_kpis: list[str] = Field(default_factory=list)
    north_star_metric: str = Field(...)
    success_criteria: list[str] = Field(default_factory=list)


PRODUCT_DISCOVERY_PROMPT = (
    "You are the Product Discovery Engine of AI ProductOS.\n"
    "Generate a comprehensive product discovery document from the given idea.\n"
    "Include vision, mission, personas with goals/frustrations, KPIs, and a clear North Star metric.\n"
    "Return a JSON object matching ProductDiscoveryOutput schema."
)
