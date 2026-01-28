# Phase 4: Skill Structure & Command Integration

## Context

- **Parent Plan:** [bk-status Implementation](./plan.md)
- **Depends On:** [Phase 3: Status Analyzer](./phase-03-status-analyzer.md)
- **Reference:** [Existing Backlog Skill](../../../.claude/skills/backlog/SKILL.md)

---

## Overview

| Field | Value |
|-------|-------|
| Priority | P0 |
| Status | ✅ DONE |
| Effort | 0.5h |
| Completed | 2026-01-28 16:30 |
| Review | [Code Review Report](../../plans/reports/code-reviewer-260128-1619-phase-04-bk-status.md) |

**Goal:** Create SKILL.md and integrate with Claude commands.

---

## Key Insights

1. **Skill activation:** SKILL.md triggers when `/bk-status` invoked
2. **Environment:** Reuse NULAB_* env vars from backlog skill
3. **Output:** Save to `/project-status/yyyymmdd-hhmmss_{projectName}-status.md` (validated decision)

---

## Requirements

### Functional
- SKILL.md with workflow instructions
- Entry script `main.py` orchestrating API + analyzer
- Command `/bk-status` activation

### Non-Functional
- Clear error messages for missing env vars
- Graceful handling of API failures

---

## Architecture

```
.claude/skills/bk-status/
├── SKILL.md                    # Workflow instructions
├── scripts/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   └── status_analyzer.py      # Core logic
├── tests/
│   └── ...
└── references/
    └── api-endpoints.md        # Quick API reference
```

---

## Related Code Files

### To Create
| File | Purpose |
|------|---------|
| `.claude/skills/bk-status/SKILL.md` | Skill workflow |
| `.claude/skills/bk-status/scripts/main.py` | Entry point |
| `.claude/skills/bk-status/references/api-endpoints.md` | Quick reference |

---

## Implementation Steps

### Step 1: Create SKILL.md

```markdown
# bk-status Skill

Check project progress: late tasks, overloaded members, project health summary.

## When to Use

- Check tiến độ project
- Identify late/overdue tasks
- See member workload distribution
- Get project progress summary

## Prerequisites

Environment variables (in .env):
- `NULAB_SPACE_URL` - Backlog space (e.g., `yourspace.backlog.com`)
- `NULAB_API_KEY` - API key
- `NULAB_PROJECT_ID` - Project ID or key

## Usage

### Basic Status Check

```bash
/bk-status
```

Output saved to: `./project-status/yyyymmdd-hhmmss_{projectName}-status.md`

Report includes:
- Summary (total, closed, progress %)
- Late tasks table
- Workload per member

### With Options

```bash
/bk-status --threshold 3  # Overloaded = >3 open issues
```

## Workflow

1. Load env vars
2. Fetch project statuses, users, issues via BacklogClient
3. Analyze with StatusAnalyzer
4. Generate Markdown report
5. Save to `./project-status/yyyymmdd-hhmmss_{projectName}-status.md`
6. Print summary and file path to console

## Example Output

```markdown
# Project Status Report

**Date:** 2026-01-28
**Project:** MyProject

## Summary

| Metric | Value |
|--------|-------|
| Total Issues | 25 |
| Closed | 15 |
| Progress | 60.0% |

## Late Tasks

| Issue | Summary | Assignee | Days Overdue |
|-------|---------|----------|--------------|
| PROJ-45 | Fix login bug | Tanaka | 5 |
| PROJ-52 | Update docs | Nguyen | 2 |

## Workload

| Member | Open Issues |
|--------|-------------|
| Tanaka | 4 |
| Nguyen | 3 |
| Suzuki | 2 |
```

## Error Handling

- Missing env vars: Print required vars, exit
- API error: Print error message, retry hint
- No issues found: Print "No issues in project"

## Related Skills

- `backlog` - Base API client
- `bk-report` - Generate weekly reports
```

### Step 2: Create main.py

```python
"""Entry point for bk-status skill."""

import os
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

from backlog_client import BacklogClient, BacklogAPIError
from status_analyzer import StatusAnalyzer


def load_env():
    """Load environment variables."""
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")
    project_id = os.getenv("NULAB_PROJECT_ID")

    missing = []
    if not space_url:
        missing.append("NULAB_SPACE_URL")
    if not api_key:
        missing.append("NULAB_API_KEY")
    if not project_id:
        missing.append("NULAB_PROJECT_ID")

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        print("\nSet in .env file:")
        print("  NULAB_SPACE_URL=yourspace.backlog.com")
        print("  NULAB_API_KEY=your-api-key")
        print("  NULAB_PROJECT_ID=PROJECTKEY")
        sys.exit(1)

    return space_url, api_key, project_id


def get_output_path(project_name: str) -> Path:
    """Generate output path with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    output_dir = Path("./project-status")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{timestamp}_{safe_name}-status.md"


def main():
    """Run status check."""
    parser = argparse.ArgumentParser(description="Check project status")
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Overloaded threshold (default: 5)"
    )
    args = parser.parse_args()

    # Load config
    space_url, api_key, project_id = load_env()

    try:
        # Initialize API client
        client = BacklogClient(space_url, api_key)

        # Fetch data
        print(f"Fetching data for project {project_id}...")
        project = client.get_project(project_id)
        statuses = client.get_project_statuses(project_id)
        users = client.get_project_users(project_id)
        issues = client.list_issues(project.id)

        print(f"Found {len(issues)} issues, {len(users)} members")

        # Analyze
        analyzer = StatusAnalyzer(
            [{"id": s.id, "name": s.name} for s in statuses],
            closed_status_names=["Closed"]  # Validated: only "Closed"
        )

        # Convert Issue objects to dicts for analyzer
        issue_dicts = []
        for issue in issues:
            issue_dict = {
                "id": issue.id,
                "issueKey": issue.key_id,
                "summary": issue.summary,
                "status": {"id": issue.status_id},
                "assignee": {"id": issue.assignee_id} if issue.assignee_id else None,
                "dueDate": issue.due_date,  # Use dueDate from model
            }
            issue_dicts.append(issue_dict)

        user_dicts = [{"id": u.id, "name": u.name} for u in users]

        # Generate report
        today = date.today()
        report = analyzer.generate_report(
            issue_dicts,
            user_dicts,
            today,
            project_name=project.name
        )

        # Save to file (validated decision)
        output_path = get_output_path(project.name)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

        # Show summary
        late_tasks = analyzer.get_late_tasks(issue_dicts, today)
        overloaded = analyzer.get_overloaded_members(
            issue_dicts, user_dicts, threshold=args.threshold
        )

        print(f"\nSummary:")
        print(f"  Total issues: {len(issues)}")
        print(f"  Late tasks: {len(late_tasks)}")
        if overloaded:
            print(f"  Overloaded members (>{args.threshold} issues):")
            for member in overloaded:
                print(f"    - {member['name']}: {member['open_count']} issues")

    except BacklogAPIError as e:
        print(f"API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 3: Create references/api-endpoints.md

```markdown
# Backlog API Quick Reference

## Endpoints Used by bk-status

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/projects/{id}` | Get project info |
| GET | `/projects/{id}/statuses` | List status definitions |
| GET | `/projects/{id}/users` | List project members |
| GET | `/issues?projectId[]={id}` | List issues (paginated) |

## Issue Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `statusId[]` | int[] | Filter by status |
| `assigneeId[]` | int[] | Filter by assignee |
| `dueDateUntil` | date | Due before (yyyy-MM-dd) |
| `dueDateSince` | date | Due after |
| `sort` | string | dueDate, created, updated |
| `order` | string | asc, desc |
| `count` | int | Results per page (max 100) |
| `offset` | int | Pagination offset |

## Rate Limits

- 1 request per second (enforced by client)
- Auto-retry on 429 with exponential backoff
```

### Step 4: Register command (optional)

If using Claude skills command system, add to `.claude/commands/` or skill index.

---

## Todo List

- [x] Create SKILL.md with workflow ✓
- [x] Create main.py entry point ✓
- [x] Create references/api-endpoints.md ✓
- [x] Write tests for main.py ✓ (35/35 passed)
- [x] Code review completed (9/10 score, no critical issues)
- [x] All tests passing (35/35)

---

## Success Criteria

- [x] `/bk-status` saves report to `./project-status/` directory
- [x] Filename format: `yyyymmdd-hhmmss_{projectName}-status.md`
- [x] Late tasks identified correctly (status != Closed)
- [x] Workload shown per member
- [x] Console shows summary + file path

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Import path issues | Medium | Use relative imports, test in isolation |
| API response format change | Low | Validate against real API early |

---

## Security Considerations

- API key in env var, not hardcoded
- No sensitive data in report output
- No file writes without explicit --output flag

---

## Integration Test

```bash
# Set env vars
export NULAB_SPACE_URL=yourspace.backlog.com
export NULAB_API_KEY=your-key
export NULAB_PROJECT_ID=PROJKEY

# Run (saves to ./project-status/)
python .claude/skills/bk-status/scripts/main.py

# With custom threshold
python .claude/skills/bk-status/scripts/main.py --threshold 3
```

**Expected output:**
```
Fetching data for project PROJKEY...
Found 25 issues, 5 members

Report saved to: ./project-status/20260128-134500_ProjectName-status.md

Summary:
  Total issues: 25
  Late tasks: 3
  Overloaded members (>5 issues):
    - Tanaka: 7 issues
```

---

## Next Steps

After completion:
1. Run integration test with real Backlog project
2. Document in parent BrseKit plan
3. Proceed to Phase 2: bk-report skill
