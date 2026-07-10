import hashlib
import hmac
import logging
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from app.models.integration import IntegrationLog, IntegrationWebhook

logger = logging.getLogger("app.services.integration.webhook_engine")


class WebhookEngine:
    def register_webhook(
        self,
        db: Session,
        workspace_id: UUID,
        name: str,
        target_url: str,
        events: list[str],
        secret_token: str | None = None,
    ) -> IntegrationWebhook:
        """Registers a new webhook subscriber."""
        webhook = IntegrationWebhook(
            workspace_id=workspace_id,
            name=name,
            target_url=target_url,
            events=events,
            secret_token=secret_token
            or "whsec_" + hashlib.sha256(name.encode()).hexdigest()[:16],
            is_active=True,
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        logger.info(
            f"Registered Webhook {name} targeting {target_url} for workspace {workspace_id}"
        )
        return webhook

    def list_webhooks(
        self, db: Session, workspace_id: UUID
    ) -> list[IntegrationWebhook]:
        return (
            db.query(IntegrationWebhook)
            .filter(
                IntegrationWebhook.workspace_id == workspace_id,
                IntegrationWebhook.deleted_at.is_(None),
            )
            .all()
        )

    def delete_webhook(self, db: Session, workspace_id: UUID, webhook_id: UUID) -> bool:
        webhook = (
            db.query(IntegrationWebhook)
            .filter(
                IntegrationWebhook.id == webhook_id,
                IntegrationWebhook.workspace_id == workspace_id,
            )
            .first()
        )
        if not webhook:
            return False
        db.delete(webhook)
        db.commit()
        logger.info(f"Deleted Webhook {webhook_id}")
        return True

    async def trigger_event(
        self, db: Session, workspace_id: UUID, event: str, payload: dict[str, Any]
    ) -> int:
        """Dispatches an event payload to all webhooks subscribed to it."""
        subscribers = (
            db.query(IntegrationWebhook)
            .filter(
                IntegrationWebhook.workspace_id == workspace_id,
                IntegrationWebhook.is_active.is_(True),
                IntegrationWebhook.deleted_at.is_(None),
            )
            .all()
        )

        dispatched_count = 0
        async with httpx.AsyncClient(timeout=5.0) as client:
            for sub in subscribers:
                # Check if subscribed to this event or "*" wildcard
                if event in sub.events or "*" in sub.events:
                    # Sign the payload using secret_token
                    body_bytes = str(payload).encode("utf-8")
                    signature = hmac.new(
                        (sub.secret_token or "").encode("utf-8"),
                        body_bytes,
                        hashlib.sha256,
                    ).hexdigest()

                    headers = {
                        "Content-Type": "application/json",
                        "X-AIProductOS-Event": event,
                        "X-AIProductOS-Signature": signature,
                    }

                    status = "Success"
                    error_msg = None
                    try:
                        res = await client.post(
                            sub.target_url, json=payload, headers=headers
                        )
                        if res.status_code >= 400:
                            status = "Failed"
                            error_msg = f"HTTP Error {res.status_code}: {res.text}"
                    except Exception as e:
                        status = "Failed"
                        error_msg = str(e)

                    # Log execution audit trail
                    log = IntegrationLog(
                        workspace_id=workspace_id,
                        action=f"Webhook Delivery: {event}",
                        status=status,
                        payload={
                            "event": event,
                            "target_url": sub.target_url,
                            "payload": payload,
                        },
                        error_message=error_msg,
                    )
                    db.add(log)
                    dispatched_count += 1

        db.commit()
        logger.info(
            f"Dispatched event {event} to {dispatched_count} webhook subscribers."
        )
        return dispatched_count


webhook_engine = WebhookEngine()
