from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseEntity


class CEOReport(BaseEntity):
    __tablename__ = "ceo_reports"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    strategy_data = Column(
        JSON, default=dict, nullable=False
    )  # Business Strategy, SWOT, PESTLE, GTM
    portfolio_data = Column(
        JSON, default=dict, nullable=False
    )  # Product portfolio manager
    financials = Column(
        JSON, default=dict, nullable=False
    )  # Revenue forecasts, pricing strategy
    market_intelligence = Column(
        JSON, default=dict, nullable=False
    )  # Competitor Intelligence, risk analyzer
    recommendations = Column(
        JSON, default=list, nullable=False
    )  # Investment recommendation list
    marketing_sales = Column(
        JSON, default=dict, nullable=False
    )  # Sales/Marketing generators, Customer journey
    created_by = Column(String(255), default="AI CEO Agent", nullable=False)

    workspace = relationship("Workspace")


class CTOReport(BaseEntity):
    __tablename__ = "cto_reports"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    architecture_review = Column(
        JSON, default=dict, nullable=False
    )  # Tech Stack, Infrastructure, Cloud
    optimization_plans = Column(
        JSON, default=dict, nullable=False
    )  # Code quality, DB/API/Performance optimization
    security_devops = Column(
        JSON, default=dict, nullable=False
    )  # Security, DevOps, CI/CD
    technical_debt = Column(
        JSON, default=dict, nullable=False
    )  # Tech debt and dependency analysis
    health_metrics = Column(
        JSON, default=dict, nullable=False
    )  # Engineering/System Health
    created_by = Column(String(255), default="AI CTO Agent", nullable=False)

    workspace = relationship("Workspace")


class COOReport(BaseEntity):
    __tablename__ = "coo_reports"

    workspace_id = Column(
        Uuid,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    resource_capacity = Column(
        JSON, default=dict, nullable=False
    )  # Resource allocation, Team capacity/perf
    delivery_monitoring = Column(
        JSON, default=dict, nullable=False
    )  # Sprint monitoring, Delivery, Release
    incidents_risks = Column(
        JSON, default=dict, nullable=False
    )  # Incident, Risk, Budget monitoring
    operations_analytics = Column(
        JSON, default=dict, nullable=False
    )  # Cost, org, team, productivity analytics
    notification_center = Column(
        JSON, default=list, nullable=False
    )  # Operational logs/notifications
    created_by = Column(String(255), default="AI COO Agent", nullable=False)

    workspace = relationship("Workspace")
