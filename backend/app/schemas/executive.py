from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

# -------------------------------------------------------------
# AI CEO Schemas
# -------------------------------------------------------------
class CEOGenerationRequest(BaseModel):
    product_idea: str
    target_industry: Optional[str] = "Tech"
    competitors: List[str] = []
    budget: Optional[float] = 100000.0

class CEOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    strategy_data: Dict[str, Any]  # Strategy, SWOT, PESTLE, GTM
    portfolio_data: Dict[str, Any]
    financials: Dict[str, Any]
    market_intelligence: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    marketing_sales: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------------------------------------
# AI CTO Schemas
# -------------------------------------------------------------
class CTOGenerationRequest(BaseModel):
    product_spec: str
    preferred_cloud: Optional[str] = "AWS"
    compliance_needs: List[str] = ["GDPR", "SOC2"]

class CTOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    architecture_review: Dict[str, Any]
    optimization_plans: Dict[str, Any]
    security_devops: Dict[str, Any]
    technical_debt: Dict[str, Any]
    health_metrics: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------------------------------------
# AI COO Schemas
# -------------------------------------------------------------
class COOGenerationRequest(BaseModel):
    sprint_name: str
    team_members: List[str] = ["Dev1", "Dev2", "Dev3", "QA1"]
    total_budget: Optional[float] = 50000.0

class COOReportResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    resource_capacity: Dict[str, Any]
    delivery_monitoring: Dict[str, Any]
    incidents_risks: Dict[str, Any]
    operations_analytics: Dict[str, Any]
    notification_center: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
