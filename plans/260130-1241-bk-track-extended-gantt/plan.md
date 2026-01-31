# bk-track Extended Gantt & Log Reminder

**Date:** 2026-01-30
**Status:** Ready for implementation

## Overview

Mở rộng báo cáo bk-track status với:
1. **Extended Gantt**: Hiển thị actual time (quá khứ) + proposed schedule (tương lai)
2. **Log Reminder**: Nhắc nhở member chưa log time

## Phases

- [Phase 1: Extended Gantt Chart](phase-01-extended-gantt.md) - Priority: High
- [Phase 2: Log Reminder Section](phase-02-log-reminder.md) - Priority: Medium

## Prerequisites

Đã hoàn thành:
- [x] Vault schema với `time_logs` table
- [x] `TimeLogStore` class với `get_daily_summary()`, `get_members_not_logged()`
- [x] bk-recall sync actualHours changelog từ Backlog activities
- [x] bk-track đọc time_logs từ vault

## Key Files

| File | Purpose |
|------|---------|
| `.claude/skills/bk-track/scripts/gantt_generator.py` | Gantt chart generation |
| `.claude/skills/bk-track/scripts/report_generator.py` | Report assembly |
| `.claude/skills/bk-track/scripts/translations.py` | i18n strings |
| `.claude/skills/bk-track/scripts/main.py` | CLI entry point |
| `.claude/skills/lib/vault/time_log_store.py` | Time log queries |

## Data Flow

```
┌──────────────────┐
│  time_logs       │ (vault.db)
│  - member_name   │
│  - logged_at     │
│  - hours_delta   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ get_daily_summary│────►│ Extended Gantt   │
│ (sprint_start →  │     │ ACTUAL | PROPOSED│
│  today)          │     └──────────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ get_members_not_ │────►│ Log Reminder     │
│ logged(today)    │     │ Section          │
└──────────────────┘     └──────────────────┘
```
