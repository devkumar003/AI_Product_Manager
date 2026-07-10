import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.development import GeneratedCodeFile
from app.services.ai.agents.base import AgentConfig
from app.services.ai.llm_manager import llm_manager

logger = logging.getLogger("app.services.development.pipelines")


class DevelopmentPipelines:
    def run_prd_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Automatic PRD Generation Pipeline.
        """
        logger.info(f"Running PRD pipeline for project: {project_id}")
        system_prompt = "You are a Principal Product Manager. Generate a detailed Product Requirement Document (PRD) in clean Markdown."
        llm_prompt = (
            f"Generate a professional, detailed PRD for '{target_name}' based on these user instructions:\n"
            f"Instructions: {prompt}\n\n"
            f"Include sections for Product Overview, User Personas, Agile User Stories, Functional Requirements, and Non-Functional constraints."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.3),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"docs/PRD_{target_name.replace(' ', '_')}.md",
            file_type="PRD",
            content=response.content,
            language="Markdown",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_requirement_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Requirement Analysis Pipeline.
        """
        logger.info(f"Running Requirement Analysis pipeline for: {target_name}")
        system_prompt = "You are a Senior Business Analyst. Perform a rigorous, multi-faceted requirement analysis in Markdown."
        llm_prompt = (
            f"Perform a comprehensive requirement analysis for the target system '{target_name}':\n"
            f"Product Scope: {prompt}\n\n"
            f"Provide list of User Requirements, System Requirements, API Requirements, Security Requirements, and a Traceability Matrix mapping user demands to technical implementations."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"docs/Requirement_Analysis_{target_name.replace(' ', '_')}.md",
            file_type="RequirementAnalysis",
            content=response.content,
            language="Markdown",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_architecture_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Architecture Generation Pipeline.
        """
        logger.info(f"Running Architecture design pipeline for: {target_name}")
        system_prompt = "You are a Principal Software Architect. Output a comprehensive System Architecture Design Document in Markdown."
        llm_prompt = (
            f"Design a clean architecture diagram and system specifications for the application '{target_name}':\n"
            f"Requirements Details: {prompt}\n\n"
            f"Include high level block structure, design patterns used, microservice interactions, infrastructure flow, and security layers."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"docs/Architecture_{target_name.replace(' ', '_')}.md",
            file_type="Architecture",
            content=response.content,
            language="Markdown",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_database_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Database Schema Generation Pipeline.
        """
        logger.info(f"Running Database DDL generation pipeline for: {target_name}")
        system_prompt = "You are a Senior Database Administrator. Generate production-ready database SQL DDL scripts."
        llm_prompt = (
            f"Write a PostgreSQL database schema script for '{target_name}':\n"
            f"Context: {prompt}\n\n"
            f"Include CREATE TABLE statements, primary keys, foreign keys, constraints, indexes, triggers, and mock data insertion scripts."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.1),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"database/schema_{target_name.lower().replace(' ', '_')}.sql",
            file_type="Database",
            content=response.content,
            language="SQL",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_backend_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Backend Code Generation Pipeline.
        """
        logger.info(f"Running Backend code generation pipeline for: {target_name}")
        system_prompt = "You are a Staff Python & FastAPI developer. Generate production-grade backend controller routes and models."
        llm_prompt = (
            f"Develop a complete FastAPI backend service module for '{target_name}' based on the requirements:\n"
            f"Requirements: {prompt}\n\n"
            f"Ensure proper Pydantic schemas, dependency injection DB sessions, and structured error responses. Include comments."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"backend/app/controllers/{target_name.lower().replace(' ', '_')}.py",
            file_type="Backend",
            content=response.content,
            language="Python",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_frontend_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        Frontend Code Generation Pipeline.
        """
        logger.info(
            f"Running Frontend React components generation pipeline for: {target_name}"
        )
        system_prompt = "You are an Expert React / Next.js and Tailwind CSS developer. Generate gorgeous, responsive TSX views."
        llm_prompt = (
            f"Build a React Next.js page component for '{target_name}':\n"
            f"Interface Goals: {prompt}\n\n"
            f"Include React state hooks, Lucide icons, responsive Tailwind grids, hover effect micro-animations, and descriptive labels. Ensure clean imports."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"frontend/src/app/dashboard/{target_name.lower().replace(' ', '_')}/page.tsx",
            file_type="Frontend",
            content=response.content,
            language="TypeScript",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_api_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        prompt: str,
    ) -> GeneratedCodeFile:
        """
        API Interface / Endpoint Generation Pipeline.
        """
        logger.info(f"Running API specs generation pipeline for: {target_name}")
        system_prompt = "You are an API Architect. Generate standardized API Specifications in OpenAPI YAML format."
        llm_prompt = (
            f"Draft the OpenAPI schema for endpoints related to '{target_name}':\n"
            f"Details: {prompt}\n\n"
            f"Ensure accurate path parameters, query params, JSON request/response schema structures, and HTTP error codes."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.1),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"docs/api_spec_{target_name.lower().replace(' ', '_')}.yaml",
            file_type="API",
            content=response.content,
            language="YAML",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_unit_test_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        code_content: str,
    ) -> GeneratedCodeFile:
        """
        Unit Test Generation Module (generation only, do not execute).
        """
        logger.info(f"Generating unit test suite for: {target_name}")
        system_prompt = "You are a QA Engineering Specialist. Generate comprehensive unit tests in Pytest or Jest."
        llm_prompt = (
            f"Write a thorough suite of unit tests for the following code:\n\n"
            f"```python\n{code_content}\n```\n\n"
            f"Include positive, negative, validation, and boundary conditions. Mock any database or external client dependencies."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"backend/tests/test_unit_{target_name.lower().replace(' ', '_')}.py",
            file_type="UnitTestCase",
            content=response.content,
            language="Python",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_integration_test_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        api_endpoints: str,
    ) -> GeneratedCodeFile:
        """
        Integration Test Generation Module (generation only, do not execute).
        """
        logger.info(f"Generating integration test suite for: {target_name}")
        system_prompt = "You are an Integration Testing Expert. Write automated integration tests targeting HTTP APIs."
        llm_prompt = (
            f"Write integration tests using FastAPIs TestClient/httpx for the following endpoints:\n\n"
            f"Endpoints description: {api_endpoints}\n\n"
            f"Ensure test flows call endpoints sequentially (e.g. Create -> Read -> Update -> Delete) and verify status codes and JSON payload contents."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"backend/tests/test_integration_{target_name.lower().replace(' ', '_')}.py",
            file_type="IntegrationTestCase",
            content=response.content,
            language="Python",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file

    def run_documentation_pipeline(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        target_name: str,
        context: str,
    ) -> GeneratedCodeFile:
        """
        Documentation Generation Pipeline.
        """
        logger.info(f"Running Documentation Generation pipeline for: {target_name}")
        system_prompt = "You are a Lead Technical Writer. Write rich, clean, and comprehensive markdown documentation."
        llm_prompt = (
            f"Generate reference documentation for '{target_name}':\n"
            f"Context: {context}\n\n"
            f"Include an Introduction, Setup Guide, API Reference, Database structure, and Troubleshooting tips."
        )

        response = llm_manager.generate_sync(
            prompt=llm_prompt,
            system_prompt=system_prompt,
            config=AgentConfig(temperature=0.2),
        )

        code_file = GeneratedCodeFile(
            workspace_id=workspace_id,
            project_id=project_id,
            file_path=f"docs/User_Guide_{target_name.lower().replace(' ', '_')}.md",
            file_type="Documentation",
            content=response.content,
            language="Markdown",
            is_merged=False,
        )
        db.add(code_file)
        db.commit()
        db.refresh(code_file)
        return code_file


dev_pipelines = DevelopmentPipelines()
