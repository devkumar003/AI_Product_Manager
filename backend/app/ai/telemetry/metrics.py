from typing import Any

from pydantic import BaseModel, Field


class ServiceMetrics(BaseModel):
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    accumulated_latency_ms: float = 0.0
    provider_usage: dict[str, int] = Field(default_factory=dict)
    model_usage: dict[str, int] = Field(default_factory=dict)


class TelemetryRegistry:
    """
    Tracks and aggregates AI performance, token usage metrics, and resource costs.
    """

    def __init__(self) -> None:
        self._global_metrics = ServiceMetrics()
        self._workspace_metrics: dict[str, ServiceMetrics] = {}

    def record_request(
        self,
        workspace_id: str,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency_ms: float,
        success: bool,
    ) -> None:
        """
        Record operational telemetry variables from an agent or workflow step execution.
        """
        # 1. Update Global Metrics
        self._update_metrics_object(
            self._global_metrics, provider, model, tokens, cost, latency_ms, success
        )

        # 2. Update Workspace-level Metrics
        if workspace_id not in self._workspace_metrics:
            self._workspace_metrics[workspace_id] = ServiceMetrics()
        self._update_metrics_object(
            self._workspace_metrics[workspace_id],
            provider,
            model,
            tokens,
            cost,
            latency_ms,
            success,
        )

    def _update_metrics_object(
        self,
        metrics: ServiceMetrics,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency_ms: float,
        success: bool,
    ) -> None:
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        metrics.total_tokens += tokens
        metrics.total_cost_usd += cost
        metrics.accumulated_latency_ms += latency_ms

        metrics.provider_usage[provider] = metrics.provider_usage.get(provider, 0) + 1
        metrics.model_usage[model] = metrics.model_usage.get(model, 0) + 1

    def get_global_summary(self) -> dict[str, Any]:
        return self._format_summary(self._global_metrics)

    def get_workspace_summary(self, workspace_id: str) -> dict[str, Any]:
        metrics = self._workspace_metrics.get(workspace_id, ServiceMetrics())
        return self._format_summary(metrics)

    def _format_summary(self, m: ServiceMetrics) -> dict[str, Any]:
        success_rate = (
            (m.successful_requests / m.total_requests) * 100
            if m.total_requests > 0
            else 100.0
        )
        avg_latency = (
            m.accumulated_latency_ms / m.total_requests if m.total_requests > 0 else 0.0
        )
        return {
            "total_requests": m.total_requests,
            "success_rate_percent": round(success_rate, 2),
            "total_tokens_consumed": m.total_tokens,
            "total_cost_usd": round(m.total_cost_usd, 6),
            "average_latency_ms": round(avg_latency, 2),
            "provider_distribution": m.provider_usage,
            "model_distribution": m.model_usage,
        }
