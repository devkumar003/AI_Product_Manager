"""
Task 7 — Architecture Generator
Task 8 — Database Generator
Task 9 — API Generator
"""

from typing import Any
from pydantic import BaseModel, Field


# ── Task 7: Architecture Generator ──

class ArchitectureInput(BaseModel):
    requirements: str = Field(..., description="Requirements and technical context")
    technology_preferences: str = Field(default="", description="Any tech stack preferences")


class ArchitectureOutput(BaseModel):
    system_architecture: str = Field(...)
    application_architecture: str = Field(...)
    deployment_architecture: str = Field(...)
    microservice_recommendation: list[dict[str, Any]] = Field(default_factory=list)
    database_recommendation: dict[str, Any] = Field(default_factory=dict)
    caching_recommendation: dict[str, Any] = Field(default_factory=dict)
    security_architecture: list[str] = Field(default_factory=list)
    scalability_plan: list[str] = Field(default_factory=list)
    folder_structure: str = Field(...)


ARCHITECTURE_PROMPT = (
    "You are the Architecture Generator of AI ProductOS.\n"
    "Design a complete system architecture including application layers, deployment topology,\n"
    "microservice boundaries, database selections, caching layers, security controls,\n"
    "and a detailed folder structure.\n"
    "Return JSON matching ArchitectureOutput schema."
)


# ── Task 8: Database Generator ──

class DatabaseInput(BaseModel):
    architecture: str = Field(..., description="Architecture output for schema design")
    requirements: str = Field(default="", description="Requirements for entity extraction")


class DatabaseOutput(BaseModel):
    er_diagram_description: str = Field(...)
    entities: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    indexes: list[dict[str, Any]] = Field(default_factory=list)
    foreign_keys: list[dict[str, Any]] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    migration_strategy: str = Field(...)
    optimization_suggestions: list[str] = Field(default_factory=list)


DATABASE_PROMPT = (
    "You are the Database Generator of AI ProductOS.\n"
    "Design a complete database schema with entities, relationships, indexes,\n"
    "foreign keys, constraints, migration strategy, and optimization tips.\n"
    "Each entity should include name, attributes (name, type, nullable, default), and primary_key.\n"
    "Each relationship should include from_entity, to_entity, type (1:1, 1:N, M:N), foreign_key.\n"
    "Return JSON matching DatabaseOutput schema."
)


# ── Task 9: API Generator ──

class APIInput(BaseModel):
    database_schema: str = Field(..., description="Database schema for endpoint derivation")
    architecture: str = Field(default="", description="Architecture context")


class APIEndpoint(BaseModel):
    path: str
    method: str
    summary: str
    request_body: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any] = Field(default_factory=dict)
    auth_required: bool = True
    pagination: bool = False


class APIOutput(BaseModel):
    endpoints: list[APIEndpoint] = Field(default_factory=list)
    authentication_strategy: str = Field(...)
    authorization_model: str = Field(...)
    pagination_defaults: dict[str, Any] = Field(default_factory=dict)
    sorting_support: list[str] = Field(default_factory=list)
    filtering_support: list[str] = Field(default_factory=list)
    error_schema: dict[str, Any] = Field(default_factory=dict)
    swagger_metadata: dict[str, Any] = Field(default_factory=dict)


API_PROMPT = (
    "You are the API Generator of AI ProductOS.\n"
    "Generate a complete REST API specification from the database schema.\n"
    "Include CRUD endpoints, authentication, authorization, pagination,\n"
    "sorting, filtering, error schemas, and OpenAPI/Swagger metadata.\n"
    "Return JSON matching APIOutput schema."
)
