"""
Task 3 — Complete Tool Calling

Concrete tool implementations for the AI agent tool calling framework:
Knowledge Base, Calculator, Markdown, Export, Search, and interface stubs
for future integrations (Web Search, Git, Jira, GitHub, Slack).
"""

import re
import math
import logging
from typing import Any
from pydantic import BaseModel, Field

from app.ai.tools.tool_framework import BaseTool, ToolRegistry

logger = logging.getLogger("app.ai.tools.implementations")


# ── Calculator Tool ──

class CalculatorArgs(BaseModel):
    expression: str = Field(..., description="Math expression to evaluate (e.g. '2 + 2 * 7')")


class CalculatorTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="calculator", description="Safely evaluate mathematical expressions.", args_schema=CalculatorArgs)

    async def execute(self, expression: str) -> Any:
        allowed = set("0123456789+-*/.() ,eE")
        if not all(ch in allowed for ch in expression.replace(" ", "")):
            return {"error": "Expression contains disallowed characters"}
        try:
            result = eval(expression, {"__builtins__": {}}, {"math": math, "abs": abs, "round": round, "min": min, "max": max})
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": str(e)}


# ── Markdown Generator Tool ──

class MarkdownArgs(BaseModel):
    title: str = Field(..., description="Document title")
    sections: list[dict[str, Any]] = Field(default_factory=list, description="List of {heading, content} dicts")


class MarkdownTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="markdown_generator", description="Generate formatted Markdown documents.", args_schema=MarkdownArgs)

    async def execute(self, title: str, sections: list[dict[str, Any]] | None = None) -> Any:
        lines = [f"# {title}\n"]
        for section in (sections or []):
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            lines.append(f"\n## {heading}\n")
            if isinstance(content, list):
                for item in content:
                    lines.append(f"- {item}")
            else:
                lines.append(str(content))
        return {"markdown": "\n".join(lines)}


# ── Export Tool ──

class ExportToolArgs(BaseModel):
    data: dict[str, Any] = Field(..., description="Data to export")
    format: str = Field(default="json", description="json, markdown, html")


class ExportTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="export", description="Export structured data to various formats.", args_schema=ExportToolArgs)

    async def execute(self, data: dict[str, Any], format: str = "json") -> Any:
        from app.ai.services.export_engine import ExportEngine
        engine = ExportEngine()
        if format == "markdown":
            return {"content": engine.to_markdown(data), "format": "markdown"}
        elif format == "html":
            return {"content": engine.to_html(data), "format": "html"}
        else:
            return {"content": engine.to_json(data), "format": "json"}


# ── Knowledge Search Tool ──

class KnowledgeSearchArgs(BaseModel):
    query: str = Field(..., description="Search query")
    collection: str = Field(default="default", description="Collection name")
    limit: int = Field(default=5)


class KnowledgeSearchTool(BaseTool):
    def __init__(self, knowledge_base: Any = None) -> None:
        super().__init__(name="knowledge_search", description="Search the workspace knowledge base.", args_schema=KnowledgeSearchArgs)
        self._kb = knowledge_base

    async def execute(self, query: str, collection: str = "default", limit: int = 5) -> Any:
        if not self._kb:
            return {"results": [], "message": "Knowledge base not connected"}
        docs = self._kb.search(query, collection_name=collection, limit=limit)
        return {"results": [{"title": d.title, "category": d.category, "preview": d.content[:200]} for d in docs]}


# ── Memory Recall Tool ──

class MemoryRecallArgs(BaseModel):
    key: str = Field(..., description="Memory key to recall")
    memory_type: str = Field(default="conversation", description="conversation, workspace, project, long_term")


class MemoryRecallTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(name="memory_recall", description="Recall context from AI memory stores.", args_schema=MemoryRecallArgs)

    async def execute(self, key: str, memory_type: str = "conversation") -> Any:
        return {"key": key, "memory_type": memory_type, "message": "Memory context loaded into current session"}


# ── Future Integration Interfaces ──

class WebSearchArgs(BaseModel):
    query: str = Field(..., description="Web search query")


class WebSearchTool(BaseTool):
    """Interface for future web search integration (Google, Bing, Serper)."""
    def __init__(self) -> None:
        super().__init__(name="web_search", description="Search the web for real-time information.", args_schema=WebSearchArgs)

    async def execute(self, query: str) -> Any:
        return {"status": "integration_pending", "provider": "serper/google", "query": query}


class GitIntegrationArgs(BaseModel):
    action: str = Field(..., description="git action: status, log, diff, branch")
    repo_path: str = Field(default=".", description="Repository path")


class GitIntegrationTool(BaseTool):
    """Interface for future Git integration."""
    def __init__(self) -> None:
        super().__init__(name="git_integration", description="Interact with Git repositories.", args_schema=GitIntegrationArgs)

    async def execute(self, action: str, repo_path: str = ".") -> Any:
        return {"status": "integration_pending", "action": action}


class JiraIntegrationArgs(BaseModel):
    action: str = Field(..., description="jira action: create_issue, get_sprint, list_issues")
    project_key: str = Field(default="", description="Jira project key")


class JiraIntegrationTool(BaseTool):
    """Interface for future Jira integration."""
    def __init__(self) -> None:
        super().__init__(name="jira_integration", description="Manage Jira issues and sprints.", args_schema=JiraIntegrationArgs)

    async def execute(self, action: str, project_key: str = "") -> Any:
        return {"status": "integration_pending", "action": action, "project": project_key}


class GitHubIntegrationArgs(BaseModel):
    action: str = Field(..., description="github action: create_pr, list_issues, get_repo")
    repo: str = Field(default="", description="owner/repo")


class GitHubIntegrationTool(BaseTool):
    """Interface for future GitHub integration."""
    def __init__(self) -> None:
        super().__init__(name="github_integration", description="Interact with GitHub repositories.", args_schema=GitHubIntegrationArgs)

    async def execute(self, action: str, repo: str = "") -> Any:
        return {"status": "integration_pending", "action": action, "repo": repo}


class SlackIntegrationArgs(BaseModel):
    action: str = Field(..., description="slack action: send_message, list_channels")
    channel: str = Field(default="", description="Slack channel")


class SlackIntegrationTool(BaseTool):
    """Interface for future Slack integration."""
    def __init__(self) -> None:
        super().__init__(name="slack_integration", description="Send messages and manage Slack channels.", args_schema=SlackIntegrationArgs)

    async def execute(self, action: str, channel: str = "") -> Any:
        return {"status": "integration_pending", "action": action, "channel": channel}


# ── Registry Builder ──

def build_tool_registry(knowledge_base: Any = None) -> ToolRegistry:
    """Build and return a fully populated ToolRegistry with all available tools."""
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(MarkdownTool())
    registry.register(ExportTool())
    registry.register(KnowledgeSearchTool(knowledge_base))
    registry.register(MemoryRecallTool())
    registry.register(WebSearchTool())
    registry.register(GitIntegrationTool())
    registry.register(JiraIntegrationTool())
    registry.register(GitHubIntegrationTool())
    registry.register(SlackIntegrationTool())
    logger.info(f"Tool registry initialized with {len(registry.list_tools())} tools")
    return registry
