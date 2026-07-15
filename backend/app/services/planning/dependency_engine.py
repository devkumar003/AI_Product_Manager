import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.utils.json_parser import generate_with_json_healing
from app.models.planning import PlanningDependency, PlanningItem

logger = logging.getLogger("app.services.planning.dependency_engine")


class DependencyEngine:
    """
    Dependency Engine. Scans planning items, detects logical, API, database,
    infrastructure, and task-level dependencies using AI, and creates dependency links.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def detect_and_save_dependencies(
        self, db: Session, workspace_id: UUID
    ) -> list[PlanningDependency]:
        """
        Scans all workspace items (particularly Tasks and Features) to discover dependencies.
        """
        # Fetch items
        items = (
            db.query(PlanningItem)
            .filter(
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.deleted_at.is_(None),
            )
            .all()
        )

        if len(items) < 2:
            return []

        # Prepare a list of item profiles for the LLM
        item_profiles = []
        for it in items:
            item_profiles.append(
                {
                    "id": str(it.id),
                    "type": it.type,
                    "title": it.title,
                    "description": it.description or "",
                }
            )

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a Technical Lead and DevOps Architect. "
                    "Analyze the list of project work items and determine dependency relations.\n"
                    "Identify which items MUST be completed BEFORE other items can start.\n"
                    "Consider:\n"
                    "- API dependencies (e.g. frontend needs backend routes)\n"
                    "- Database dependencies (e.g. tasks need schemas/tables)\n"
                    "- Infrastructure dependencies (e.g. server deployment needs cloud setup)\n"
                    "- Blocker dependencies (logical sequence of completion)\n\n"
                    "Provide a JSON response containing a key 'dependencies' which is a list of objects. Each object contains:\n"
                    "- 'source_item_id': string UUID of the blocker / prerequisite item\n"
                    "- 'target_item_id': string UUID of the blocked / dependent item\n"
                    "- 'dependency_type': string (Blocker, API, Database, Infrastructure, Task)\n"
                    "Ensure you only return valid JSON, and only reference the exact IDs provided."
                ),
            },
            {
                "role": "user",
                "content": f"Here is the list of project items:\n{json.dumps(item_profiles)}",
            },
        ]

        detected_deps = []
        try:
            data = await generate_with_json_healing(
                self.llm, prompt, {"temperature": 0.2}
            )
            detected_deps = data.get("dependencies", [])
        except Exception as e:
            logger.error(f"Failed to detect dependencies via LLM: {str(e)}")

        saved_dependencies = []
        for dep in detected_deps:
            try:
                src_id = UUID(dep["source_item_id"])
                tgt_id = UUID(dep["target_item_id"])
                dep_type = dep.get("dependency_type", "Blocker")

                # Verify both exist and belong to the workspace
                src_exists = (
                    db.query(PlanningItem)
                    .filter(PlanningItem.id == src_id, PlanningItem.workspace_id == workspace_id)
                    .first()
                )
                tgt_exists = (
                    db.query(PlanningItem)
                    .filter(PlanningItem.id == tgt_id, PlanningItem.workspace_id == workspace_id)
                    .first()
                )

                if src_exists and tgt_exists and src_id != tgt_id:
                    # Check if dependency already exists
                    existing = (
                        db.query(PlanningDependency)
                        .filter(
                            PlanningDependency.source_item_id == src_id,
                            PlanningDependency.target_item_id == tgt_id,
                        )
                        .first()
                    )

                    if not existing:
                        p_dep = PlanningDependency(
                            workspace_id=workspace_id,
                            source_item_id=src_id,
                            target_item_id=tgt_id,
                            dependency_type=dep_type,
                        )
                        db.add(p_dep)
                        saved_dependencies.append(p_dep)
            except Exception as e:
                logger.warning(f"Error persisting detected dependency: {str(e)}")

        if saved_dependencies:
            db.commit()
            for sd in saved_dependencies:
                db.refresh(sd)

        return saved_dependencies

    def list_dependencies(
        self, db: Session, workspace_id: UUID
    ) -> list[PlanningDependency]:
        return (
            db.query(PlanningDependency)
            .filter(
                PlanningDependency.workspace_id == workspace_id,
                PlanningDependency.deleted_at.is_(None),
            )
            .all()
        )
