---
name: bk-status
description: "[DEPRECATED] Use /bk-track status instead. Check project progress."
deprecated: true
redirect: bk-track status
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
---

> ⚠️ **DEPRECATED**: This skill is deprecated. Use `/bk-track status` instead.

## Migration Guide

| Old Command | New Command |
|------------|-------------|
| `/bk-status` | `/bk-track status` |
| `/bk-status --threshold 5` | `/bk-track status --threshold 5` |
| `/bk-status --capacity 6` | `/bk-track status --capacity 6` |
| `/bk-status --lang vi` | `/bk-track status --lang vi` |

## Why Deprecated?

bk-status has been merged into bk-track for a unified project tracking experience. All functionality is preserved in the new skill.

---

# bk-status - Project Status Check

Check Nulab Backlog project progress: late tasks, overloaded members, project health.

## Setup

```bash
# Copy .env.example and fill in credentials
cp .claude/skills/bk-status/.env.example .claude/skills/bk-status/.env

# Install dependencies (use forward slashes for Git Bash/MINGW64)
cd ".claude/skills" && ".venv/Scripts/pip.exe" install -r bk-status/requirements.txt
```

## Usage

```
/bk-status [--threshold N] [--capacity H] [--lang LANG]
```

**Examples:**
```
/bk-status                    # Default: threshold=5, capacity=4h/day, lang from master.yaml
/bk-status --threshold 3      # Custom overloaded threshold
/bk-status --capacity 6       # Custom hours per day capacity
/bk-status --lang vi          # Vietnamese report output
/bk-status --lang ja          # Japanese report output
```

**Language Options:**
- `en` - English (default)
- `vi` - Vietnamese (Tiếng Việt)
- `ja` - Japanese (日本語)

Default language can be set in `brsekit/master.yaml` under `lang` field.

## Workflow Instructions (for Claude Code)

### Step 1: Load Environment
Read `.claude/skills/bk-status/.env` for `NULAB_SPACE_URL`, `NULAB_API_KEY`, `NULAB_PROJECT_ID`.

### Step 2: Fetch Data
```bash
# IMPORTANT: Use forward slashes for cross-platform compatibility (Git Bash/MINGW64)
cd ".claude/skills/bk-status" && "../.venv/Scripts/python.exe" scripts/main.py [--threshold N]
```

### Step 3: Report Output
Report saved to: `./project-status/YYYYMMDD-HHMMSS_{projectName}-status.md`

## Report Contents

| Section | Description |
|---------|-------------|
| Summary | Total issues, closed count, count-based progress % |
| Hours Progress | Estimated vs actual hours, hours-based progress % |
| At-Risk Tasks | Tasks requiring more than capacity to meet deadline |
| Late Tasks | Issues past due date (status != Closed) |
| Workload | Open issues per member |

## Risk Detection Logic

- **Late** = `dueDate < today` AND status is NOT "Closed"
- **At-Risk** = `required_velocity > capacity` (needs more hours/day than available)
- **On-Track** = `required_velocity <= capacity`
- **Overloaded** = member has > threshold open issues (default: 5)

**Velocity Calculation:**
```
hours_remaining = estimated_hours - actual_hours
days_remaining = due_date - today
required_velocity = hours_remaining / days_remaining
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NULAB_SPACE_URL` | Yes | Backlog space (e.g., `yourspace.backlog.com`) |
| `NULAB_API_KEY` | Yes | API key |
| `NULAB_PROJECT_ID` | Yes | Project key (e.g., `MYPROJECT`) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | Entry point - orchestrates API + analyzer |
| `scripts/backlog_client.py` | API client with rate limiting, pagination |
| `scripts/models.py` | Issue, User, Status, Project dataclasses |
| `scripts/status_analyzer.py` | Core analysis logic (Phase 3) |

## Tests

```bash
# Use forward slashes for Git Bash/MINGW64 compatibility
cd ".claude/skills/bk-status" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```
