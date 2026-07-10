import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.planning import PlanningItem

logger = logging.getLogger("app.services.planning.workspace_intelligence")

# Reusable planning templates library
TEMPLATES = {
    "SaaS": {
        "name": "SaaS Platform Bootstrap Template",
        "description": "Typical epics, features, and tasks to launch a secure, subscription-based SaaS product.",
        "items": [
            {
                "type": "Epic",
                "title": "SaaS Core Infrastructure",
                "description": "Database, server hosting, CORS, routing setups",
                "priority": "High",
                "hours": 40.0,
                "roles": ["DevOps", "Backend"],
            },
            {
                "type": "Feature",
                "title": "Multi-Tenant Authentication",
                "description": "Tenant registration, JWT auth, RBAC roles",
                "priority": "Critical",
                "hours": 24.0,
                "roles": ["Backend", "Frontend"],
            },
            {
                "type": "Feature",
                "title": "Stripe Payments Integration",
                "description": "Pricing tiers, webhooks, checkout flows",
                "priority": "High",
                "hours": 32.0,
                "roles": ["Backend", "Frontend"],
            },
        ],
    },
    "AI Products": {
        "name": "AI Product / Multi-Agent Platform Template",
        "description": "Epics and tasks for LLM integration, prompt templates, vector DB RAG, and agent orchestrators.",
        "items": [
            {
                "type": "Epic",
                "title": "AI Infrastructure and Gateway",
                "description": "LLM Manager, fallback routing, tokens rate limiter",
                "priority": "Critical",
                "hours": 48.0,
                "roles": ["AI Engineer", "Backend"],
            },
            {
                "type": "Feature",
                "title": "Semantic RAG Search",
                "description": "Embedding models, PGVector storage, document ingestion",
                "priority": "High",
                "hours": 32.0,
                "roles": ["AI Engineer", "Backend"],
            },
            {
                "type": "Feature",
                "title": "Agent Orchestrator Dashboard",
                "description": "Agent execution UI, step-by-step token execution, memory storage",
                "priority": "High",
                "hours": 40.0,
                "roles": ["Frontend", "Backend"],
            },
        ],
    },
    "CRM": {
        "name": "Customer Relationship Management (CRM) Template",
        "description": "Typical work items for contacts pipelines, activities tracking, and sales boards.",
        "items": [
            {
                "type": "Epic",
                "title": "Contacts and Accounts Management",
                "description": "CRUD for contacts, custom fields, organization links",
                "priority": "High",
                "hours": 30.0,
                "roles": ["Backend", "Frontend"],
            },
            {
                "type": "Feature",
                "title": "Visual Deals Pipeline",
                "description": "Drag-and-drop kanban board of sales stages",
                "priority": "High",
                "hours": 28.0,
                "roles": ["Frontend", "Backend"],
            },
        ],
    },
    "ERP": {
        "name": "Enterprise Resource Planning (ERP) Template",
        "description": "Work items for inventory tracks, invoice ledgers, and procurement audits.",
        "items": [
            {
                "type": "Epic",
                "title": "General Ledger & Invoicing",
                "description": "Double-entry bookkeeping engines, tax rates, print receipts",
                "priority": "Critical",
                "hours": 60.0,
                "roles": ["Backend", "QA"],
            },
            {
                "type": "Feature",
                "title": "Inventory Control",
                "description": "Real-time stock alerts, warehouses mapping, purchase orders",
                "priority": "High",
                "hours": 45.0,
                "roles": ["Backend", "Frontend"],
            },
        ],
    },
    "Healthcare": {
        "name": "HIPAA Compliant Healthcare Template",
        "description": "Patients records EHR, doctor appointment bookings, and secure audit trails.",
        "items": [
            {
                "type": "Epic",
                "title": "Patient Portal & EHR",
                "description": "Protected health information storage with encrypt-at-rest",
                "priority": "Critical",
                "hours": 50.0,
                "roles": ["Backend", "Security"],
            },
            {
                "type": "Feature",
                "title": "Telehealth Scheduling",
                "description": "Doctor appointments calendar, video room tokens",
                "priority": "High",
                "hours": 35.0,
                "roles": ["Frontend", "Backend"],
            },
        ],
    },
    "Education": {
        "name": "LMS / EdTech Platform Template",
        "description": "Curriculum management, assignments grading, and student progress reports.",
        "items": [
            {
                "type": "Epic",
                "title": "Course Curriculum Builder",
                "description": "Drag-drop lectures, quizzes, and multimedia slides",
                "priority": "High",
                "hours": 40.0,
                "roles": ["Frontend", "Backend"],
            },
            {
                "type": "Feature",
                "title": "Quizzes & Auto-grading",
                "description": "Multiple choice, matching, and text inputs with answer keys",
                "priority": "Medium",
                "hours": 20.0,
                "roles": ["Backend"],
            },
        ],
    },
    "Finance": {
        "name": "FinTech / Portfolio Ledger Template",
        "description": "Transaction processing, charts, budget caps, and multi-currency ledgers.",
        "items": [
            {
                "type": "Epic",
                "title": "Multi-Currency Transactions Engine",
                "description": "Atomic transfers, exchange rates, audit ledgers",
                "priority": "Critical",
                "hours": 55.0,
                "roles": ["Backend", "QA"],
            },
            {
                "type": "Feature",
                "title": "Spending Visualizations",
                "description": "Interactive charts showing category breakdowns",
                "priority": "Medium",
                "hours": 18.0,
                "roles": ["Frontend"],
            },
        ],
    },
    "Mobile Apps": {
        "name": "React Native / Mobile App Template",
        "description": "App store assets, offline storage, push notifications, and bio-auth.",
        "items": [
            {
                "type": "Epic",
                "title": "Mobile App Foundation",
                "description": "React Native base, offline caching, deep-linking routing",
                "priority": "High",
                "hours": 45.0,
                "roles": ["Mobile Developer"],
            },
            {
                "type": "Feature",
                "title": "Push Notifications Service",
                "description": "FCM tokens registration, notification center integration",
                "priority": "Medium",
                "hours": 22.0,
                "roles": ["Backend", "Mobile Developer"],
            },
        ],
    },
}


class WorkspaceIntelligence:
    """
    Workspace Intelligence. Provides reusable templates, compiles roadmaps,
    and returns historical planning telemetry metrics.
    """

    def get_templates(self) -> dict:
        return TEMPLATES

    def apply_template_to_workspace(
        self,
        db: Session,
        workspace_id: UUID,
        project_id: UUID | None,
        template_key: str,
    ) -> list[PlanningItem]:
        if template_key not in TEMPLATES:
            raise ValueError(f"Template '{template_key}' does not exist.")

        template = TEMPLATES[template_key]
        created_items = []

        epic_map = {}  # Keep track of epics to assign features to them

        for item_def in template["items"]:
            # Find parent epic if it is a Feature/Task and we have an epic created
            parent_id = None
            if item_def["type"] != "Epic" and epic_map:
                parent_id = list(epic_map.values())[
                    0
                ]  # Simply bind to the first epic for demo

            item = PlanningItem(
                workspace_id=workspace_id,
                project_id=project_id,
                parent_id=parent_id,
                type=item_def["type"],
                title=item_def["title"],
                description=item_def["description"],
                status="Todo",
                priority=item_def["priority"],
                estimated_hours=item_def["hours"],
                assigned_roles=item_def["roles"],
            )
            db.add(item)
            db.commit()
            db.refresh(item)

            if item_def["type"] == "Epic":
                epic_map[item_def["title"]] = item.id

            created_items.append(item)

        return created_items

    def get_workspace_roadmap(self, db: Session, workspace_id: UUID) -> dict:
        """
        Compiles a timeline-based roadmap of active Epics and Features.
        """
        items = (
            db.query(PlanningItem)
            .filter(
                PlanningItem.workspace_id == workspace_id,
                PlanningItem.deleted_at.is_(None),
            )
            .all()
        )

        epics = [it for it in items if it.type == "Epic"]
        features = [it for it in items if it.type == "Feature"]

        roadmap = []
        for ep in epics:
            ep_features = [f for f in features if f.parent_id == ep.id]
            roadmap.append(
                {
                    "epic_id": str(ep.id),
                    "title": ep.title,
                    "description": ep.description,
                    "status": ep.status,
                    "priority": ep.priority,
                    "estimated_hours": ep.estimated_hours,
                    "features": [
                        {
                            "feature_id": str(fe.id),
                            "title": fe.title,
                            "status": fe.status,
                            "priority": fe.priority,
                            "estimated_hours": fe.estimated_hours,
                        }
                        for fe in ep_features
                    ],
                }
            )

        return {
            "workspace_id": str(workspace_id),
            "roadmap": roadmap,
            "total_epics": len(epics),
            "total_features": len(features),
        }
