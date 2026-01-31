# Phase 1: Extended Gantt Chart

**Priority:** High
**Status:** Complete

## Overview

Mở rộng Gantt chart để hiển thị cả **actual hours** (quá khứ) và **proposed schedule** (tương lai).

## Current State

Hiện tại `gantt_generator.py` chỉ hiển thị từ `today → sprint_end`:

```
| Task      | 30F | 02M | 03T | 04W | 05T | 06F |
|-----------|-----|-----|-----|-----|-----|-----|
| BKT-1     | 4   | 4   | 4✅ |     |     |     |
```

## Target State

```
| Task      | 20M | 21T | ... | 29W | 30T | 31F | 02M | ... |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|
| BKT-1     | 2✓  | 4✓  | ... | 3✓  | 📍  | 4   | 4   | ... |
|           | ← ACTUAL (logged) →  | now | ← PROPOSED → |

Legend:
✓ = actual hours logged
📍 = today marker
plain = proposed hours
```

## Implementation Steps

### 1. Update `gantt_generator.py`

**File:** `.claude/skills/bk-track/scripts/gantt_generator.py`

```python
def generate_gantt_schedule_with_analysis(
    member_capacity: list[dict],
    today: date,
    hours_per_day: float = 6.0,
    sprint_end: Optional[date] = None,
    get_working_days_list_fn = None,
    lang: str = "en",
    # NEW PARAMETERS
    sprint_start: Optional[date] = None,
    time_log_data: Optional[Dict[str, Dict[date, float]]] = None  # {member: {date: hours}}
) -> tuple[str, Optional[dict]]:
```

**Changes needed:**

1. Accept `sprint_start` and `time_log_data` parameters
2. Generate date columns from `sprint_start` (or earliest task start) to `sprint_end`
3. For dates < today: show actual hours from `time_log_data` with `✓` marker
4. For dates >= today: show proposed hours (existing logic)
5. Add `📍` marker on today column

### 2. Update `report_generator.py`

**File:** `.claude/skills/bk-track/scripts/report_generator.py`

Pass `time_log_data` to gantt generator:

```python
def generate_report(
    ...
    time_log_data: Optional[Dict[str, Dict[date, float]]] = None,  # NEW
    sprint_start: Optional[date] = None,  # NEW
) -> str:
    ...
    gantt_section, gantt_analysis = generate_gantt_schedule_with_analysis(
        member_capacity, today, hours_per_day, sprint_end,
        get_working_days_list_fn, lang,
        sprint_start=sprint_start,  # NEW
        time_log_data=time_log_data  # NEW
    )
```

### 3. Update `status_analyzer.py`

Pass through `time_log_data` from analyzer to report generator.

### 4. Update `main.py`

Pass `time_log_data` và `sprint_start` to `generate_report()`:

```python
# In cmd_status()
report = analyzer.generate_report(
    ...
    time_log_data=time_log_data,  # Already loaded from vault
    sprint_start=sprint_info.get("start_date") if sprint_info else None
)
```

### 5. Update `translations.py`

Add new translation keys:

```python
# English
"gantt_actual_note": "**Legend:** ✓ = actual logged | 📍 = today | plain = proposed",
"gantt_extended_title": "## Daily Schedule (Actual + Proposed)",

# Vietnamese
"gantt_actual_note": "**Chú thích:** ✓ = đã log | 📍 = hôm nay | số = đề xuất",
"gantt_extended_title": "## Lịch làm việc hàng ngày (Thực tế + Đề xuất)",
```

## Gantt Generation Logic

```python
def _generate_extended_gantt_row(
    task: dict,
    working_days: List[date],
    today: date,
    actual_by_date: Dict[date, float],  # from time_log_data
    proposed_by_date: Dict[date, float]  # from existing scheduling
) -> str:
    """Generate single task row with actual + proposed."""
    cells = []
    for day in working_days:
        if day < today:
            # Past: show actual logged
            hours = actual_by_date.get(day, 0)
            cell = f"{hours:.0f}✓" if hours > 0 else ""
        elif day == today:
            # Today: show with marker
            hours = proposed_by_date.get(day, 0) or actual_by_date.get(day, 0)
            cell = f"{hours:.0f}📍" if hours > 0 else "📍"
        else:
            # Future: show proposed
            hours = proposed_by_date.get(day, 0)
            cell = f"{hours:.0f}" if hours > 0 else ""
        cells.append(cell)
    return " | ".join(cells)
```

## Success Criteria

- [x] Gantt hiển thị từ sprint_start đến sprint_end
- [x] Past dates hiển thị actual hours với ✓
- [x] Today có 📍 marker
- [x] Future dates hiển thị proposed hours
- [x] Chú thích legend rõ ràng
- [x] Hoạt động đúng với cả 3 ngôn ngữ (en, vi, ja)

## Test Cases

1. Sprint đã chạy được 5 ngày, có time logs → hiển thị 5 ngày actual + future
2. Sprint mới bắt đầu hôm nay → chỉ có today + future
3. Không có time_log_data → chỉ hiển thị proposed (backward compatible)
