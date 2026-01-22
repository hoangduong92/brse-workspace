---
name: backlog
description: Automate ticket creation from customer backlog to internal backlog with AI translation (JA ↔ VI) and dynamic task templates
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Backlog Automation

Copy tickets from customer Nulab Backlog to internal backlog with automatic JA ↔ VI translation.

## Setup

```bash
# Copy .env.example to .env and fill in your API keys
cp .claude/skills/backlog/.env.example .claude/skills/backlog/.env

# Install dependencies (uses shared venv)
cd .claude/skills && .venv/Scripts/pip install -r backlog/requirements.txt
```

## Usage

**Via slash command:**
```
/backlog create-ticket HB21373-123
```

**With manual type override:**
```
/backlog create-ticket HB21373-123 --type=feature
```

**Dry run (preview without creating):**
```
/backlog create-ticket HB21373-123 --dry-run
```

**Direct execution:**
```bash
cd .claude/skills
.venv/Scripts/python backlog/scripts/main.py HB21373-123
.venv/Scripts/python backlog/scripts/main.py HB21373-123 --dry-run
.venv/Scripts/python backlog/scripts/main.py HB21373-123 --type=feature
```

## Task Types

| Type | Subtasks | Priority | Description |
|------|----------|----------|-------------|
| `feature` | 4 (Analysis, Implementation, Testing, Code Review) | Normal | Feature development |
| `scenario` | 0 | High | Upload scenario |
| `issue` | 0 | Urgent | Investigate issue |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NULAB_SPACE_URL` | Yes | Nulab space URL (e.g., `hblab.backlogtool.com`) |
| `NULAB_API_KEY` | Yes | Nulab API key (same project for MVP) |
| `NULAB_PROJECT_ID` | Yes | Nulab project ID (e.g., `HB21373`) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for translation |
| `CLAUDE_MODEL` | No | Model for translation (default: `claude-3-5-haiku-20241022`) |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

## Features

- Language detection (Japanese/Vietnamese)
- AI-powered translation (JA ↔ VI) via Claude Haiku
- Dynamic templates by task type
- Auto-subtask creation for feature development
- Attachment copying from source to destination
- Priority preservation from source ticket
