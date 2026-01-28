---
name: bk-status
description: Check project progress - identify late tasks, overloaded members, health summary. Outputs Markdown report to ./project-status/
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
---

# bk-status - Project Status Check

Check Nulab Backlog project progress: late tasks, overloaded members, project health.

## Setup

```bash
# Copy .env.example and fill in credentials
cp .claude/skills/bk-status/.env.example .claude/skills/bk-status/.env

# Install dependencies
cd .claude/skills && .venv/Scripts/pip install -r bk-status/requirements.txt
```

## Usage

```
/bk-status [--threshold N]
```

**Examples:**
```
/bk-status                    # Default threshold: >5 issues = overloaded
/bk-status --threshold 3      # Custom threshold
```

## Workflow Instructions (for Claude Code)

### Step 1: Load Environment
Read `.claude/skills/bk-status/.env` for `NULAB_SPACE_URL`, `NULAB_API_KEY`, `NULAB_PROJECT_ID`.

### Step 2: Fetch Data
```bash
cd .claude/skills/bk-status && python scripts/main.py [--threshold N]
```

### Step 3: Report Output
Report saved to: `./project-status/YYYYMMDD-HHMMSS_{projectName}-status.md`

## Report Contents

| Section | Description |
|---------|-------------|
| Summary | Total issues, closed count, progress % |
| Late Tasks | Issues past due date (status != Closed) |
| Workload | Open issues per member |

## Late Task Logic

- **Late** = `dueDate < today` AND status is NOT "Closed"
- **Overloaded** = member has > threshold open issues (default: 5)

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
cd .claude/skills/bk-status && python -m pytest tests/ -v
```
