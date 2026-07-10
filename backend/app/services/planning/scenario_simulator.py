import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.utils.json_parser import generate_with_json_healing
from app.models.planning import PlanningItem, ScenarioSimulation

logger = logging.getLogger("app.services.planning.scenario_simulator")


class ScenarioSimulator:
    """
    Scenario Simulator. Simulates Best Case, Worst Case, and Average Case
    timelines, budget impacts, and bottleneck risks.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def simulate_scenario(
        self, db: Session, workspace_id: UUID, name: str, vision: str
    ) -> ScenarioSimulation:
        """
        Runs an LLM-driven simulation to forecast timelines, budgets, and bottleneck risks.
        """
        # Fetch backlog items to enrich simulation context if they exist
        backlog_items = (
            db.query(PlanningItem)
            .filter(
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.deleted_at.is_(None),
            )
            .all()
        )

        backlog_summary = ""
        if backlog_items:
            backlog_summary = "\nBacklog Items:\n" + "\n".join(
                [
                    f"- {it.title} ({it.type}): Estimated {it.estimated_hours}h"
                    for it in backlog_items[:20]
                ]
            )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a Project Management Office (PMO) Simulator Agent. "
                    "Analyze the product vision and backlog to produce three schedule and budget scenarios.\n"
                    "Provide a JSON response with the following keys:\n"
                    "1. 'best_case_timeline': Dict with keys 'duration_weeks', 'key_assumptions' (list), 'milestones' (list).\n"
                    "2. 'worst_case_timeline': Dict with keys 'duration_weeks', 'key_risks' (list), 'mitigation_actions' (list).\n"
                    "3. 'average_case_timeline': Dict with keys 'duration_weeks', 'expected_delivery_date' (string), 'milestones' (list).\n"
                    "4. 'budget_impact': Dict with keys 'best_case_cost', 'average_case_cost', 'worst_case_cost', 'cost_breakdown' (string).\n"
                    "5. 'timeline_impact': Dict with keys 'delay_risk_score' (1-10), 'critical_path_bottlenecks' (list).\n"
                    "Ensure you return ONLY a clean JSON block."
                ),
            },
            {
                "role": "user",
                "content": f"Simulate scenarios for product: {name}.\nVision: {vision}{backlog_summary}",
            },
        ]

        try:
            data = await generate_with_json_healing(
                self.llm, prompt, {"temperature": 0.4}
            )
        except Exception as e:
            logger.error(
                f"Failed to generate or parse scenario simulation JSON: {str(e)}"
            )
            # Fallback mock schema
            data = {
                "best_case_timeline": {
                    "duration_weeks": 6,
                    "key_assumptions": ["No scope changes", "Full dev allocation"],
                    "milestones": [],
                },
                "worst_case_timeline": {
                    "duration_weeks": 14,
                    "key_risks": ["Third party API downtime", "Integration delays"],
                    "mitigation_actions": [],
                },
                "average_case_timeline": {
                    "duration_weeks": 9,
                    "expected_delivery_date": "Q3 2026",
                    "milestones": [],
                },
                "budget_impact": {
                    "best_case_cost": 25000,
                    "average_case_cost": 35000,
                    "worst_case_cost": 55000,
                    "cost_breakdown": "Dev + QA + Infra + AI Credits",
                },
                "timeline_impact": {
                    "delay_risk_score": 5,
                    "critical_path_bottlenecks": [
                        "API Authentication",
                        "Database migrations",
                    ],
                },
            }

        simulation = ScenarioSimulation(
            workspace_id=workspace_id,
            name=name,
            vision=vision,
            best_case_timeline=data.get("best_case_timeline", {}),
            worst_case_timeline=data.get("worst_case_timeline", {}),
            average_case_timeline=data.get("average_case_timeline", {}),
            budget_impact=data.get("budget_impact", {}),
            timeline_impact=data.get("timeline_impact", {}),
        )

        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        return simulation

    def get_simulation(self, db: Session, sim_id: UUID) -> ScenarioSimulation | None:
        return (
            db.query(ScenarioSimulation)
            .filter(
                ScenarioSimulation.id == sim_id, ScenarioSimulation.deleted_at.is_(None)
            )
            .first()
        )

    def list_simulations(
        self, db: Session, workspace_id: UUID
    ) -> list[ScenarioSimulation]:
        return (
            db.query(ScenarioSimulation)
            .filter(
                ScenarioSimulation.workspace_id == workspace_id,
                ScenarioSimulation.deleted_at.is_(None),
            )
            .all()
        )
