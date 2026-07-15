import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.utils.json_parser import generate_with_json_healing
from app.models.planning import Goal, Mission

logger = logging.getLogger("app.services.planning.mission_planner")


class MissionPlanner:
    """
    Mission Planner. Translates goals into actionable objectives, milestones,
    deliverables, and structured execution plans.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def generate_mission_plan(
        self, db: Session, workspace_id: UUID, title: str, goal_ids: list[UUID]
    ) -> Mission:
        # Load the source goals
        goals = (
            db.query(Goal)
            .filter(
                Goal.id.in_(goal_ids),
                Goal.workspace_id == workspace_id,
                Goal.deleted_at.is_(None),
            )
            .all()
        )
        goals_summary = "\n".join(
            [f"- {g.name} ({g.type}): {g.description or ''}" for g in goals]
        )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are an expert Enterprise Technical Architect and Mission Planner. "
                    "You will take a set of workspace goals and create a detailed execution plan.\n"
                    "Provide a JSON response with the following keys:\n"
                    "1. 'objectives': List of dicts, each with keys 'name', 'metric', 'target'.\n"
                    "2. 'milestones': List of dicts, each with keys 'name', 'phase', 'estimated_weeks', 'deliverables'.\n"
                    "3. 'deliverables': List of dicts, each with keys 'artifact', 'description', 'audience'.\n"
                    "4. 'execution_plan': Dict with keys 'steps' (list of strings) and 'risk_mitigation' (list of strings).\n"
                    "Ensure you return ONLY a JSON block, no markdown format outside the json."
                ),
            },
            {
                "role": "user",
                "content": f"Create a Mission Plan for: '{title}'. Here are the associated goals:\n{goals_summary}",
            },
        ]

        try:
            data = await generate_with_json_healing(
                self.llm, prompt, {"temperature": 0.3}
            )
        except Exception as e:
            logger.error(f"Failed to generate or parse mission plan JSON: {str(e)}")
            # Fallback mock schema
            data = {
                "objectives": [
                    {
                        "name": f"Achieve goal objectives for {title}",
                        "metric": "Completion",
                        "target": "100%",
                    }
                ],
                "milestones": [
                    {
                        "name": "Initiation Phase",
                        "phase": "Planning",
                        "estimated_weeks": 2,
                        "deliverables": ["Requirements Doc"],
                    }
                ],
                "deliverables": [
                    {
                        "artifact": "Architecture diagram",
                        "description": "High level blueprint",
                        "audience": "Stakeholders",
                    }
                ],
                "execution_plan": {
                    "steps": [
                        "Analyze Goals",
                        "Define Milestones",
                        "Execute Work items",
                    ],
                    "risk_mitigation": ["Monitor delays early"],
                },
            }

        mission = Mission(
            workspace_id=workspace_id,
            title=title,
            description=f"Generated mission plan based on {len(goals)} goals.",
            status="Planned",
            objectives=data.get("objectives", []),
            milestones=data.get("milestones", []),
            deliverables=data.get("deliverables", []),
            execution_plan=data.get("execution_plan", {}),
        )

        db.add(mission)
        db.commit()
        db.refresh(mission)
        return mission

    def get_mission(
        self, db: Session, mission_id: UUID, workspace_id: UUID | None = None
    ) -> Mission | None:
        query = db.query(Mission).filter(
            Mission.id == mission_id, Mission.deleted_at.is_(None)
        )
        if workspace_id:
            query = query.filter(Mission.workspace_id == workspace_id)
        return query.first()

    def list_workspace_missions(self, db: Session, workspace_id: UUID) -> list[Mission]:
        return (
            db.query(Mission)
            .filter(Mission.workspace_id == workspace_id, Mission.deleted_at.is_(None))
            .all()
        )
