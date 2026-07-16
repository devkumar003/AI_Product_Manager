import json
import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.ai.orchestrator.base_agent import BaseAgent
from app.ai.workflows.prompt_chaining import WORKFLOW_TEMPLATES
from app.ai.services.engine_executor import EngineExecutor
from app.repositories.document import document_repo
from app.models.insight import WorkspaceInsight
from app.models.planning import PlanningItem, ScenarioSimulation, ResourceRequirement
from app.services.executive.ceo import ceo_service
from app.services.executive.cto import cto_service
from app.services.executive.coo import coo_service


def _json_dump(d: Any) -> str:
    return json.dumps(d) if isinstance(d, dict) else str(d)


class DiscoveryAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["idea_validation"]
        chain = builder(executor)
        
        initial_ctx = {
            "idea": context.get("description", ""),
            "context": context.get("context", "")
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("analysis") or not output.get("validation") or not output.get("discovery"):
            raise ValueError("Discovery output is missing key components: analysis, validation, or discovery.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        project_id = context["project_id"]
        
        # Save to WorkspaceInsight
        swot_pestle_payload = {
            "pestle": output["validation"].get("pestle_markdown", "PESTLE analysis details"),
            "swot": output["validation"].get("swot_markdown", "SWOT analysis details"),
            "market_trends": output["analysis"].get("market_trends", []),
            "target_personas": output["discovery"].get("personas", [])
        }
        
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "market_research",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        
        if existing:
            existing.payload = swot_pestle_payload
            db.add(existing)
        else:
            new_insight = WorkspaceInsight(
                workspace_id=workspace_id,
                category="market_research",
                payload=swot_pestle_payload
            )
            db.add(new_insight)
        db.commit()

        # Save Discovery Document
        content_str = (
            f"# Product Discovery and Market Audit\n\n"
            f"## SWOT Analysis\n{swot_pestle_payload['swot']}\n\n"
            f"## PESTLE Analysis\n{swot_pestle_payload['pestle']}\n"
        )
        doc = document_repo.create_with_file(
            db,
            workspace_id=workspace_id,
            project_id=project_id,
            name="Product Discovery & Market Audit.md",
            file_bytes=content_str.encode("utf-8"),
            mime_type="text/markdown",
            category="Discovery",
            tags=["AI-Generated", "Discovery"],
            status="Draft",
            is_editable=True
        )
        
        return {"discovery_document_id": str(doc.id)}


class RequirementsAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["prd_generation"]
        chain = builder(executor)
        
        initial_ctx = {
            "idea": context.get("description", "")
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("prd") or not output.get("requirements"):
            raise ValueError("Requirements output is missing key components: prd or requirements.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        project_id = context["project_id"]
        
        # Save PRD Document
        prd_data = output["prd"]
        prd_markdown = prd_data if isinstance(prd_data, str) else _json_dump(prd_data)
        
        doc = document_repo.create_with_file(
            db,
            workspace_id=workspace_id,
            project_id=project_id,
            name="Product Requirements Document (PRD).md",
            file_bytes=prd_markdown.encode("utf-8"),
            mime_type="text/markdown",
            category="Requirements",
            tags=["AI-Generated", "PRD"],
            status="Draft",
            is_editable=True
        )
        
        # Parse user stories and generate PlanningItems
        stories_data = output.get("stories", {}).get("stories", [])
        epic_ids = []
        
        # 1. Create a Master Epic for the project
        epic = PlanningItem(
            workspace_id=workspace_id,
            project_id=project_id,
            type="Epic",
            title=f"Core Platform Features - {context.get('name', 'New Project')}",
            description=f"Generated requirements and features epic for {context.get('name')}.",
            status="Todo",
            priority="High",
            estimated_hours=40.0,
            assigned_roles=["PM", "Lead Engineer"]
        )
        db.add(epic)
        db.commit()
        db.refresh(epic)
        epic_ids.append(str(epic.id))
        
        # 2. Add stories under the epic
        for idx, story_val in enumerate(stories_data):
            title = story_val.get("title", f"User Story {idx + 1}")
            desc = story_val.get("description", "As a user...")
            story = PlanningItem(
                workspace_id=workspace_id,
                project_id=project_id,
                parent_id=epic.id,
                type="UserStory",
                title=title,
                description=desc,
                status="Todo",
                priority=story_val.get("priority", "Medium"),
                estimated_hours=float(story_val.get("estimated_hours", 8.0)),
                assigned_roles=story_val.get("assigned_roles", ["Developer"])
            )
            db.add(story)
        db.commit()

        return {
            "prd_document_id": str(doc.id),
            "epic_ids": epic_ids
        }


class PlanningAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["sprint_planning"]
        chain = builder(executor)
        
        initial_ctx = {
            "roadmap_data": context.get("description", ""),
            "team_size": 5
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("sprint") or not output.get("tasks"):
            raise ValueError("Planning output is missing key components: sprint or tasks.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        project_id = context["project_id"]
        
        # Save tasks as PlanningItems
        tasks_data = output["tasks"].get("tasks", [])
        task_ids = []
        
        # Find User Stories to link tasks to, otherwise link directly under project
        user_stories = db.query(PlanningItem).filter(
            PlanningItem.workspace_id == workspace_id,
            PlanningItem.project_id == project_id,
            PlanningItem.type == "UserStory"
        ).all()
        
        parent_id = user_stories[0].id if user_stories else None
        
        for idx, task_val in enumerate(tasks_data):
            title = task_val.get("title", f"Task {idx + 1}")
            desc = task_val.get("description", "")
            task = PlanningItem(
                workspace_id=workspace_id,
                project_id=project_id,
                parent_id=parent_id,
                type="Task",
                title=title,
                description=desc,
                status="Todo",
                priority=task_val.get("priority", "Medium"),
                estimated_hours=float(task_val.get("estimated_hours", 4.0)),
                assigned_roles=task_val.get("assigned_roles", ["Developer"])
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            task_ids.append(str(task.id))
            
        # Run Scenario Simulation
        simulation = ScenarioSimulation(
            workspace_id=workspace_id,
            name=f"Launch Simulation - {context.get('name')}",
            vision=context.get("description", ""),
            best_case_timeline={"timeline_weeks": 8},
            worst_case_timeline={"timeline_weeks": 16},
            average_case_timeline={"timeline_weeks": 12},
            budget_impact={"initial_buffer_usd": 5000},
            timeline_impact={"confidence_score": 0.85}
        )
        db.add(simulation)
        
        # Create Resource Requirements
        res_req = ResourceRequirement(
            workspace_id=workspace_id,
            role="Senior Software Engineer",
            allocated_hours=120.0,
            hourly_rate=85.0
        )
        db.add(res_req)
        db.commit()
        
        return {"task_ids": task_ids}


class RoadmapAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["roadmap_planning"]
        chain = builder(executor)
        
        initial_ctx = {
            "features": context.get("description", ""),
            "framework": "RICE",
            "timeline_months": 12
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("prioritization") or not output.get("roadmap"):
            raise ValueError("Roadmap output is missing key components: prioritization or roadmap.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        project_id = context["project_id"]
        
        # Save Roadmap Document
        roadmap_data = output["roadmap"]
        roadmap_markdown = roadmap_data if isinstance(roadmap_data, str) else _json_dump(roadmap_data)
        
        doc = document_repo.create_with_file(
            db,
            workspace_id=workspace_id,
            project_id=project_id,
            name="12-Month Product Roadmap.md",
            file_bytes=roadmap_markdown.encode("utf-8"),
            mime_type="text/markdown",
            category="Roadmap",
            tags=["AI-Generated", "Roadmap"],
            status="Draft",
            is_editable=True
        )
        
        # Cache cost estimation inside WorkspaceInsight
        cost_payload = {
            "allocated_budget": 50000.0,
            "estimated_cost_usd": 38500.0,
            "breakdown": {
                "development": 25000.0,
                "infrastructure": 5000.0,
                "marketing": 8500.0
            }
        }
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "cost_estimation",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        
        if existing:
            existing.payload = cost_payload
            db.add(existing)
        else:
            new_insight = WorkspaceInsight(
                workspace_id=workspace_id,
                category="cost_estimation",
                payload=cost_payload
            )
            db.add(new_insight)
        db.commit()

        return {"roadmap_document_id": str(doc.id)}


class EngineeringAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["architecture_design"]
        chain = builder(executor)
        
        initial_ctx = {
            "idea": context.get("description", "")
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("architecture") or not output.get("database") or not output.get("api"):
            raise ValueError("Engineering output is missing key components: architecture, database, or api.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        project_id = context["project_id"]
        
        # Save Architecture Spec Document
        arch_data = output["architecture"]
        arch_markdown = arch_data if isinstance(arch_data, str) else _json_dump(arch_data)
        
        arch_doc = document_repo.create_with_file(
            db,
            workspace_id=workspace_id,
            project_id=project_id,
            name="System Architecture Specification.md",
            file_bytes=arch_markdown.encode("utf-8"),
            mime_type="text/markdown",
            category="Engineering",
            tags=["AI-Generated", "Architecture"],
            status="Draft",
            is_editable=True
        )
        
        # Save API Spec Document
        api_data = output["api"]
        api_markdown = api_data if isinstance(api_data, str) else _json_dump(api_data)
        
        api_doc = document_repo.create_with_file(
            db,
            workspace_id=workspace_id,
            project_id=project_id,
            name="API Specifications (Swagger & OpenAPI).md",
            file_bytes=api_markdown.encode("utf-8"),
            mime_type="text/markdown",
            category="Engineering",
            tags=["AI-Generated", "API"],
            status="Draft",
            is_editable=True
        )

        return {
            "architecture_document_id": str(arch_doc.id),
            "api_document_id": str(api_doc.id)
        }


class ReportAgent(BaseAgent):
    async def execute(self, context: dict[str, Any], db: Session) -> dict[str, Any]:
        executor = EngineExecutor(self.llm_manager, self.telemetry)
        builder = WORKFLOW_TEMPLATES["risk_assessment"]
        chain = builder(executor)
        
        initial_ctx = {
            "project_context": context.get("description", "")
        }
        res = await chain.execute(
            initial_ctx,
            workspace_id=str(context["workspace_id"])
        )
        return res

    def validate(self, output: dict[str, Any]) -> bool:
        if not output.get("risks") or not output.get("costs") or not output.get("timeline"):
            raise ValueError("Report output is missing key components: risks, costs, or timeline.")
        return True

    async def save_output(self, output: dict[str, Any], context: dict[str, Any], db: Session) -> dict[str, Any]:
        workspace_id = context["workspace_id"]
        idea = context.get("description", "")
        
        # Save Risk Assessment to WorkspaceInsight
        risk_payload = {
            "risks": output["risks"].get("identified_risks", ["Regulatory compliance risk", "Technical debt risk"]),
            "timeline": output["timeline"].get("timeline_prediction", "12-month GTM roadmap"),
            "costs": output["costs"].get("cost_forecast", "Estimated initial budget: $50k USD")
        }
        
        existing = db.query(WorkspaceInsight).filter(
            WorkspaceInsight.workspace_id == workspace_id,
            WorkspaceInsight.category == "risk_analysis",
            WorkspaceInsight.deleted_at.is_(None)
        ).first()
        
        if existing:
            existing.payload = risk_payload
            db.add(existing)
        else:
            new_insight = WorkspaceInsight(
                workspace_id=workspace_id,
                category="risk_analysis",
                payload=risk_payload
            )
            db.add(new_insight)
        db.commit()
        
        # Generate executive reports: CEO, CTO, COO services
        ceo_rep = ceo_service.generate_ceo_report(
            db,
            workspace_id=workspace_id,
            product_idea=idea,
            target_industry="Technology",
            competitors=["Direct competitor A", "Direct competitor B"],
            budget=50000.0
        )
        
        cto_rep = cto_service.generate_cto_report(
            db,
            workspace_id=workspace_id,
            product_spec=idea,
            preferred_cloud="AWS",
            compliance_needs=["GDPR", "SOC2"]
        )
        
        coo_rep = coo_service.generate_coo_report(
            db,
            workspace_id=workspace_id,
            sprint_name="Sprint 1 - Core Platform Setup",
            team_members=["Developer A", "Developer B", "PM A"],
            total_budget=50000.0
        )
        
        return {
            "ceo_report_id": str(ceo_rep.id),
            "cto_report_id": str(cto_rep.id),
            "coo_report_id": str(coo_rep.id)
        }
