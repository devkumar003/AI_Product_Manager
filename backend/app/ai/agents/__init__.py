"""
AI ProductOS — Multi-Agent System
All 24 agents plus the communication bus are exported from this package.
"""

# Task 18 — Analytics
from app.ai.agents.analytics import AnalyticsAgent, AnalyticsAgentInput

# Task 9 — API Architect
from app.ai.agents.api_architect import APIArchitect, APIArchitectInput

# Task 10 — Backend Architect
from app.ai.agents.backend_architect import BackendArchitect, BackendArchitectInput
from app.ai.agents.base import BaseAgent

# Task 4 — Business Analyst
from app.ai.agents.business_analyst import BAAgent, BAAgentInput

# Task 2 — CEO
from app.ai.agents.CEO import CEOAgent, CEOAgentInput
from app.ai.agents.communication import (
    AgentCommunicationBus,
    AgentMessage,
    SharedContext,
)

# Task 8 — Database Architect
from app.ai.agents.database_architect import DBArchitect, DBArchitectInput

# Task 17 — DevOps
from app.ai.agents.devops import DevOpsAgent, DevOpsAgentInput

# Task 20 — Documentation
from app.ai.agents.documentation import DocumentationAgent, DocumentationAgentInput

# Task 23 — Estimation
from app.ai.agents.estimation import EstimationAgent, EstimationAgentInput

# Task 11 — Frontend Architect
from app.ai.agents.frontend_architect import FrontendArchitect, FrontendArchitectInput

# Task 21 — Knowledge
from app.ai.agents.knowledge import KnowledgeAgent, KnowledgeAgentInput

# Task 5 — Market Research
from app.ai.agents.market_research import ResearchAgent, ResearchAgentInput

# Task 19 — Meeting
from app.ai.agents.meeting import MeetingAgent, MeetingAgentInput

# Task 25 — Priority
from app.ai.agents.priority import PriorityAgent, PriorityAgentInput

# Task 3 — Product Manager
from app.ai.agents.product_manager import PMAgent, PMAgentInput

# Task 15 — QA
from app.ai.agents.qa import QAAgent, QAAgentInput

# Task 22 — Review
from app.ai.agents.review import ReviewAgent, ReviewAgentInput

# Task 24 — Risk
from app.ai.agents.risk import RiskAgent, RiskAgentInput

# Task 12 — Roadmap
from app.ai.agents.roadmap import RoadmapAgent, RoadmapAgentInput

# Task 16 — Security
from app.ai.agents.security import SecurityAgent, SecurityAgentInput

# Task 13 — Sprint
from app.ai.agents.sprint import SprintAgent, SprintAgentInput

# Task 14 — Task Generator
from app.ai.agents.task import TaskAgent, TaskAgentInput

# Task 7 — Technical Architect
from app.ai.agents.technical_architect import TechArchitect, TechArchitectInput

# Task 6 — UX Designer
from app.ai.agents.ux_designer import UXAgent, UXAgentInput

__all__ = [
    "BaseAgent",
    "AgentCommunicationBus",
    "AgentMessage",
    "SharedContext",
    "CEOAgent",
    "CEOAgentInput",
    "PMAgent",
    "PMAgentInput",
    "BAAgent",
    "BAAgentInput",
    "ResearchAgent",
    "ResearchAgentInput",
    "UXAgent",
    "UXAgentInput",
    "TechArchitect",
    "TechArchitectInput",
    "DBArchitect",
    "DBArchitectInput",
    "APIArchitect",
    "APIArchitectInput",
    "BackendArchitect",
    "BackendArchitectInput",
    "FrontendArchitect",
    "FrontendArchitectInput",
    "RoadmapAgent",
    "RoadmapAgentInput",
    "SprintAgent",
    "SprintAgentInput",
    "TaskAgent",
    "TaskAgentInput",
    "QAAgent",
    "QAAgentInput",
    "SecurityAgent",
    "SecurityAgentInput",
    "DevOpsAgent",
    "DevOpsAgentInput",
    "AnalyticsAgent",
    "AnalyticsAgentInput",
    "MeetingAgent",
    "MeetingAgentInput",
    "DocumentationAgent",
    "DocumentationAgentInput",
    "KnowledgeAgent",
    "KnowledgeAgentInput",
    "ReviewAgent",
    "ReviewAgentInput",
    "EstimationAgent",
    "EstimationAgentInput",
    "RiskAgent",
    "RiskAgentInput",
    "PriorityAgent",
    "PriorityAgentInput",
]
