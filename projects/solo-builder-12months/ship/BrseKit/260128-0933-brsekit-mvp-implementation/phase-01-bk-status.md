# Phase 1: bk-status - Check Tiến Độ

## Context Links
- [Parent Plan](./plan.md)
- [Existing backlog skill](../.claude/skills/backlog/)

## Overview
- **Priority:** P0
- **Status:** pending
- **Skill:** `bk-status`
- **Approach:** TDD - Test first
- **Description:** Check tiến độ project, late tasks, member workload

## Pain Point Addressed
> "Làm task không kịp, không biết ai đang overload, task nào late"

## Requirements

### Input
```
/bk-status [project_id] [--days=7]
```

### Output
```markdown
## Project Status: {project_name}
**Period:** {start_date} - {end_date}

### Summary
- Total tasks: 25
- Completed: 15 (60%)
- In Progress: 7
- Late: 3 ⚠️

### Late Tasks
| ID | Task | Assignee | Due | Days Late |
|----|------|----------|-----|-----------|
| HB-123 | Fix login bug | Tam | 01/25 | 3 days |
| HB-124 | API endpoint | Hai | 01/24 | 4 days |

### Workload by Member
| Member | Assigned | Completed | In Progress | Overloaded? |
|--------|----------|-----------|-------------|-------------|
| Tam | 8 | 5 | 3 | ⚠️ Yes |
| Hai | 6 | 4 | 2 | No |
| An | 5 | 5 | 0 | No |

### Recommendation
- Tam cần support, đang overload 3 tasks
- 2 tasks critical late > 3 ngày
```

---

## TDD: Test Cases First

### TC1: Fetch project tasks
```python
def test_fetch_project_tasks():
    """Fetch all tasks from project within date range"""
    # Input
    project_id = "HB21373"
    days = 7

    # Expected
    # - Returns list of tasks
    # - Each task has: id, summary, assignee, due_date, status, actual_hours
    # - Only tasks updated within last 7 days

    tasks = status_checker.fetch_tasks(project_id, days=7)
    assert len(tasks) > 0
    assert all(hasattr(t, 'id') for t in tasks)
```

### TC2: Identify late tasks
```python
def test_identify_late_tasks():
    """Identify tasks past due date"""
    # Input: list of tasks with due dates
    tasks = [
        Task(id="HB-1", due_date="2026-01-25", status="in_progress"),
        Task(id="HB-2", due_date="2026-01-30", status="in_progress"),
        Task(id="HB-3", due_date="2026-01-20", status="completed"),
    ]
    today = "2026-01-28"

    # Expected: only HB-1 is late (in_progress + past due)
    late_tasks = status_checker.get_late_tasks(tasks, today)
    assert len(late_tasks) == 1
    assert late_tasks[0].id == "HB-1"
```

### TC3: Calculate member workload
```python
def test_calculate_workload():
    """Calculate workload per member"""
    # Input: list of tasks with assignees
    tasks = [
        Task(id="HB-1", assignee="Tam", estimated_hours=8, status="in_progress"),
        Task(id="HB-2", assignee="Tam", estimated_hours=4, status="in_progress"),
        Task(id="HB-3", assignee="Hai", estimated_hours=6, status="completed"),
    ]

    # Expected: Tam has 12h in_progress, Hai has 0h in_progress
    workload = status_checker.calculate_workload(tasks)
    assert workload["Tam"]["in_progress_hours"] == 12
    assert workload["Hai"]["in_progress_hours"] == 0
```

### TC4: Detect overloaded members
```python
def test_detect_overloaded():
    """Flag members with too many in-progress tasks"""
    # Threshold: > 6h/day (Sprint standard)
    workload = {
        "Tam": {"in_progress_hours": 40, "days_remaining": 5},  # 8h/day
        "Hai": {"in_progress_hours": 20, "days_remaining": 5},  # 4h/day
    }

    # Expected: Tam is overloaded (8h/day > 6h threshold)
    overloaded = status_checker.detect_overloaded(workload, threshold=6)
    assert "Tam" in overloaded
    assert "Hai" not in overloaded
```

### TC5: Generate status report
```python
def test_generate_report():
    """Generate markdown report from data"""
    # Input: processed data
    data = {
        "project_name": "HB Project",
        "total_tasks": 25,
        "completed": 15,
        "late_tasks": [...],
        "workload": {...}
    }

    # Expected: Markdown string with all sections
    report = status_checker.generate_report(data)
    assert "## Project Status" in report
    assert "Late Tasks" in report
    assert "Workload by Member" in report
```

---

## Architecture

```
brsekit/skills/bk-status/
├── SKILL.md                    # Skill entry point
├── scripts/
│   ├── status_checker.py       # Main logic
│   └── __init__.py
├── references/
│   └── workload-calculation.md # How workload is calculated
└── tests/
    ├── test_status_checker.py  # Unit tests
    └── fixtures/
        └── sample_tasks.json   # Test data
```

---

## Implementation Steps

### Step 1: Create test fixtures (30 min)
1. `tests/fixtures/sample_tasks.json`:
   - 10-15 tasks với mixed status
   - 3 late tasks
   - 3 members với different workload

### Step 2: Write tests (1 hour)
1. Create `tests/test_status_checker.py`
2. Write all 5 test cases
3. Run tests → all FAIL

### Step 3: Implement status_checker.py (2 hours)
1. `fetch_tasks(project_id, days)` - call Backlog API
2. `get_late_tasks(tasks, today)` - filter late
3. `calculate_workload(tasks)` - sum by member
4. `detect_overloaded(workload, threshold)` - flag
5. `generate_report(data)` - markdown output

### Step 4: Run tests → PASS (30 min)
1. Fix until all tests pass

### Step 5: Create SKILL.md (30 min)
1. Command syntax
2. Examples
3. Output format

### Step 6: Integration test (1 hour)
1. Test với real Backlog project
2. Verify accuracy
3. Fix edge cases

---

## Todo List

- [ ] Create `tests/fixtures/sample_tasks.json`
- [ ] Write `test_fetch_project_tasks`
- [ ] Write `test_identify_late_tasks`
- [ ] Write `test_calculate_workload`
- [ ] Write `test_detect_overloaded`
- [ ] Write `test_generate_report`
- [ ] Run tests → all FAIL
- [ ] Implement `status_checker.py`
- [ ] Run tests → all PASS
- [ ] Create `SKILL.md`
- [ ] Integration test với real Backlog

---

## Success Criteria

1. All 5 unit tests pass
2. `/bk-status HB21373` returns formatted report
3. Late tasks identified correctly
4. Overloaded members flagged
5. Works với real Backlog data

---

## Workload Calculation Logic

```
Standard: 6h productive/day/person (Sprint standard)
Sprint: 2 weeks = 10 working days = 60h/person

Overloaded if:
  in_progress_hours / days_remaining > 6h/day
```

---

## Next Steps
After Phase 1: → Phase 2 `bk-report`
