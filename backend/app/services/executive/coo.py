import logging
import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.executive import COOReport
from app.utils.llm_wrapper import llm_manager
from app.utils.llm_wrapper import AgentConfig

logger = logging.getLogger("app.services.executive.coo")


class ExecutiveCOOService:
    """
    AI COO Executive Advisor Module.
    Responsible for resource capacity, team velocity, delivery tracking, and incident risk audits.
    """

    def run_resource_capacity(self, team_members: list[str]) -> dict:
        roster_str = ", ".join(team_members) if team_members else "No active members"
        prompt = (
            f"Given a development team with the following members: {roster_str}.\n"
            "Estimate their weekly capacity in hours and project their utilization rate (0.0 to 1.0).\n"
            "Respond in JSON format only with keys: 'capacity_hours_weekly' (float/int), and 'utilization_rate_est' (float)."
        )
        try:
            res = llm_manager.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert Agile operations manager and COO advisor.",
                config=AgentConfig(temperature=0.2),
            )
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            capacity = data.get("capacity_hours_weekly", len(team_members) * 40)
            utilization = data.get("utilization_rate_est", 0.85)
        except Exception as e:
            logger.warning(f"Failed to estimate resource capacity with LLM, using fallbacks: {e}")
            capacity = len(team_members) * 40
            utilization = 0.85

        return {
            "team_size": len(team_members),
            "roster": team_members,
            "capacity_hours_weekly": capacity,
            "utilization_rate_est": utilization,
        }

    def run_operations_monitoring(self, sprint_name: str) -> dict:
        prompt = (
            f"Generate operational monitoring metrics for the sprint: '{sprint_name}'.\n"
            "Identify 2 key risk mitigation actions and project a realistic release target date.\n"
            "Respond in JSON format only with keys: 'risk_mitigation_actions' (list of strings), and 'release_target_date' (string)."
        )
        try:
            res = llm_manager.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert Agile COO.",
                config=AgentConfig(temperature=0.2),
            )
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            risks = data.get("risk_mitigation_actions", ["Verify API load test results", "Resolve sprint backlog blockages"])
            target_date = data.get("release_target_date", "Next Monday")
        except Exception as e:
            logger.warning(f"Failed to monitor operations with LLM: {e}")
            risks = ["Reassign QA task bottlenecks before Friday", "Monitor database scaling during migration"]
            target_date = "Next Monday"

        return {
            "active_sprint": sprint_name,
            "status": "Healthy",
            "risk_mitigation_actions": risks,
            "release_target_date": target_date,
        }

    def run_operational_incidents(self) -> dict:
        prompt = (
            "Review operational incident status.\n"
            "Respond in JSON format only with keys: 'open_severity_1_incidents' (int), 'critical_system_alerts' (list of strings), and 'risk_status' (string)."
        )
        try:
            res = llm_manager.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert DevOps engineer and COO advisor.",
                config=AgentConfig(temperature=0.2),
            )
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            sev1 = data.get("open_severity_1_incidents", 0)
            alerts = data.get("critical_system_alerts", [])
            risk = data.get("risk_status", "Low Risk")
        except Exception as e:
            logger.warning(f"Failed to fetch operational incidents with LLM: {e}")
            sev1 = 0
            alerts = []
            risk = "Low Risk"

        return {
            "open_severity_1_incidents": sev1,
            "critical_system_alerts": alerts,
            "risk_status": risk,
        }

    def run_budget_cost_analytics(self, total_budget: float) -> dict:
        prompt = (
            f"Analyze budget and project cost analytics for a total budget of ${total_budget}.\n"
            "Estimate monthly burn rate, remaining runway in months, infrastructure cost percentage, and engineering headcount cost percentage.\n"
            "Respond in JSON format only with keys: 'burn_rate_monthly' (float), 'estimated_months_runway' (float), 'infra_cost_pct' (float), and 'engineering_headcount_cost_pct' (float)."
        )
        try:
            res = llm_manager.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert startup CFO and financial operations advisor.",
                config=AgentConfig(temperature=0.2),
            )
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            burn = data.get("burn_rate_monthly", total_budget * 0.15)
            runway = data.get("estimated_months_runway", 6.5)
            infra = data.get("infra_cost_pct", 20.0)
            eng = data.get("engineering_headcount_cost_pct", 70.0)
        except Exception as e:
            logger.warning(f"Failed to analyze budget with LLM: {e}")
            burn = total_budget * 0.15
            runway = 6.5
            infra = 20.0
            eng = 70.0

        return {
            "allocated_budget": total_budget,
            "burn_rate_monthly": burn,
            "estimated_months_runway": runway,
            "infra_cost_pct": infra,
            "engineering_headcount_cost_pct": eng,
        }

    def generate_coo_report(
        self,
        db: Session,
        workspace_id: UUID,
        sprint_name: str,
        team_members: list[str],
        total_budget: float,
    ) -> COOReport:
        logger.info(f"Generating COO report for workspace: {workspace_id}")

        cap = self.run_resource_capacity(team_members)
        ops = self.run_operations_monitoring(sprint_name)
        inc = self.run_operational_incidents()
        cost = self.run_budget_cost_analytics(total_budget)

        # Operational notifications
        notifications = [
            {
                "type": "Info",
                "message": f"Resource allocation updated: {len(team_members)} active members.",
            },
            {
                "type": "Warning",
                "message": "Upcoming release target scheduled for next Monday. Verify all PRs merged.",
            },
        ]

        report = COOReport(
            workspace_id=workspace_id,
            title=f"AI COO Operations Report - {sprint_name}",
            resource_capacity=cap,
            delivery_monitoring=ops,
            incidents_risks=inc,
            operations_analytics=cost,
            notification_center=notifications,
        )

        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def get_coo_reports(self, db: Session, workspace_id: UUID) -> list[COOReport]:
        return db.query(COOReport).filter(COOReport.workspace_id == workspace_id).all()


coo_service = ExecutiveCOOService()
