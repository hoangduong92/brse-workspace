# Phase 2: TDD Test Fixtures & Test Cases

## Context

- **Parent Plan:** [bk-status Implementation](./plan.md)
- **Depends On:** [Phase 1: Extend BacklogAPI](./phase-01-extend-backlog-client.md)
- **Research:** [Backlog Skill Analysis](./research/researcher-01-backlog-skill.md)

---

## Overview

| Field | Value |
|-------|-------|
| Priority | P0 |
| Status | ✅ DONE |
| Effort | 1h |
| Date | 2026-01-28 |

**Goal:** Create test fixtures and TDD test cases before implementation.

---

## Key Insights

1. **TDD approach:** Write failing tests first, then implement
2. **Fixtures cover:** Late tasks, on-time tasks, overloaded members, empty project
3. **Test isolation:** Use mocked API responses, not real API calls
4. **Edge cases:** No due date, unassigned issues, zero issues

---

## Requirements

### Functional
- Test fixtures for issues, users, statuses
- Test cases for late task detection
- Test cases for workload calculation
- Test cases for summary generation

### Non-Functional
- Tests run offline (mocked)
- Clear assertion messages
- Fixtures are human-readable JSON

---

## Related Code Files

### To Create
| File | Purpose |
|------|---------|
| `.claude/skills/bk-status/tests/__init__.py` | Package marker |
| `.claude/skills/bk-status/tests/test_status_analyzer.py` | Unit tests |
| `.claude/skills/bk-status/tests/fixtures/sample_issues.json` | Issue test data |
| `.claude/skills/bk-status/tests/fixtures/sample_users.json` | User test data |
| `.claude/skills/bk-status/tests/fixtures/sample_statuses.json` | Status test data |

---

## Implementation Steps

### Step 1: Create directory structure

```bash
mkdir -p .claude/skills/bk-status/tests/fixtures
touch .claude/skills/bk-status/tests/__init__.py
```

### Step 2: Create sample_statuses.json

```json
[
  {"id": 1, "name": "Open", "projectId": 12345, "displayOrder": 1},
  {"id": 2, "name": "In Progress", "projectId": 12345, "displayOrder": 2},
  {"id": 3, "name": "Resolved", "projectId": 12345, "displayOrder": 3},
  {"id": 4, "name": "Closed", "projectId": 12345, "displayOrder": 4}
]
```

### Step 3: Create sample_users.json

```json
[
  {"id": 101, "userId": "tanaka", "name": "Tanaka Taro", "roleType": 2},
  {"id": 102, "userId": "nguyen", "name": "Nguyen Van A", "roleType": 2},
  {"id": 103, "userId": "suzuki", "name": "Suzuki Hanako", "roleType": 2}
]
```

### Step 4: Create sample_issues.json

Design 6 issues covering all scenarios:

```json
[
  {
    "id": 1001,
    "projectId": 12345,
    "issueKey": "TEST-1",
    "summary": "Late task - Tanaka",
    "description": "This task is overdue",
    "issueType": {"id": 1},
    "priority": {"id": 2},
    "status": {"id": 1},
    "assignee": {"id": 101},
    "dueDate": "2026-01-20",
    "created": "2026-01-10T10:00:00Z",
    "updated": "2026-01-15T10:00:00Z"
  },
  {
    "id": 1002,
    "projectId": 12345,
    "issueKey": "TEST-2",
    "summary": "Late task - Nguyen",
    "description": "Also overdue",
    "issueType": {"id": 1},
    "priority": {"id": 2},
    "status": {"id": 2},
    "assignee": {"id": 102},
    "dueDate": "2026-01-25",
    "created": "2026-01-10T10:00:00Z",
    "updated": "2026-01-20T10:00:00Z"
  },
  {
    "id": 1003,
    "projectId": 12345,
    "issueKey": "TEST-3",
    "summary": "On-time task - Tanaka",
    "description": "Due in future",
    "issueType": {"id": 1},
    "priority": {"id": 3},
    "status": {"id": 2},
    "assignee": {"id": 101},
    "dueDate": "2026-02-15",
    "created": "2026-01-10T10:00:00Z",
    "updated": "2026-01-25T10:00:00Z"
  },
  {
    "id": 1004,
    "projectId": 12345,
    "issueKey": "TEST-4",
    "summary": "Closed task - was late",
    "description": "Completed after due date",
    "issueType": {"id": 1},
    "priority": {"id": 2},
    "status": {"id": 4},
    "assignee": {"id": 101},
    "dueDate": "2026-01-15",
    "created": "2026-01-05T10:00:00Z",
    "updated": "2026-01-20T10:00:00Z"
  },
  {
    "id": 1005,
    "projectId": 12345,
    "issueKey": "TEST-5",
    "summary": "No due date task",
    "description": "Unscheduled",
    "issueType": {"id": 1},
    "priority": {"id": 4},
    "status": {"id": 1},
    "assignee": {"id": 102},
    "dueDate": null,
    "created": "2026-01-10T10:00:00Z",
    "updated": "2026-01-10T10:00:00Z"
  },
  {
    "id": 1006,
    "projectId": 12345,
    "issueKey": "TEST-6",
    "summary": "Unassigned late task",
    "description": "No owner",
    "issueType": {"id": 1},
    "priority": {"id": 1},
    "status": {"id": 1},
    "assignee": null,
    "dueDate": "2026-01-22",
    "created": "2026-01-10T10:00:00Z",
    "updated": "2026-01-10T10:00:00Z"
  }
]
```

### Step 5: Create test_status_analyzer.py

```python
"""TDD tests for bk-status analyzer."""

import json
import pytest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

# Will fail until implemented
# from scripts.status_analyzer import StatusAnalyzer

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> list:
    """Load JSON fixture file."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


class TestLateTasks:
    """Tests for late task detection."""

    def test_identifies_late_tasks_correctly(self):
        """Late = dueDate < today AND status not closed."""
        # Arrange
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        # Act
        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        # Assert
        assert len(late_tasks) == 3  # TEST-1, TEST-2, TEST-6
        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-1" in late_keys  # Due 2026-01-20, status Open
        assert "TEST-2" in late_keys  # Due 2026-01-25, status In Progress
        assert "TEST-6" in late_keys  # Due 2026-01-22, status Open (unassigned)

    def test_excludes_closed_tasks(self):
        """Closed tasks should not appear as late."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-4" not in late_keys  # Closed, even though past due

    def test_excludes_no_due_date(self):
        """Tasks without due date should not be flagged as late."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        late_keys = [t["issueKey"] for t in late_tasks]
        assert "TEST-5" not in late_keys  # No due date

    def test_calculates_days_overdue(self):
        """Each late task should have days_overdue calculated."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        late_tasks = analyzer.get_late_tasks(issues, today)

        test1 = next(t for t in late_tasks if t["issueKey"] == "TEST-1")
        assert test1["days_overdue"] == 8  # Due 01-20, today 01-28


class TestWorkload:
    """Tests for workload calculation."""

    def test_counts_open_issues_per_assignee(self):
        """Workload = count of non-closed issues per user."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        workload = analyzer.get_workload(issues, users)

        # Tanaka: TEST-1 (Open), TEST-3 (In Progress) = 2
        # Nguyen: TEST-2 (In Progress), TEST-5 (Open) = 2
        # Suzuki: 0
        assert workload[101]["open_count"] == 2  # Tanaka
        assert workload[102]["open_count"] == 2  # Nguyen
        assert workload[103]["open_count"] == 0  # Suzuki

    def test_identifies_overloaded_members(self):
        """Overloaded = open_count > threshold."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        overloaded = analyzer.get_overloaded_members(issues, users, threshold=1)

        # Both Tanaka and Nguyen have 2 issues, threshold=1
        assert len(overloaded) == 2

    def test_handles_unassigned_issues(self):
        """Unassigned issues should be tracked separately."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        workload = analyzer.get_workload(issues, users)

        # TEST-6 is unassigned - should appear in "unassigned" bucket
        assert workload.get("unassigned", {}).get("open_count", 0) == 1


class TestProjectSummary:
    """Tests for project summary generation."""

    def test_counts_by_status(self):
        """Summary should show count per status."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        # Open: TEST-1, TEST-5, TEST-6 = 3
        # In Progress: TEST-2, TEST-3 = 2
        # Closed: TEST-4 = 1
        assert summary["by_status"]["Open"] == 3
        assert summary["by_status"]["In Progress"] == 2
        assert summary["by_status"]["Closed"] == 1

    def test_calculates_progress_percentage(self):
        """Progress = closed / total * 100."""
        issues = load_fixture("sample_issues.json")
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary(issues)

        # 1 closed out of 6 = 16.67%
        assert summary["progress_percent"] == pytest.approx(16.67, rel=0.1)

    def test_handles_empty_project(self):
        """Should not crash on empty issue list."""
        statuses = load_fixture("sample_statuses.json")

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        summary = analyzer.get_summary([])

        assert summary["total"] == 0
        assert summary["progress_percent"] == 0


class TestMarkdownReport:
    """Tests for Markdown report generation."""

    def test_generates_markdown_with_tables(self):
        """Report should contain late tasks table, workload table, summary."""
        issues = load_fixture("sample_issues.json")
        users = load_fixture("sample_users.json")
        statuses = load_fixture("sample_statuses.json")
        today = date(2026, 1, 28)

        analyzer = StatusAnalyzer(statuses, closed_status_names=["Closed"])
        report = analyzer.generate_report(issues, users, today)

        # Check structure
        assert "# Project Status Report" in report
        assert "## Late Tasks" in report
        assert "## Workload" in report
        assert "## Summary" in report
        assert "| Issue |" in report  # Table header
```

---

## Todo List

- [x] Create directory structure
- [x] Create sample_statuses.json fixture
- [x] Create sample_users.json fixture
- [x] Create sample_issues.json fixture (6 issues covering all scenarios)
- [x] Create test_status_analyzer.py with failing tests
- [x] Verify tests fail (TDD red phase)

---

## Success Criteria

- [x] All fixture files valid JSON
- [x] Tests import correctly
- [x] Tests fail with meaningful errors (class not found)
- [x] Test scenarios cover: late tasks, workload, summary, edge cases

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Fixture format mismatch with API | Low | Match actual API response structure |
| Missing edge cases | Medium | Review after initial impl, add more tests |

---

## Next Steps

After tests written: [Phase 3: Status Analyzer](./phase-03-status-analyzer.md)
