import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.integration import IntegrationConnection, IntegrationPlugin

logger = logging.getLogger("app.services.integration.plugin_manager")


class PluginManager:
    # Standard plugins library to seed
    DEFAULT_PLUGINS = [
        {
            "name": "GitHub",
            "slug": "github",
            "plugin_type": "OAuth",
            "category": "Developer Tools",
            "description": "Sync codebases, branches, pull requests, and issues.",
        },
        {
            "name": "GitLab",
            "slug": "gitlab",
            "plugin_type": "OAuth",
            "category": "Developer Tools",
            "description": "Manage repositories, merge requests, issues, and pipelines.",
        },
        {
            "name": "Bitbucket",
            "slug": "bitbucket",
            "plugin_type": "OAuth",
            "category": "Developer Tools",
            "description": "Connect repositories, commits, and pull requests.",
        },
        {
            "name": "Jira",
            "slug": "jira",
            "plugin_type": "OAuth",
            "category": "Productivity",
            "description": "Sync issues, sprints, backlogs, and work logs.",
        },
        {
            "name": "Linear",
            "slug": "linear",
            "plugin_type": "APIKey",
            "category": "Productivity",
            "description": "Issue tracking and lightweight sprint cycles.",
        },
        {
            "name": "Notion",
            "slug": "notion",
            "plugin_type": "OAuth",
            "category": "Knowledge Base",
            "description": "Sync pages, databases, templates, and document boards.",
        },
        {
            "name": "Confluence",
            "slug": "confluence",
            "plugin_type": "OAuth",
            "category": "Knowledge Base",
            "description": "Manage enterprise wikis, notes, and pages.",
        },
        {
            "name": "Slack",
            "slug": "slack",
            "plugin_type": "OAuth",
            "category": "Communication",
            "description": "Deliver automated notifications and chat updates.",
        },
        {
            "name": "Discord",
            "slug": "discord",
            "plugin_type": "Webhook",
            "category": "Communication",
            "description": "Relay alerts, channels logs, and bot commands.",
        },
        {
            "name": "Gmail",
            "slug": "gmail",
            "plugin_type": "OAuth",
            "category": "Email & Calendar",
            "description": "Process inbox threads, triggers, and automated templates.",
        },
        {
            "name": "Outlook",
            "slug": "outlook",
            "plugin_type": "OAuth",
            "category": "Email & Calendar",
            "description": "Sync corporate emails, categories, and calendar events.",
        },
        {
            "name": "Google Calendar",
            "slug": "google_calendar",
            "plugin_type": "OAuth",
            "category": "Email & Calendar",
            "description": "Manage team schedules, meetings, and dates.",
        },
        {
            "name": "Google Drive",
            "slug": "google_drive",
            "plugin_type": "OAuth",
            "category": "Cloud Storage",
            "description": "Index documents, folders, and collaborative workspaces.",
        },
        {
            "name": "OneDrive",
            "slug": "onedrive",
            "plugin_type": "OAuth",
            "category": "Cloud Storage",
            "description": "Access Microsoft corporate file directories.",
        },
        {
            "name": "Zoom",
            "slug": "zoom",
            "plugin_type": "OAuth",
            "category": "Video Calls",
            "description": "Schedule meeting links and retrieve transcripts.",
        },
        {
            "name": "Google Meet",
            "slug": "google_meet",
            "plugin_type": "OAuth",
            "category": "Video Calls",
            "description": "Schedule video calls directly in workspace events.",
        },
        {
            "name": "Microsoft Teams",
            "slug": "teams",
            "plugin_type": "OAuth",
            "category": "Communication",
            "description": "Deliver chat updates and connect meeting invitations.",
        },
        {
            "name": "Figma",
            "slug": "figma",
            "plugin_type": "OAuth",
            "category": "Design & UI",
            "description": "Embed mockups, styles, design tokens, and components.",
        },
    ]

    def seed_default_plugins(self, db: Session) -> None:
        """Seeds the database with standard default plugins if they don't exist."""
        for p in self.DEFAULT_PLUGINS:
            existing = (
                db.query(IntegrationPlugin)
                .filter(IntegrationPlugin.slug == p["slug"])
                .first()
            )
            if not existing:
                plugin = IntegrationPlugin(
                    name=p["name"],
                    slug=p["slug"],
                    description=p["description"],
                    plugin_type=p["plugin_type"],
                    category=p["category"],
                    is_active=True,
                    plugin_version="1.0.0",
                    settings_schema={},
                )
                db.add(plugin)
                logger.info(f"Seeded plugin marketplace item: {p['name']}")
        db.commit()

    def get_plugin_by_slug(self, db: Session, slug: str) -> IntegrationPlugin | None:
        return (
            db.query(IntegrationPlugin).filter(IntegrationPlugin.slug == slug).first()
        )

    def list_plugins(
        self, db: Session, active_only: bool = True
    ) -> list[IntegrationPlugin]:
        query = db.query(IntegrationPlugin)
        if active_only:
            query = query.filter(IntegrationPlugin.is_active.is_(True))
        return query.all()

    def enable_plugin(self, db: Session, plugin_id: UUID) -> IntegrationPlugin | None:
        plugin = (
            db.query(IntegrationPlugin)
            .filter(IntegrationPlugin.id == plugin_id)
            .first()
        )
        if plugin:
            plugin.is_active = True
            db.commit()
            db.refresh(plugin)
        return plugin

    def disable_plugin(self, db: Session, plugin_id: UUID) -> IntegrationPlugin | None:
        plugin = (
            db.query(IntegrationPlugin)
            .filter(IntegrationPlugin.id == plugin_id)
            .first()
        )
        if plugin:
            plugin.is_active = False
            db.commit()
            db.refresh(plugin)
        return plugin

    def update_plugin_version(
        self, db: Session, plugin_id: UUID, new_version: str
    ) -> IntegrationPlugin | None:
        plugin = (
            db.query(IntegrationPlugin)
            .filter(IntegrationPlugin.id == plugin_id)
            .first()
        )
        if plugin:
            plugin.plugin_version = new_version
            db.commit()
            db.refresh(plugin)
        return plugin

    # Connection operations
    def create_connection(
        self,
        db: Session,
        workspace_id: UUID,
        plugin_id: UUID,
        config: dict | None = None,
    ) -> IntegrationConnection:
        # Check if connection already exists
        connection = (
            db.query(IntegrationConnection)
            .filter(
                IntegrationConnection.workspace_id == workspace_id,
                IntegrationConnection.plugin_id == plugin_id,
            )
            .first()
        )

        if connection:
            connection.status = "Connected"
            if config is not None:
                connection.config = config
            connection.last_sync_at = None
            db.commit()
            db.refresh(connection)
            return connection

        connection = IntegrationConnection(
            workspace_id=workspace_id,
            plugin_id=plugin_id,
            config=config or {},
            status="Connected",
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection

    def disconnect_connection(
        self, db: Session, workspace_id: UUID, connection_id: UUID
    ) -> bool:
        conn = (
            db.query(IntegrationConnection)
            .filter(
                IntegrationConnection.id == connection_id,
                IntegrationConnection.workspace_id == workspace_id,
            )
            .first()
        )
        if not conn:
            return False
        conn.status = "Disconnected"
        db.commit()
        return True


plugin_manager = PluginManager()
