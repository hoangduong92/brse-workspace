"""Markdown formatter for bk-track reports."""
from typing import Dict, Any, List
from models import TaskStatus, MemberLoad, ProjectHealth, ReportData


class MarkdownFormatter:
    """Format analysis results as markdown."""

    def format_status(self, analysis: Dict[str, Any]) -> str:
        """Format status analysis as markdown.

        Args:
            analysis: Analysis results from StatusAnalyzer

        Returns:
            Markdown formatted string
        """
        health = analysis.get("health")
        if not health:
            return "No analysis data available."

        lines = [
            "# Project Status Report",
            "",
            "## Health Overview",
            f"- **Health Score:** {health.health_score}%",
            f"- **Total Issues:** {health.total_issues}",
            f"- **Completed:** {health.completed}",
            f"- **In Progress:** {health.in_progress}",
            f"- **Late:** {health.late_count}",
            f"- **At Risk:** {health.at_risk_count}",
            "",
        ]

        # Late tasks
        late_tasks = analysis.get("late_tasks", [])
        if late_tasks:
            lines.append("## Late Tasks")
            for task in late_tasks:
                risk_icon = "🔴" if task.risk_level == "high" else "🟡"
                lines.append(f"- {risk_icon} [{task.issue_key}] {task.summary} ({task.days_late}d late)")
            lines.append("")

        # At risk tasks
        at_risk = analysis.get("at_risk_tasks", [])
        if at_risk:
            lines.append("## At Risk")
            for task in at_risk:
                lines.append(f"- [{task.issue_key}] {task.summary}")
            lines.append("")

        # Member workload
        members = analysis.get("member_loads", [])
        if members:
            lines.append("## Team Workload")
            lines.append("| Member | Tasks | Done | Active | Overdue |")
            lines.append("|--------|-------|------|--------|---------|")
            for m in members:
                overdue_flag = "⚠️" if m.overdue > 0 else ""
                lines.append(f"| {m.name} | {m.total_tasks} | {m.completed} | {m.in_progress} | {m.overdue} {overdue_flag} |")
            lines.append("")

        return "\n".join(lines)

    def format_health_badge(self, health: ProjectHealth) -> str:
        """Format health score as badge.

        Args:
            health: ProjectHealth object

        Returns:
            Badge string
        """
        score = health.health_score
        if score >= 80:
            return f"🟢 {score}%"
        elif score >= 50:
            return f"🟡 {score}%"
        else:
            return f"🔴 {score}%"
