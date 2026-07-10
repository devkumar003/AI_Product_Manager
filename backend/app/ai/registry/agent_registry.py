import inspect
from typing import Any

from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: list[str] = Field(default_factory=list)
    status: str = "active"  # active, inactive, deprecated
    health: str = "healthy"  # healthy, degraded, unhealthy


class AgentRegistry:
    """
    Registry for dynamic discovery, loading, instantiation, and cataloging of AI Agents.
    Supports agent capability mapping, registration metadata, version tracking, and health status logs.
    """

    def __init__(self) -> None:
        self._agents: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        agent_class: type[Any],
        version: str = "1.0.0",
        description: str = "",
        capabilities: list[str] | None = None,
    ) -> None:
        """Register a new agent class in the workspace catalog."""
        metadata = AgentMetadata(
            name=name,
            version=version,
            description=description,
            capabilities=capabilities or [],
        )
        self._agents[name] = {
            "class": agent_class,
            "metadata": metadata,
        }

    def unregister(self, name: str) -> None:
        """Remove an agent from the workspace catalog."""
        if name in self._agents:
            del self._agents[name]

    def get_agent_class(self, name: str) -> type[Any] | None:
        """Retrieve the registered agent class by identifier."""
        entry = self._agents.get(name)
        return entry["class"] if entry else None

    def get_metadata(self, name: str) -> AgentMetadata | None:
        """Retrieve registered metadata for a given agent name."""
        entry = self._agents.get(name)
        return entry["metadata"] if entry else None

    def update_status(self, name: str, status: str, health: str) -> None:
        """Update operational status and health metrics of an agent."""
        if name in self._agents:
            self._agents[name]["metadata"].status = status
            self._agents[name]["metadata"].health = health

    def list_agents(self) -> list[AgentMetadata]:
        """List all active discovered agents in the workspace."""
        return [entry["metadata"] for entry in self._agents.values()]

    def discover_from_module(self, module: Any, base_class: type[Any]) -> None:
        """Automatically scan and register all subclasses of base_class in a python module."""
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, base_class)
                and obj is not base_class
            ):
                # Deduce metadata from class attributes if present, otherwise set defaults
                version = getattr(obj, "version", "1.0.0")
                description = getattr(obj, "__doc__", "") or f"Discovered class {name}"
                capabilities = getattr(obj, "capabilities", [])

                # Normalize registry name to lowercase
                reg_name = name.lower().replace("agent", "")
                self.register(
                    name=reg_name,
                    agent_class=obj,
                    version=version,
                    description=description.strip(),
                    capabilities=capabilities,
                )
