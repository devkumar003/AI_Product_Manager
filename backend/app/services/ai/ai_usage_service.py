from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ai_token_usage import AITokenUsage

# Approximate cost per 1K tokens in USD
COST_TABLE_USD_PER_1K = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "gemini-1.5-pro": {"prompt": 0.0035, "completion": 0.0105},
    "claude-3-5-sonnet": {"prompt": 0.003, "completion": 0.015},
    "default": {"prompt": 0.002, "completion": 0.006},
}


class AIUsageService:
    @staticmethod
    def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
        rates = COST_TABLE_USD_PER_1K.get(model.lower(), COST_TABLE_USD_PER_1K["default"])
        prompt_cost = (prompt_tokens / 1000.0) * rates["prompt"]
        comp_cost = (completion_tokens / 1000.0) * rates["completion"]
        return round(prompt_cost + comp_cost, 6)

    @classmethod
    def record_usage(
        cls,
        db: Session,
        workspace_id: UUID | str,
        user_id: UUID | str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        provider: str = "openai",
        action_type: str = "chat",
    ) -> AITokenUsage:
        if isinstance(workspace_id, str):
            workspace_id = UUID(workspace_id)
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        cost = cls.calculate_cost(model, prompt_tokens, completion_tokens)
        record = AITokenUsage(
            workspace_id=workspace_id,
            user_id=user_id,
            provider=provider or "openai",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost_usd=cost,
            action_type=action_type,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_workspace_usage_summary(db: Session, workspace_id: UUID | str) -> dict:
        if isinstance(workspace_id, str):
            workspace_id = UUID(workspace_id)

        total_prompt = (
            db.query(func.sum(AITokenUsage.prompt_tokens))
            .filter(AITokenUsage.workspace_id == workspace_id)
            .scalar()
            or 0
        )
        total_comp = (
            db.query(func.sum(AITokenUsage.completion_tokens))
            .filter(AITokenUsage.workspace_id == workspace_id)
            .scalar()
            or 0
        )
        total_cost = (
            db.query(func.sum(AITokenUsage.total_cost_usd))
            .filter(AITokenUsage.workspace_id == workspace_id)
            .scalar()
            or 0.0
        )
        count = (
            db.query(func.count(AITokenUsage.id))
            .filter(AITokenUsage.workspace_id == workspace_id)
            .scalar()
            or 0
        )

        return {
            "workspace_id": str(workspace_id),
            "total_requests": count,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_comp,
            "total_tokens": total_prompt + total_comp,
            "total_cost_usd": round(total_cost, 4),
            "monthly_quota_tokens": 500000,
            "quota_exceeded": (total_prompt + total_comp) >= 500000,
        }


ai_usage_service = AIUsageService()
