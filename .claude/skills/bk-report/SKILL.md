---
name: bk-report
description: "[DEPRECATED] Use /bk-track report instead. Weekly report generation."
deprecated: true
redirect: bk-track report
---

> ⚠️ **DEPRECATED**: This skill is deprecated. Use `/bk-track report` instead.

## Migration Guide

| Old Command | New Command |
|------------|-------------|
| `/bk-report` | `/bk-track report` |
| `/bk-report --lang=ja` | `/bk-track report --lang=ja` |
| `/bk-report --lang=vi` | `/bk-track report --lang=vi` |
| `/bk-report --period=2026-01-20:2026-01-26` | `/bk-track report --period=2026-01-20:2026-01-26` |

## Why Deprecated?

bk-report has been merged into bk-track for a unified project tracking experience. All functionality is preserved in the new skill.

---

# bk-report - Weekly Report Generator

Generate weekly progress reports from Backlog project data.

## Usage

```
/bk-report [--lang=ja|vi|en] [--period=YYYY-MM-DD:YYYY-MM-DD]
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--lang` | ja | Report language (ja/vi/en) |
| `--period` | Last 7 days | Date range (start:end) |
| `--include-closed` | true | Include closed tasks in summary |

## Output

Markdown report saved to `./weekly-reports/YYYYMMDD-HHMMSS_project-weekly.md`

## Report Sections

1. **概要/Overview** - Summary statistics
2. **今週の成果/Accomplishments** - Completed tasks
3. **進行中/In Progress** - Current work
4. **来週の予定/Next Week** - Upcoming tasks
5. **課題・リスク/Issues & Risks** - Late/at-risk items

## Environment Variables

```bash
NULAB_SPACE_URL=yourspace.backlog.com
NULAB_API_KEY=your-api-key
NULAB_PROJECT_ID=PROJECT_KEY
```

## Example

```bash
# Japanese weekly report (default)
.claude/skills/.venv/Scripts/python.exe .claude/skills/bk-report/scripts/main.py

# Vietnamese report
.claude/skills/.venv/Scripts/python.exe .claude/skills/bk-report/scripts/main.py --lang=vi

# Custom period
.claude/skills/.venv/Scripts/python.exe .claude/skills/bk-report/scripts/main.py --period=2026-01-20:2026-01-26
```

## Dependencies

- `common/backlog/client.py` - Backlog API client
- `common/backlog/models.py` - Data models
- `common/backlog/calendar_utils.py` - Working day calculation

## Related Skills

- `bk-status` - Detailed status check with member capacity analysis
