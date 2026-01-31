# Phase 2: Log Reminder Section

**Priority:** Medium
**Status:** Pending
**Depends on:** Phase 1 (can be done in parallel)

## Overview

Thêm section nhắc nhở member chưa log time gần đây.

## Target Output

```markdown
## ⏰ Chưa log time

| Member | Last logged | Days missing | Action |
|--------|-------------|--------------|--------|
| bibonihongo | 01/28 | 2 days | Nhắc log time hôm nay |
| Nguyen Hoang Duong | 01/30 | 0 days | ✅ OK |
```

## Implementation Steps

### 1. Add helper function in `report_generator.py`

```python
def _generate_log_reminder_section(
    tr: Translator,
    project_key: str,
    all_members: List[str],
    today: date,
    time_log_store: "TimeLogStore",
    reminder_threshold: int = 1  # days
) -> list[str]:
    """Generate log reminder section for members who haven't logged time."""
    lines = []

    # Get last log date per member
    last_logs = time_log_store.get_last_log_date_per_member(project_key, all_members)

    # Find members who need reminder
    needs_reminder = []
    for member, last_date in last_logs.items():
        if last_date is None:
            days_missing = "never"
            needs_reminder.append((member, None, days_missing))
        else:
            days_diff = (today - last_date).days
            if days_diff >= reminder_threshold:
                needs_reminder.append((member, last_date, days_diff))

    if not needs_reminder:
        return []  # Everyone logged today, no section needed

    lines.extend([
        f"## {tr.t('log_reminder_title')}",
        "",
        tr.t("log_reminder_note"),
        "",
        f"| {tr.t('member')} | {tr.t('last_logged')} | {tr.t('days_missing')} | {tr.t('action')} |",
        "|--------|-------------|--------------|--------|",
    ])

    for member, last_date, days in needs_reminder:
        last_str = last_date.strftime("%m/%d") if last_date else "-"
        days_str = f"{days} days" if isinstance(days, int) else days
        action = tr.t("action_remind_log")
        lines.append(f"| {member} | {last_str} | {days_str} | {action} |")

    lines.append("")
    return lines
```

### 2. Update `translations.py`

```python
# English
"log_reminder_title": "⏰ Time Log Reminder",
"log_reminder_note": "Members who haven't logged time recently:",
"last_logged": "Last logged",
"days_missing": "Days missing",
"action_remind_log": "Please log time today",

# Vietnamese
"log_reminder_title": "⏰ Nhắc nhở log time",
"log_reminder_note": "Các member chưa log time gần đây:",
"last_logged": "Lần cuối log",
"days_missing": "Số ngày thiếu",
"action_remind_log": "Nhắc log time hôm nay",

# Japanese
"log_reminder_title": "⏰ 工数入力リマインダー",
"log_reminder_note": "最近工数を入力していないメンバー：",
"last_logged": "最終入力",
"days_missing": "未入力日数",
"action_remind_log": "本日の工数入力をお願いします",
```

### 3. Integrate into `generate_report()`

```python
def generate_report(...) -> str:
    ...
    # After BrSE Insights section, before Gantt
    if time_log_store:
        all_member_names = [u["name"] for u in users]
        lines.extend(_generate_log_reminder_section(
            tr, project_key, all_member_names, today, time_log_store
        ))
    ...
```

### 4. Update `main.py` to pass TimeLogStore

```python
# In cmd_status()
report = analyzer.generate_report(
    ...
    time_log_store=time_log_store if TimeLogStore else None,
    project_key=project_id
)
```

### 5. Add CLI option for threshold

```python
# In argparse
status_parser.add_argument("--reminder-threshold", type=int, default=1,
                            help="Days without log to trigger reminder (default: 1)")
```

## TimeLogStore Methods (Already Implemented)

```python
# .claude/skills/lib/vault/time_log_store.py

def get_members_not_logged(
    self,
    project_key: str,
    check_date: date,
    all_members: List[str]
) -> List[str]:
    """Get members who haven't logged time on a specific date."""

def get_last_log_date_per_member(
    self,
    project_key: str,
    members: List[str]
) -> Dict[str, Optional[date]]:
    """Get last log date for each member."""
```

## Success Criteria

- [ ] Section chỉ hiển thị khi có member cần nhắc nhở
- [ ] Hiển thị đúng last logged date
- [ ] Tính đúng số ngày chưa log
- [ ] Threshold có thể config qua CLI
- [ ] Hoạt động với cả 3 ngôn ngữ

## Test Cases

1. Tất cả member đã log hôm nay → không hiển thị section
2. 1 member chưa log 2 ngày → hiển thị với threshold=1
3. Member chưa bao giờ log → hiển thị "never"
4. threshold=3, member chưa log 2 ngày → không hiển thị

## Notes

- Section này nên đặt sau "Action Items" nhưng trước "Summary"
- Chỉ nhắc những member có task đang open (không nhắc member không có việc)
