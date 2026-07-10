"""
Task 14 — Cost Estimation Engine
Task 15 — Timeline Prediction Engine
Task 16 — Risk Analysis Engine
"""

from typing import Any

from pydantic import BaseModel, Field

# ── Task 14: Cost Estimation Engine ──


class CostEstimationInput(BaseModel):
    task_breakdown: str = Field(..., description="Task breakdown with estimates")
    team_rates: dict[str, float] = Field(
        default_factory=lambda: {"senior": 120, "mid": 80, "junior": 50},
        description="Hourly rates per level in USD",
    )


class CostEstimationOutput(BaseModel):
    development_cost_usd: float = Field(...)
    infrastructure_cost_usd: float = Field(...)
    ai_cost_usd: float = Field(...)
    cloud_cost_monthly_usd: float = Field(...)
    maintenance_cost_annual_usd: float = Field(...)
    licensing_cost_usd: float = Field(...)
    overall_budget_usd: float = Field(...)
    cost_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    budget_recommendations: list[str] = Field(default_factory=list)


COST_ESTIMATION_PROMPT = (
    "You are the Cost Estimation Engine of AI ProductOS.\n"
    "Calculate comprehensive project costs: development, infrastructure, AI/ML,\n"
    "cloud hosting, maintenance, licensing, and overall budget.\n"
    "Provide a detailed breakdown by phase and category.\n"
    "Return JSON matching CostEstimationOutput schema."
)


# ── Task 15: Timeline Prediction Engine ──


class TimelineInput(BaseModel):
    task_breakdown: str = Field(..., description="Task breakdown data")
    team_size: int = Field(default=5)


class TimelineOutput(BaseModel):
    development_duration_weeks: int = Field(...)
    testing_duration_weeks: int = Field(...)
    deployment_duration_weeks: int = Field(...)
    risk_buffer_weeks: int = Field(...)
    overall_timeline_weeks: int = Field(...)
    phase_timeline: list[dict[str, Any]] = Field(default_factory=list)
    critical_path: list[str] = Field(default_factory=list)
    parallel_tracks: list[dict[str, Any]] = Field(default_factory=list)


TIMELINE_PROMPT = (
    "You are the Timeline Prediction Engine of AI ProductOS.\n"
    "Estimate realistic durations for development, testing, deployment,\n"
    "and risk buffer. Identify the critical path and parallel work tracks.\n"
    "Return JSON matching TimelineOutput schema."
)


# ── Task 16: Risk Analysis Engine ──


class RiskAnalysisInput(BaseModel):
    project_context: str = Field(..., description="Combined project context")


class RiskItem(BaseModel):
    id: str
    category: str
    risk: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high, critical
    severity_score: float = 0.0
    mitigation: str = ""
    contingency: str = ""
    owner: str = ""


class RiskAnalysisOutput(BaseModel):
    technical_risks: list[RiskItem] = Field(default_factory=list)
    business_risks: list[RiskItem] = Field(default_factory=list)
    financial_risks: list[RiskItem] = Field(default_factory=list)
    security_risks: list[RiskItem] = Field(default_factory=list)
    compliance_risks: list[RiskItem] = Field(default_factory=list)
    operational_risks: list[RiskItem] = Field(default_factory=list)
    overall_risk_score: float = Field(..., ge=0.0, le=10.0)
    mitigation_plan: list[dict[str, Any]] = Field(default_factory=list)


RISK_ANALYSIS_PROMPT = (
    "You are the Risk Analysis Engine of AI ProductOS.\n"
    "Identify risks across all categories: technical, business, financial,\n"
    "security, compliance, and operational.\n"
    "Each risk should have id, probability, impact, severity_score, mitigation, contingency.\n"
    "Calculate an overall risk score (0-10) and provide a mitigation plan.\n"
    "Return JSON matching RiskAnalysisOutput schema."
)
