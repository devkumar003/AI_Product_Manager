import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("app.websockets")

router = APIRouter()


class WorkspaceConnectionManager:
    """
    Manages active WebSocket connections grouped by workspace ID.
    Enables real-time collaboration updates across team members.
    """

    def __init__(self):
        # Maps workspace_id -> list of active WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, workspace_id: str, websocket: WebSocket):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        logger.info(
            f"WebSocket connected to workspace {workspace_id}. Total: {len(self.active_connections[workspace_id])}"
        )

    def disconnect(self, workspace_id: str, websocket: WebSocket):
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
        logger.info(f"WebSocket disconnected from workspace {workspace_id}")

    async def broadcast_to_workspace(self, workspace_id: str, message: dict):
        if workspace_id in self.active_connections:
            msg_str = json.dumps(message)
            for connection in self.active_connections[workspace_id]:
                try:
                    await connection.send_text(msg_str)
                except Exception as e:
                    logger.error(f"Error sending broadcast message: {e}")


manager = WorkspaceConnectionManager()


@router.websocket("/ws/workspace/{workspace_id}")
async def workspace_collaboration_ws(websocket: WebSocket, workspace_id: str):
    await manager.connect(workspace_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except Exception:
                payload = {"event": "raw", "data": data}

            # Echo or broadcast updates (e.g. document edits, sprint card moves)
            event_type = payload.get("event", "update")
            await manager.broadcast_to_workspace(
                workspace_id,
                {
                    "event": event_type,
                    "workspace_id": workspace_id,
                    "sender": payload.get("sender", "anonymous"),
                    "data": payload.get("data", {}),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(workspace_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error in workspace {workspace_id}: {e}")
        manager.disconnect(workspace_id, websocket)
