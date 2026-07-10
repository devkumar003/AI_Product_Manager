"""
Agent Communication Bus — Task 26

Provides:
- Agent-to-Agent messaging via a shared context bus
- Shared memory references across agents within a workflow
- Output schema standardization enforcement
- Agent registry lookup for dynamic chaining
"""

import logging
from typing import Any
from pydantic import BaseModel, Field

from app.ai.schemas import AgentResponse

logger = logging.getLogger("app.ai.agents.communication")


class AgentMessage(BaseModel):
    """A message sent between agents through the communication bus."""
    source_agent: str = Field(..., description="Name of the sending agent")
    target_agent: str = Field(..., description="Name of the receiving agent")
    payload: dict[str, Any] = Field(default_factory=dict, description="Structured data payload")
    message_type: str = Field(default="output_handoff", description="Type: output_handoff, query, feedback")


class SharedContext(BaseModel):
    """
    Workspace-scoped shared context carried across all agents in a workflow execution.
    Every agent reads from and writes to this context so downstream agents
    have access to all prior agent outputs without direct coupling.
    """
    workspace_id: str
    user_id: str
    idea: str = ""
    agent_outputs: dict[str, AgentResponse] = Field(
        default_factory=dict,
        description="Map of agent_name -> AgentResponse from completed agents",
    )
    message_log: list[AgentMessage] = Field(
        default_factory=list,
        description="Ordered log of all inter-agent messages",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata shared across agents",
    )

    def get_agent_output(self, agent_name: str) -> AgentResponse | None:
        """Retrieve a specific agent's output from the shared context."""
        return self.agent_outputs.get(agent_name)

    def get_combined_summary(self) -> str:
        """Concatenate all agent summaries into a single context string for downstream agents."""
        parts = []
        for name, output in self.agent_outputs.items():
            parts.append(f"[{name.upper()}]: {output.summary}")
        return "\n".join(parts) if parts else ""

    def store_agent_output(self, agent_name: str, output: AgentResponse) -> None:
        """Record an agent's output and log the storage event."""
        self.agent_outputs[agent_name] = output
        logger.info(f"Stored output for agent '{agent_name}' in shared context.")


class AgentCommunicationBus:
    """
    Central message bus enabling agent-to-agent communication.
    Agents never call each other directly; they post messages to the bus
    and the orchestrator routes them.
    """

    def __init__(self) -> None:
        self._message_queue: list[AgentMessage] = []
        self._subscribers: dict[str, list[str]] = {}

    def send_message(self, message: AgentMessage) -> None:
        """Enqueue a message from one agent to another."""
        self._message_queue.append(message)
        logger.info(
            f"Message queued: {message.source_agent} -> {message.target_agent} "
            f"(type={message.message_type})"
        )

    def get_messages_for(self, agent_name: str) -> list[AgentMessage]:
        """Retrieve all pending messages addressed to a specific agent."""
        targeted = [m for m in self._message_queue if m.target_agent == agent_name]
        # Remove consumed messages from the queue
        self._message_queue = [m for m in self._message_queue if m.target_agent != agent_name]
        return targeted

    def broadcast(self, source_agent: str, payload: dict[str, Any]) -> None:
        """Send a message to all registered agents (fan-out)."""
        for subscriber_name in self._subscribers.get("_all", []):
            self.send_message(
                AgentMessage(
                    source_agent=source_agent,
                    target_agent=subscriber_name,
                    payload=payload,
                    message_type="broadcast",
                )
            )

    def subscribe(self, agent_name: str, channel: str = "_all") -> None:
        """Subscribe an agent to a communication channel."""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        if agent_name not in self._subscribers[channel]:
            self._subscribers[channel].append(agent_name)

    def flush(self) -> list[AgentMessage]:
        """Drain and return all queued messages."""
        drained = list(self._message_queue)
        self._message_queue.clear()
        return drained
