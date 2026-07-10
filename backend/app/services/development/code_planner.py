import logging
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.development import CodePlan
from app.services.ai.orchestrator import ai_orchestrator
from app.services.ai.llm_manager import llm_manager
from app.services.ai.agents.base import AgentConfig

logger = logging.getLogger("app.services.development.code_planner")


class CodePlanner:
    def create_plan(
        self, 
        db: Session, 
        workspace_id: UUID, 
        title: str, 
        description: str,
        requirements: str
    ) -> CodePlan:
        """
        AI Code Planning Pipeline.
        Converts user descriptions and requirements into a structured, step-by-step code plan.
        """
        logger.info(f"Generating Code Plan for workspace: {workspace_id}")
        
        # Invoke orchestrator or LLM manager directly to draft step-by-step steps
        prompt = (
            f"You are a Staff Software Architect. Draft a step-by-step technical implementation plan for a product with the following description:\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Requirements details: {requirements}\n\n"
            f"Provide a structured plan with target components (Database, Backend APIs, Frontend Views) and a list of steps to execute."
        )
        
        try:
            messages = [
                {"role": "system", "content": "You are a Staff Technical Planner. Return plain text instructions."},
                {"role": "user", "content": prompt}
            ]
            content = llm_manager.generate_sync(
                messages=messages,
                temperature=0.2
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}. Falling back to default plan.")
            content = "1. Setup development branch.\n2. Initialize database models.\n3. Implement CRUD REST APIs.\n4. Design frontend user interface views."

        # Parse steps from lines
        steps = [line.strip() for line in content.split("\n") if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-"))]
        if not steps:
            steps = [
                "Initialize repository structure and base templates",
                "Define SQL schema design DDL migrations",
                "Develop FastAPI controller routes",
                "Build Next.js responsive UI forms",
                "Generate unit tests coverage files"
            ]

        # Save to database
        code_plan = CodePlan(
            workspace_id=workspace_id,
            title=title,
            description=description,
            scope={
                "requirements_summary": requirements[:500],
                "target_languages": ["Python", "TypeScript", "SQL"],
                "created_by": "AI Planning Pipeline"
            },
            steps=steps,
            status="Planned"
        )
        db.add(code_plan)
        db.commit()
        db.refresh(code_plan)
        return code_plan

    def get_plans(self, db: Session, workspace_id: UUID) -> list[CodePlan]:
        return db.query(CodePlan).filter(CodePlan.workspace_id == workspace_id).all()

    def update_plan_status(self, db: Session, workspace_id: UUID, plan_id: UUID, status: str) -> CodePlan | None:
        plan = db.query(CodePlan).filter(
            CodePlan.id == plan_id, 
            CodePlan.workspace_id == workspace_id
        ).first()
        if plan:
            plan.status = status
            db.commit()
            db.refresh(plan)
        return plan


code_planner = CodePlanner()
