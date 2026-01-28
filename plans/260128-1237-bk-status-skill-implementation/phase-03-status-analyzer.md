# Phase 3: Status Analyzer Implementation

## Context

- **Parent Plan:** [bk-status Implementation](./plan.md)
- **Depends On:** [Phase 2: TDD Test Fixtures](./phase-02-tdd-test-fixtures.md)
- **Research:** [Backlog API Capabilities](./research/researcher-02-backlog-api.md)

---

## Overview

| Field | Value |
|-------|-------|
| Priority | P0 |
| Status | ✅ DONE |
| Effort | 1.5h |
| Date | 2026-01-28 |

**Goal:** Implement `StatusAnalyzer` class to pass all TDD tests.

---

## Key Insights

1. **Active vs Closed:** Only "Closed" status (validated decision - simple, final status only)
2. **Workload calculation:** Simple count, weighted priority optional (post-MVP)
3. **Days overdue:** `(today - due_date).days`
4. **Markdown tables:** Pipe-delimited format

---

## Requirements

### Functional
- `get_late_tasks(issues, today)` - Filter and enrich with days_overdue
- `get_workload(issues, users)` - Count per assignee
- `get_overloaded_members(issues, users, threshold)` - Filter by threshold
- `get_summary(issues)` - Status counts and progress %
- `generate_report(issues, users, today)` - Full Markdown report

### Non-Functional
- Pure Python, no external deps
- Testable without API calls
- Type hints throughout

---

## Architecture

```
StatusAnalyzer
├── __init__(statuses, closed_status_names)  # Config
├── _is_closed(status_id) -> bool            # Helper
├── _parse_date(date_str) -> date            # Helper
├── get_late_tasks(issues, today) -> list
├── get_workload(issues, users) -> dict
├── get_overloaded_members(issues, users, threshold) -> list
├── get_summary(issues) -> dict
└── generate_report(issues, users, today) -> str
```

---

## Related Code Files

### To Create
| File | Purpose |
|------|---------|
| `.claude/skills/bk-status/scripts/__init__.py` | Package marker |
| `.claude/skills/bk-status/scripts/status_analyzer.py` | Core logic |

### Reference (read-only)
| File | Purpose |
|------|---------|
| `.claude/skills/backlog/scripts/models.py` | Issue, User, Status models |

---

## Implementation Steps

### Step 1: Create directory and __init__.py

```bash
mkdir -p .claude/skills/bk-status/scripts
touch .claude/skills/bk-status/scripts/__init__.py
```

### Step 2: Create status_analyzer.py

```python
"""Status analyzer for bk-status skill."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class StatusAnalyzer:
    """Analyzes project status from Backlog issues."""

    def __init__(
        self,
        statuses: list[dict],
        closed_status_names: Optional[list[str]] = None
    ):
        """Initialize analyzer.

        Args:
            statuses: List of status dicts from API
            closed_status_names: Names considered "closed" (default: ["Closed"])
        """
        self.statuses = {s["id"]: s["name"] for s in statuses}
        self.closed_status_names = closed_status_names or ["Closed"]
        self.closed_status_ids = {
            sid for sid, name in self.statuses.items()
            if name in self.closed_status_names
        }

    def _is_closed(self, status_id: int) -> bool:
        """Check if status is considered closed."""
        return status_id in self.closed_status_ids

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            # Handle both formats: "2026-01-28" and "2026-01-28T10:00:00Z"
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None

    def _get_status_id(self, issue: dict) -> int:
        """Extract status ID from issue dict."""
        status = issue.get("status", {})
        if isinstance(status, dict):
            return status.get("id", 0)
        return issue.get("status_id", 0)

    def _get_assignee_id(self, issue: dict) -> Optional[int]:
        """Extract assignee ID from issue dict."""
        assignee = issue.get("assignee")
        if isinstance(assignee, dict):
            return assignee.get("id")
        return issue.get("assignee_id")

    def get_late_tasks(self, issues: list[dict], today: date) -> list[dict]:
        """Get tasks that are past due date but not closed.

        Args:
            issues: List of issue dicts
            today: Current date for comparison

        Returns:
            List of late tasks with days_overdue added
        """
        late = []

        for issue in issues:
            due_date = self._parse_date(issue.get("dueDate"))
            if not due_date:
                continue  # No due date = not late

            status_id = self._get_status_id(issue)
            if self._is_closed(status_id):
                continue  # Already closed

            if due_date < today:
                days_overdue = (today - due_date).days
                late.append({
                    **issue,
                    "days_overdue": days_overdue
                })

        # Sort by days overdue (most overdue first)
        return sorted(late, key=lambda x: x["days_overdue"], reverse=True)

    def get_workload(self, issues: list[dict], users: list[dict]) -> dict:
        """Calculate workload per assignee.

        Args:
            issues: List of issue dicts
            users: List of user dicts

        Returns:
            Dict mapping assignee_id -> {name, open_count}
        """
        # Initialize with all users
        workload = {
            u["id"]: {"name": u["name"], "open_count": 0}
            for u in users
        }
        workload["unassigned"] = {"name": "Unassigned", "open_count": 0}

        for issue in issues:
            status_id = self._get_status_id(issue)
            if self._is_closed(status_id):
                continue  # Don't count closed issues

            assignee_id = self._get_assignee_id(issue)
            if assignee_id and assignee_id in workload:
                workload[assignee_id]["open_count"] += 1
            else:
                workload["unassigned"]["open_count"] += 1

        return workload

    def get_overloaded_members(
        self,
        issues: list[dict],
        users: list[dict],
        threshold: int = 5
    ) -> list[dict]:
        """Get members with more than threshold open issues.

        Args:
            issues: List of issue dicts
            users: List of user dicts
            threshold: Max acceptable open issues

        Returns:
            List of overloaded member dicts
        """
        workload = self.get_workload(issues, users)

        overloaded = []
        for user_id, data in workload.items():
            if user_id == "unassigned":
                continue
            if data["open_count"] > threshold:
                overloaded.append({
                    "id": user_id,
                    "name": data["name"],
                    "open_count": data["open_count"]
                })

        return sorted(overloaded, key=lambda x: x["open_count"], reverse=True)

    def get_summary(self, issues: list[dict]) -> dict:
        """Get project summary with status counts.

        Args:
            issues: List of issue dicts

        Returns:
            Summary dict with by_status, total, progress_percent
        """
        if not issues:
            return {
                "total": 0,
                "by_status": {},
                "closed_count": 0,
                "progress_percent": 0
            }

        by_status = {}
        closed_count = 0

        for issue in issues:
            status_id = self._get_status_id(issue)
            status_name = self.statuses.get(status_id, "Unknown")

            by_status[status_name] = by_status.get(status_name, 0) + 1

            if self._is_closed(status_id):
                closed_count += 1

        total = len(issues)
        progress = (closed_count / total * 100) if total > 0 else 0

        return {
            "total": total,
            "by_status": by_status,
            "closed_count": closed_count,
            "progress_percent": round(progress, 2)
        }

    def generate_report(
        self,
        issues: list[dict],
        users: list[dict],
        today: date,
        project_name: str = "Project"
    ) -> str:
        """Generate Markdown status report.

        Args:
            issues: List of issue dicts
            users: List of user dicts
            today: Current date
            project_name: Name for report header

        Returns:
            Markdown formatted report string
        """
        late_tasks = self.get_late_tasks(issues, today)
        workload = self.get_workload(issues, users)
        summary = self.get_summary(issues)

        lines = [
            f"# Project Status Report",
            f"",
            f"**Date:** {today.isoformat()}",
            f"**Project:** {project_name}",
            f"",
        ]

        # Summary section
        lines.extend([
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Issues | {summary['total']} |",
            f"| Closed | {summary['closed_count']} |",
            f"| Progress | {summary['progress_percent']:.1f}% |",
            "",
        ])

        # Status breakdown
        lines.append("### By Status")
        lines.append("")
        lines.append("| Status | Count |")
        lines.append("|--------|-------|")
        for status, count in summary["by_status"].items():
            lines.append(f"| {status} | {count} |")
        lines.append("")

        # Late tasks section
        lines.extend([
            "## Late Tasks",
            "",
        ])

        if late_tasks:
            lines.append("| Issue | Summary | Assignee | Days Overdue |")
            lines.append("|-------|---------|----------|--------------|")
            for task in late_tasks:
                issue_key = task.get("issueKey", task.get("key_id", "?"))
                summary_text = task.get("summary", "")[:40]
                assignee = task.get("assignee", {})
                assignee_name = assignee.get("name", "Unassigned") if assignee else "Unassigned"
                days = task["days_overdue"]
                lines.append(f"| {issue_key} | {summary_text} | {assignee_name} | {days} |")
        else:
            lines.append("No late tasks.")
        lines.append("")

        # Workload section
        lines.extend([
            "## Workload",
            "",
            "| Member | Open Issues |",
            "|--------|-------------|",
        ])
        for user_id, data in workload.items():
            if user_id == "unassigned" and data["open_count"] == 0:
                continue
            lines.append(f"| {data['name']} | {data['open_count']} |")
        lines.append("")

        return "\n".join(lines)
```

### Step 3: Run tests to verify

```bash
cd .claude/skills/bk-status
python -m pytest tests/ -v
```

---

## Todo List

- [x] Create scripts directory
- [x] Create __init__.py
- [x] Implement StatusAnalyzer class
- [x] Implement _is_closed helper
- [x] Implement _parse_date helper
- [x] Implement get_late_tasks method
- [x] Implement get_workload method
- [x] Implement get_overloaded_members method
- [x] Implement get_summary method
- [x] Implement generate_report method
- [x] Run tests - all must pass (29/29)

---

## Success Criteria

- [x] All TDD tests pass (29/29)
- [x] Late tasks detected correctly
- [x] Workload calculated per user
- [x] Summary includes progress %
- [x] Markdown report well-formatted

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Date parsing edge cases | Medium | Handle both ISO formats |
| Status ID mismatch | Low | Use dict from API, not hardcoded |
| Large issue list performance | Low | Simple iteration, no API calls |

---

## Security Considerations

- No API calls in analyzer (pure logic)
- No file writes
- No external dependencies

---

## Next Steps

After tests pass: [Phase 4: Skill Structure](./phase-04-skill-structure.md)
