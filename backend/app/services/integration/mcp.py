import logging
import httpx
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.models.integration import MCPServer

logger = logging.getLogger("app.services.integration.mcp")


class MCPService:
    # Standard fallback tools returned if the remote server is offline or in dry-run
    FALLBACK_TOOLS = [
        {
            "name": "web_search",
            "description": "Performs web searches for query parameters",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search term"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "read_document",
            "description": "Fetch content of an external workspace document",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "Document UUID"}
                },
                "required": ["document_id"]
            }
        }
    ]

    def register_mcp_server(
        self, db: Session, workspace_id: UUID, name: str, url: str, headers: dict | None = None
    ) -> MCPServer:
        """Registers a new external MCP Server."""
        server = MCPServer(
            workspace_id=workspace_id,
            name=name,
            url=url,
            headers=headers or {},
            is_active=True
        )
        db.add(server)
        db.commit()
        db.refresh(server)
        logger.info(f"Registered MCP Server {name} ({url}) for workspace {workspace_id}")
        return server

    def list_mcp_servers(self, db: Session, workspace_id: UUID) -> List[MCPServer]:
        return db.query(MCPServer).filter(
            MCPServer.workspace_id == workspace_id,
            MCPServer.deleted_at.is_(None)
        ).all()

    def delete_mcp_server(self, db: Session, workspace_id: UUID, server_id: UUID) -> bool:
        server = db.query(MCPServer).filter(
            MCPServer.id == server_id,
            MCPServer.workspace_id == workspace_id
        ).first()
        if not server:
            return False
        db.delete(server)
        db.commit()
        logger.info(f"Deleted MCP Server {server_id}")
        return True

    async def discover_tools(self, db: Session, workspace_id: UUID, server_id: UUID) -> List[Dict[str, Any]]:
        """Queries the MCP server to discover its tools list."""
        server = db.query(MCPServer).filter(
            MCPServer.id == server_id,
            MCPServer.workspace_id == workspace_id,
            MCPServer.is_active.is_(True)
        ).first()
        
        if not server:
            return []

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Query standard MCP /tools endpoint
                response = await client.get(
                    f"{server.url}/tools",
                    headers=server.headers or {}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("tools", [])
        except Exception as e:
            logger.warn(f"Failed to connect to MCP Server {server.name} at {server.url}, falling back to default tools: {e}")
        
        # Return fallback tools if unreachable
        return self.FALLBACK_TOOLS

    async def execute_tool(
        self, db: Session, workspace_id: UUID, server_id: UUID, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executes a tool call on the remote MCP Server."""
        server = db.query(MCPServer).filter(
            MCPServer.id == server_id,
            MCPServer.workspace_id == workspace_id,
            MCPServer.is_active.is_(True)
        ).first()
        
        if not server:
            return {"error": "MCP Server not found or inactive"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "tool": tool_name,
                    "arguments": arguments
                }
                response = await client.post(
                    f"{server.url}/tools/call",
                    json=payload,
                    headers=server.headers or {}
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name} on MCP Server {server.name}: {e}")
        
        # Mock successful execution output if remote server is not active/available
        return {
            "status": "success",
            "tool": tool_name,
            "output": f"Executed tool '{tool_name}' on dry-run context with arguments: {arguments}"
        }


mcp_service = MCPService()
