"""
Deployment Guide Engine — Generates CI/CD pipelines, Docker configurations,
monitoring setup, and deployment documentation.
"""

from typing import Any

from pydantic import BaseModel, Field


class DeploymentGuideInput(BaseModel):
    project_description: str = Field(
        ..., description="Description of the project to deploy"
    )
    tech_stack: str = Field(
        default="", description="Technology stack details"
    )
    cloud_provider: str = Field(
        default="AWS",
        description="Target cloud provider: AWS, GCP, Azure, DigitalOcean",
    )
    deployment_type: str = Field(
        default="containerized",
        description="Deployment type: containerized, serverless, bare-metal, hybrid",
    )


class PipelineStage(BaseModel):
    stage_name: str = Field(..., description="Pipeline stage name")
    description: str = Field(..., description="What this stage does")
    tools: list[str] = Field(default_factory=list, description="Tools used")
    commands: list[str] = Field(
        default_factory=list, description="Key commands to execute"
    )


class DeploymentGuideOutput(BaseModel):
    deployment_summary: str = Field(
        ..., description="Overview of the deployment architecture"
    )
    docker_configuration: str = Field(
        ..., description="Dockerfile and docker-compose recommendations"
    )
    ci_cd_pipeline: list[PipelineStage] = Field(
        default_factory=list, description="CI/CD pipeline stages"
    )
    environment_config: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables and configuration",
    )
    monitoring_setup: list[str] = Field(
        default_factory=list,
        description="Monitoring, logging, and alerting recommendations",
    )
    scaling_strategy: str = Field(
        default="",
        description="Auto-scaling and load balancing strategy",
    )
    security_checklist: list[str] = Field(
        default_factory=list,
        description="Deployment security checklist",
    )
    rollback_plan: str = Field(
        default="",
        description="Rollback and disaster recovery plan",
    )


DEPLOYMENT_GUIDE_PROMPT = (
    "You are the Deployment Guide Engine of AI ProductOS.\n"
    "Generate a complete deployment guide for the described project.\n"
    "Include:\n"
    "- Docker/containerization configuration\n"
    "- CI/CD pipeline stages with tools and commands\n"
    "- Environment variable configuration\n"
    "- Monitoring, logging, and alerting setup\n"
    "- Auto-scaling and load balancing strategy\n"
    "- Security checklist for production deployment\n"
    "- Rollback and disaster recovery plan\n"
    "Return JSON matching the DeploymentGuideOutput schema."
)
