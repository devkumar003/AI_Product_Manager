import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.utils.json_parser import generate_with_json_healing
from app.models.planning import PlanningItem, ResourceRequirement

logger = logging.getLogger("app.services.planning.resource_planner")


class ResourcePlanner:
    """
    Resource Planner. Estimates developer, QA, designer count, infrastructure
    monthly costs, and AI service consumption for Epics and Backlog items.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def plan_resources_for_epic(
        self, db: Session, workspace_id: UUID, epic_id: UUID
    ) -> ResourceRequirement:
        """
        Estimates resource allocations for a specific Epic PlanningItem.
        """
        epic = (
            db.query(PlanningItem)
            .filter(
                PlanningItem.id == epic_id,
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.type == "Epic",
                PlanningItem.deleted_at.is_(None),
            )
            .first()
        )

        if not epic:
            raise ValueError("Epic not found or not of type Epic in this workspace")

        from app.ai.utils.security import AISecurityManager
        # Sanitize and scan for prompt injection
        epic_title = AISecurityManager.sanitize_input(epic.title)
        epic_desc = AISecurityManager.sanitize_input(epic.description or "")
        AISecurityManager.verify_prompt_injection(epic_title)
        if epic_desc:
            AISecurityManager.verify_prompt_injection(epic_desc)

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a Technical Director and Resource Planner. "
                    "Estimate the exact headcount and operational budget needed to build the described Epic.\n"
                    "Provide a JSON response with the following keys:\n"
                    "1. 'developer_count': Integer headcount\n"
                    "2. 'qa_count': Integer headcount\n"
                    "3. 'designer_count': Integer headcount\n"
                    "4. 'infra_cost_est': Float monthly USD hosting cost\n"
                    "5. 'ai_cost_est': Float monthly USD AI/LLM API consumption cost\n"
                    "6. 'duration_weeks': Integer duration\n"
                    "Ensure you return ONLY a clean JSON block."
                ),
            },
            {
                "role": "user",
                "content": f"Estimate resources for Epic: '{epic_title}'\nDescription: {epic_desc or 'No description'}",
            },
        ]

        try:
            data = await generate_with_json_healing(
                self.llm, prompt, {"temperature": 0.2}
            )
        except Exception as e:
            logger.error(f"Failed to generate or parse resource plan JSON: {str(e)}")
            # Fallback mock schema
            data = {
                "developer_count": 3,
                "qa_count": 1,
                "designer_count": 1,
                "infra_cost_est": 150.0,
                "ai_cost_est": 100.0,
                "duration_weeks": 6,
            }

        req = ResourceRequirement(
            workspace_id=workspace_id,
            epic_id=epic_id,
            developer_count=data.get("developer_count", 0),
            qa_count=data.get("qa_count", 0),
            designer_count=data.get("designer_count", 0),
            infra_cost_est=float(data.get("infra_cost_est", 0.0)),
            ai_cost_est=float(data.get("ai_cost_est", 0.0)),
            duration_weeks=data.get("duration_weeks", 0),
        )

        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    def get_resource_plan(
        self, db: Session, req_id: UUID, workspace_id: UUID | None = None
    ) -> ResourceRequirement | None:
        query = db.query(ResourceRequirement).filter(
            ResourceRequirement.id == req_id,
            ResourceRequirement.deleted_at.is_(None),
        )
        if workspace_id:
            query = query.filter(ResourceRequirement.workspace_id == workspace_id)
        return query.first()

    def get_epic_resource_plan(
        self, db: Session, epic_id: UUID, workspace_id: UUID | None = None
    ) -> ResourceRequirement | None:
        query = db.query(ResourceRequirement).filter(
            ResourceRequirement.epic_id == epic_id,
            ResourceRequirement.deleted_at.is_(None),
        )
        if workspace_id:
            query = query.filter(ResourceRequirement.workspace_id == workspace_id)
        return query.first()

    def list_workspace_resource_plans(
        self, db: Session, workspace_id: UUID
    ) -> list[ResourceRequirement]:
        return (
            db.query(ResourceRequirement)
            .filter(
                ResourceRequirement.workspace_id == workspace_id,
                ResourceRequirement.deleted_at.is_(None),
            )
            .all()
        )
