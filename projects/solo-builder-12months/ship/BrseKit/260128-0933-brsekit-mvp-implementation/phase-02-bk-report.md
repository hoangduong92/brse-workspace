# Phase 2: bk-report - Weekly Report Generation

## Context Links
- [Parent Plan](./plan.md)
- [Phase 1 bk-status](./phase-01-bk-status.md)

## Overview
- **Priority:** P0
- **Status:** pending
- **Skill:** `bk-report`
- **Approach:** TDD - Test first
- **Description:** Generate weekly report từ Backlog data với template

## Pain Point Addressed
> "Làm report weekly tốn thời gian, làm report PPTX cũng tốn thời gian"

## Requirements

### Input
```
/bk-report [project_id] --period=weekly --format=markdown|xlsx|pptx --lang=ja|vi
```

### Output (Markdown - MVP)
```markdown
# 週次進捗報告
**プロジェクト:** HB Project
**期間:** 2026/01/21 - 2026/01/28
**報告者:** BrSE Name

## 1. 概要
- 完了タスク: 15件
- 進行中: 7件
- 遅延: 3件
- 進捗率: 60%

## 2. 今週の成果
| ID | タスク | 担当 | ステータス |
|----|--------|------|------------|
| HB-101 | ログイン機能実装 | Tam | 完了 |
| HB-102 | API設計 | Hai | 完了 |

## 3. 来週の予定
| ID | タスク | 担当 | 予定日 |
|----|--------|------|--------|
| HB-105 | テスト実施 | An | 01/30 |

## 4. 課題・リスク
- HB-123: 3日遅延中 → 対応: Tamをサポート予定

## 5. 所感
(User填入)
```

---

## TDD: Test Cases First

### TC1: Fetch weekly data
```python
def test_fetch_weekly_data():
    """Fetch tasks completed/updated in the week"""
    project_id = "HB21373"
    week_start = "2026-01-21"
    week_end = "2026-01-28"

    data = report_generator.fetch_weekly_data(project_id, week_start, week_end)

    assert "completed_tasks" in data
    assert "in_progress_tasks" in data
    assert "next_week_tasks" in data
```

### TC2: Calculate statistics
```python
def test_calculate_statistics():
    """Calculate completion rate, counts"""
    tasks = [
        Task(status="completed"),
        Task(status="completed"),
        Task(status="in_progress"),
        Task(status="open"),
    ]

    stats = report_generator.calculate_stats(tasks)

    assert stats["total"] == 4
    assert stats["completed"] == 2
    assert stats["completion_rate"] == 50  # 2/4 = 50%
```

### TC3: Format tasks table
```python
def test_format_tasks_table():
    """Format tasks as markdown table"""
    tasks = [
        Task(id="HB-101", summary="Login feature", assignee="Tam", status="completed"),
    ]

    table = report_generator.format_table(tasks, lang="ja")

    assert "| HB-101 |" in table
    assert "完了" in table  # Japanese status
```

### TC4: Generate report with template
```python
def test_generate_report_ja():
    """Generate Japanese weekly report"""
    data = {
        "project_name": "HB Project",
        "period": "2026/01/21 - 2026/01/28",
        "stats": {"completed": 15, "in_progress": 7},
        "completed_tasks": [...],
        "next_week_tasks": [...],
    }

    report = report_generator.generate(data, lang="ja", format="markdown")

    assert "週次進捗報告" in report
    assert "今週の成果" in report
    assert "来週の予定" in report
```

### TC5: Generate Vietnamese report
```python
def test_generate_report_vi():
    """Generate Vietnamese weekly report"""
    data = {...}

    report = report_generator.generate(data, lang="vi", format="markdown")

    assert "Báo cáo tiến độ tuần" in report
    assert "Kết quả tuần này" in report
```

---

## Architecture

```
brsekit/skills/bk-report/
├── SKILL.md                    # Skill entry point
├── scripts/
│   ├── report_generator.py     # Main logic
│   └── __init__.py
├── templates/
│   ├── weekly-report-ja.md     # Japanese template
│   ├── weekly-report-vi.md     # Vietnamese template
│   └── weekly-report.xlsx      # Excel template (Phase 2+)
├── references/
│   └── report-format-guide.md
└── tests/
    ├── test_report_generator.py
    └── fixtures/
        └── sample_weekly_data.json
```

---

## Implementation Steps

### Step 1: Create test fixtures (30 min)
1. `tests/fixtures/sample_weekly_data.json`
2. Sample completed tasks, in-progress, next week

### Step 2: Create templates (30 min)
1. `templates/weekly-report-ja.md` - Japanese template
2. `templates/weekly-report-vi.md` - Vietnamese template

### Step 3: Write tests (1 hour)
1. Create `tests/test_report_generator.py`
2. Write all 5 test cases
3. Run tests → all FAIL

### Step 4: Implement report_generator.py (2 hours)
1. `fetch_weekly_data(project_id, start, end)` - call Backlog API
2. `calculate_stats(tasks)` - compute metrics
3. `format_table(tasks, lang)` - markdown table
4. `generate(data, lang, format)` - apply template

### Step 5: Run tests → PASS (30 min)

### Step 6: Create SKILL.md (30 min)

### Step 7: Integration test (1 hour)
1. Test với real Backlog project
2. Verify report accuracy
3. Test both JA and VI

---

## Todo List

- [ ] Create `tests/fixtures/sample_weekly_data.json`
- [ ] Create `templates/weekly-report-ja.md`
- [ ] Create `templates/weekly-report-vi.md`
- [ ] Write `test_fetch_weekly_data`
- [ ] Write `test_calculate_statistics`
- [ ] Write `test_format_tasks_table`
- [ ] Write `test_generate_report_ja`
- [ ] Write `test_generate_report_vi`
- [ ] Run tests → all FAIL
- [ ] Implement `report_generator.py`
- [ ] Run tests → all PASS
- [ ] Create `SKILL.md`
- [ ] Integration test

---

## Success Criteria

1. All unit tests pass
2. `/bk-report HB21373 --lang=ja` generates Japanese report
3. `/bk-report HB21373 --lang=vi` generates Vietnamese report
4. Report includes all required sections
5. Data matches real Backlog

---

## Template Variables

| Variable | Description |
|----------|-------------|
| `{{project_name}}` | Project name |
| `{{period}}` | Report period |
| `{{reporter}}` | Reporter name |
| `{{stats.completed}}` | Completed count |
| `{{stats.in_progress}}` | In progress count |
| `{{stats.completion_rate}}` | Completion % |
| `{{completed_tasks_table}}` | Markdown table |
| `{{next_week_table}}` | Markdown table |
| `{{issues_list}}` | Issues/risks |

---

## Future: Excel/PPTX Support

MVP = Markdown only. Add Excel/PPTX later:
- Use `openpyxl` for Excel
- Use `python-pptx` for PowerPoint
- Template-based generation

---

## Next Steps
After Phase 2: → Phase 3 `bk-task`
