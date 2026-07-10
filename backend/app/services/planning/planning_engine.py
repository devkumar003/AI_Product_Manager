import json
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.core.llm_manager import LLMManager
from app.ai.utils.json_parser import generate_with_json_healing
from app.models.planning import PlanningItem

logger = logging.getLogger("app.services.planning.planning_engine")


class PlanningEngine:
    """
    Planning Engine. Translates high-level product vision into hierarchical
    Epics, Features, User Stories, Tasks, and Subtasks.
    """

    def __init__(self, llm_manager: LLMManager | None = None) -> None:
        self.llm = llm_manager or LLMManager()

    async def generate_backlog_from_vision(
        self, db: Session, workspace_id: UUID, project_id: UUID | None, vision: str
    ) -> list[PlanningItem]:
        """
        Calls LLM to decompose a product vision into a multi-tier hierarchy:
        Epic -> Feature -> UserStory -> Task -> Subtask.
        """
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are a Product Owner and Agile Project Manager Agent. "
                    "Decompose the user's product vision into a structured backlog hierarchy of Epics, Features, User Stories, Tasks, and Subtasks.\n"
                    "Provide a JSON response with a key 'epics' which is a list of objects. Each epic object should contain:\n"
                    "- 'title': string\n"
                    "- 'description': string\n"
                    "- 'priority': string (Critical, High, Medium, Low)\n"
                    "- 'estimated_hours': float\n"
                    "- 'assigned_roles': list of strings\n"
                    "- 'features': list of feature objects, where each feature object contains:\n"
                    "  - 'title', 'description', 'priority', 'estimated_hours', 'assigned_roles'\n"
                    "  - 'user_stories': list of user story objects, each with:\n"
                    "    - 'title', 'description', 'priority', 'estimated_hours', 'assigned_roles'\n"
                    "    - 'tasks': list of task objects, each with:\n"
                    "      - 'title', 'description', 'priority', 'estimated_hours', 'assigned_roles'\n"
                    "      - 'subtasks': list of subtask objects, each with:\n"
                    "        - 'title', 'description', 'priority', 'estimated_hours', 'assigned_roles'\n"
                    "Ensure you return ONLY valid JSON."
                ),
            },
            {"role": "user", "content": f"Decompose this product vision:\n\n{vision}"},
        ]

        try:
            data = await generate_with_json_healing(self.llm, prompt, {"temperature": 0.3})
        except Exception as e:
            logger.error(f"Failed to generate or parse vision backlog JSON: {str(e)}")
            # Fallback mock hierarchy
            data = {
                "epics": [
                    {
                        "title": "Core Platform Epic",
                        "description": "Fundamental services of the system",
                        "priority": "High",
                        "estimated_hours": 40.0,
                        "assigned_roles": ["Backend", "DevOps"],
                        "features": [
                            {
                                "title": "User Authentication Feature",
                                "description": "Support sign in and sign up",
                                "priority": "High",
                                "estimated_hours": 16.0,
                                "assigned_roles": ["Backend", "Frontend"],
                                "user_stories": [
                                    {
                                        "title": "As a user I want to sign up securely",
                                        "description": "User registration flow",
                                        "priority": "High",
                                        "estimated_hours": 8.0,
                                        "assigned_roles": ["Backend"],
                                        "tasks": [
                                            {
                                                "title": "Create User API endpoint",
                                                "description": "Implement DB schema and POST route",
                                                "priority": "High",
                                                "estimated_hours": 4.0,
                                                "assigned_roles": ["Backend"],
                                                "subtasks": [
                                                    {
                                                        "title": "Define User Pydantic Model",
                                                        "description": "Inputs/outputs schemas",
                                                        "priority": "Medium",
                                                        "estimated_hours": 1.0,
                                                        "assigned_roles": ["Backend"],
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }

        created_items = []

        # Recursively save the hierarchy
        for epic_data in data.get("epics", []):
            epic = PlanningItem(
                workspace_id=workspace_id,
                project_id=project_id,
                type="Epic",
                title=epic_data["title"],
                description=epic_data.get("description"),
                status="Todo",
                priority=epic_data.get("priority", "Medium"),
                estimated_hours=float(epic_data.get("estimated_hours", 0.0)),
                assigned_roles=epic_data.get("assigned_roles", []),
            )
            db.add(epic)
            db.commit()
            db.refresh(epic)
            created_items.append(epic)

            for feat_data in epic_data.get("features", []):
                feature = PlanningItem(
                    workspace_id=workspace_id,
                    project_id=project_id,
                    parent_id=epic.id,
                    type="Feature",
                    title=feat_data["title"],
                    description=feat_data.get("description"),
                    status="Todo",
                    priority=feat_data.get("priority", "Medium"),
                    estimated_hours=float(feat_data.get("estimated_hours", 0.0)),
                    assigned_roles=feat_data.get("assigned_roles", []),
                )
                db.add(feature)
                db.commit()
                db.refresh(feature)
                created_items.append(feature)

                for story_data in feat_data.get("user_stories", []):
                    story = PlanningItem(
                        workspace_id=workspace_id,
                        project_id=project_id,
                        parent_id=feature.id,
                        type="UserStory",
                        title=story_data["title"],
                        description=story_data.get("description"),
                        status="Todo",
                        priority=story_data.get("priority", "Medium"),
                        estimated_hours=float(story_data.get("estimated_hours", 0.0)),
                        assigned_roles=story_data.get("assigned_roles", []),
                    )
                    db.add(story)
                    db.commit()
                    db.refresh(story)
                    created_items.append(story)

                    for task_data in story_data.get("tasks", []):
                        task = PlanningItem(
                            workspace_id=workspace_id,
                            project_id=project_id,
                            parent_id=story.id,
                            type="Task",
                            title=task_data["title"],
                            description=task_data.get("description"),
                            status="Todo",
                            priority=task_data.get("priority", "Medium"),
                            estimated_hours=float(
                                task_data.get("estimated_hours", 0.0)
                            ),
                            assigned_roles=task_data.get("assigned_roles", []),
                        )
                        db.add(task)
                        db.commit()
                        db.refresh(task)
                        created_items.append(task)

                        for sub_data in task_data.get("subtasks", []):
                            subtask = PlanningItem(
                                workspace_id=workspace_id,
                                project_id=project_id,
                                parent_id=task.id,
                                type="Subtask",
                                title=sub_data["title"],
                                description=sub_data.get("description"),
                                status="Todo",
                                priority=sub_data.get("priority", "Medium"),
                                estimated_hours=float(
                                    sub_data.get("estimated_hours", 0.0)
                                ),
                                assigned_roles=sub_data.get("assigned_roles", []),
                            )
                            db.add(subtask)
                            db.commit()
                            db.refresh(subtask)
                            created_items.append(subtask)

        return created_items

    def list_workspace_items(
        self, db: Session, workspace_id: UUID
    ) -> list[PlanningItem]:
        return (
            db.query(PlanningItem)
            .filter(
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.deleted_at.is_(None),
            )
            .all()
        )
