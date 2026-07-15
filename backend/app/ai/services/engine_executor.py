"""
Unified Business Engine Executor

Routes all 16 business engines (Tasks 1-16) through the LLM Manager.
Each engine call follows: schema → prompt → LLM → parse → validate → return.
"""

import json
import logging
import time
from typing import Any

from pydantic import BaseModel

from app.ai.core.llm_manager import LLMManager
from app.ai.exceptions import ValidationException
from app.ai.services.architecture_engine import (
    API_PROMPT,
    ARCHITECTURE_PROMPT,
    DATABASE_PROMPT,
    APIInput,
    APIOutput,
    ArchitectureInput,
    ArchitectureOutput,
    DatabaseInput,
    DatabaseOutput,
)
from app.ai.services.estimation_engine import (
    COST_ESTIMATION_PROMPT,
    RISK_ANALYSIS_PROMPT,
    TIMELINE_PROMPT,
    CostEstimationInput,
    CostEstimationOutput,
    RiskAnalysisInput,
    RiskAnalysisOutput,
    TimelineInput,
    TimelineOutput,
)
from app.ai.services.idea_engine import (
    IDEA_ANALYSIS_PROMPT,
    IDEA_VALIDATION_PROMPT,
    PRODUCT_DISCOVERY_PROMPT,
    IdeaAnalysisInput,
    IdeaAnalysisOutput,
    IdeaValidationInput,
    IdeaValidationOutput,
    ProductDiscoveryInput,
    ProductDiscoveryOutput,
)
from app.ai.services.planning_engine import (
    PRIORITIZATION_PROMPT,
    ROADMAP_PROMPT,
    SPRINT_PROMPT,
    TASK_BREAKDOWN_PROMPT,
    PrioritizationInput,
    PrioritizationOutput,
    RoadmapInput,
    RoadmapOutput,
    SprintInput,
    SprintOutput,
    TaskBreakdownInput,
    TaskBreakdownOutput,
)
from app.ai.services.requirement_engine import (
    PRD_PROMPT,
    REQUIREMENT_PROMPT,
    USER_STORY_PROMPT,
    PRDInput,
    PRDOutput,
    RequirementInput,
    RequirementOutput,
    UserStoryInput,
    UserStoryOutput,
)
from app.ai.telemetry.metrics import TelemetryRegistry
from app.ai.utils.security import AISecurityManager
from app.ai.services.intelligence_engines import (
    MarketResearchInput,
    MarketResearchOutput,
    MARKET_RESEARCH_PROMPT,
    CompetitorAnalysisInput,
    CompetitorAnalysisOutput,
    COMPETITOR_ANALYSIS_PROMPT,
)
from app.ai.services.acceptance_criteria_engine import (
    AcceptanceCriteriaInput,
    AcceptanceCriteriaOutput,
    ACCEPTANCE_CRITERIA_PROMPT,
)
from app.ai.services.wireframe_engine import (
    WireframeInput,
    WireframeOutput,
    WIREFRAME_PROMPT,
)
from app.ai.services.testing_strategy_engine import (
    TestingStrategyInput,
    TestingStrategyOutput,
    TESTING_STRATEGY_PROMPT,
)
from app.ai.services.deployment_guide_engine import (
    DeploymentGuideInput,
    DeploymentGuideOutput,
    DEPLOYMENT_GUIDE_PROMPT,
)

logger = logging.getLogger("app.ai.services.engine_executor")


# Map engine names to (InputType, OutputType, system_prompt)
ENGINE_REGISTRY: dict[str, tuple[type[BaseModel], type[BaseModel], str]] = {
    "idea_analysis": (IdeaAnalysisInput, IdeaAnalysisOutput, IDEA_ANALYSIS_PROMPT),
    "idea_validation": (
        IdeaValidationInput,
        IdeaValidationOutput,
        IDEA_VALIDATION_PROMPT,
    ),
    "product_discovery": (
        ProductDiscoveryInput,
        ProductDiscoveryOutput,
        PRODUCT_DISCOVERY_PROMPT,
    ),
    "requirement_generator": (RequirementInput, RequirementOutput, REQUIREMENT_PROMPT),
    "user_story_generator": (UserStoryInput, UserStoryOutput, USER_STORY_PROMPT),
    "prd_generator": (PRDInput, PRDOutput, PRD_PROMPT),
    "architecture_generator": (
        ArchitectureInput,
        ArchitectureOutput,
        ARCHITECTURE_PROMPT,
    ),
    "database_generator": (DatabaseInput, DatabaseOutput, DATABASE_PROMPT),
    "api_generator": (APIInput, APIOutput, API_PROMPT),
    "roadmap_generator": (RoadmapInput, RoadmapOutput, ROADMAP_PROMPT),
    "sprint_generator": (SprintInput, SprintOutput, SPRINT_PROMPT),
    "task_breakdown": (TaskBreakdownInput, TaskBreakdownOutput, TASK_BREAKDOWN_PROMPT),
    "feature_prioritization": (
        PrioritizationInput,
        PrioritizationOutput,
        PRIORITIZATION_PROMPT,
    ),
    "cost_estimation": (
        CostEstimationInput,
        CostEstimationOutput,
        COST_ESTIMATION_PROMPT,
    ),
    "timeline_prediction": (TimelineInput, TimelineOutput, TIMELINE_PROMPT),
    "risk_analysis": (RiskAnalysisInput, RiskAnalysisOutput, RISK_ANALYSIS_PROMPT),
    "market_research": (MarketResearchInput, MarketResearchOutput, MARKET_RESEARCH_PROMPT),
    "competitor_analysis": (CompetitorAnalysisInput, CompetitorAnalysisOutput, COMPETITOR_ANALYSIS_PROMPT),
    "acceptance_criteria": (AcceptanceCriteriaInput, AcceptanceCriteriaOutput, ACCEPTANCE_CRITERIA_PROMPT),
    "wireframe_suggestions": (WireframeInput, WireframeOutput, WIREFRAME_PROMPT),
    "testing_strategy": (TestingStrategyInput, TestingStrategyOutput, TESTING_STRATEGY_PROMPT),
    "deployment_guide": (DeploymentGuideInput, DeploymentGuideOutput, DEPLOYMENT_GUIDE_PROMPT),
}
class EngineExecutor:
    """Executes any registered business engine through the LLM pipeline."""

    def __init__(self, llm_manager: LLMManager, telemetry: TelemetryRegistry) -> None:
        self.llm = llm_manager
        self.telemetry = telemetry

    async def execute(
        self,
        engine_name: str,
        input_data: dict[str, Any],
        workspace_id: str = "",
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        if engine_name not in ENGINE_REGISTRY:
            raise ValueError(
                f"Unknown engine: '{engine_name}'. Available: {list(ENGINE_REGISTRY.keys())}"
            )

        # Check database cache first if workspace_id is provided and refresh is not forced
        db = None
        if workspace_id and not input_data.get("refresh", False):
            from app.database.session import SessionLocal
            from app.models.insight import WorkspaceInsight
            from uuid import UUID
            try:
                ws_uuid = UUID(workspace_id)
                db = SessionLocal()
                existing = db.query(WorkspaceInsight).filter(
                    WorkspaceInsight.workspace_id == ws_uuid,
                    WorkspaceInsight.category == engine_name,
                    WorkspaceInsight.deleted_at.is_(None)
                ).first()
                if existing:
                    logger.info(f"Loaded cached engine result for '{engine_name}' in workspace '{workspace_id}'")
                    return existing.payload
            except Exception as e:
                logger.warning(f"Failed to query cache for engine '{engine_name}': {e}")
            finally:
                if db:
                    db.close()

        input_cls, output_cls, system_prompt = ENGINE_REGISTRY[engine_name]
        start_time = time.time()

        # 1. Validate input
        validated_input = input_cls(**input_data)

        # 2. Security check on text fields
        for field_name, value in validated_input.model_dump().items():
            if isinstance(value, str) and value:
                AISecurityManager.verify_prompt_injection(value)

        # 3. Build schema-enforced prompt
        schema_json = json.dumps(output_cls.model_json_schema(), indent=2)
        full_prompt = (
            f"{system_prompt}\n\n"
            f"OUTPUT SCHEMA (return ONLY valid JSON matching this):\n{schema_json}\n"
            f"Do NOT wrap in markdown code fences. Return raw JSON only."
        )

        messages = [
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": validated_input.model_dump_json()},
        ]

        # 4. Execute via LLM Manager
        logger.info(f"Executing engine '{engine_name}'")
        response = await self.llm.generate(
            messages=messages,
            provider=provider,
            model=model,
            max_tokens=8192,
        )

        # 5. Parse and validate output
        content = response.content.strip()
        parsed = self._extract_json(content)

        try:
            validated_output = output_cls(**parsed)
        except Exception as e:
            raise ValidationException(
                message=f"Engine '{engine_name}' output failed validation: {str(e)}",
                details={"raw": content[:500]},
            )

        # 6. Record telemetry
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_request(
            workspace_id=workspace_id,
            provider=response.provider,
            model=response.model,
            tokens=response.usage.total_tokens,
            cost=response.usage.estimated_cost_usd,
            latency_ms=latency,
            success=True,
        )

        # Persist to database if workspace_id is provided
        if workspace_id:
            from app.database.session import SessionLocal
            from app.models.insight import WorkspaceInsight
            from uuid import UUID
            db = None
            try:
                ws_uuid = UUID(workspace_id)
                db = SessionLocal()
                existing = db.query(WorkspaceInsight).filter(
                    WorkspaceInsight.workspace_id == ws_uuid,
                    WorkspaceInsight.category == engine_name,
                    WorkspaceInsight.deleted_at.is_(None)
                ).first()
                if existing:
                    existing.payload = validated_output.model_dump()
                    db.add(existing)
                else:
                    new_insight = WorkspaceInsight(
                        workspace_id=ws_uuid,
                        category=engine_name,
                        payload=validated_output.model_dump()
                    )
                    db.add(new_insight)
                db.commit()
                logger.info(f"Cached engine result for '{engine_name}' in workspace '{workspace_id}'")
            except Exception as e:
                logger.warning(f"Failed to persist engine result for '{engine_name}': {e}")
            finally:
                if db:
                    db.close()

        return validated_output.model_dump()

    def list_engines(self) -> list[dict[str, str]]:
        return [
            {
                "name": name,
                "input_schema": cls[0].__name__,
                "output_schema": cls[1].__name__,
            }
            for name, cls in ENGINE_REGISTRY.items()
        ]

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(cleaned)
        except Exception as e:
            raise ValidationException(
                message=f"Failed to parse engine output as JSON: {str(e)}",
                details={"raw": text[:500]},
            )
