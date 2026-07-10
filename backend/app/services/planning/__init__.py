from app.services.planning.ai_scheduler import AIScheduler
from app.services.planning.context_compression import ContextCompressor
from app.services.planning.dependency_engine import DependencyEngine
from app.services.planning.execution_queue import ExecutionQueue
from app.services.planning.goal_manager import GoalManager
from app.services.planning.mission_planner import MissionPlanner
from app.services.planning.planning_analytics import PlanningAnalyticsService
from app.services.planning.planning_engine import PlanningEngine
from app.services.planning.resource_planner import ResourcePlanner
from app.services.planning.scenario_simulator import ScenarioSimulator
from app.services.planning.workspace_intelligence import WorkspaceIntelligence

goal_manager = GoalManager()
mission_planner = MissionPlanner()
planning_engine = PlanningEngine()
dependency_engine = DependencyEngine()
execution_queue = ExecutionQueue()
ai_scheduler = AIScheduler()
scenario_simulator = ScenarioSimulator()
resource_planner = ResourcePlanner()
workspace_intelligence = WorkspaceIntelligence()
planning_analytics = PlanningAnalyticsService()
context_compressor = ContextCompressor()

__all__ = [
    "goal_manager",
    "mission_planner",
    "planning_engine",
    "dependency_engine",
    "execution_queue",
    "ai_scheduler",
    "scenario_simulator",
    "resource_planner",
    "workspace_intelligence",
    "planning_analytics",
    "context_compressor",
]
