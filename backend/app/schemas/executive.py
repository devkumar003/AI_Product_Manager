from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


# -------------------------------------------------------------
# AI CEO Schemas
# -------------------------------------------------------------
class CEOGenerationRequest(BaseModel):
    product_idea: str
    target_industry: str | None = "Tech"
    competitors: list[str] = []
    budget: float | None = 100000.0


class CEOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    strategy_data: dict[str, Any]  # Strategy, SWOT, PESTLE, GTM
    portfolio_data: dict[str, Any]
    financials: dict[str, Any]
    market_intelligence: dict[str, Any]
    recommendations: list[dict[str, Any]]
    marketing_sales: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# AI CTO Schemas
# -------------------------------------------------------------
class CTOGenerationRequest(BaseModel):
    product_spec: str
    preferred_cloud: str | None = "AWS"
    compliance_needs: list[str] = ["GDPR", "SOC2"]


class CTOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    architecture_review: dict[str, Any]
    optimization_plans: dict[str, Any]
    security_devops: dict[str, Any]
    technical_debt: dict[str, Any]
    health_metrics: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# AI COO Schemas
# -------------------------------------------------------------
class COOGenerationRequest(BaseModel):
    sprint_name: str
    team_members: list[str] = ["Dev1", "Dev2", "Dev3", "QA1"]
    total_budget: float | None = 50000.0


class COOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    resource_capacity: dict[str, Any]
    delivery_monitoring: dict[str, Any]
    incidents_risks: dict[str, Any]
    operations_analytics: dict[str, Any]
    notification_center: list[dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
